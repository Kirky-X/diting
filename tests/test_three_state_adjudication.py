#!/usr/bin/env python3
"""三态发现裁决回归测试（references/review-workflow.md 的核心机制）。

裁决规则：
  - confidence >= 80  → confirmed：计分，可驱动 verdict
  - 55 <= confidence < 80 → needs-verification 桶：正式报告但不计分、不影响 verdict
  - confidence < 55（或低于自定义 candidate floor）→ 丢弃，但丢弃数必须披露

本文件覆盖：纯函数分桶边界、公式→桶映射、run_review_agent 端到端分桶、
三种报告格式对"候选数 + 丢弃数"的强制披露，以及"候选不评分/不驱动 verdict"。
"""
import asyncio
import json
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

import parallel_review as pr


def make_result(issues=None, nv=None, below=0, status="completed", dimension="Quality"):
    return pr.ReviewResult(
        agent_name="Test Agent",
        dimension=dimension,
        issues=issues or [],
        confidence_scores=[i.get("confidence", 0) for i in (issues or [])],
        execution_time=0.001,
        status=status,
        needs_verification=nv or [],
        below_floor_dropped=below,
    )


class TestAdjudicateBoundaries(unittest.TestCase):
    """adjudicate_by_confidence 三段边界：80 / 79 / 55 / 54。"""

    def test_full_spectrum_bucketing(self):
        issues = [{"confidence": c} for c in (95, 80, 79, 55, 54, 0)]
        confirmed, nv, dropped = pr.adjudicate_by_confidence(issues)
        self.assertEqual([i["confidence"] for i in confirmed], [95, 80])
        self.assertEqual([i["confidence"] for i in nv], [79, 55])
        self.assertEqual(dropped, 2)

    def test_boundary_80_is_confirmed_and_79_is_not(self):
        confirmed, nv, _ = pr.adjudicate_by_confidence(
            [{"confidence": 80}, {"confidence": 79}]
        )
        self.assertEqual(len(confirmed), 1)
        self.assertEqual(confirmed[0]["confidence"], 80)
        self.assertEqual(len(nv), 1)

    def test_floor_55_reported_and_54_dropped(self):
        confirmed, nv, dropped = pr.adjudicate_by_confidence(
            [{"confidence": 55}, {"confidence": 54}]
        )
        self.assertEqual(confirmed, [])
        self.assertEqual([i["confidence"] for i in nv], [55])
        self.assertEqual(dropped, 1)

    def test_candidate_issues_tagged_needs_verification(self):
        _, nv, _ = pr.adjudicate_by_confidence([{"confidence": 60}])
        self.assertTrue(nv[0]["needs_verification"])

    def test_confirmed_issues_not_tagged(self):
        confirmed, _, _ = pr.adjudicate_by_confidence([{"confidence": 90}])
        self.assertNotIn("needs_verification", confirmed[0])

    def test_empty_input(self):
        self.assertEqual(pr.adjudicate_by_confidence([]), ([], [], 0))

    def test_custom_thresholds(self):
        confirmed, nv, dropped = pr.adjudicate_by_confidence(
            [{"confidence": 90}, {"confidence": 70}, {"confidence": 69}],
            confirmed_at=90,
            candidate_at=70,
        )
        self.assertEqual(len(confirmed), 1)
        self.assertEqual(len(nv), 1)
        self.assertEqual(dropped, 1)


class TestConfidenceToBucketMapping(unittest.TestCase):
    """calculate_confidence 公式产出落到正确的桶（真实 issue dict，非手填 confidence）。"""

    def test_security_critical_full_evidence_is_confirmed(self):
        issue = {
            "severity": "critical",
            "has_code_evidence": True,
            "matches_pattern": True,
            "has_fix_suggestion": True,
        }
        self.assertGreaterEqual(pr.calculate_confidence(issue), pr.CONFIDENCE_CONFIRMED)

    def test_performance_medium_nested_loop_is_confirmed(self):
        # analyze_performance 产出的 issue 形状：medium + 三项证据 → 85
        issue = {
            "severity": "medium",
            "has_code_evidence": True,
            "matches_pattern": True,
            "has_fix_suggestion": True,
        }
        self.assertEqual(pr.calculate_confidence(issue), 85)

    def test_architecture_borderline_low_is_candidate_exactly_at_floor(self):
        # analyze_architecture：25 个 import → low + matches_pattern=False + pedantic → 55
        issue = {
            "severity": "low",
            "has_code_evidence": True,
            "matches_pattern": False,
            "has_fix_suggestion": True,
            "is_pedantic": True,
        }
        confidence = pr.calculate_confidence(issue)
        self.assertEqual(confidence, pr.CONFIDENCE_CANDIDATE)
        _, nv, dropped = pr.adjudicate_by_confidence([dict(issue, confidence=confidence)])
        self.assertEqual(len(nv), 1)
        self.assertEqual(dropped, 0)

    def test_no_evidence_medium_falls_below_floor(self):
        # 无任何证据标记的 medium → 40 → 必须被丢弃并计数
        issue = {"severity": "medium"}
        confidence = pr.calculate_confidence(issue)
        self.assertEqual(confidence, 40)
        confirmed, nv, dropped = pr.adjudicate_by_confidence(
            [dict(issue, confidence=confidence)]
        )
        self.assertEqual((confirmed, nv, dropped), ([], [], 1))

    def test_penalties_can_clamp_to_zero(self):
        issue = {
            "severity": "medium",
            "is_pre_existing": True,
            "is_lint_catchable": True,
            "is_pedantic": True,
        }
        self.assertEqual(pr.calculate_confidence(issue), 0)


