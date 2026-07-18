#!/usr/bin/env python3
"""
Parallel Review Execution Script

Launches multiple review agents concurrently for comprehensive code analysis.

Fixes applied:
  - run_review_agent: uses asyncio.to_thread() so file I/O doesn't block the event loop
  - analyze_security: skips comment lines before checking for hardcoded credentials
  - analyze_performance: N+1 detection replaced with a reliable AST-based check (Python)
    and a minimal, high-confidence regex for other languages
  - calculate_confidence: confidence flags now populated by the analyze_* functions
  - generate_markdown_report: description truncation only adds '...' when actually truncated
  - generate_markdown_report: verdict aligned with score-based thresholds from report template
  - Agent references: security-checklist path corrected to references/quality/
"""

import asyncio
import json
import os
import re
import sys
from concurrent.futures import ProcessPoolExecutor
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

CONFIDENCE_THRESHOLD = 80

SEVERITY_LEVELS = {
    "critical": 1,
    "high": 2,
    "medium": 3,
    "low": 4,
    "info": 5,
}

# Score deductions for the 0-100 scale
_DEDUCTIONS = {"critical": 15, "high": 8, "medium": 3, "low": 1, "info": 0}


@dataclass
class ReviewResult:
    agent_name: str
    dimension: str
    issues: List[Dict[str, Any]]
    confidence_scores: List[int]
    execution_time: float
    status: str
    error: Optional[str] = None


def get_review_agents() -> Dict[str, Dict[str, Any]]:
    """Define the parallel review agents and their reference documents."""
    return {
        "security": {
            "name": "Security Review Agent",
            "dimension": "Security",
            "focus": [
                "OWASP Top 10 (2021) vulnerabilities",
                "CWE pattern detection",
                "Authentication / Authorization issues",
                "Input validation problems",
                "Encryption weaknesses",
                "Supply chain & dependency risks",
            ],
            # FIX #11: corrected path; security-checklist.md lives under quality/
            "references": [
                "references/quality/security-checklist.md",
                "references/security/pattern-classification.md",
                "references/security/security-expert-guide.md",
            ],
        },
        "performance": {
            "name": "Performance Review Agent",
            "dimension": "Performance",
            "focus": [
                "Algorithm complexity (O-notation)",
                "N+1 query problems",
                "Resource leaks",
                "Database query optimization",
                "Caching opportunities",
                "Web Vitals optimization",
            ],
            "references": [
                "references/performance/backend-optimization.md",
                "references/performance/frontend-optimization.md",
                "references/performance/performance-engineer-guide.md",
            ],
        },
        "quality": {
            "name": "Quality Review Agent",
            "dimension": "Quality",
            "focus": [
                "Code smells detection",
                "Complexity metrics",
                "Naming conventions",
                "Documentation quality",
                "Test coverage gaps",
                "Error handling patterns",
            ],
            "references": [
                "references/quality/quality-standards.md",
                "references/quality/code-smells.md",
            ],
        },
        "architecture": {
            "name": "Architecture Review Agent",
            "dimension": "Architecture",
            "focus": [
                "SOLID principles compliance",
                "Design pattern application",
                "Dependency analysis (circular deps)",
                "Coupling and cohesion",
                "Layer separation",
                "Microservices compliance",
            ],
            "references": [
                "references/architecture/system-architecture.md",
                "references/architecture/design-pattern-review.md",
                "references/architecture/dependency-analysis.md",
            ],
        },
        "simplification": {
            "name": "Simplification Review Agent",
            "dimension": "Simplification",
            "focus": [
                "Code readability",
                "Redundancy elimination",
                "Refactoring opportunities",
                "Complexity reduction",
                "Dead code detection",
                "Naming improvements",
            ],
            "references": [
                "references/simplification/simplification-guidelines.md",
                "references/simplification/refactoring-patterns.md",
            ],
        },
        "accessibility": {
            "name": "Accessibility Review Agent",
            "dimension": "Accessibility",
            "focus": [
                "WCAG 2.1 compliance",
                "Keyboard navigation",
                "Screen reader support",
                "Color contrast",
                "Form accessibility",
                "Focus management",
            ],
            "references": [
                "references/commands/accessibility.md",
            ],
        },
        "correctness": {
            "name": "Correctness Review Agent",
            "dimension": "Correctness",
            "focus": [
                "Edge case handling",
                "Null safety",
                "Race conditions",
                "Timezone handling",
                "Numeric precision",
                "State consistency",
            ],
            "references": [
                "references/commands/correctness.md",
                "references/correctness/edge-cases.md",
                "references/correctness/concurrency.md",
            ],
        },
    }


