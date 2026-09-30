#!/usr/bin/env python3
"""parallel_review 通用单测与 CLI 冒烟。

覆盖：confidence 公式与钳制、去重/排序/计分/截断等纯函数、agent 注册表完整性、
报告委托（sarif 格式）、CLI（--help、JSON 输出、--output、无目标文件退出码）。
三态裁决专项见 test_three_state_adjudication.py。
"""
import asyncio
import json
import os
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

import parallel_review as pr

SCRIPT = os.path.join(os.path.dirname(__file__), "..", "scripts", "parallel_review.py")
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


class TestCalculateConfidence(unittest.TestCase):
    def test_base_without_evidence(self):
        self.assertEqual(pr.calculate_confidence({}), 50)

    def test_full_evidence_medium(self):
        issue = {
            "has_code_evidence": True,
            "matches_pattern": True,
            "has_fix_suggestion": True,
            "severity": "medium",
        }
        self.assertEqual(pr.calculate_confidence(issue), 85)

    def test_severity_deductions(self):
        full = {
            "has_code_evidence": True,
            "matches_pattern": True,
            "has_fix_suggestion": True,
        }
        self.assertEqual(pr.calculate_confidence(dict(full, severity="critical")), 95)
        self.assertEqual(pr.calculate_confidence(dict(full, severity="high")), 90)
        self.assertEqual(pr.calculate_confidence(dict(full, severity="low")), 95)

    def test_penalty_stack(self):
        issue = {"severity": "info", "is_pre_existing": True}
        self.assertEqual(pr.calculate_confidence(issue), 50 - 30)
        issue = {"severity": "info", "is_lint_catchable": True}
        self.assertEqual(pr.calculate_confidence(issue), 50 - 20)
        issue = {"severity": "info", "is_pedantic": True}
        self.assertEqual(pr.calculate_confidence(issue), 50 - 25)

    def test_unknown_severity_no_deduction(self):
        self.assertEqual(pr.calculate_confidence({"severity": "WHATEVER"}), 50)


class TestPureFunctions(unittest.TestCase):
    def test_deduplicate_keeps_first_and_preserves_order(self):
        issues = [
            {"file": "a.py", "line": 1, "category": "quality", "tag": "first"},
            {"file": "a.py", "line": 1, "category": "quality", "tag": "dup"},
            {"file": "a.py", "line": 2, "category": "quality", "tag": "other"},
        ]
        unique = pr.deduplicate_issues(issues)
        self.assertEqual([i["tag"] for i in unique], ["first", "other"])

    def test_sort_by_severity_ordering(self):
        issues = [
            {"severity": "low"},
            {"severity": "critical"},
            {"severity": "mystery"},
            {"severity": "high"},
        ]
        order = [i["severity"] for i in pr.sort_by_severity(issues)]
        self.assertEqual(order, ["critical", "high", "low", "mystery"])

    def test_calculate_score_deduction_model(self):
        issues = [
            {"severity": "critical"},
            {"severity": "high"},
            {"severity": "medium"},
            {"severity": "low"},
            {"severity": "info"},
        ]
        self.assertEqual(pr.calculate_score(issues), 100 - 15 - 8 - 3 - 1 - 0)

    def test_calculate_score_floors_at_zero(self):
        issues = [{"severity": "critical"}] * 10
        self.assertEqual(pr.calculate_score(issues), 0)

    def test_truncate_only_appends_ellipsis_when_truncated(self):
        self.assertEqual(pr._truncate("short"), "short")
        self.assertEqual(pr._truncate("x" * 61), "x" * 60 + "...")
        self.assertEqual(len(pr._truncate("x" * 60)), 60)


class TestAgentRegistry(unittest.TestCase):
    def test_seven_agents_with_unique_dimensions(self):
        agents = pr.get_review_agents()
        self.assertEqual(len(agents), 7)
        dimensions = [cfg["dimension"] for cfg in agents.values()]
        self.assertEqual(len(set(dimensions)), len(dimensions))

    def test_every_referenced_document_exists_on_disk(self):
        # FIX #11 回归：security-checklist 路径曾指向不存在的 references/security/
        for key, cfg in pr.get_review_agents().items():
            for ref in cfg["references"]:
                self.assertTrue(
                    os.path.isfile(os.path.join(REPO_ROOT, ref)),
                    f"{key} 引用的文档缺失: {ref}",
                )

    def test_adjudication_constants_documented_values(self):
        self.assertEqual(pr.CONFIDENCE_CONFIRMED, 80)
        self.assertEqual(pr.CONFIDENCE_CANDIDATE, 55)


class TestSarifDelegation(unittest.TestCase):
    def test_sarif_format_validates_against_sarif_report(self):
        import sarif_report

        result = make_completed(
            issues=[
                {
                    "file": "a.py",
                    "line": 3,
                    "severity": "high",
                    "category": "security",
                    "issue_type": "eval_usage",
                    "description": "d",
                    "recommendation": "r",
                    "confidence": 90,
                }
            ]
        )
        doc = json.loads(pr.generate_report([result], "sarif"))
        ok, errors = sarif_report.validate_sarif(doc)
        self.assertTrue(ok, errors)
        self.assertNotIn("__validation_errors__", doc)


def make_completed(issues):
    return pr.ReviewResult(
        agent_name="A",
        dimension="Security",
        issues=issues,
        confidence_scores=[i.get("confidence", 0) for i in issues],
        execution_time=0.0,
        status="completed",
    )


class TestCli(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)

    def _write(self, name, text):
        path = os.path.join(self._tmp.name, name)
        with open(path, "w", encoding="utf-8") as f:
            f.write(text)
        return path

    def test_help_exits_zero(self):
        proc = subprocess.run(
            [sys.executable, SCRIPT, "--help"], capture_output=True, text=True
        )
        self.assertEqual(proc.returncode, 0)
        self.assertIn("--min-confidence", proc.stdout)
        self.assertIn("--format", proc.stdout)

    def test_json_output_on_temp_file(self):
        target = self._write("s.py", "value = eval(user_input)\n")
        proc = subprocess.run(
            [sys.executable, SCRIPT, target, "--agents", "security", "--format", "json"],
            capture_output=True,
            text=True,
        )
        self.assertEqual(proc.returncode, 0)
        payload = json.loads(proc.stdout)
        self.assertEqual(payload["summary"]["agents_run"], 1)
        self.assertEqual(payload["agents"][0]["status"], "completed")

    def test_output_flag_writes_report_file(self):
        target = self._write("q.py", "for a in x:\n    for b in a:\n        pass\n")
        out = os.path.join(self._tmp.name, "report.md")
        proc = subprocess.run(
            [sys.executable, SCRIPT, target, "--agents", "performance", "--output", out],
            capture_output=True,
            text=True,
        )
        self.assertEqual(proc.returncode, 0)
        self.assertTrue(os.path.isfile(out))
        with open(out, encoding="utf-8") as f:
            self.assertIn("Code Review Report", f.read())

    def test_no_supported_files_exits_one(self):
        proc = subprocess.run(
            [sys.executable, SCRIPT, os.path.join(self._tmp.name, "missing")],
            capture_output=True,
            text=True,
        )
        self.assertEqual(proc.returncode, 1)
        self.assertIn("No supported source files found", proc.stderr)


if __name__ == "__main__":
    unittest.main()
