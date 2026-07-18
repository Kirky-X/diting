#!/usr/bin/env python3
"""
Security Design Pattern Check Script

Used to verify code compliance with security design pattern requirements.

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
        "description": "Potential SQL injection: string concatenation passed to database query",
        "fix": "Use parameterized queries (PreparedStatement / parameterized queries) instead of string concatenation",
    },
    # FIX #5: case-insensitive flag (re.IGNORECASE) so UPPERCASE names are caught
    "hardcoded_credential": {
        "pattern": re.compile(
            r"(?i)(password|passwd|secret|api_key|apikey|access_token|auth_token|private_key)"
            r'\s*=\s*["\'][^"\']{4,}["\']',
        ),
        "level": SecurityLevel.HIGH,
        "description": "Hardcoded sensitive credentials",
        "fix": "Use environment variables, config center, or key management service (KMS / Vault)",
    },
    "weak_password_hash": {
        "pattern": re.compile(
            r'\b(MD5|SHA-?1|MessageDigest\.getInstance\s*\(\s*["\']MD5["\']'
            r'|MessageDigest\.getInstance\s*\(\s*["\']SHA-?1["\'])\b',
            re.IGNORECASE,
        ),
        "level": SecurityLevel.HIGH,
        "description": "Insecure algorithm used for password hashing (MD5/SHA1)",
        "fix": "Use bcrypt, Argon2, or scrypt for password hashing",
    },
    "unsafe_deserialization": {
        "pattern": re.compile(
            r"\b(ObjectInputStream|readObject|XmlDecoder|YAML\.load\s*\(|pickle\.loads\s*\()\b",
        ),
        "level": SecurityLevel.HIGH,
        "description": "Unsafe deserialization — may lead to RCE",
        "fix": "Use whitelist validation for class types; use yaml.safe_load() in Python; use Jackson safe configuration in Java",
    },
    "xss_dom_write": {
        "pattern": re.compile(
            r"\b(innerHTML|outerHTML|document\.write)\s*[=\(]",
        ),
        "level": SecurityLevel.HIGH,
        "description": "Direct DOM attribute write — potential XSS vulnerability",
        "fix": "Use textContent, DOMPurify.sanitize(), or framework safe binding mechanisms",
    },
    "path_traversal": {
        "pattern": re.compile(
            r"(FileInputStream|FileReader|Paths\.get|new File|open\s*\()\s*\([^)]*\+\s*(request|param|input|user)",
            re.IGNORECASE,
        ),
        "level": SecurityLevel.HIGH,
        "description": "Potential path traversal vulnerability",
        "fix": "Use Path.normalize() / os.path.realpath() to normalize paths and validate they are within allowed directories",
    },
    "command_injection": {
        "pattern": re.compile(
            r"(subprocess\.(call|run|Popen)|os\.system|Runtime\.exec)\s*\([^,)]*\+",
        ),
        "level": SecurityLevel.HIGH,
        "description": "Potential command injection — user input concatenated into system command",
        "fix": "Use parameter arrays instead of strings; disable shell=True in Python",
    },
    "eval_usage": {
        # Consolidated single source for eval() detection (previously duplicated in
        # parallel_review.py as _EVAL_RE). eval() on untrusted input → direct RCE.
        "pattern": re.compile(r"\beval\s*\("),
        "level": SecurityLevel.HIGH,
        "description": "eval() usage — potential code injection vector",
        "fix": "Avoid eval; use safe alternatives (ast.literal_eval, JSON.parse, shutil.which, etc.)",
    },
    "ssrf_risk": {
        "pattern": re.compile(
            r"(requests\.get|requests\.post|urllib\.request|fetch|axios\.(get|post))\s*\([^)]*\b(url|href|redirect|endpoint)\b",
            re.IGNORECASE,
        ),
        "level": SecurityLevel.MEDIUM,
        "description": "Potential SSRF — HTTP request target comes from a variable (possibly user input)",
        "fix": "Validate URL against allowed host whitelist; prohibit access to internal network addresses (169.254.x.x, 10.x.x.x, etc.)",
    },
    "weak_crypto_algorithm": {
        "pattern": re.compile(
            r"\b(DES|TripleDES|Blowfish|RC4|ECB)\b",
        ),
        "level": SecurityLevel.MEDIUM,
        "description": "Use of insecure encryption algorithm",
        "fix": "Use AES-256-GCM or ChaCha20-Poly1305",
    },
    "insecure_random": {
        "pattern": re.compile(
            # D-P1-3: removed trailing \b — after ')' (non-word char) \b never matches,
            # causing Math.random() / random.random() / new Random() to be silently missed
            r"\b(Math\.random\s*\(\s*\)|random\.random\s*\(\s*\)|new Random\s*\(\s*\))",
        ),
        "level": SecurityLevel.MEDIUM,
        "description": "Use of non-cryptographically secure random number generator",
        "fix": "Use SecureRandom (Java) / secrets module (Python) / crypto.getRandomValues (JS)",
    },
    # FIX #7: use re.DOTALL to match multiline catch blocks
    "broad_exception_catch": {
        "pattern": re.compile(
            r"catch\s*\(\s*(Exception|Throwable)\b.*?\)\s*\{",
            re.DOTALL,
        ),
        "level": SecurityLevel.LOW,
        "description": "Catching overly broad exception type",
        "fix": "Catch specific exception types; ensure internal implementation details are not exposed in catch blocks",
    },
    "open_redirect": {
        "pattern": re.compile(
            r"(sendRedirect|HttpResponseRedirect|redirect\s*\()\s*\([^)]*\b(request|param|url|redirect)\b",
            re.IGNORECASE,
        ),
        "level": SecurityLevel.MEDIUM,
        "description": "Potential open redirect vulnerability",
        "fix": "Validate redirect targets against an allowed URL whitelist",
    },
}

_GOOD_PATTERNS = {
    "parameterized_query": {
        "pattern": re.compile(
            r"\b(PreparedStatement|QueryDSL|JpaRepository|cursor\.execute\s*\([^)]*%s)\b"
        ),
        "description": "Uses parameterized queries ✅",
    },
    "secure_random": {
        "pattern": re.compile(r"\b(SecureRandom|secrets\.|crypto\.getRandomValues)\b"),
        "description": "Uses secure random ✅",
    },
    "strong_password_hash": {
        "pattern": re.compile(
            r"\b(BCrypt|Argon2|scrypt|PasswordEncoder|pbkdf2)\b", re.IGNORECASE
        ),
        "description": "Uses strong password hashing ✅",
    },
    "https_cookie": {
        "pattern": re.compile(
            r"(secure\s*=\s*true|setSecure\s*\(\s*true\s*\))", re.IGNORECASE
        ),
        "description": "Cookie sets Secure attribute ✅",
    },
    "httponly_cookie": {
        "pattern": re.compile(
            r"(httpOnly\s*=\s*true|setHttpOnly\s*\(\s*true\s*\))", re.IGNORECASE
        ),
        "description": "Cookie sets HttpOnly attribute ✅",
    },
}

# Lines starting with these prefixes are comments — skip unsafe pattern checks
_COMMENT_PREFIXES = ("#", "//", "/*", "*", '"""', "'''")


