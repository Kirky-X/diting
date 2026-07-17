#!/usr/bin/env python3
"""GitNexus bridge for the diting scanner suite.

Architectural note — why this module does NOT call `mcp__gitnexus__*` directly:
  The three Engine-A scanners run as standalone Python subprocesses. MCP tools
  (`mcp__gitnexus__impact`, `mcp__gitnexus__query`, …) are JSON-RPC calls served
  to the agent layer (Claude Code) over its MCP transport — they are NOT reachable
  from a child process. So this module does the part that *must* live in the
  scripts (detect the index, extract & prioritize symbol-level blast-radius
  targets from concrete findings) and emits a structured worklist. The agent
  layer then executes the listed `mcp__gitnexus__*` calls — the only place they
  can actually run. See SKILL.md "步骤 1.5 — GitNexus 爆炸半径预检" for the contract.

The embedded sub-skills under `.claude/skills/gitnexus/` (6 files) describe the
full MCP workflow; this module is the scanner-side adapter that feeds it.
"""

from __future__ import annotations

import os
import re
from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Optional

# Severity ordering for target prioritization — only critical/high findings are
# worth a blast-radius check (those are the ones that block approval).
_IMPACT_SEVERITIES = {"critical", "high"}

# Pattern that introduces a named callable/type. Used to recover the enclosing
# symbol for a finding when the scanner didn't attach one (most don't).
_DEF_RE = re.compile(
    r"^\s*(?:def|class|function|func|fn|public|private|protected|static|async)"
    r"\s+(\w+)"
)

# Heuristic concept keywords per finding category, fed to gitnexus_query so the
# agent can locate the execution flow a finding lives in.
_CATEGORY_CONCEPTS: Dict[str, str] = {
    "security": "security-sensitive code path",
    "correctness": "data flow and state mutation",
    "performance": "hot loop and query execution path",
    "quality": "module structure and call graph",
    "architecture": "cross-module dependency and layering",
    "simplification": "duplication and shared logic",
}


@dataclass(frozen=True)
class ImpactTarget:
    """A single symbol worth a `mcp__gitnexus__impact` call."""

    symbol: str
    file: str
    line: int
    severity: str
    category: str
    rule_id: str


def find_repo_root(start: str = ".") -> str:
    """Walk upward from `start` looking for a directory containing a .gitnexus/ index.

    Returns the repo root if found, else the resolved `start`. Never raises.
    """
    here = os.path.abspath(start)
    if os.path.isfile(here):
        here = os.path.dirname(here)
    while True:
        if os.path.isdir(os.path.join(here, ".gitnexus")):
            return here
        parent = os.path.dirname(here)
        if parent == here:
            return os.path.abspath(start)
        here = parent


def index_available(start: str = ".") -> bool:
    """True iff a GitNexus index (`.gitnexus/`) is present at/above `start`."""
    return os.path.isdir(os.path.join(find_repo_root(start), ".gitnexus"))


def enclosing_symbol(file_path: str, line: int) -> Optional[str]:
    """Best-effort name of the function/method/class enclosing `line` in `file_path`.

    Walks backward from `line` to the nearest definition line. Returns None if the
    file cannot be read or no definition is found (module-level finding).
    """
    try:
        with open(file_path, "r", encoding="utf-8", errors="replace") as f:
            lines = f.readlines()
    except OSError:
        return None
    for i in range(min(line, len(lines)) - 1, -1, -1):
        m = _DEF_RE.match(lines[i])
        if m:
            return m.group(1)
    return None


def _severity(issue: Dict[str, Any]) -> str:
    return str(issue.get("severity", "info")).lower()


def _rule_id(issue: Dict[str, Any]) -> str:
    cat = str(issue.get("category") or issue.get("issue_type") or "generic").lower()
    if issue.get("issue_type"):
        return f"{cat}/{issue['issue_type']}"
    return cat