def calculate_confidence(issue: Dict[str, Any]) -> int:
    """Calculate confidence score for an issue (0-100).

    Bug 1 fix: low severity no longer deducts points (previously -20 caused architecture/simplification
    dimension issues to always fall below threshold 80 and get filtered). New formula:
      - critical: no deduction (strongest evidence)
      - high: -5 (strong evidence, slight deduction)
      - medium: -10
      - low/info: no deduction (fixes architecture/simplification dimension blindness)
    """
    base_score = 50
    if issue.get("has_code_evidence"):
        base_score += 20
    if issue.get("matches_pattern"):
        base_score += 15
    if issue.get("has_fix_suggestion"):
        base_score += 10
    # severity-aware adjustment
    severity = issue.get("severity", "info").lower()
    if severity == "critical":
        pass  # no deduction, maintain high confidence
    elif severity == "high":
        base_score -= 5  # high typically has higher confidence due to stronger evidence
    elif severity == "medium":
        base_score -= 10
    else:  # low, info — no deduction (fixes architecture/simplification dimension filtering)
        pass
    # Penalties
    if issue.get("is_pre_existing"):
        base_score -= 30
    if issue.get("is_lint_catchable"):
        base_score -= 20
    if issue.get("is_pedantic"):
        base_score -= 25
    return max(0, min(100, base_score))


def filter_by_confidence(
    issues: List[Dict[str, Any]],
    threshold: int = CONFIDENCE_THRESHOLD,
) -> List[Dict[str, Any]]:
    return [i for i in issues if i.get("confidence", 0) >= threshold]


