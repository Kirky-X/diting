#!/usr/bin/env python3
"""analyzer 单测与 CLI 冒烟。

覆盖：语言检测、代码度量（行数/注释/圈复杂度含 BoolOp N-1 修复）、
issue 检测（长方法含嵌套 def 栈修复与 EOF flush、深嵌套、长行、TODO、
魔数白名单、可访问性、null-chain、check-then-act、除零与字符串字面量
状态机）、结构提取、目录分析、CLI JSON 输出与退出码。
"""
import json
import os
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

import analyzer as az
from analyzer import CodeAnalyzer, analyze_directory, analyze_file

SCRIPT = os.path.join(os.path.dirname(__file__), "..", "scripts", "analyzer.py")


class AnalyzerCase(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)

    def write(self, name, text):
        path = os.path.join(self._tmp.name, name)
        with open(path, "w", encoding="utf-8") as f:
            f.write(text)
        return path

    def issues_of(self, result, category=None, desc_prefix=None):
        out = result.issues
        if category:
            out = [i for i in out if i["category"] == category]
        if desc_prefix:
            out = [i for i in out if i["description"].startswith(desc_prefix)]
        return out


class TestLanguageDetection(unittest.TestCase):
    def test_extension_mapping(self):
        analyzer = CodeAnalyzer()
        cases = {
            "a.py": "python",
            "b.js": "javascript",
            "c.tsx": "typescript",
            "d.java": "java",
            "e.rs": "rust",
            "f.md": "unknown",
        }
        for name, expected in cases.items():
            self.assertEqual(analyzer._detect_language(name), expected, name)


class TestMetrics(AnalyzerCase):
    def test_line_counts(self):
        path = self.write("m.py", "x = 1\n\n# comment\ny = 2\n")
        metrics = analyze_file(path).metrics
        # content.split("\n") 使结尾换行产生一个尾随空元素 → 5 行、2 个空白行
        self.assertEqual(metrics["total_lines"], 5)
        # lines_of_code 统计非空行（含注释行）
        self.assertEqual(metrics["lines_of_code"], 3)
        self.assertEqual(metrics["blank_lines"], 2)
        self.assertEqual(metrics["comment_lines"], 1)

    def test_cyclomatic_complexity_counts_decision_points(self):
        # 基数 1 + if 1 + BoolOp(3 操作数 → +2) + for + while + except = 7
        path = self.write(
            "cc.py",
            "def f(a, b):\n"
            "    if a and b or a:\n"
            "        return 1\n"
            "    for i in range(3):\n"
            "        while a:\n"
            "            a -= 1\n"
            "    try:\n"
            "        pass\n"
            "    except ValueError:\n"
            "        pass\n",
        )
        metrics = analyze_file(path).metrics
        self.assertEqual(metrics["cyclomatic_complexity"], 7)
        self.assertEqual(metrics["function_count"], 1)

    def test_syntax_error_leaves_python_metrics_at_defaults(self):
        path = self.write("bad.py", "def f(:\n")
        result = analyze_file(path)
        self.assertEqual(result.metrics["cyclomatic_complexity"], 0)
        self.assertNotIn("function_count", result.metrics)

    def test_block_comment_counting_c_style(self):
        analyzer = CodeAnalyzer()
        count = analyzer._count_comments(["/* a", "b */", "// c", "x = 1"], "javascript")
        self.assertEqual(count, 3)