def build_impact_targets(
    findings: Iterable[Dict[str, Any]],
    max_targets: int = 15,
) -> List[ImpactTarget]:
    """Extract deduplicated, prioritized GitNexus impact targets from findings.

    Only critical/high findings are considered — lower-severity findings rarely
    warrant a blast-radius check, and impact queries are not free. When the scanner
    did not attach a symbol name we recover one by scanning the source file.
    """
    seen: set = set()
    targets: List[ImpactTarget] = []
    # Stable ordering: severity (critical first), then file, then line.
    prioritized = sorted(
        findings,
        key=lambda f: (
            0 if _severity(f) == "critical" else 1,
            str(f.get("file") or f.get("file_path") or ""),
            int(f.get("line") or f.get("line_number") or 0),
        ),
    )
    for f in prioritized:
        if _severity(f) not in _IMPACT_SEVERITIES:
            continue
        file_path = f.get("file") or f.get("file_path")
        line = int(f.get("line") or f.get("line_number") or 0)
        if not file_path or not line:
            continue
        symbol = (
            f.get("method") or f.get("symbol") or enclosing_symbol(str(file_path), line)
        )
        if not symbol:
            continue  # nothing to target with `mcp__gitnexus__impact`
        key = (symbol, os.path.basename(str(file_path)))
        if key in seen:
            continue
        seen.add(key)
        targets.append(
            ImpactTarget(
                symbol=symbol,
                file=str(file_path),
                line=line,
                severity=_severity(f),
                category=str(f.get("category") or "generic").lower(),
                rule_id=_rule_id(f),
            )
        )
        if len(targets) >= max_targets:
            break
    return targets


def build_query_concepts(findings: Iterable[Dict[str, Any]]) -> List[str]:
    """Distinct concept strings for `mcp__gitnexus__query`, one per finding category.

    These let the agent locate the execution flows the findings live in, even when
    no individual symbol is impact-worthy (e.g. medium-severity findings).
    """
    categories = {str(f.get("category") or "").lower() for f in findings}
    concepts: List[str] = []
    for cat in sorted(categories):
        if not cat:
            continue
        concepts.append(_CATEGORY_CONCEPTS.get(cat, f"{cat} execution flow"))
    return concepts


def format_gitnexus_section(
    targets: List[ImpactTarget],
    concepts: List[str],
    repo_root: Optional[str] = None,
) -> str:
    """Render a markdown worklist the agent executes via `mcp__gitnexus__*`.

    Returns an empty string when there is nothing to recommend (no targets AND no
    concepts), so callers can unconditionally append the result.
    """
    if not targets and not concepts:
        return ""
    lines: List[str] = []
    lines.append("### 🔭 GitNexus 爆炸半径预检\n")
    if repo_root:
        lines.append(f"**Index detected**: `{repo_root}/.gitnexus/`\n")
    lines.append(
        "> Scanner-side adapter. The listed `mcp__gitnexus__*` calls must be made "
        "by the agent (MCP is not reachable from the scanner subprocess). See "
        "`.claude/skills/gitnexus/gitnexus-impact-analysis/SKILL.md`.\n"
    )
    if targets:
        lines.append("**Impact analysis** (critical/high findings → upstream callers):")
        lines.append("")
        for t in targets:
            lines.append(
                f'- `mcp__gitnexus__impact({{target: "{t.symbol}", '
                f'direction: "upstream"}})` — {t.severity}/{t.rule_id} @ '
                f"`{os.path.basename(t.file)}:{t.line}`"
            )
        lines.append("")
        lines.append(
            "> Review `d=1` (WILL BREAK) callers first; cross-check affected "
            "execution flows via `READ gitnexus://repo/{name}/processes`."
        )
        lines.append("")
    if concepts:
        lines.append("**Execution-flow location** (one query per finding category):")
        lines.append("")
        for c in concepts:
            lines.append(f'- `mcp__gitnexus__query({{query: "{c}"}})`')
        lines.append("")
    return "\n".join(lines)


def section_for_findings(
    findings: List[Dict[str, Any]],
    start: str = ".",
    max_targets: int = 15,
) -> str:
    """One-call helper: build & format the GitNexus section if an index exists.

    Returns "" when no GitNexus index is present at/above `start` (graceful no-op),
    so scanners can call this unconditionally and only emit output when relevant.
    """
    root = find_repo_root(start)
    if not os.path.isdir(os.path.join(root, ".gitnexus")):
        return ""
    targets = build_impact_targets(findings, max_targets=max_targets)
    concepts = build_query_concepts(findings)
    return format_gitnexus_section(targets, concepts, repo_root=root)
