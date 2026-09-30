#!/usr/bin/env python3
"""sarif_report 单测与 CLI 冒烟。

覆盖：severity→level 映射、ruleId 构造、location/region 形状、
to_sarif 三来源聚合（ReviewResult / AnalysisResult / SecurityIssue，
跳过未完成 agent 与无位置发现）、_build_rules 去重、validate_sarif
对合法/非法文档的判定、from_parallel_json_report 与指纹稳定性、
set_tool_info 覆盖（测试内恢复默认）、CLI（--help/--validate/--output/坏输入）。
"""
import json
import os
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

import sarif_report as sr
import security_check as sc
from security_check import SecurityIssue, SecurityLevel

SCRIPT = os.path.join(os.path.dirname(__file__), "..", "scripts", "sarif_report.py")


class FakeReviewResult:
    """duck-typed parallel_review.ReviewResult：只暴露 to_sarif 用到的属性。"""

    def __init__(self, issues, status="completed"):
        self.status = status
        self.issues = issues


class FakeAnalysisResult:
    def __init__(self, issues):
        self.issues = issues


class TestHelpers(unittest.TestCase):
    def test_severity_to_level(self):
        self.assertEqual(sr._severity_to_level("critical"), "error")
        self.assertEqual(sr._severity_to_level("HIGH"), "error")
        self.assertEqual(sr._severity_to_level("medium"), "warning")
        self.assertEqual(sr._severity_to_level("low"), "note")
        self.assertEqual(sr._severity_to_level(None), "note")
        self.assertEqual(sr._severity_to_level("banana"), "note")

    def test_rule_id(self):
        self.assertEqual(sr._rule_id("Security", "eval_usage"), "security/eval_usage")
        self.assertEqual(sr._rule_id("quality"), "quality")
        self.assertEqual(sr._rule_id(""), "generic")

    def test_location_region_shape(self):
        loc = sr._location("a.py", 3, None)
        region = loc["physicalLocation"]["region"]
        self.assertEqual(region, {"startLine": 3})
        loc2 = sr._location("a.py", 3, 3)
        self.assertNotIn("endLine", loc2["physicalLocation"]["region"])
        loc3 = sr._location("a.py", 3, 7)
        self.assertEqual(loc3["physicalLocation"]["region"]["endLine"], 7)

    def test_location_clamps_start_line(self):
        region = sr._location("a.py", 0, None)["physicalLocation"]["region"]
        self.assertEqual(region["startLine"], 1)


class TestToSarif(unittest.TestCase):
    def test_aggregates_all_three_sources(self):
        rr = FakeReviewResult(
            [
                {
                    "file": "a.py",
                    "line": 1,
                    "severity": "critical",
                    "category": "security",
                    "issue_type": "eval_usage",
                    "description": "d",
                    "recommendation": "r",
                }
            ]
        )
        ar = FakeAnalysisResult(
            [
                {
                    "file": "b.py",
                    "line": 2,
                    "end_line": 5,
                    "severity": "medium",
                    "category": "quality",
                    "description": "long method",
                }
            ]
        )
        si = SecurityIssue(
            file_path="c.py",
            line_number=3,
            issue_type="sql_injection",
            description="SQL concat",
            severity=SecurityLevel.HIGH,
            suggestion="parameterize",
        )
        doc = sr.to_sarif(parallel_results=[rr], analyzer_results=[ar], security_issues=[si])
        ok, errors = sr.validate_sarif(doc)
        self.assertTrue(ok, errors)
        results = doc["runs"][0]["results"]
        self.assertEqual(len(results), 3)
        levels = sorted(r["level"] for r in results)
        self.assertEqual(levels, ["error", "error", "warning"])
        rule_ids = {r["ruleId"] for r in results}
        self.assertEqual(
            rule_ids, {"security/eval_usage", "quality", "security/sql_injection"}
        )
        # 推荐 → 拼进 message.text
        self.assertIn("Recommendation:", results[0]["message"]["text"])

    def test_skips_non_completed_review_results(self):
        rr = FakeReviewResult([], status="error")
        doc = sr.to_sarif(parallel_results=[rr])
        self.assertEqual(doc["runs"][0]["results"], [])

    def test_skips_findings_without_location(self):
        rr = FakeReviewResult([{"severity": "high", "description": "no file"}])
        doc = sr.to_sarif(parallel_results=[rr])
        self.assertEqual(doc["runs"][0]["results"], [])

    def test_empty_input_is_still_valid_sarif(self):
        doc = sr.to_sarif()
        ok, errors = sr.validate_sarif(doc)
        self.assertTrue(ok, errors)
        self.assertEqual(doc["runs"][0]["results"], [])

    def test_run_tags_emitted(self):
        doc = sr.to_sarif(run_tags=["ci", "pr-42"])
        self.assertEqual(doc["runs"][0]["automationDetails"]["id"], "ci/pr-42")

    def test_rules_deduped_with_short_descriptions(self):
        rr = FakeReviewResult(
            [
                {
                    "file": "a.py",
                    "line": 1,
                    "severity": "high",
                    "category": "security",
                    "issue_type": "eval_usage",
                    "description": "d1",
                },
                {
                    "file": "a.py",
                    "line": 2,
                    "severity": "high",
                    "category": "security",
                    "issue_type": "eval_usage",
                    "description": "d2",
                },
            ]
        )
        doc = sr.to_sarif(parallel_results=[rr])
        rules = doc["runs"][0]["tool"]["driver"]["rules"]
        self.assertEqual(len(rules), 1)
        self.assertEqual(rules[0]["id"], "security/eval_usage")
        self.assertIn("eval()", rules[0]["shortDescription"]["text"])