class TestRunReviewAgentBuckets(unittest.TestCase):
    """端到端：真实分析器产出的发现按三态分桶。"""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)

    def _write(self, name, text):
        path = os.path.join(self._tmp.name, name)
        with open(path, "w", encoding="utf-8") as f:
            f.write(text)
        return path

    def _run(self, agent_key, files, **kw):
        agent = pr.get_review_agents()[agent_key]
        return asyncio.run(pr.run_review_agent(agent, files, **kw))

    def test_security_findings_land_in_confirmed_bucket(self):
        target = self._write("evil.py", "value = eval(user_input)\n")
        result = self._run("security", [target])
        self.assertEqual(result.status, "completed")
        self.assertEqual(len(result.issues), 1)
        self.assertEqual(result.issues[0]["category"], "security")
        self.assertGreaterEqual(result.confidence_scores[0], pr.CONFIDENCE_CONFIRMED)
        self.assertEqual(result.needs_verification, [])
        self.assertEqual(result.below_floor_dropped, 0)

    def test_performance_findings_land_in_confirmed_bucket(self):
        target = self._write("loops.py", "for a in items:\n    for b in a:\n        pass\n")
        result = self._run("performance", [target])
        self.assertEqual(len(result.issues), 1)
        self.assertGreaterEqual(result.confidence_scores[0], pr.CONFIDENCE_CONFIRMED)
        self.assertEqual(result.needs_verification, [])
        self.assertEqual(result.below_floor_dropped, 0)

    def test_borderline_architecture_finding_goes_to_needs_verification(self):
        # 25 个 import（<30 → pedantic）→ confidence 55，恰好落在候选桶
        target = self._write(
            "god.py", "".join(f"import module_{i}\n" for i in range(25))
        )
        result = self._run("architecture", [target])
        self.assertEqual(result.status, "completed")
        self.assertEqual(result.issues, [])
        self.assertEqual(result.confidence_scores, [])
        self.assertEqual(len(result.needs_verification), 1)
        candidate = result.needs_verification[0]
        self.assertEqual(candidate["confidence"], pr.CONFIDENCE_CANDIDATE)
        self.assertTrue(candidate["needs_verification"])
        self.assertEqual(result.below_floor_dropped, 0)

    def test_raising_min_confidence_drops_borderline_with_count(self):
        target = self._write(
            "god.py", "".join(f"import module_{i}\n" for i in range(25))
        )
        result = self._run("architecture", [target], min_confidence=60)
        self.assertEqual(result.issues, [])
        self.assertEqual(result.needs_verification, [])
        self.assertEqual(result.below_floor_dropped, 1)

    def test_architecture_30_plus_imports_is_confirmed(self):
        # 30 个 import → pedantic=False → confidence 80 → confirmed
        target = self._write(
            "god.py", "".join(f"import module_{i}\n" for i in range(30))
        )
        result = self._run("architecture", [target])
        self.assertEqual(len(result.issues), 1)
        self.assertEqual(result.confidence_scores, [pr.CONFIDENCE_CONFIRMED])
        self.assertEqual(result.needs_verification, [])

    def test_missing_files_yield_clean_completed_result(self):
        result = self._run("quality", [os.path.join(self._tmp.name, "nope.py")])
        self.assertEqual(result.status, "completed")
        self.assertEqual(result.issues, [])
        self.assertEqual(result.below_floor_dropped, 0)

    def test_unsupported_dimension_is_skipped_not_silent_zero(self):
        result = self._run("accessibility", ["whatever.py"])
        self.assertEqual(result.status, "skipped")
        self.assertIsNotNone(result.error)
        self.assertIn("not actually checked", result.error)


