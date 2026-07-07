#!/usr/bin/env python3
"""SARIF 2.1.0 report aggregator for the diting scanner suite.

Aggregates findings from all three Engine-A scanners into a single SARIF
(Static Analysis Results Interchange Format) 2.1.0 document, consumable by
GitHub Code Scanning, Azure DevOps, SonarCloud, IDE SARIF viewers, etc.

Input sources (any combination; pass None for the unused ones):
  - parallel_review.ReviewResult  (per-agent issue dicts with severity/category)
  - analyzer.AnalysisResult       (metrics + issue dicts)
  - security_check.SecurityIssue  (typed security findings)

Output: a dict conforming to SARIF 2.1.0 (validate with `validate_sarif`).

Reference: https://docs.oasis-open.org/sarif/sarif/v2.1.0/sarif-v2.1.0.html
Schema:    https://json.schemastore.org/sarif-2.1.0.json
"""

from __future__ import annotations

import hashlib
import json
import sys
from typing import Any, Dict, Iterable, List, Optional, Tuple

SARIF_SCHEMA = "https://json.schemastore.org/sarif-2.1.0.json"
SARIF_VERSION = "2.1.0"
TOOL_NAME = "diting"
TOOL_VERSION = "0.1.1"
TOOL_INFO_URI = (
    "https://example.invalid/diting"  # placeholder; override via set_tool_info()
)

# diting severity → SARIF result.level
# SARIF level is one of: error | warning | note | none
_LEVEL_MAP: Dict[str, str] = {
    "critical": "error",
    "high": "error",
    "medium": "warning",
    "low": "note",
    "info": "note",
}

# Short human rule descriptions keyed by ruleId. ruleId convention: "<scope>/<id>".
_RULE_SHORT_DESC: Dict[str, str] = {
    "security/sql_injection": "Potential SQL injection via string concatenation",
    "security/hardcoded_credential": "Hardcoded credential in source",
    "security/eval_usage": "eval() usage — potential code injection",
    "security/unsafe_deserialization": "Unsafe deserialization — potential RCE",
    "security/command_injection": "Potential command injection",
    "security/xss_dom_write": "Direct DOM write — potential XSS",
    "security/path_traversal": "Potential path traversal",
    "security/ssrf_risk": "Potential SSRF",
    "security/weak_crypto_algorithm": "Use of a weak crypto algorithm",
    "security/insecure_random": "Non-cryptographic random used for security purposes",
    "security/broad_exception_catch": "Overly broad exception catch",
    "security/open_redirect": "Potential open redirect",
    "security/weak_password_hash": "Weak password hash algorithm",
    "correctness/null_safety": "Chained access on a nullable source without a guard",
    "correctness/race_condition": "Check-then-act race condition",
    "correctness/division_zero": "Division without a zero check",
    "performance/nested_loop": "Nested loops — potential O(n²) complexity",
    "performance/n_plus_1": "N+1 query pattern inside a loop",
    "quality/deep_nesting": "Deeply nested control flow",
    "quality/long_method": "Method exceeds length threshold",
    "quality/long_line": "Line exceeds length threshold",
    "quality/magic_number": "Unexplained numeric literal",
    "architecture/high_imports": "High import count — possible God module",
    "simplification/nested_ternary": "Nested ternary operator",
    "maintenance/todo": "TODO/FIXME/HACK comment",
    "style/long_line": "Line exceeds length threshold",
    "accessibility/img_missing_alt": "Image missing alt attribute",
    "accessibility/outline_none": "outline:none without visible focus alternative",
    "accessibility/input_no_label": "Input may lack an accessible label",
}


def set_tool_info(
    name: str = TOOL_NAME, version: str = TOOL_VERSION, info_uri: str = TOOL_INFO_URI
) -> None:
    """Override the tool identity emitted in the SARIF `tool.driver` block."""
    global TOOL_NAME, TOOL_VERSION, TOOL_INFO_URI
    TOOL_NAME = name
    TOOL_VERSION = version
    TOOL_INFO_URI = info_uri


def _severity_to_level(severity: Optional[str]) -> str:
    if not severity:
        return "note"
    return _LEVEL_MAP.get(str(severity).lower(), "note")


def _rule_id(category: str, issue_type: Optional[str] = None) -> str:
    """Build a stable ruleId from a finding's category / issue_type.

    For security_check findings we use the explicit issue_type (sql_injection, …).
    For parallel_review / analyzer findings we fall back to the category.
    """
    cat = (category or "generic").lower()
    if issue_type:
        return f"{cat}/{issue_type}"
    return cat


def _short_description(rule_id: str, fallback: str) -> str:
    if rule_id in _RULE_SHORT_DESC:
        return _RULE_SHORT_DESC[rule_id]
    # category-only ruleId (e.g. "performance") — use the finding's own description.
    return fallback or rule_id


