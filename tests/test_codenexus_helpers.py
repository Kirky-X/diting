#!/usr/bin/env python3
"""codenexus_helpers 单测。

覆盖：CodeNexus 索引探测（向上走查/文件参数/未命中回退）、enclosing_symbol
回溯、impact 目标抽取（严重度过滤/排序/去重/上限/symbol 覆盖）、概念查询
生成、markdown 段落渲染（空输入返回空串、db 标志、引号转义）、
section_for_findings 无索引时优雅空输出。
"""
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

import codenexus_helpers as cn


class DbDetectionCase(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.root = self._tmp.name

    def touch_db(self, directory):
        path = os.path.join(directory, "codenexus.lbug")
        with open(path, "w") as f:
            f.write("")
        return path


class TestFindDb(DbDetectionCase):
    def test_no_db_anywhere_returns_none(self):
        nested = os.path.join(self.root, "a", "b")
        os.makedirs(nested)
        self.assertIsNone(cn._find_db(nested))
        self.assertFalse(cn.index_available(nested))

    def test_walks_up_to_parent_db(self):
        nested = os.path.join(self.root, "a", "b")
        os.makedirs(nested)
        db = self.touch_db(self.root)
        self.assertEqual(cn._find_db(nested), db)
        self.assertTrue(cn.index_available(nested))

    def test_file_argument_uses_its_directory(self):
        db = self.touch_db(self.root)
        some_file = os.path.join(self.root, "m.py")
        with open(some_file, "w") as f:
            f.write("x = 1\n")
        self.assertEqual(cn._find_db(some_file), db)

    def test_find_repo_root(self):
        nested = os.path.join(self.root, "a")
        os.makedirs(nested)
        self.assertEqual(cn.find_repo_root(nested), os.path.abspath(nested))
        db = self.touch_db(self.root)
        self.assertEqual(cn.find_repo_root(nested), os.path.dirname(db))


class TestEnclosingSymbol(DbDetectionCase):
    def test_walks_back_to_nearest_definition(self):
        source = os.path.join(self.root, "m.py")
        with open(source, "w") as f:
            f.write("def top():\n    x = 1\n\nclass C:\n    def meth(self):\n        y = 2\n")
        self.assertEqual(cn.enclosing_symbol(source, 6), "meth")
        self.assertEqual(cn.enclosing_symbol(source, 2), "top")
        self.assertEqual(cn.enclosing_symbol(source, 1), "top")

    def test_missing_file_returns_none(self):
        self.assertIsNone(cn.enclosing_symbol(os.path.join(self.root, "nope.py"), 1))


class TestBuildImpactTargets(unittest.TestCase):
    SOURCE = "def top():\n    x = 1\n\nclass C:\n    def meth(self):\n        y = 2\n"

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.source = os.path.join(self._tmp.name, "m.py")
        with open(self.source, "w") as f:
            f.write(self.SOURCE)

    def finding(self, severity="high", line=2, category="security", **extra):
        return dict(
            file=self.source, line=line, severity=severity, category=category, **extra
        )

    def test_only_critical_and_high_considered(self):
        targets = cn.build_impact_targets(
            [self.finding("medium"), self.finding("low"), self.finding("info")]
        )
        self.assertEqual(targets, [])

    def test_critical_sorted_before_high(self):
        targets = cn.build_impact_targets(
            [self.finding("high", line=2), self.finding("critical", line=6)]
        )
        self.assertEqual([t.severity for t in targets], ["critical", "high"])

    def test_symbols_recovered_from_source(self):
        targets = cn.build_impact_targets([self.finding("high", line=6)])
        self.assertEqual([t.symbol for t in targets], ["meth"])

    def test_symbol_override_wins(self):
        targets = cn.build_impact_targets([self.finding(symbol="custom")])
        self.assertEqual([t.symbol for t in targets], ["custom"])

    def test_dedup_by_symbol_and_basename(self):
        duplicated = [
            self.finding("high", line=6),
            self.finding("critical", line=2),  # 同文件不同 symbol → 保留
            self.finding("critical", line=6),  # 同 symbol → 去重
        ]
        targets = cn.build_impact_targets(duplicated)
        self.assertEqual(sorted(t.symbol for t in targets), ["meth", "top"])

    def test_max_targets_cap(self):
        many = [
            self.finding("high", line=i + 1, category="quality", symbol=f"s{i}")
            for i in range(20)
        ]
        self.assertEqual(len(cn.build_impact_targets(many, max_targets=3)), 3)

    def test_findings_without_location_skipped(self):
        targets = cn.build_impact_targets([{"severity": "high", "line": 1}])
        self.assertEqual(targets, [])

    def test_rule_id_from_issue_type_or_category(self):
        with_type = cn.build_impact_targets([self.finding(issue_type="eval_usage")])
        self.assertEqual(with_type[0].rule_id, "security/eval_usage")
        without_type = cn.build_impact_targets([self.finding()])
        self.assertEqual(without_type[0].rule_id, "security")


class TestQueryConcepts(unittest.TestCase):
    def test_known_and_unknown_categories(self):
        findings = [
            {"category": "performance"},
            {"category": "security"},
            {"category": "weird"},
            {"category": ""},
        ]
        concepts = cn.build_query_concepts(findings)
        self.assertEqual(
            concepts,
            [
                "hot loop and query execution path",
                "security-sensitive code path",
                "weird execution flow",
            ],
        )

    def test_empty_findings(self):
        self.assertEqual(cn.build_query_concepts([]), [])


class TestFormatSection(unittest.TestCase):
    def test_empty_inputs_return_empty_string(self):
        self.assertEqual(cn.format_codenexus_section([], []), "")

    def test_contains_impact_commands_and_db_flag(self):
        target = cn.ImpactTarget(
            symbol="meth",
            file="/r/m.py",
            line=6,
            severity="critical",
            category="security",
            rule_id="security/eval_usage",
        )
        section = cn.format_codenexus_section([target], ["security path"], repo_root="/r", db="/r/codenexus.lbug")
        self.assertIn("CodeNexus Blast Radius Pre-check", section)
        self.assertIn("codenexus impact --symbol meth --depth 3", section)
        self.assertIn("--db /r/codenexus.lbug", section)
        self.assertIn("codenexus query --cypher", section)

    def test_double_quotes_escaped_for_cypher(self):
        section = cn.format_codenexus_section([], ['say "hi"'])
        self.assertNotIn('"hi"', section)
        self.assertIn("'hi'", section)


class TestSectionForFindings(unittest.TestCase):
    def test_no_db_graceful_empty(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(
                cn.section_for_findings(
                    [{"file": os.path.join(tmp, "m.py"), "line": 1, "severity": "high"}],
                    start=tmp,
                ),
                "",
            )

    def test_with_db_emits_section(self):
        with tempfile.TemporaryDirectory() as tmp:
            db = os.path.join(tmp, "codenexus.lbug")
            with open(db, "w") as f:
                f.write("")
            source = os.path.join(tmp, "m.py")
            with open(source, "w") as f:
                f.write("def top():\n    eval(x)\n")
            section = cn.section_for_findings(
                [
                    {
                        "file": source,
                        "line": 2,
                        "severity": "critical",
                        "category": "security",
                        "issue_type": "eval_usage",
                    }
                ],
                start=tmp,
            )
            self.assertIn("codenexus impact --symbol top", section)
            self.assertIn(f"--db {db}", section)


if __name__ == "__main__":
    unittest.main()
