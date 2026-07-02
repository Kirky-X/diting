#!/usr/bin/env python3
"""Diting parallel_review.py 修复验证测试。"""
import asyncio
import os
import sys
import unittest
from unittest import mock
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))


class TestDispatchCoverage(unittest.TestCase):
    """D-P0-1: accessibility/correctness Agent 不应静默返回空结果。"""

    def test_accessibility_agent_marked_skipped(self):
        """accessibility 维度应返回 status='skipped' 而非静默 completed。"""
        import parallel_review
        agent_config = parallel_review.get_review_agents()['accessibility']
        result = asyncio.run(parallel_review.run_review_agent(agent_config, []))
        self.assertEqual(result.status, 'skipped')
        self.assertIn('not actually checked', result.error or '')

    def test_correctness_agent_marked_skipped(self):
        """correctness 维度应返回 status='skipped'。"""
        import parallel_review
        agent_config = parallel_review.get_review_agents()['correctness']
        result = asyncio.run(parallel_review.run_review_agent(agent_config, []))
        self.assertEqual(result.status, 'skipped')

    def test_security_agent_not_skipped(self):
        """security 维度应正常运行，不应被标记为 skipped。"""
        import parallel_review
        agent_config = parallel_review.get_review_agents()['security']
        # 用空文件列表运行，应返回 completed（无 issues 但维度被支持）
        result = asyncio.run(parallel_review.run_review_agent(agent_config, []))
        self.assertNotEqual(result.status, 'skipped')


class TestConfidenceScoring(unittest.TestCase):
    """D-P1-4: 置信度评分不应所有 issue 都是 95。"""

    def test_confidence_varies_by_severity(self):
        """不同严重度的 issue 应有不同的置信度。"""
        import parallel_review
        critical_issue = {
            'severity': 'critical', 'has_code_evidence': True,
            'matches_pattern': True, 'has_fix_suggestion': True,
        }
        low_issue = {
            'severity': 'low', 'has_code_evidence': True,
            'matches_pattern': True, 'has_fix_suggestion': True,
        }
        critical_score = parallel_review.calculate_confidence(critical_issue)
        low_score = parallel_review.calculate_confidence(low_issue)
        self.assertGreater(critical_score, low_score,
                           "critical issue should have higher confidence than low")

    def test_low_severity_filtered_by_threshold(self):
        """low 严重度的 issue 应被阈值 80 过滤。"""
        import parallel_review
        low_issue = {
            'severity': 'low', 'has_code_evidence': True,
            'matches_pattern': True, 'has_fix_suggestion': True,
        }
        score = parallel_review.calculate_confidence(low_issue)
        self.assertLess(score, 80,
                        f"low issue score {score} should be below threshold 80")


class TestUtf8Output(unittest.TestCase):
    """D-P1-5: 输出文件应使用 UTF-8 编码。"""

    def test_open_uses_utf8_encoding(self):
        """源码中 open(args.output) 应指定 encoding='utf-8'。"""
        source = open(os.path.join(os.path.dirname(__file__), "..", "scripts", "parallel_review.py")).read()
        # 查找 open(args.output 行，应包含 encoding='utf-8'
        self.assertIn("encoding='utf-8'", source)


class TestInsecureRandomRegex(unittest.TestCase):
    """D-P1-3: insecure_random 正则不应有尾部 \b。"""

    def test_insecure_random_matches_without_trailing_word_boundary(self):
        """Math.random() 后跟分号或换行时应能匹配。"""
        import security_check
        pattern = security_check._UNSAFE_PATTERNS['insecure_random']['pattern']
        # 这些都应该匹配
        self.assertTrue(pattern.search('const x = Math.random();'))
        self.assertTrue(pattern.search('return Math.random()\n'))
        self.assertTrue(pattern.search('random.random()'))
        self.assertTrue(pattern.search('new Random()'))


if __name__ == "__main__":
    unittest.main()