def _fingerprint(file_path: str, rule_id: str, start_line: int) -> str:
    raw = f"{file_path}|{rule_id}|{start_line}".encode("utf-8", errors="replace")
    return hashlib.sha256(raw).hexdigest()[:16]


def _location(
    file_path: str, start_line: int, end_line: Optional[int]
) -> Dict[str, Any]:
    region: Dict[str, Any] = {"startLine": max(1, int(start_line))}
    if end_line is not None and int(end_line) != int(start_line):
        region["endLine"] = max(1, int(end_line))
    return {
        "physicalLocation": {
            "artifactLocation": {"uri": file_path},
            "region": region,
        }
    }


def _result_from_dict(
    issue: Dict[str, Any], category_hint: str = "generic"
) -> Optional[Dict[str, Any]]:
    """Convert a parallel_review / analyzer issue dict into a SARIF result object."""
    file_path = issue.get("file") or issue.get("file_path")
    start_line = issue.get("line") or issue.get("line_number")
    if not file_path or not start_line:
        return None  # a finding without a location cannot be expressed in SARIF
    category = issue.get("category") or category_hint
    rule_id = _rule_id(category, issue.get("issue_type"))
    description = issue.get("description") or _short_description(rule_id, "")
    recommendation = issue.get("recommendation")
    message_text = (
        description
        if not recommendation
        else f"{description}\nRecommendation: {recommendation}"
    )
    level = _severity_to_level(issue.get("severity"))
    return {
        "ruleId": rule_id,
        "level": level,
        "message": {"text": message_text},
        "locations": [
            _location(str(file_path), int(start_line), issue.get("end_line"))
        ],
        "fingerprints": {
            "primary": _fingerprint(str(file_path), rule_id, int(start_line)),
        },
    }


def _result_from_security_issue(si: Any) -> Optional[Dict[str, Any]]:
    """Convert a security_check.SecurityIssue (dataclass) into a SARIF result."""
    file_path = getattr(si, "file_path", None)
    line_number = getattr(si, "line_number", None)
    if not file_path or not line_number:
        return None
    issue_type = getattr(si, "issue_type", None)
    rule_id = _rule_id("security", issue_type)
    severity = getattr(
        getattr(si, "severity", None), "value", None
    )  # SecurityLevel enum
    suggestion = getattr(si, "suggestion", "")
    description = getattr(si, "description", "") or _short_description(rule_id, "")
    message_text = (
        description
        if not suggestion
        else f"{description}\nRecommendation: {suggestion}"
    )
    return {
        "ruleId": rule_id,
        "level": _severity_to_level(severity),
        "message": {"text": message_text},
        "locations": [_location(str(file_path), int(line_number), int(line_number))],
        "fingerprints": {
            "primary": _fingerprint(str(file_path), rule_id, int(line_number)),
        },
    }