class TestValidateSarif(unittest.TestCase):
    def test_good_document_passes(self):
        ok, errors = sr.validate_sarif(sr.to_sarif())
        self.assertTrue(ok)
        self.assertEqual(errors, [])

    def test_broken_document_reports_all_classes_of_errors(self):
        bad = {
            "$schema": "wrong",
            "version": "1.0",
            "runs": [
                {
                    "tool": {},
                    "results": [
                        {"level": "banana", "message": {}, "locations": []},
                        {"ruleId": "x", "level": "note", "message": {"text": "m"}},
                    ],
                }
            ],
        }
        ok, errors = sr.validate_sarif(bad)
        self.assertFalse(ok)
        joined = "\n".join(errors)
        for fragment in ("$schema", "version", "driver.name", "level", "ruleId", "locations"):
            self.assertIn(fragment, joined)

    def test_runs_missing_or_empty(self):
        ok, errors = sr.validate_sarif({"$schema": sr.SARIF_SCHEMA, "version": sr.SARIF_VERSION})
        self.assertFalse(ok)
        self.assertIn("runs must be a non-empty list", errors[0])
        ok2, _ = sr.validate_sarif(
            {"$schema": sr.SARIF_SCHEMA, "version": sr.SARIF_VERSION, "runs": []}
        )
        self.assertFalse(ok2)


class TestFromParallelJson(unittest.TestCase):
    def _report(self):
        return {
            "issues": [
                {
                    "file": "a.py",
                    "line": 1,
                    "severity": "high",
                    "category": "security",
                    "issue_type": "sql_injection",
                    "description": "concat",
                    "recommendation": "parameterize",
                }
            ]
        }

    def test_builds_valid_document(self):
        doc = sr.from_parallel_json_report(self._report())
        ok, errors = sr.validate_sarif(doc)
        self.assertTrue(ok, errors)
        result = doc["runs"][0]["results"][0]
        self.assertEqual(result["level"], "error")
        self.assertIn("Recommendation:", result["message"]["text"])

    def test_fingerprint_stable_per_location(self):
        doc1 = sr.from_parallel_json_report(self._report())
        doc2 = sr.from_parallel_json_report(self._report())
        fp1 = doc1["runs"][0]["results"][0]["fingerprints"]["primary"]
        fp2 = doc2["runs"][0]["results"][0]["fingerprints"]["primary"]
        self.assertEqual(fp1, fp2)
        self.assertEqual(len(fp1), 16)
        changed = self._report()
        changed["issues"][0]["line"] = 9
        fp3 = sr.from_parallel_json_report(changed)["runs"][0]["results"][0][
            "fingerprints"
        ]["primary"]
        self.assertNotEqual(fp1, fp3)


class TestSetToolInfo(unittest.TestCase):
    def test_override_and_restore(self):
        original = (sr.TOOL_NAME, sr.TOOL_VERSION, sr.TOOL_INFO_URI)
        try:
            sr.set_tool_info(name="other", version="9.9", info_uri="https://o")
            doc = sr.to_sarif()
            driver = doc["runs"][0]["tool"]["driver"]
            self.assertEqual(driver["name"], "other")
            self.assertEqual(driver["version"], "9.9")
            self.assertEqual(driver["informationUri"], "https://o")
        finally:
            sr.set_tool_info(*original)
        self.assertEqual(
            (sr.TOOL_NAME, sr.TOOL_VERSION, sr.TOOL_INFO_URI), original
        )


class TestCli(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)

    def _report_path(self):
        path = os.path.join(self._tmp.name, "report.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(
                {
                    "issues": [
                        {
                            "file": "a.py",
                            "line": 1,
                            "severity": "high",
                            "category": "security",
                            "issue_type": "eval_usage",
                            "description": "d",
                        }
                    ]
                },
                f,
            )
        return path

    def test_help_exits_zero(self):
        proc = subprocess.run(
            [sys.executable, SCRIPT, "--help"], capture_output=True, text=True
        )
        self.assertEqual(proc.returncode, 0)
        self.assertIn("--validate", proc.stdout)

    def test_valid_input_with_validate_flag(self):
        proc = subprocess.run(
            [sys.executable, SCRIPT, self._report_path(), "--validate"],
            capture_output=True,
            text=True,
        )
        self.assertEqual(proc.returncode, 0)
        self.assertIn("SARIF validation: OK", proc.stderr)
        doc = json.loads(proc.stdout)
        self.assertEqual(doc["version"], "2.1.0")

    def test_output_flag_writes_file(self):
        out = os.path.join(self._tmp.name, "out.sarif")
        proc = subprocess.run(
            [sys.executable, SCRIPT, self._report_path(), "--output", out],
            capture_output=True,
            text=True,
        )
        self.assertEqual(proc.returncode, 0)
        with open(out, encoding="utf-8") as f:
            self.assertEqual(json.load(f)["version"], "2.1.0")

    def test_missing_input_exits_one(self):
        proc = subprocess.run(
            [sys.executable, SCRIPT, os.path.join(self._tmp.name, "nope.json")],
            capture_output=True,
            text=True,
        )
        self.assertEqual(proc.returncode, 1)

    def test_invalid_json_exits_one(self):
        bad = os.path.join(self._tmp.name, "bad.json")
        with open(bad, "w", encoding="utf-8") as f:
            f.write("{not json")
        proc = subprocess.run(
            [sys.executable, SCRIPT, bad], capture_output=True, text=True
        )
        self.assertEqual(proc.returncode, 1)


if __name__ == "__main__":
    unittest.main()
