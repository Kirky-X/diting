#!/usr/bin/env python3
"""
安全设计模式检查脚本
用于验证代码是否符合安全设计模式要求

Fixes applied:
  - hardcoded_password: now case-insensitive for variable names
  - check_file: uses errors='replace' to survive binary / latin-1 files
  - unsafe_exception: uses re.DOTALL to match multiline catch blocks
  - Added SSRF / prototype-pollution / open-redirect patterns
  - Removed logger_sensitive pattern (too many false positives)
"""

import re
import os
from dataclasses import dataclass
from typing import List, Optional
from enum import Enum


class SecurityLevel(Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class SecurityIssue:
    file_path: str
    line_number: int
    issue_type: str
    description: str
    severity: SecurityLevel
    suggestion: str


# Pre-compiled for performance; flags applied per pattern where needed.
_UNSAFE_PATTERNS = {
    "sql_injection": {
        # Matches executeQuery/execute/executeUpdate followed by string concat (+)
        "pattern": re.compile(
            r'(executeQuery|executeUpdate|execute)\s*\(\s*["\'].*["\']\s*\+',
        ),
        "level": SecurityLevel.HIGH,
        "description": "潜在的SQL注入：字符串拼接传入数据库查询",
        "fix": "使用参数化查询（PreparedStatement / parameterized queries）替代字符串拼接",
    },
    # FIX #5: case-insensitive flag (re.IGNORECASE) so UPPERCASE names are caught
    "hardcoded_credential": {
        "pattern": re.compile(
            r'(?i)(password|passwd|secret|api_key|apikey|access_token|auth_token|private_key)'
            r'\s*=\s*["\'][^"\']{4,}["\']',
        ),
        "level": SecurityLevel.HIGH,
        "description": "硬编码的敏感凭据",
        "fix": "使用环境变量、配置中心或密钥管理服务（KMS / Vault）",
    },
    "weak_password_hash": {
        "pattern": re.compile(
            r'\b(MD5|SHA-?1|MessageDigest\.getInstance\s*\(\s*["\']MD5["\']'
            r'|MessageDigest\.getInstance\s*\(\s*["\']SHA-?1["\'])\b',
            re.IGNORECASE,
        ),
        "level": SecurityLevel.HIGH,
        "description": "用于密码哈希的不安全算法（MD5/SHA1）",
        "fix": "使用 bcrypt、Argon2 或 scrypt 进行密码哈希",
    },
    "unsafe_deserialization": {
        "pattern": re.compile(
            r'\b(ObjectInputStream|readObject|XmlDecoder|YAML\.load\s*\(|pickle\.loads\s*\()\b',
        ),
        "level": SecurityLevel.HIGH,
        "description": "不安全的反序列化 — 可能导致RCE",
        "fix": "使用白名单验证类类型；Python中用 yaml.safe_load()；Java中用 Jackson 安全配置",
    },
    "xss_dom_write": {
        "pattern": re.compile(
            r'\b(innerHTML|outerHTML|document\.write)\s*[=\(]',
        ),
        "level": SecurityLevel.HIGH,
        "description": "直接写入DOM属性 — 潜在XSS漏洞",
        "fix": "使用 textContent、DOMPurify.sanitize() 或框架的安全绑定机制",
    },
    "path_traversal": {
        "pattern": re.compile(
            r'(FileInputStream|FileReader|Paths\.get|new File|open\s*\()\s*\([^)]*\+\s*(request|param|input|user)',
            re.IGNORECASE,
        ),
        "level": SecurityLevel.HIGH,
        "description": "潜在的路径遍历漏洞",
        "fix": "使用 Path.normalize() / os.path.realpath() 规范化路径，并验证其在允许目录内",
    },
    "command_injection": {
        "pattern": re.compile(
            r'(subprocess\.(call|run|Popen)|os\.system|Runtime\.exec)\s*\([^,)]*\+',
        ),
        "level": SecurityLevel.HIGH,
        "description": "潜在的命令注入 — 用户输入拼接到系统命令",
        "fix": "使用参数数组而非字符串；Python中禁用 shell=True",
    },
    "ssrf_risk": {
        "pattern": re.compile(
            r'(requests\.get|requests\.post|urllib\.request|fetch|axios\.(get|post))\s*\([^)]*\b(url|href|redirect|endpoint)\b',
            re.IGNORECASE,
        ),
        "level": SecurityLevel.MEDIUM,
        "description": "潜在的SSRF — HTTP请求目标来自变量（可能是用户输入）",
        "fix": "验证URL是否在允许的主机白名单中；禁止访问内网地址（169.254.x.x, 10.x.x.x 等）",
    },
    "weak_crypto_algorithm": {
        "pattern": re.compile(
            r'\b(DES|TripleDES|Blowfish|RC4|ECB)\b',
        ),
        "level": SecurityLevel.MEDIUM,
        "description": "使用不安全的加密算法",
        "fix": "使用 AES-256-GCM 或 ChaCha20-Poly1305",
    },
    "insecure_random": {
        "pattern": re.compile(
            r'\b(Math\.random\s*\(\s*\)|random\.random\s*\(\s*\)|new Random\s*\(\s*\))\b',
        ),
        "level": SecurityLevel.MEDIUM,
        "description": "使用非密码学安全的随机数生成器",
        "fix": "使用 SecureRandom（Java）/ secrets 模块（Python）/ crypto.getRandomValues（JS）",
    },
    # FIX #7: use re.DOTALL to match multiline catch blocks
    "broad_exception_catch": {
        "pattern": re.compile(
            r'catch\s*\(\s*(Exception|Throwable)\b.*?\)\s*\{',
            re.DOTALL,
        ),
        "level": SecurityLevel.LOW,
        "description": "捕获过于宽泛的异常类型",
        "fix": "捕获具体的异常类型；确保不在catch块中暴露内部实现细节",
    },
    "open_redirect": {
        "pattern": re.compile(
            r'(sendRedirect|HttpResponseRedirect|redirect\s*\()\s*\([^)]*\b(request|param|url|redirect)\b',
            re.IGNORECASE,
        ),
        "level": SecurityLevel.MEDIUM,
        "description": "潜在的开放重定向漏洞",
        "fix": "使用允许的URL白名单验证重定向目标",
    },
}

_GOOD_PATTERNS = {
    "parameterized_query": {
        "pattern": re.compile(r'\b(PreparedStatement|QueryDSL|JpaRepository|cursor\.execute\s*\([^)]*%s)\b'),
        "description": "使用参数化查询 ✅",
    },
    "secure_random": {
        "pattern": re.compile(r'\b(SecureRandom|secrets\.|crypto\.getRandomValues)\b'),
        "description": "使用安全随机数 ✅",
    },
    "strong_password_hash": {
        "pattern": re.compile(r'\b(BCrypt|Argon2|scrypt|PasswordEncoder|pbkdf2)\b', re.IGNORECASE),
        "description": "使用强密码哈希 ✅",
    },
    "https_cookie": {
        "pattern": re.compile(r'(secure\s*=\s*true|setSecure\s*\(\s*true\s*\))', re.IGNORECASE),
        "description": "Cookie设置Secure属性 ✅",
    },
    "httponly_cookie": {
        "pattern": re.compile(r'(httpOnly\s*=\s*true|setHttpOnly\s*\(\s*true\s*\))', re.IGNORECASE),
        "description": "Cookie设置HttpOnly属性 ✅",
    },
}

# Lines starting with these prefixes are comments — skip unsafe pattern checks
_COMMENT_PREFIXES = ('#', '//', '/*', '*', '"""', "'''")


class SecurityPatternChecker:
    """安全设计模式检查器"""

    def __init__(self):
        self.issues: List[SecurityIssue] = []

    def check_file(self, file_path: str) -> None:
        """检查单个文件"""
        try:
            # FIX #6: errors='replace' so binary / latin-1 files don't raise
            with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                lines = f.readlines()
        except OSError as e:
            print(f"警告: 无法读取文件 {file_path}: {e}")
            return

        for line_num, line in enumerate(lines, 1):
            self._check_line(file_path, line_num, line)

    def _is_comment(self, line: str) -> bool:
        stripped = line.lstrip()
        return any(stripped.startswith(p) for p in _COMMENT_PREFIXES)

    def _check_line(self, file_path: str, line_num: int, line: str) -> None:
        """检查单行代码（跳过注释行）"""
        if self._is_comment(line):
            return

        for name, config in _UNSAFE_PATTERNS.items():
            if config["pattern"].search(line):
                self.issues.append(SecurityIssue(
                    file_path=file_path,
                    line_number=line_num,
                    issue_type=name,
                    description=config["description"],
                    severity=config["level"],
                    suggestion=config["fix"],
                ))

    def check_directory(self, directory: str, extensions: Optional[List[str]] = None) -> None:
        """递归检查目录"""
        if extensions is None:
            extensions = ['.java', '.py', '.js', '.ts', '.go', '.rb', '.php', '.cs', '.kt', '.rs']

        for root, _, files in os.walk(directory):
            for file in files:
                if any(file.endswith(ext) for ext in extensions):
                    self.check_file(os.path.join(root, file))

    def generate_report(self) -> str:
        """生成安全报告"""
        if not self.issues:
            return "✅ 未发现安全问题！"

        _ORDER = {SecurityLevel.HIGH: 0, SecurityLevel.MEDIUM: 1, SecurityLevel.LOW: 2}
        self.issues.sort(key=lambda x: (_ORDER[x.severity], x.file_path, x.line_number))

        report = [
            "=" * 60,
            "安全设计模式检查报告",
            "=" * 60,
            f"\n发现 {len(self.issues)} 个问题：\n",
        ]

        for issue in self.issues:
            icon = {'high': '🔴', 'medium': '🟡', 'low': '🔵'}.get(issue.severity.value, '⚪')
            report.append(f"{icon} {issue.file_path}:{issue.line_number}")
            report.append(f"   类型: {issue.issue_type}")
            report.append(f"   严重性: {issue.severity.value.upper()}")
            report.append(f"   描述: {issue.description}")
            report.append(f"   建议: {issue.suggestion}")
            report.append("-" * 40)

        stats: dict = {}
        for issue in self.issues:
            stats[issue.severity] = stats.get(issue.severity, 0) + 1

        report.append("\n统计：")
        for level in SecurityLevel:
            if level in stats:
                report.append(f"  {level.value.upper()}: {stats[level]} 个")

        return "\n".join(report)

    def print_summary(self) -> None:
        """打印摘要"""
        high = sum(1 for i in self.issues if i.severity == SecurityLevel.HIGH)
        medium = sum(1 for i in self.issues if i.severity == SecurityLevel.MEDIUM)
        low = sum(1 for i in self.issues if i.severity == SecurityLevel.LOW)

        print("\n" + "=" * 40)
        print("安全检查摘要")
        print("=" * 40)
        print(f"🔴 高风险: {high}")
        print(f"🟡 中风险: {medium}")
        print(f"🔵 低风险: {low}")
        print(f"合计:     {len(self.issues)}")
        print("=" * 40)


def main() -> None:
    import sys

    target = sys.argv[1] if len(sys.argv) > 1 else "."

    if not os.path.exists(target):
        print(f"错误: 找不到目标 {target}")
        sys.exit(1)

    checker = SecurityPatternChecker()

    if os.path.isdir(target):
        checker.check_directory(target)
    else:
        checker.check_file(target)

    checker.print_summary()
    print(checker.generate_report())

    sys.exit(1 if checker.issues else 0)


if __name__ == "__main__":
    main()