class TestReportDisclosure(unittest.TestCase):
    """三种报告格式都必须披露候选数与丢弃数；候选绝不计分、绝不驱动 verdict。"""

    confirmed_critical = {
        "file": "a.py",
        "line": 1,
        "severity": "critical",
        "category": "security",
        "description": "Hardcoded credential in production config",
        "recommendation": "Move to env / KMS",
        "confidence": 95,
    }
    candidate = {
        "file": "b.py",
        "line": 2,
        "severity": "medium",
        "category": "quality",
        "description": "Possible duplication",
        "confidence": 60,
        "needs_verification": True,
    }

    def test_markdown_discloses_counts(self):
        report = pr.generate_report(
            [make_result(issues=[self.confirmed_critical], nv=[self.candidate], below=3)],
            "markdown",
        )
        self.assertIn(
            "**Needs Verification**: 1 candidate(s) reported without score", report
        )
        self.assertIn(
            "Below candidate floor (< 55): 3 dropped (count disclosed, never silently)",
            report,
        )
        self.assertIn("### 🔎 Needs Verification (1)", report)

    def test_markdown_clean_run_has_no_disclosure_line(self):
        report = pr.generate_report([make_result()], "markdown")
        self.assertNotIn("Needs Verification", report)
        self.assertIn("**Overall Score**: 100 / 100", report)

    def test_json_discloses_counts_and_keeps_buckets_separate(self):
        payload = json.loads(
            pr.generate_report(
                [make_result(issues=[self.confirmed_critical], nv=[self.candidate], below=3)],
                "json",
            )
        )
        summary = payload["summary"]
        self.assertEqual(summary["needs_verification_count"], 1)
        self.assertEqual(summary["below_floor_dropped"], 3)
        self.assertEqual(summary["confidence_confirmed"], pr.CONFIDENCE_CONFIRMED)
        self.assertEqual(summary["confidence_candidate_floor"], pr.CONFIDENCE_CANDIDATE)
        self.assertEqual(len(payload["issues"]), 1)
        self.assertEqual(payload["issues"][0]["severity"], "critical")
        self.assertEqual(len(payload["needs_verification"]), 1)
        self.assertEqual(payload["needs_verification"][0]["confidence"], 60)
        self.assertEqual(payload["agents"][0]["below_floor_dropped"], 3)

    def test_text_discloses_counts(self):
        report = pr.generate_report(
            [make_result(issues=[self.confirmed_critical], nv=[self.candidate], below=3)],
            "text",
        )
        self.assertIn("Needs Verification (unscored): 1", report)
        self.assertIn("Below candidate floor (< 55) dropped: 3", report)

    def test_candidate_does_not_change_score(self):
        with_candidate = pr.generate_report(
            [make_result(issues=[self.confirmed_critical], nv=[self.candidate], below=3)],
            "markdown",
        )
        without_candidate = pr.generate_report(
            [make_result(issues=[self.confirmed_critical], below=3)],
            "markdown",
        )
        self.assertIn("**Overall Score**: 85 / 100", with_candidate)
        self.assertIn("**Overall Score**: 85 / 100", without_candidate)

    def test_candidate_alone_cannot_block_approval(self):
        report = pr.generate_report(
            [make_result(nv=[self.candidate], below=0)], "markdown"
        )
        self.assertIn("**Overall Score**: 100 / 100", report)
        self.assertIn("Approved", report)

    def test_sarif_includes_only_confirmed_issues(self):
        text = pr.generate_report(
            [make_result(issues=[self.confirmed_critical], nv=[self.candidate], below=3)],
            "sarif",
        )
        doc = json.loads(text)
        results = doc["runs"][0]["results"]
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["level"], "error")


class TestVerdictFromScore(unittest.TestCase):
    """verdict 只由 confirmed 发现的扣分驱动。"""

    def _verdict(self, issues):
        report = pr.generate_report([make_result(issues=issues)], "markdown")
        return report

    def test_clean_approved(self):
        self.assertIn("Approved", self._verdict([]))

    def test_critical_blocks_approval(self):
        issue = {
            "file": "a.py",
            "line": 1,
            "severity": "critical",
            "category": "security",
            "description": "d",
            "recommendation": "r",
            "confidence": 95,
        }
        self.assertIn("Changes Requested", self._verdict([issue]))

    def test_accumulated_mediums_reject(self):
        # 14 个 medium → 扣 42 → 58 < 60 且无 critical/high → Rejected
        issues = [
            {
                "file": "m.py",
                "line": i,
                "severity": "medium",
                "category": "quality",
                "description": "d",
                "recommendation": "r",
                "confidence": 90,
            }
            for i in range(14)
        ]
        self.assertIn("Rejected", self._verdict(issues))


if __name__ == "__main__":
    unittest.main()