class SecurityPatternChecker:
    """Security Design Pattern Checker"""

    def __init__(self):
        self.issues: List[SecurityIssue] = []

    def check_file(self, file_path: str) -> None:
        """Check a single file"""
        try:
            # FIX #6: errors='replace' so binary / latin-1 files don't raise
            with open(file_path, "r", encoding="utf-8", errors="replace") as f:
                content = f.read()
        except OSError as e:
            print(f"Warning: Unable to read file {file_path}: {e}")
            return

        lines = content.splitlines(keepends=True)

        # Bug 3 fix: match patterns with re.DOTALL against the entire file content (so DOTALL actually takes effect)
        # Multi-line patterns (e.g., broad_exception_catch spanning catch blocks) must match against the entire content
        for name, config in _UNSAFE_PATTERNS.items():
            pattern = config["pattern"]
            if pattern.flags & re.DOTALL:
                match = pattern.search(content)
                if match:
                    line_number = content.count("\n", 0, match.start()) + 1
                    self.issues.append(
                        SecurityIssue(
                            file_path=file_path,
                            line_number=line_number,
                            issue_type=name,
                            description=config["description"],
                            severity=config["level"],
                            suggestion=config["fix"],
                        )
                    )

        # Single-line patterns (without DOTALL) — match line by line (fast path)
        for line_num, line in enumerate(lines, 1):
            self._check_line(file_path, line_num, line)

    def _is_comment(self, line: str) -> bool:
        stripped = line.lstrip()
        return any(stripped.startswith(p) for p in _COMMENT_PREFIXES)

    def _check_line(self, file_path: str, line_num: int, line: str) -> None:
        """Check a single line of code (skip comment lines) — only handles single-line patterns"""
        if self._is_comment(line):
            return

        for name, config in _UNSAFE_PATTERNS.items():
            pattern = config["pattern"]
            # Bug 3 fix: skip patterns with DOTALL (already matched against full file in check_file)
            if pattern.flags & re.DOTALL:
                continue
            if pattern.search(line):
                self.issues.append(
                    SecurityIssue(
                        file_path=file_path,
                        line_number=line_num,
                        issue_type=name,
                        description=config["description"],
                        severity=config["level"],
                        suggestion=config["fix"],
                    )
                )

    def check_directory(
        self, directory: str, extensions: Optional[List[str]] = None
    ) -> None:
        """Recursively check a directory"""
        if extensions is None:
            extensions = [
                ".java",
                ".py",
                ".js",
                ".ts",
                ".go",
                ".rb",
                ".php",
                ".cs",
                ".kt",
                ".rs",
            ]

        for root, _, files in os.walk(directory):
            for file in files:
                if any(file.endswith(ext) for ext in extensions):
                    self.check_file(os.path.join(root, file))

    def generate_report(self) -> str:
        """Generate security report"""
        if not self.issues:
            return "✅ No security issues found!"

        _ORDER = {SecurityLevel.HIGH: 0, SecurityLevel.MEDIUM: 1, SecurityLevel.LOW: 2}
        self.issues.sort(key=lambda x: (_ORDER[x.severity], x.file_path, x.line_number))

        report = [
            "=" * 60,
            "Security Design Pattern Check Report",
            "=" * 60,
            f"\nFound {len(self.issues)} issues:\n",
        ]

        for issue in self.issues:
            icon = {"high": "🔴", "medium": "🟡", "low": "🔵"}.get(
                issue.severity.value, "⚪"
            )
            report.append(f"{icon} {issue.file_path}:{issue.line_number}")
            report.append(f"   Type: {issue.issue_type}")
            report.append(f"   Severity: {issue.severity.value.upper()}")
            report.append(f"   Description: {issue.description}")
            report.append(f"   Suggestion: {issue.suggestion}")
            report.append("-" * 40)

        stats: dict = {}
        for issue in self.issues:
            stats[issue.severity] = stats.get(issue.severity, 0) + 1

        report.append("\nStatistics:")
        for level in SecurityLevel:
            if level in stats:
                report.append(f"  {level.value.upper()}: {stats[level]}")

        return "\n".join(report)

    def print_summary(self) -> None:
        """Print summary"""
        high = sum(1 for i in self.issues if i.severity == SecurityLevel.HIGH)
        medium = sum(1 for i in self.issues if i.severity == SecurityLevel.MEDIUM)
        low = sum(1 for i in self.issues if i.severity == SecurityLevel.LOW)

        print("\n" + "=" * 40)
        print("Security Check Summary")
        print("=" * 40)
        print(f"🔴 High risk: {high}")
        print(f"🟡 Medium risk: {medium}")
        print(f"🔵 Low risk: {low}")
        print(f"Total:       {len(self.issues)}")
        print("=" * 40)


def main() -> None:
    import sys

    target = sys.argv[1] if len(sys.argv) > 1 else "."

    if not os.path.exists(target):
        print(f"Error: Target not found {target}")
        sys.exit(1)

    checker = SecurityPatternChecker()

    if os.path.isdir(target):
        checker.check_directory(target)
    else:
        checker.check_file(target)

    checker.print_summary()
    print(checker.generate_report())

    # P1: CodeNexus bridge — emit a blast-radius worklist to stderr when an index
    # is present. The agent layer runs the listed `codenexus` CLI commands (the CLI
    # is not invoked from this subprocess). See SKILL.md Step 1.5.
    try:
        import codenexus_helpers

        findings = [
            {
                "file": si.file_path,
                "line": si.line_number,
                "severity": si.severity.value,
                "category": "security",
                "issue_type": si.issue_type,
            }
            for si in checker.issues
        ]
        section = codenexus_helpers.section_for_findings(findings, start=target)
        if section:
            import sys as _sys

            print("\n" + section, file=_sys.stderr)
    except ImportError:
        pass

    sys.exit(1 if checker.issues else 0)


if __name__ == "__main__":
    main()
