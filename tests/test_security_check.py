#!/usr/bin/env python3
"""security_check 单测与 CLI 冒烟。

覆盖：注入/凭证/弱哈希/反序列化/XSS/弱随机等模式的真实命中与行号、
注释行跳过、大小写不敏感凭证（FIX #5）、DOTALL 多行 catch（FIX #7 与
"全文件匹配不逐行重复计数"）、insecure_random 边界修复（D-P1-3）、
good-pattern 白名单、报告排序与统计、目录递归、二进制文件容错、退出码。
"""
import os
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

import security_check as sc
from security_check import SecurityLevel, SecurityPatternChecker

SCRIPT = os.path.join(os.path.dirname(__file__), "..", "scripts", "security_check.py")


class CheckerCase(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.checker = SecurityPatternChecker()

    def write(self, name, text, encoding="utf-8"):
        path = os.path.join(self._tmp.name, name)
        with open(path, "w", encoding=encoding) as f:
            f.write(text)
        return path

    def check(self, name, text):
        path = self.write(name, text)
        self.checker.check_file(path)
        return path


class TestUnsafePatterns(CheckerCase):
    def test_sql_injection_with_line_number(self):
        self.check(
            "Dao.java",
            'Statement st = conn.createStatement();\n'
            'ResultSet rs = st.executeQuery("SELECT * FROM u WHERE id=" + input);\n',
        )
        self.assertEqual(
            [(i.issue_type, i.line_number) for i in self.checker.issues],
            [("sql_injection", 2)],
        )
        self.assertEqual(self.checker.issues[0].severity, SecurityLevel.HIGH)

    def test_hardcoded_credential_case_insensitive(self):
        # FIX #5 回归：UPPERCASE 变量名必须命中
        self.check(
            "cfg.py",
            'API_KEY = "supersecret12345"\npassword = "anothersecret9"\n',
        )
        self.assertEqual(
            sorted(i.line_number for i in self.checker.issues), [1, 2]
        )
        self.assertTrue(
            all(i.issue_type == "hardcoded_credential" for i in self.checker.issues)
        )

    def test_comment_lines_are_skipped(self):
        self.check("c.py", '# password = "incomment1234"\n// API_KEY = "alsosecret12"\n')
        self.assertEqual(self.checker.issues, [])

    def test_short_values_not_flagged(self):
        # 模式要求 4+ 个非引号字符，空串/短串不报
        self.check("ok.py", 'password = ""\napi_key = "ab"\n')
        self.assertEqual(self.checker.issues, [])

    def test_eval_usage(self):
        self.check("ev.py", "value = eval(user_input)\n")
        self.assertEqual([i.issue_type for i in self.checker.issues], ["eval_usage"])

    def test_insecure_random_variants(self):
        # D-P1-3 回归：random.random() / Math.random() / new Random() 都必须命中
        self.check(
            "rnd.py",
            "r = random.random()\nm = Math.random()\nj = new Random()\n",
        )
        self.assertEqual(
            [(i.issue_type, i.line_number) for i in self.checker.issues],
            [("insecure_random", 1), ("insecure_random", 2), ("insecure_random", 3)],
        )

    def test_weak_password_hash(self):
        self.check("h.py", "digest = MD5(pwd)\nold = SHA1(data)\n")
        self.assertEqual(
            {i.issue_type for i in self.checker.issues}, {"weak_password_hash"}
        )

    def test_unsafe_deserialization(self):
        self.check("d.py", "obj = pickle.loads(blob)\n")
        self.assertEqual(
            [i.issue_type for i in self.checker.issues], ["unsafe_deserialization"]
        )

    def test_xss_dom_write(self):
        self.check("x.js", "el.innerHTML = userHtml;\n")
        self.assertEqual([i.issue_type for i in self.checker.issues], ["xss_dom_write"])

    def test_weak_crypto(self):
        self.check("c2.py", "cipher = DES.new(key)\n")
        self.assertEqual(
            [i.issue_type for i in self.checker.issues], ["weak_crypto_algorithm"]
        )

    def test_ssrf_risk(self):
        self.check("s.py", 'resp = requests.get(url=user_url)\n')
        self.assertEqual([i.issue_type for i in self.checker.issues], ["ssrf_risk"])

    def test_clean_file_has_no_findings(self):
        self.check("clean.py", "x = 1\ny = compute(x)\nprint(y)\n")
        self.assertEqual(self.checker.issues, [])


class TestMultilinePatterns(CheckerCase):
    def test_broad_exception_catch_multiline(self):
        # FIX #7 回归：DOTALL 捕获跨行 catch 块，行号定位到 catch 行
        self.check(
            "Ex.java",
            "try {\n  doIt();\n} catch (Exception e) {\n  log(e);\n}\n",
        )
        self.assertEqual(
            [(i.issue_type, i.line_number) for i in self.checker.issues],
            [("broad_exception_catch", 3)],
        )

    def test_dotall_pattern_not_double_counted_per_line(self):
        # DOTALL 模式只全文件匹配一次，不再被逐行 fast path 重复计数
        self.check("Ex2.java", "catch (Throwable t) {\n  t.printStackTrace();\n}\n")
        broad = [i for i in self.checker.issues if i.issue_type == "broad_exception_catch"]
        self.assertEqual(len(broad), 1)


class TestBinaryTolerance(CheckerCase):
    def test_latin1_bytes_survive(self):
        # FIX #6 回归：errors='replace'，非 UTF-8 文件不抛异常
        path = os.path.join(self._tmp.name, "bin.py")
        with open(path, "wb") as f:
            f.write("eval(x)\n".encode("utf-8") + b"\xff\xfe\n")
        self.checker.check_file(path)
        self.assertEqual(
            sorted(i.issue_type for i in self.checker.issues), ["eval_usage"]
        )

    def test_unreadable_file_is_reported_not_raised(self):
        self.checker.check_file(os.path.join(self._tmp.name, "missing.py"))
        self.assertEqual(self.checker.issues, [])


class TestGoodPatterns(CheckerCase):
    def test_parameterized_query_and_secrets_are_clean(self):
        self.check(
            "good.py",
            "cursor.execute(\"SELECT * FROM t WHERE id=%s\", (uid,))\n"
            "token = secrets.token_hex(16)\n",
        )
        self.assertEqual(self.checker.issues, [])
        self.assertIn("No security issues found", self.checker.generate_report())


class TestReport(CheckerCase):
    def test_report_sorted_high_first_with_stats(self):
        self.write("ev.py", "value = eval(user_input)\n")  # HIGH
        self.write("Ex.java", "catch (Exception e) {\n}\n")  # LOW（DOTALL）
        self.checker.check_directory(self._tmp.name)
        report = self.checker.generate_report()
        self.assertIn("Found 2 issues", report)
        self.assertIn("Statistics:", report)
        self.assertIn("HIGH: 1", report)
        self.assertIn("LOW: 1", report)
        # HIGH 排在 LOW 之前
        self.assertLess(report.index("eval_usage"), report.index("broad_exception_catch"))

    def test_check_directory_filters_extensions(self):
        self.write("note.txt", "eval(x)\n")  # 非源码扩展名 → 不扫
        self.checker.check_directory(self._tmp.name)
        self.assertEqual(self.checker.issues, [])


class TestCli(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)

    def _write(self, name, text):
        path = os.path.join(self._tmp.name, name)
        with open(path, "w", encoding="utf-8") as f:
            f.write(text)
        return path

    def test_exit_zero_on_clean_file(self):
        path = self._write("clean.py", "x = 1\n")
        proc = subprocess.run(
            [sys.executable, SCRIPT, path], capture_output=True, text=True
        )
        self.assertEqual(proc.returncode, 0)
        self.assertIn("No security issues found", proc.stdout)

    def test_exit_one_on_findings(self):
        path = self._write("dirty.py", 'API_KEY = "supersecret12345"\n')
        proc = subprocess.run(
            [sys.executable, SCRIPT, path], capture_output=True, text=True
        )
        self.assertEqual(proc.returncode, 1)
        self.assertIn("hardcoded_credential", proc.stdout)

    def test_exit_one_on_missing_target(self):
        proc = subprocess.run(
            [sys.executable, SCRIPT, os.path.join(self._tmp.name, "nope.py")],
            capture_output=True,
            text=True,
        )
        self.assertEqual(proc.returncode, 1)


if __name__ == "__main__":
    unittest.main()
