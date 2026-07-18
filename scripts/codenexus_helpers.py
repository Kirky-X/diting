#!/usr/bin/env python3
"""CodeNexus bridge for the diting scanner suite.

Architectural note — why this module emits CLI commands, not MCP calls:
  The three Engine-A scanners run as standalone Python subprocesses. CodeNexus is
  a flag-based CLI (`codenexus <subcommand> --flag value`); its MCP server
  (`codenexus mcp`) is only reachable from the agent layer over stdio, NOT from a
  child process. So this module does the part that *must* live in the scripts
  (detect the index DB, extract & prioritize symbol-level blast-radius targets
  from concrete findings) and emits a structured worklist of `codenexus` CLI
  commands. The agent layer then runs those commands — the only place they can
  actually execute. See SKILL.md "Step 1.5 — CodeNexus Blast Radius Pre-check" for the contract.

The embedded CodeNexus skill under `.claude/skills/codenexus/SKILL.md` describes the
full CLI workflow; this module is the scanner-side adapter that feeds it.
"""

from __future__ import annotations

import os
import re
from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Optional

# Default CodeNexus database file name (used by `codenexus index` / `--db`).
_CODENEXUS_DB = "codenexus.lbug"

# Severity ordering for target prioritization — only critical/high findings are
# worth a blast-radius check (those are the ones that block approval).
_IMPACT_SEVERITIES = {"critical", "high"}

# Pattern that introduces a named callable/type. Used to recover the enclosing
# symbol for a finding when the scanner didn't attach one (most don't).
_DEF_RE = re.compile(
    r"^\s*(?:def|class|function|func|fn|public|private|protected|static|async)"
    r"\s+(\w+)"
)

# Heuristic concept keywords per finding category, fed to `codenexus query` so the
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
    """A single symbol worth a `codenexus impact` call."""

    symbol: str
    file: str
    line: int
    severity: str
    category: str
    rule_id: str


def _find_db(start: str = ".") -> Optional[str]:
    """Walk upward from `start` looking for a CodeNexus DB (`.codenexus.lbug`).

    Returns the absolute path to the DB file if found, else None. Never raises.
    """
    here = os.path.abspath(start)
    if os.path.isfile(here):
        here = os.path.dirname(here)
    while True:
        candidate = os.path.join(here, _CODENEXUS_DB)
        if os.path.isfile(candidate):
            return candidate
        parent = os.path.dirname(here)
        if parent == here:
            return None
        here = parent


def find_repo_root(start: str = ".") -> str:
    """Walk upward from `start` looking for a directory containing a CodeNexus DB.

    Returns the repo root if found, else the resolved `start`. Never raises.
    """
    db = _find_db(start)
    if db:
        return os.path.dirname(db)
    return os.path.abspath(start)


def index_available(start: str = ".") -> bool:
    """True iff a CodeNexus DB (`codenexus.lbug`) is present at/above `start`."""
    return _find_db(start) is not None


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
    """Extract deduplicated, prioritized CodeNexus impact targets from findings.

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
            continue  # nothing to target with `codenexus impact`
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
    """Distinct concept strings for `codenexus query`, one per finding category.

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


def format_codenexus_section(
    targets: List[ImpactTarget],
    concepts: List[str],
    repo_root: Optional[str] = None,
    db: Optional[str] = None,
) -> str:
    """Render a markdown worklist the agent executes via `codenexus` CLI.

    Returns an empty string when there is nothing to recommend (no targets AND no
    concepts), so callers can unconditionally append the result.
    """
    if not targets and not concepts:
        return ""
    db_flag = f" --db {db}" if db else ""
    lines: List[str] = []
    lines.append("### 🔭 CodeNexus Blast Radius Pre-check\n")
    if repo_root:
        lines.append(f"**Index detected**: `{repo_root}/{_CODENEXUS_DB}`\n")
    lines.append(
        "> Scanner-side adapter. The listed `codenexus` CLI commands must be run "
        "by the agent (the CLI is not invoked from the scanner subprocess). See "
        "`.claude/skills/codenexus/SKILL.md`.\n"
    )
    if targets:
        lines.append("**Impact analysis** (critical/high findings → upstream callers):")
        lines.append("")
        for t in targets:
            lines.append(
                f'- `codenexus impact --symbol {t.symbol} --depth 3 '
                f'--edge_types "CALLS,IMPLEMENTS,USES_TYPE" --max_depth 3 '
                f'--include_tests false{db_flag}` — {t.severity}/{t.rule_id} @ '
                f"`{os.path.basename(t.file)}:{t.line}`"
            )
        lines.append("")
        lines.append(
            "> Review `d=1` (WILL BREAK) callers first; cross-check affected "
            "execution flows via `codenexus context --symbol <SYMBOL> --enhanced true`."
        )
        lines.append("")
    if concepts:
        lines.append("**Execution-flow location** (one query per finding category):")
        lines.append("")
        for c in concepts:
            # Escape double quotes inside the concept for safe Cypher embedding.
            safe = c.replace('"', "'")
            lines.append(
                f'- `codenexus query --cypher "MATCH (f:Function) WHERE f.name '
                f"CONTAINS '{safe}' RETURN f.name, f.filePath, f.startLine LIMIT 20\"{db_flag}`"
            )
        lines.append("")
    return "\n".join(lines)


def section_for_findings(
    findings: List[Dict[str, Any]],
    start: str = ".",
    max_targets: int = 15,
) -> str:
    """One-call helper: build & format the CodeNexus section if an index exists.

    Returns "" when no CodeNexus DB is present at/above `start` (graceful no-op),
    so scanners can call this unconditionally and only emit output when relevant.
    """
    db = _find_db(start)
    if not db:
        return ""
    root = os.path.dirname(db)
    targets = build_impact_targets(findings, max_targets=max_targets)
    concepts = build_query_concepts(findings)
    return format_codenexus_section(targets, concepts, repo_root=root, db=db)