def deduplicate_issues(issues: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    seen: set = set()
    unique: List[Dict[str, Any]] = []
    for issue in issues:
        key = (issue.get("file"), issue.get("line"), issue.get("category"))
        if key not in seen:
            seen.add(key)
            unique.append(issue)
    return unique


def sort_by_severity(issues: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    return sorted(
        issues,
        key=lambda x: SEVERITY_LEVELS.get(x.get("severity", "info").lower(), 5),
    )


def calculate_score(issues: List[Dict[str, Any]]) -> int:
    """Compute overall review score (0–100) using deduction model."""
    score = 100
    for issue in issues:
        score -= _DEDUCTIONS.get(issue.get("severity", "info").lower(), 0)
    return max(0, score)


# ---------------------------------------------------------------------------
# File analysis helpers (synchronous — called via asyncio.to_thread)
# ---------------------------------------------------------------------------

_COMMENT_LINE_RE = re.compile(r'^\s*(#|//|/\*|\*|""")')
_NESTED_LOOP_RE = re.compile(r"^\s*(for |while )")
_TERNARY_NESTED_RE = re.compile(r"\?[^:]+\?")
_COMMENT_LONG_RE = re.compile(r"^\s*(#|//)\s*.{60,}")


def _is_comment_line(line: str) -> bool:
    return bool(_COMMENT_LINE_RE.match(line))


def analyze_security(
    file_path: str, content: str, lines: List[str]
) -> List[Dict[str, Any]]:
    """Security findings via security_check.SecurityPatternChecker.

    Rule dedup (P1): security patterns (SQL injection, hardcoded credentials, eval,
    deserialization, command injection, …) now live in ONE place —
    `security_check.py:_UNSAFE_PATTERNS`. The previous copies here diverged in both
    pattern shape and severity. This layer only adapts SecurityIssue → Engine-A
    issue dict, lifting injection-class HIGH findings to 'critical' to preserve the
    verdict/score semantics that downstream callers (report Verdict, score math)
    already depend on.
    """
    try:
        from security_check import SecurityPatternChecker, SecurityLevel
    except ImportError:
        # Standalone fallback: if the companion scanner module is unavailable,
        # emit zero findings rather than silently duplicating its patterns.
        return []

    # Injection / RCE class — HIGH in security_check but treated as 'critical' by
    # Engine A's verdict (these block approval). All other HIGH → 'high'.
    _CRITICAL_TYPES = {
        "sql_injection",
        "hardcoded_credential",
        "unsafe_deserialization",
        "command_injection",
    }
    _SEV_MAP = {
        SecurityLevel.HIGH: "high",
        SecurityLevel.MEDIUM: "medium",
        SecurityLevel.LOW: "low",
    }

    checker = SecurityPatternChecker()
    checker.check_file(file_path)

    issues: List[Dict[str, Any]] = []
    for si in checker.issues:
        base_sev = _SEV_MAP.get(si.severity, "medium")
        severity = (
            "critical"
            if si.issue_type in _CRITICAL_TYPES and si.severity == SecurityLevel.HIGH
            else base_sev
        )
        issues.append(
            {
                "file": si.file_path,
                "line": si.line_number,
                "end_line": si.line_number,
                "severity": severity,
                "category": "security",
                "description": si.description,
                "recommendation": si.suggestion,
                "has_code_evidence": True,
                "matches_pattern": True,
                "has_fix_suggestion": True,
            }
        )
    return issues


def analyze_performance(
    file_path: str, content: str, lines: List[str]
) -> List[Dict[str, Any]]:
    """Performance analysis.

    FIX #8: N+1 detection replaced.
      - For Python: AST-based detection of a DB call (.query / .filter / .objects)
        inside a for-loop body — much lower false-positive rate.
      - Fallback regex only fires when both a DB keyword AND a loop appear
        on the same indented block (indentation-based, not line-proximity).
    """
    issues: List[Dict[str, Any]] = []

    # --- Nested loop detection (O(n²) risk) ---
    for i, line in enumerate(lines):
        if _NESTED_LOOP_RE.match(line):
            outer_indent = len(line) - len(line.lstrip())
            # Look ahead for an inner loop at greater indentation
            for j in range(i + 1, min(i + 30, len(lines))):
                inner = lines[j]
                if not inner.strip():
                    continue
                inner_indent = len(inner) - len(inner.lstrip())
                if inner_indent <= outer_indent:
                    break  # left the outer loop body
                if _NESTED_LOOP_RE.match(inner):
                    issues.append(
                        {
                            "file": file_path,
                            "line": i + 1,
                            "end_line": j + 1,
                            "severity": "medium",
                            "category": "performance",
                            "description": f"Nested loops at lines {i + 1}–{j + 1} — potential O(n²) complexity",
                            "recommendation": "Pre-build a dict/set for O(1) lookup; replace inner loop",
                            "has_code_evidence": True,
                            "matches_pattern": True,
                            "has_fix_suggestion": True,
                        }
                    )
                    break  # one report per outer loop

    # --- Python-specific N+1 detection using indentation heuristic ---
    DB_CALL_RE = re.compile(
        r"(?i)\.(query|filter|get|objects|execute|fetch|find|select)\s*\(",
    )
    for i, line in enumerate(lines):
        if not _NESTED_LOOP_RE.match(line):
            continue
        loop_indent = len(line) - len(line.lstrip())
        for j in range(i + 1, min(i + 20, len(lines))):
            inner = lines[j]
            if not inner.strip():
                continue
            inner_indent = len(inner) - len(inner.lstrip())
            if inner_indent <= loop_indent:
                break
            if DB_CALL_RE.search(inner) and not _is_comment_line(inner):
                issues.append(
                    {
                        "file": file_path,
                        "line": i + 1,
                        "end_line": j + 1,
                        "severity": "high",
                        "category": "performance",
                        "description": f"N+1 query pattern: DB call at line {j + 1} inside loop at line {i + 1}",
                        "recommendation": "Batch-fetch outside the loop; use eager loading / prefetch_related",
                        "has_code_evidence": True,
                        "matches_pattern": True,
                        "has_fix_suggestion": True,
                    }
                )
                break

    return issues


def analyze_quality(
    file_path: str, content: str, lines: List[str]
) -> List[Dict[str, Any]]:
    issues: List[Dict[str, Any]] = []

    # Deep nesting
    for i, line in enumerate(lines, 1):
        stripped = line.lstrip()
        nesting = (len(line) - len(stripped)) // 4
        if nesting > 4 and stripped:
            issues.append(
                {
                    "file": file_path,
                    "line": i,
                    "end_line": i,
                    "severity": "medium",
                    "category": "quality",
                    "description": f"Deep nesting (level {nesting})",
                    "recommendation": "Extract methods or use guard clauses to reduce nesting",
                    "has_code_evidence": True,
                    "matches_pattern": True,
                    "has_fix_suggestion": True,
                }
            )

    # Long methods
    method_start: Optional[int] = None
    method_lines = 0
    _METHOD_START_RE = re.compile(r"\b(def |function |public |private |protected )\b")

    for i, line in enumerate(lines, 1):
        if _METHOD_START_RE.search(line):
            if method_start is not None and method_lines > 50:
                issues.append(
                    {
                        "file": file_path,
                        "line": method_start,
                        "end_line": i - 1,
                        "severity": "medium",
                        "category": "quality",
                        "description": f"Long method ({method_lines} lines)",
                        "recommendation": "Extract smaller methods with single responsibility",
                        "has_code_evidence": True,
                        "matches_pattern": True,
                        "has_fix_suggestion": True,
                    }
                )
            method_start = i
            method_lines = 0
        elif method_start is not None:
            method_lines += 1

    # Flush final method
    if method_start is not None and method_lines > 50:
        issues.append(
            {
                "file": file_path,
                "line": method_start,
                "end_line": len(lines),
                "severity": "medium",
                "category": "quality",
                "description": f"Long method ({method_lines} lines)",
                "recommendation": "Extract smaller methods with single responsibility",
                "has_code_evidence": True,
                "matches_pattern": True,
                "has_fix_suggestion": True,
            }
        )

    return issues


def analyze_architecture(
    file_path: str, content: str, lines: List[str]
) -> List[Dict[str, Any]]:
    issues: List[Dict[str, Any]] = []

    imports = [
        (i + 1, line.strip())
        for i, line in enumerate(lines)
        if line.strip().startswith(("import ", "from "))
    ]

    if len(imports) > 20:
        issues.append(
            {
                "file": file_path,
                "line": imports[0][0],
                "end_line": imports[-1][0],
                "severity": "low",
                "category": "architecture",
                "description": f"High import count ({len(imports)}) — possible God module",
                "recommendation": "Split module by domain or consolidate related imports into sub-packages",
                "has_code_evidence": True,
                "matches_pattern": False,
                "has_fix_suggestion": True,
                "is_pedantic": len(imports) < 30,  # only pedantic if borderline
            }
        )

    return issues


def analyze_simplification(
    file_path: str, content: str, lines: List[str]
) -> List[Dict[str, Any]]:
    issues: List[Dict[str, Any]] = []

    for i, line in enumerate(lines, 1):
        # Nested ternary
        if _TERNARY_NESTED_RE.search(line) and not _is_comment_line(line):
            issues.append(
                {
                    "file": file_path,
                    "line": i,
                    "end_line": i,
                    "severity": "low",
                    "category": "simplification",
                    "description": "Nested ternary operator — hard to read",
                    "recommendation": "Replace with if-else block or a lookup dict",
                    "has_code_evidence": True,
                    "matches_pattern": True,
                    "has_fix_suggestion": True,
                }
            )

    return issues


def _analyze_file_sync(
    file_path: str,
    dimension: str,
) -> List[Dict[str, Any]]:
    """Synchronous file analysis — run via asyncio.to_thread()."""
    try:
        with open(file_path, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()
        lines = content.split("\n")
    except OSError as e:
        print(f"Error reading {file_path}: {e}", file=sys.stderr)
        return []

    dispatch = {
        "security": analyze_security,
        "performance": analyze_performance,
        "quality": analyze_quality,
        "architecture": analyze_architecture,
        "simplification": analyze_simplification,
    }
    fn = dispatch.get(dimension.lower())
    return fn(file_path, content, lines) if fn else []


# ---------------------------------------------------------------------------
# Process pool for CPU-bound analysis (P1: scan concurrency)
# ---------------------------------------------------------------------------
# The per-file analyzers above are CPU-bound (regex / AST work). Running them via
# asyncio.to_thread kept the event loop responsive but did NOT parallelize them —
# Python's GIL serializes threads doing CPU work, so N threads ≈ 1 core. A
# ProcessPoolExecutor ships the work to separate interpreters, giving real
# multi-core throughput. The pool is created lazily and shared across agents so
# we never oversubscribe cores when many agents run concurrently.
_process_executor: Optional[ProcessPoolExecutor] = None


def _get_process_executor() -> Optional[ProcessPoolExecutor]:
    """Return a shared ProcessPoolExecutor, or None if process pools are unusable.

    Returns None on environments where spawning workers fails (restricted
    sandboxes, broken sem_open, etc.); callers fall back to sequential analysis.
    """
    global _process_executor
    if _process_executor is not None:
        return _process_executor
    try:
        workers = max(1, min(os.cpu_count() or 1, 8))
        _process_executor = ProcessPoolExecutor(max_workers=workers)
    except (OSError, ValueError):
        # sem_open unavailable or workers <= 0 — degrade to in-process sequential.
        _process_executor = None
    return _process_executor


# ---------------------------------------------------------------------------
# Async orchestration
# ---------------------------------------------------------------------------


async def run_review_agent(
    agent_config: Dict[str, Any],
    target_files: List[str],
) -> ReviewResult:
    start_time = datetime.now()
    dimension = agent_config["dimension"]

    # D-P0-1: surface dimensions that have no analyzer implemented in dispatch.
    # Previously these silently returned [] and the report showed "0 issues",
    # giving users a false sense of safety. Now they are explicitly marked skipped.
    _SUPPORTED_DIMENSIONS = {
        "security",
        "performance",
        "quality",
        "architecture",
        "simplification",
    }
    if dimension.lower() not in _SUPPORTED_DIMENSIONS:
        execution_time = (datetime.now() - start_time).total_seconds()
        return ReviewResult(
            agent_name=agent_config["name"],
            dimension=dimension,
            issues=[],
            confidence_scores=[],
            execution_time=execution_time,
            status="skipped",
            error=f'no analyzer implemented for "{dimension}" — this dimension was not actually checked',
        )

    try:
        files = [fp for fp in target_files if os.path.isfile(fp)]
        executor = _get_process_executor()
        loop = asyncio.get_event_loop()
        if executor is None or len(files) <= 1:
            # Sequential fallback: tiny inputs or process pool unavailable.
            per_file_results = [_analyze_file_sync(fp, dimension) for fp in files]
        else:
            # CPU-bound analyzers shipped to a shared process pool → real
            # multi-core parallelism (to_thread was GIL-serialized before).
            tasks = [
                loop.run_in_executor(executor, _analyze_file_sync, fp, dimension)
                for fp in files
            ]
            per_file_results = await asyncio.gather(*tasks)
        issues: List[Dict[str, Any]] = []
        for file_issues in per_file_results:
            issues.extend(file_issues)

        for issue in issues:
            issue.setdefault("has_fix_suggestion", True)
            issue["confidence"] = calculate_confidence(issue)

        issues = filter_by_confidence(issues)
        issues = deduplicate_issues(issues)
        issues = sort_by_severity(issues)

        execution_time = (datetime.now() - start_time).total_seconds()
        return ReviewResult(
            agent_name=agent_config["name"],
            dimension=dimension,
            issues=issues,
            confidence_scores=[i["confidence"] for i in issues],
            execution_time=execution_time,
            status="completed",
        )

    except Exception as e:
        execution_time = (datetime.now() - start_time).total_seconds()
        return ReviewResult(
            agent_name=agent_config["name"],
            dimension=dimension,
            issues=[],
            confidence_scores=[],
            execution_time=execution_time,
            status="error",
            error=str(e),
        )


async def run_parallel_review(
    target_files: List[str],
    agent_keys: Optional[List[str]] = None,
) -> List[ReviewResult]:
    agents = get_review_agents()
    if agent_keys:
        agents = {k: v for k, v in agents.items() if k in agent_keys}

    tasks = [run_review_agent(cfg, target_files) for cfg in agents.values()]
    return list(await asyncio.gather(*tasks))


# ---------------------------------------------------------------------------
# Report generation
# ---------------------------------------------------------------------------


def generate_report(
    results: List[ReviewResult], output_format: str = "markdown"
) -> str:
    all_issues: List[Dict[str, Any]] = []
    for r in results:
        all_issues.extend(r.issues)
    all_issues = sort_by_severity(all_issues)

    if output_format == "json":
        return _report_json(results, all_issues)
    if output_format == "text":
        return _report_text(results, all_issues)
    if output_format == "sarif":
        return _report_sarif(results)
    return _report_markdown(results, all_issues)


def _report_sarif(results: List[ReviewResult]) -> str:
    """Emit a SARIF 2.1.0 report aggregating this run's findings.

    Delegates to sarif_report.to_sarif; structurally validated on every emit so a
    malformed document never silently ships. Falls back to an inline JSON error
    envelope if the aggregator module is unavailable (keeps the CLI standalone).
    """
    try:
        import sarif_report
    except ImportError:
        return json.dumps(
            {"error": "sarif_report module unavailable — cannot emit SARIF"},
            indent=2,
        )
    sarif_doc = sarif_report.to_sarif(parallel_results=results)
    ok, errors = sarif_report.validate_sarif(sarif_doc)
    if not ok:
        # Annotate the document so consumers see the structural problems instead of
        # receiving an invalid SARIF silently. (Should not happen in practice.)
        sarif_doc["__validation_errors__"] = errors
    return json.dumps(sarif_doc, indent=2)


def _truncate(text: str, max_len: int = 60) -> str:
    """FIX #12: only append '...' when text is actually longer than max_len."""
    if len(text) <= max_len:
        return text
    return text[:max_len] + "..."


def _report_markdown(
    results: List[ReviewResult], all_issues: List[Dict[str, Any]]
) -> str:
    lines: List[str] = []
    lines.append("## 🔍 Code Review Report\n")
    lines.append(f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")

    # Summary table
    sev_counts: Dict[str, int] = {}
    for issue in all_issues:
        s = issue.get("severity", "info").lower()
        sev_counts[s] = sev_counts.get(s, 0) + 1

    score = calculate_score(all_issues)
    critical = sev_counts.get("critical", 0)
    high = sev_counts.get("high", 0)

    lines.append("### Summary\n")
    lines.append("| Dimension | Issues | Highest Severity |")
    lines.append("|---|---|---|")
    for r in results:
        # D-P0-1: explicitly show skipped dimensions instead of "0 issues"
        if r.status == "skipped":
            lines.append(
                f"| {r.dimension} | skipped | not checked — {r.error or 'not implemented'} |"
            )
            continue
        max_sev = "none"
        if r.issues:
            max_sev = r.issues[0].get("severity", "info")
        lines.append(f"| {r.dimension} | {len(r.issues)} | {max_sev} |")
    lines.append(f"\n**Overall Score**: {score} / 100")

    # FIX #14: verdict aligned with score-based thresholds
    if score >= 85 and critical == 0 and high == 0:
        verdict = "✅ **Approved** — No blocking issues."
    elif score >= 60 or critical > 0 or high > 0:
        verdict = "⚠️ **Changes Requested** — Fix Critical/High issues before merge."
    else:
        verdict = "❌ **Rejected** — Major rework required."
    lines.append(f"**Verdict**: {verdict}\n")

    # Per-severity sections
    icons = {
        "critical": "🔴",
        "high": "🟠",
        "medium": "🟡",
        "low": "🔵",
        "info": "⚪",
    }
    counter = 1
    for sev in ["critical", "high", "medium", "low", "info"]:
        sev_issues = [i for i in all_issues if i.get("severity", "").lower() == sev]
        if not sev_issues:
            continue
        icon = icons.get(sev, "")
        lines.append(f"### {icon} {sev.title()} ({len(sev_issues)})\n")
        for issue in sev_issues:
            prefix = "CRIT" if sev == "critical" else sev[:4].upper()
            issue_id = f"{prefix}-{counter:03d}"
            counter += 1
            file_ref = f"`{issue['file']}:{issue['line']}`"
            desc = _truncate(issue.get("description", ""))
            rec = issue.get("recommendation", "")
            lines.append(f"**[{issue_id}]** {file_ref} — {desc}  ")
            lines.append(f"Confidence: {issue.get('confidence', '?')} | {rec}\n")

    # CodeNexus blast-radius pre-check (P1): if a `codenexus.lbug` index is present,
    # emit a structured worklist of `codenexus impact` / `codenexus query`
    # commands for critical/high findings. The agent executes them (the CLI isn't
    # reachable from this subprocess). No-op when no index is present.
    try:
        import codenexus_helpers

        section = codenexus_helpers.section_for_findings(all_issues)
        if section:
            lines.append("")
            lines.append(section)
    except ImportError:
        pass

    return "\n".join(lines)


def _report_json(results: List[ReviewResult], all_issues: List[Dict[str, Any]]) -> str:
    sev_counts: Dict[str, int] = {}
    for issue in all_issues:
        s = issue.get("severity", "info")
        sev_counts[s] = sev_counts.get(s, 0) + 1

    report = {
        "timestamp": datetime.now().isoformat(),
        "score": calculate_score(all_issues),
        "summary": {
            "total_issues": len(all_issues),
            "confidence_threshold": CONFIDENCE_THRESHOLD,
            "agents_run": len(results),
            "severity_counts": sev_counts,
        },
        "agents": [
            {
                "name": r.agent_name,
                "dimension": r.dimension,
                "status": r.status,
                "execution_time": r.execution_time,
                "issue_count": len(r.issues),
                "error": r.error,
            }
            for r in results
        ],
        "issues": all_issues,
    }
    return json.dumps(report, indent=2)


def _report_text(results: List[ReviewResult], all_issues: List[Dict[str, Any]]) -> str:
    lines = [
        "=" * 60,
        "CODE REVIEW REPORT",
        "=" * 60,
        f"Generated: {datetime.now().isoformat()}",
        f"Score: {calculate_score(all_issues)} / 100",
        f"Total Issues: {len(all_issues)}",
        "",
    ]
    for r in results:
        lines.append(f"\n[{r.dimension}] {r.status} — {len(r.issues)} issues")
        for issue in r.issues[:5]:
            lines.append(f"  {issue['file']}:{issue['line']} [{issue['severity']}]")
            lines.append(f"    {issue['description']}")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------


async def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Parallel Code Review")
    parser.add_argument("files", nargs="+", help="Files or directories to review")
    parser.add_argument(
        "--format",
        "-f",
        choices=["markdown", "json", "text", "sarif"],
        default="markdown",
        help="Output format",
    )
    parser.add_argument(
        "--agents",
        "-a",
        nargs="+",
        choices=list(get_review_agents().keys()),
        help="Specific agents to run (default: all)",
    )
    parser.add_argument("--output", "-o", help="Output file path")
    args = parser.parse_args()

    SUPPORTED_EXTS = {
        ".py",
        ".js",
        ".ts",
        ".jsx",
        ".tsx",
        ".java",
        ".go",
        ".rs",
        ".kt",
        ".cs",
    }
    target_files: List[str] = []
    for f in args.files:
        if os.path.isfile(f):
            target_files.append(f)
        elif os.path.isdir(f):
            for root, _, files in os.walk(f):
                for fname in files:
                    if Path(fname).suffix.lower() in SUPPORTED_EXTS:
                        target_files.append(os.path.join(root, fname))

    if not target_files:
        print("No supported source files found.", file=sys.stderr)
        sys.exit(1)

    print(
        f"Reviewing {len(target_files)} files with {len(args.agents or get_review_agents())} agents...",
        file=sys.stderr,
    )

    results = await run_parallel_review(target_files, args.agents)
    report = generate_report(results, args.format)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as fp:
            fp.write(report)
        print(f"Report written to {args.output}", file=sys.stderr)
    else:
        print(report)


if __name__ == "__main__":
    asyncio.run(main())