class TestIssueDetection(AnalyzerCase):
    def test_long_line_flagged(self):
        path = self.write("ll.py", "s = '" + "a" * 130 + "'\n")
        found = self.issues_of(analyze_file(path), category="style")
        self.assertEqual(len(found), 1)
        self.assertEqual(found[0]["severity"], "low")

    def test_todo_and_fixme_comments(self):
        path = self.write("t.py", "# TODO fix later\nx = 1  # FIXME now\n")
        found = self.issues_of(analyze_file(path), category="maintenance")
        self.assertEqual(
            [i["description"] for i in found], ["TODO comment found", "FIXME comment found"]
        )

    def test_magic_numbers_respect_whitelist_and_skip_comments(self):
        path = self.write("mg.py", "# t = 314\nv = 314\nw = x % 86400\n")
        found = self.issues_of(analyze_file(path), category="quality")
        self.assertEqual([i["description"] for i in found], ["Magic number 314 — consider a named constant"])
        self.assertEqual(found[0]["line"], 2)

    def test_deep_nesting_threshold(self):
        # 缩进 20 → level 5 > 阈值 4；缩进 16 → level 4 不报
        path = self.write(
            "deep.py",
            "def f():\n"
            + "".join(" " * (4 * k) + f"if x{k}:\n" for k in range(1, 5))
            + " " * 20
            + "pass\n",
        )
        found = self.issues_of(
            analyze_file(path), category="quality", desc_prefix="Deep nesting"
        )
        self.assertEqual([i["line"] for i in found], [6])

    def test_long_method_with_nested_def_and_eof_flush(self):
        body = "\n".join("    line%d" % i for i in range(60))
        path = self.write("lm.py", "def outer():\n" + body + "\n\ndef tiny():\n    pass\n")
        found = self.issues_of(analyze_file(path), desc_prefix="Long method")
        self.assertEqual([(i["method"], i["line"]) for i in found], [("outer", 1)])

        path2 = self.write("lm2.py", "def outer():\n" + body)
        found2 = self.issues_of(analyze_file(path2), desc_prefix="Long method")
        self.assertEqual(len(found2), 1)  # EOF flush 兜底

    def test_normal_method_calls_not_flagged_as_null_chain(self):
        # 反误报保证：普通 obj.method() 调用不得命中 null-chain 模式
        path = self.write("normal.py", "v = obj.compute(1, 2)\nw = service.handle(req)\n")
        self.assertEqual(self.issues_of(analyze_file(path), category="correctness"), [])

    def test_python_null_chain_detection(self):
        path = self.write(
            "nc.py",
            "v = cfg.get('k').strip()\nv2 = re.match(r'(\\d+)', s).group(1)\n",
        )
        found = self.issues_of(analyze_file(path), category="correctness")
        self.assertEqual(len(found), 2)
        # 按模式迭代序输出（re.match 模式先于 dict.get 模式），与行序无关
        self.assertEqual(sorted(i["line"] for i in found), [1, 2])

    def test_js_optional_chaining_line_skipped(self):
        path = self.write(
            "g.js",
            "const a = obj?.name.match(rx).group;\nconst b = name.match(rx).group;\n",
        )
        found = self.issues_of(analyze_file(path), category="correctness")
        self.assertEqual([i["line"] for i in found], [2])

    def test_check_then_act_race_detected(self):
        path = self.write("r.py", "if f.exists():\n    write(f)\n")
        found = self.issues_of(analyze_file(path), category="correctness")
        self.assertEqual(len(found), 1)
        self.assertEqual(found[0]["severity"], "high")

    def test_division_without_zero_check_flagged(self):
        path = self.write("d1.py", "q = total / count\n")
        found = self.issues_of(analyze_file(path), desc_prefix="Division")
        self.assertEqual([i["line"] for i in found], [1])

    def test_division_suppressed_when_zero_check_in_context(self):
        path = self.write("d2.py", "if count != 0:\n    q = total / count\n")
        self.assertEqual(self.issues_of(analyze_file(path), desc_prefix="Division"), [])

    def test_division_inside_string_literal_suppressed(self):
        path = self.write("d3.py", "s = 'a / b'\n")
        self.assertEqual(self.issues_of(analyze_file(path), desc_prefix="Division"), [])

    def test_string_literal_state_machine_handles_escapes(self):
        analyzer = CodeAnalyzer()
        self.assertTrue(analyzer._is_in_string_literal("x = 'abc' + c", 7))
        self.assertFalse(analyzer._is_in_string_literal("x = 'abc' + c", 12))
        # 反斜杠转义的引号不结束字符串
        self.assertTrue(analyzer._is_in_string_literal("x = 'a\\'b' + c", 8))


class TestAccessibility(AnalyzerCase):
    def test_frontend_issues_detected(self):
        path = self.write(
            "p.html",
            '<img src="x.png">\n<input type="text" name="q">\n<div>{ outline: none; }</div>\n',
        )
        found = self.issues_of(analyze_file(path), category="accessibility")
        self.assertEqual(len(found), 3)
        self.assertTrue(all(i["severity"] == "high" for i in found))

    def test_labeled_input_not_flagged(self):
        path = self.write("ok.html", '<input type="text" aria-label="query">\n')
        self.assertEqual(self.issues_of(analyze_file(path), category="accessibility"), [])

    def test_non_frontend_file_skipped(self):
        path = self.write("p.py", "<img src='x.png'>\n")
        self.assertEqual(self.issues_of(analyze_file(path), category="accessibility"), [])


class TestStructureAndDirectory(AnalyzerCase):
    def test_python_structure_extraction(self):
        path = self.write(
            "st.py",
            "import json\nfrom os.path import join\n\nclass A:\n    def m(self):\n        pass\n",
        )
        structure = analyze_file(path).structure
        self.assertEqual(structure["imports"], ["json", "os.path.join"])
        self.assertEqual(structure["classes"], ["A"])
        self.assertEqual(structure["functions"], ["m"])

    def test_analyze_directory_only_code_files(self):
        self.write("code.py", "x = 1\n")
        self.write("skip.txt", "hello\n")
        results = analyze_directory(self._tmp.name)
        self.assertEqual([os.path.basename(r.file_path) for r in results], ["code.py"])


class TestCli(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)

    def test_file_json_output(self):
        path = os.path.join(self._tmp.name, "a.py")
        with open(path, "w", encoding="utf-8") as f:
            f.write("import json\nx = 314\n")
        proc = subprocess.run(
            [sys.executable, SCRIPT, path], capture_output=True, text=True
        )
        self.assertEqual(proc.returncode, 0)
        payload = json.loads(proc.stdout)
        self.assertEqual(payload["language"], "python")
        self.assertTrue(any("Magic number 314" in i["description"] for i in payload["issues"]))

    def test_missing_args_exit_one(self):
        proc = subprocess.run([sys.executable, SCRIPT], capture_output=True, text=True)
        self.assertEqual(proc.returncode, 1)
        self.assertIn("Usage", proc.stdout)


if __name__ == "__main__":
    unittest.main()