def _build_rules(results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Collect unique ruleIds referenced in results into SARIF rule entries."""
    seen: Dict[str, str] = {}  # rule_id → short description (from first occurrence)
    for r in results:
        rid = r["ruleId"]
        if rid not in seen:
            msg = r["message"]["text"].split("\n")[0]
            seen[rid] = msg
    return [
        {
            "id": rid,
            "name": rid.split("/")[-1],
            "shortDescription": {"text": _short_description(rid, desc)},
        }
        for rid, desc in sorted(seen.items())
    ]


def to_sarif(
    parallel_results: Optional[Iterable[Any]] = None,
    analyzer_results: Optional[Iterable[Any]] = None,
    security_issues: Optional[Iterable[Any]] = None,
    run_tags: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """Aggregate multi-scanner findings into a SARIF 2.1.0 document.

    Each scanner contributes its findings; all are merged into a single run under
    one `tool` (diting). Findings without a usable file/line location are skipped
    (SARIF requires a physicalLocation).
    """
    results: List[Dict[str, Any]] = []

    if parallel_results:
        for rr in parallel_results:
            # parallel_review.ReviewResult — only completed runs carry findings
            status = getattr(rr, "status", "completed")
            if status != "completed":
                continue
            for issue in getattr(rr, "issues", []):
                res = _result_from_dict(issue, category_hint="security")
                if res:
                    results.append(res)

    if analyzer_results:
        for ar in analyzer_results:
            for issue in getattr(ar, "issues", []):
                category = issue.get("category", "quality")
                res = _result_from_dict(issue, category_hint=category)
                if res:
                    results.append(res)

    if security_issues:
        for si in security_issues:
            res = _result_from_security_issue(si)
            if res:
                results.append(res)

    rules = _build_rules(results)
    run: Dict[str, Any] = {
        "tool": {
            "driver": {
                "name": TOOL_NAME,
                "version": TOOL_VERSION,
                "informationUri": TOOL_INFO_URI,
                "rules": rules,
            }
        },
        "results": results,
    }
    if run_tags:
        run["automationDetails"] = {"id": "/".join(run_tags)}

    return {
        "$schema": SARIF_SCHEMA,
        "version": SARIF_VERSION,
        "runs": [run],
    }


def from_parallel_json_report(report: Dict[str, Any]) -> Dict[str, Any]:
    """Build SARIF from the JSON output of `parallel_review.py --format json`.

    The JSON report embeds an `issues` array (already-flattened Engine-A findings).
    We treat each as a generic finding; category/issue_type are read from the dict.
    """
    results: List[Dict[str, Any]] = []
    for issue in report.get("issues", []):
        res = _result_from_dict(issue, category_hint=issue.get("category", "generic"))
        if res:
            results.append(res)
    rules = _build_rules(results)
    return {
        "$schema": SARIF_SCHEMA,
        "version": SARIF_VERSION,
        "runs": [
            {
                "tool": {
                    "driver": {
                        "name": TOOL_NAME,
                        "version": TOOL_VERSION,
                        "informationUri": TOOL_INFO_URI,
                        "rules": rules,
                    }
                },
                "results": results,
            }
        ],
    }


def validate_sarif(doc: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """Structurally validate a SARIF 2.1.0 document (no external schema fetch).

    Returns (ok, errors). Checks the required top-level fields, run shape, and the
    mandatory fields of every result/rule. This is deliberately a self-contained
    structural check — it does NOT fetch the official JSON schema over the network.
    """
    errors: List[str] = []
    if doc.get("$schema") != SARIF_SCHEMA:
        errors.append(f"missing/incorrect $schema (expected {SARIF_SCHEMA})")
    if doc.get("version") != SARIF_VERSION:
        errors.append(f"missing/incorrect version (expected {SARIF_VERSION})")
    runs = doc.get("runs")
    if not isinstance(runs, list) or not runs:
        errors.append("runs must be a non-empty list")
        return False, errors

    valid_levels = {"error", "warning", "note", "none"}
    for ri, run in enumerate(runs):
        tool = run.get("tool")
        if not isinstance(tool, dict):
            errors.append(f"runs[{ri}].tool missing")
            continue
        driver = tool.get("driver")
        if not isinstance(driver, dict) or not driver.get("name"):
            errors.append(f"runs[{ri}].tool.driver.name missing")
        results = run.get("results", [])
        if not isinstance(results, list):
            errors.append(f"runs[{ri}].results must be a list")
            continue
        for rj, res in enumerate(results):
            prefix = f"runs[{ri}].results[{rj}]"
            if not res.get("ruleId"):
                errors.append(f"{prefix}.ruleId missing")
            level = res.get("level")
            if level not in valid_levels:
                errors.append(f"{prefix}.level={level!r} not in {sorted(valid_levels)}")
            msg = res.get("message")
            if not isinstance(msg, dict) or not msg.get("text"):
                errors.append(f"{prefix}.message.text missing")
            locs = res.get("locations")
            if not isinstance(locs, list) or not locs:
                errors.append(f"{prefix}.locations missing")
            else:
                for lk, loc in enumerate(locs):
                    pl = loc.get("physicalLocation", {})
                    region = pl.get("region", {})
                    if not pl.get("artifactLocation", {}).get("uri"):
                        errors.append(
                            f"{prefix}.locations[{lk}].artifactLocation.uri missing"
                        )
                    if not region.get("startLine"):
                        errors.append(
                            f"{prefix}.locations[{lk}].region.startLine missing"
                        )

    return len(errors) == 0, errors


def _load_parallel_json(path: str) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(
        description="Aggregate diting scanner findings into a SARIF 2.1.0 report.",
    )
    parser.add_argument(
        "input",
        help="Path to a parallel_review JSON report (produced by `--format json`)",
    )
    parser.add_argument(
        "--output",
        "-o",
        help="Output SARIF file path (default: stdout)",
    )
    parser.add_argument(
        "--validate",
        action="store_true",
        help="Structurally validate the generated SARIF and report errors to stderr",
    )
    args = parser.parse_args()

    try:
        report = _load_parallel_json(args.input)
    except (OSError, json.JSONDecodeError) as e:
        print(f"Error loading {args.input}: {e}", file=sys.stderr)
        return 1

    sarif = from_parallel_json_report(report)
    text = json.dumps(sarif, indent=2)

    if args.validate:
        ok, errors = validate_sarif(sarif)
        if ok:
            print("SARIF validation: OK", file=sys.stderr)
        else:
            print(f"SARIF validation FAILED ({len(errors)} error(s)):", file=sys.stderr)
            for e in errors:
                print(f"  - {e}", file=sys.stderr)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(text)
        print(f"SARIF report written to {args.output}", file=sys.stderr)
    else:
        print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
