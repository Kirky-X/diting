---
name: diting
description: "Code quality review suite. Triggers: review/audit/tech debt/over-engineering/simplify/agent audit; or any write/add/refactor/fix task"
license: MIT
---

# Code Review Suite — Three Engines, One Skill

This skill merges three originally independent toolkits. Each engine retains its own analysis methods (they solve different problems, forcing uniform format loses information), but they share one entry point, one mode table, and — for the default full review scenario — a merged report.

| Engine | Question Answered | Output Style | Source |
| ------ | ----------------- | ------------ | ------ |
| **A. Dimensional Review** | "Is the code correct, secure, fast, well-designed?" | Severity + Confidence scored issue list, 100-point score, Approved/Changes/Rejected verdict | `references/commands/*`, `references/{security,performance,quality,architecture,correctness,simplification}/*` |
| **B. Decay Diagnosis** | "Why is this code painful to maintain? Which book principle explains it?" | Symptom → Source → Consequence → Remedy findings, Health Score, module dependency graph | `references/decay/*` |
| **C. Simplification & Refinement** | "Does this code exceed what the problem needs? Is it clear enough?" | Ladder (before writing code, minimal priority) · Deletion checklist (`tag: what to cut`, report only) · Refinement pass (post-hoc clarity edit, preserving behavior) | `references/simplicity/*` |

Only read reference files needed for the selected mode — don't preload all three engines.

**TL;DR Routing**: Reviewing/reporting code → Engine A (specified dimension) or Engine B (whole codebase/decay framework) or merged Full Review (unspecified dimension). Writing/editing code → Ladder during writing, Refinement Pass after. Want deletion checklist only, no editing → Over-engineering Review/Audit. See full details below.

## Step 1 — Route the Request

| User says... | Mode | Engine | Reference |
| ------------ | ---- | ------ | --------- |
| `review` (no args) | **Full Review** (merged) | A+B+C | See "Full Review" below |
| `review security` | Security | A | [commands/security.md](references/commands/security.md) |
| `review performance` | Performance | A | [commands/performance.md](references/commands/performance.md) |
| `review quality` | Quality | A | [commands/quality.md](references/commands/quality.md) |
| `review architecture` | Architecture | A | [commands/architecture.md](references/commands/architecture.md) |
| `review simplification` | Simplification | A | [commands/simplification.md](references/commands/simplification.md) |
| `review api` | API | A | [commands/api.md](references/commands/api.md) |
| `review database` | Database | A | [commands/database.md](references/commands/database.md) |
| `review testing` | Testing | A | [commands/testing.md](references/commands/testing.md) |
| `review documentation` | Documentation | A | [commands/documentation.md](references/commands/documentation.md) |
| `review i18n` | i18n | A | [commands/i18n.md](references/commands/i18n.md) |
| `review accessibility` | Accessibility | A | [commands/accessibility.md](references/commands/accessibility.md) |
| `review correctness` | Correctness | A | [commands/correctness.md](references/commands/correctness.md) |
| `review agent` | Agent (12-factor audit) | A | [commands/agent.md](references/commands/agent.md) |
| `review diff` | Diff Review | A | [commands/diff-review.md](references/commands/diff-review.md) |
| `review pre-commit` | Pre-commit | A | [commands/pre-commit.md](references/commands/pre-commit.md) |
| `review batch` | Batch Review | A | [commands/batch-review.md](references/commands/batch-review.md) |
| "audit this codebase", "does this follow clean architecture", "codebase tour" | Architecture Audit | B | [decay/architecture-guide.md](references/decay/architecture-guide.md) (+ [onboarding-guide.md](references/decay/onboarding-guide.md) for tour) |
| "tech debt", "what should we fix first", "refactoring roadmap" | Tech Debt Assessment | B | [decay/debt-guide.md](references/decay/debt-guide.md) |
| "our tests keep breaking", "too many mocks", test-suite review | Test Quality Review | B | [decay/test-guide.md](references/decay/test-guide.md) |
| "how healthy is this codebase", "run all the checks" | Health Dashboard | B | [decay/health-guide.md](references/decay/health-guide.md) |
| "fix everything", "sweep the codebase", "auto-fix all issues" | Full Sweep & Auto-Fix ⚠️ writes code | B | [decay/sweep-guide.md](references/decay/sweep-guide.md) |
| "review for over-engineering", "what can we delete", "is this over-engineered" | Over-engineering Review (diff) | C | [simplicity/overengineering-review.md](references/simplicity/overengineering-review.md) |
| "audit for over-engineering", "find bloat", repo-wide | Over-engineering Audit | C | [simplicity/overengineering-audit.md](references/simplicity/overengineering-audit.md) |
| "what did we mark to do later", "list the shortcuts" | Debt Ledger (`lazy:` comments) | C | [simplicity/debt-ledger.md](references/simplicity/debt-ledger.md) |
| "clean this up", "make this more readable/consistent", "refine/polish this" | Refinement Pass | C | [simplicity/refinement-pass.md](references/simplicity/refinement-pass.md) |
| "be lazy", "minimal solution", "yagni", writing/editing code | Simplicity Lens (ambient) | C | [simplicity/ladder.md](references/simplicity/ladder.md) |

**Fallback & Scope Confirmation**: Unknown mode / no args → Full Review. Vague request ("check this") → Ask: single file · PR diff · whole codebase. Missing target path → Ask, never fabricate. Before whole-codebase or batch scan, confirm target path + dimension list with user.

**"Simplify this" Disambiguation** (Engine C's three modes share vocabulary — disambiguate by what user wants to do, not by keyword):

- Want **deletion checklist**, no code changes ("what can I delete", "is this over-engineered", "review for over-engineering") → Over-engineering Review/Audit. Report only, never edit code.
- **Writing new code**, or explicitly want simplest/shortest solution ("be lazy", "yagni", "minimal solution") → Ladder (ambient). Edit directly, bias toward the least code that works.
- Want **existing/newly-written code to be clearer**, not necessarily shorter ("clean this up", "make this more readable/consistent", "refine this") → Refinement Pass. Edit directly, but clarity over brevity here — opposite bias from Ladder.
- Genuinely unsure which → ask one line: "Want deletion checklist, shortest version, or just clearer/more readable?"

**"Architecture" Disambiguation** (Both Engine A and Engine B cover architecture, different scope):

- Scope limited to **current diff/PR** ("does this PR's design make sense", `review architecture`) → Engine A [commands/architecture.md](references/commands/architecture.md).
- Scope is **whole codebase module structure** ("audit the architecture", "why does everything depend on everything", dependency graph) → Engine B [decay/architecture-guide.md](references/decay/architecture-guide.md).
- Both requested, or scope unclear on small diff → default Engine A (cheaper, matches declared scope); mention Engine B's full codebase audit as follow-up option, not both unprompted.

## Checkpoints

Ask before proceeding when:

1. **Full Sweep** — the only mode that writes files across the whole codebase without prompting. Show the pre-consent prompt from [decay/sweep-guide.md](references/decay/sweep-guide.md) Step 0, wait for one-time approval, then run hands-free.
2. **Whole codebase or batch scan** (any other mode) — confirm target path and dimension list first (see Step 1 fallback above).
3. **Genuinely ambiguous routing** — "Simplify this" or "Architecture" request doesn't cleanly map to a mode (see disambiguation above).

All other modes (Full Review, single-dimension review, Ladder, Refinement Pass) only touch the code the user is asking about this turn — no unprompted whole-codebase edits outside Full Sweep.

## Step 1.5 — CodeNexus Blast Radius Pre-check (optional, when index exists)

If the repo root has a `codenexus.lbug` index (meaning the user has run `codenexus index`), do two things **before reviewing** using the `codenexus` CLI to tie scan findings to execution flow and blast radius. Skip this section if no index exists — don't fabricate one.

1. **Locate execution flow** — for business concepts in review scope, run `codenexus query --cypher "MATCH (f:Function) WHERE f.name CONTAINS '<concept>' RETURN f.name, f.filePath, f.startLine LIMIT 20"` to get related symbols and their file locations. This upgrades "line-level findings" to "flow-level context".
2. **Assess blast radius** — for key symbols to be changed or critiqued (e.g., functions on approval, payment, auth paths), run `codenexus impact --symbol <symbol> --depth 3 --edge_types "CALLS,IMPLEMENTS,USES_TYPE" --max_depth 3 --include_tests false` and check `d=1` (WILL BREAK) direct callers first. Before commit, use `codenexus detect_changes --path <REPO> --mode staged` to map git diff to affected flows.

The script side (`parallel_review.py` / `analyzer.py` / `security_check.py`) automatically produces this worklist in reports via shared `scripts/codenexus_helpers.py` — it detects the index, extracts symbols from critical/high findings, and generates `codenexus impact` / `codenexus query` command lists for execution. **Scripts themselves cannot call the CLI** (they're subprocesses, CLI only available to the agent layer), so the list is for the agent to run, not the script itself. See the embedded `.claude/skills/codenexus/SKILL.md` (official CodeNexus skill with full subcommand docs) for complete workflow.

## Step 2 — Collect Context (All Engines)

1. Language, project type (service / CLI / library / frontend / pipeline)
2. Scope: single file, PR diff, or whole codebase — when unspecified see [decay/common.md](references/decay/common.md) Auto Scope Detection
3. Project standards: `CLAUDE.md`, `.eslintrc`, `pyproject.toml`, and — for Engine B — `.decay-review.yaml` config (disable/severity/ignore/focus/strictness overrides, see [decay/common.md](references/decay/common.md))

## Step 3 — Execute

### Single-dimension / single-engine modes

Follow the linked reference file directly; it's self-contained. Engine A files (`commands/*.md`) use the Confidence + Severity model below. Engine B files always start with "Read `decay/common.md` for the Iron Law, config, report template, and Health Score" — do that first. Engine C files are short and self-contained.

### Full Review (default, merged output)

When user asks for plain review without dimension name, run all three engines and merge into **one** report:

1. **Engine A** — scan security, performance, quality, architecture, simplification (the five default dimensions from [review-workflow.md](references/review-workflow.md)), find concrete, well-located issues. Score each with Confidence (0–100, only report ≥80) and Severity (Critical/High/Medium/Low).
2. **Engine B** — run PR-Review decay scan on same scope ([decay/pr-review-guide.md](references/decay/pr-review-guide.md)): Six Decay Risks (R1–R6), each written as Symptom → Source → Consequence → Remedy. Apply Iron Law from [decay/common.md](references/decay/common.md): no remedy without diagnosed consequence.
3. **Engine C** — do a single over-engineering pass using tags from [simplicity/overengineering-review.md](references/simplicity/overengineering-review.md) (`delete:` `stdlib:` `native:` `yagni:` `shrink:`). Scope-limited — correctness/security/performance stay in Engine A, no duplication here.
4. **Merge**: use report skeleton from [templates/report.md](references/templates/report.md) as shell (Summary table, Overall Score, Verdict), but give Engine B findings their own `### 🧬 Decay Risks` subsection (S→S→C→R format, don't squeeze into Engine A's Problem/Fix format — the reasoning chain is the point), and Engine C findings their own `### ✂️ Simplification Opportunities` subsection (one line each, ending `net: -N lines possible`).
5. **Score**: compute Engine A's Overall Score (100 − deductions) per [templates/report.md](references/templates/report.md) as headline score. Report Engine B's Health Score alongside as second number (different weighting — Health Score penalizes decay risk, not bugs — don't average them). Engine C has no independent score; its net-lines number stands alone.
6. **Verdict**: driven only by Engine A's Critical/High findings (per [templates/report.md](references/templates/report.md) table). Decay risks and simplification opportunities go into Summary but never independently block verdict — they're maintainability signals, not defects.

### Writing or editing code (not review)

Apply Ladder ambiently per [simplicity/ladder.md](references/simplicity/ladder.md): climb the ladder before writing code (YAGNI → reuse → stdlib → native → existing dep → one line → minimum), mark deliberate shortcuts with `lazy:` comments naming the ceiling and upgrade trigger, unprompted explanations max three lines. Applies regardless of whether review is requested — it governs how code is written, not just how it's scored. Never simplify away input validation, error handling, security, or accessibility. Exit switch: "stop simplify" / "normal mode" disables Ladder for remaining session; re-enable with "simplify" or specifying level (`lite`/`full`/`ultra`). If user says "just fix this, don't refactor" or similar, skip Ladder reshaping this turn — do the minimal fix requested, no more; Ladder governs new code, not rewriting working code nobody asked to touch.

**Then, before presenting results**, silently run Refinement Pass ([simplicity/refinement-pass.md](references/simplicity/refinement-pass.md)) on the just-written code — check naming, nesting, project convention alignment, fix what's worth fixing. Scope guardrail: only touch just-written or explicitly pointed-at lines; if real fix needs touching unrelated existing code, call it out rather than silently expanding diff. This is the one check that biases opposite to Ladder: Ladder biases toward least code, Refinement Pass biases toward clearest code, second pass catches where first went too far (one dense line genuinely hard to read, concerns merged that should be separate). Only mention if something actually changed.

## Reference Index

```
references/
├── review-workflow.md, anti-patterns.md        — Engine A shared workflow
├── commands/*.md                                — Engine A, 16 dimension guides
├── security/ performance/ quality/ correctness/
│   architecture/ simplification/                — Engine A deep materials
├── security/security-design-patterns.md         — Security pattern catalog
│                                                    (arch/design/impl layers, STRIDE→pattern)
├── templates/report.md, feedback-examples.md    — Engine A + merged report shell
├── workflow/three-pass-review.md                — Engine A methodology
├── decay/common.md                              — Engine B core: Iron Law, config,
│                                                    report template, Health Score,
│                                                    history tracking, triage
├── decay/decay-risks.md, test-decay-risks.md,
│   source-coverage.md, custom-risks-guide.md,
│   remedy-guide.md                              — Engine B risk definitions
├── decay/{architecture,debt,pr-review,sweep,
│   health,test,onboarding}-guide.md             — Engine B mode workflows
├── simplicity/ladder.md                         — Engine C: minimal priority ladder
├── simplicity/overengineering-review.md         — Engine C: diff-scope deletion checklist
├── simplicity/overengineering-audit.md          — Engine C: repo-scope deletion checklist
├── simplicity/refinement-pass.md                — Engine C: post-hoc clarity edit
└── simplicity/debt-ledger.md                    — Engine C: `lazy:` comment ledger

scripts/
├── analyzer.py           — Static analysis helper (Engine A)
├── security_check.py     — Pattern-based security scan (Engine A; single source for security patterns)
├── parallel_review.py    — Fan-out multi-dimension review (Engine A); its per-dimension
│                             reference paths remain valid after this merge; CPU-bound
│                             analysis via multiprocessing.Pool, --format sarif outputs SARIF
├── sarif_report.py       — Aggregates three scanner results into SARIF 2.1.0 (with structural validation)
└── codenexus_helpers.py  — Detects codenexus.lbug index, extracts blast radius targets, produces
                              codenexus impact/query command lists for agent execution (CLI runs on agent layer)

.claude/skills/codenexus/  — Embedded official CodeNexus skill (single SKILL.md file);
                             defines complete codenexus CLI workflow, referenced in Step 1.5
```

## Notes

- Engine B's `.decay-review.yaml` config (disable/severity/ignore/focus/strictness) and Ladder's intensity levels (`lite`/`full`/`ultra`) are independent settings — a project can set both without conflict.
- Engine B's history tracking (`.decay-review-history.json`) and Engine C's debt ledger (`SIMPLIFY-DEBT.md`) are separate artifacts; don't merge them.
- Engine A has no config file of its own, always runs default dimensions; Engine B's `.decay-review.yaml` only affects Engine B. If a project disables a risk in `.decay-review.yaml` (e.g., architecture decay), but the same concern appears as an Engine A finding (e.g., from `review architecture`), report it normally there — config only silences Engine B's own findings, doesn't suppress Engine A.
- Refinement Pass is the latest Engine C mode: it edits code for clarity post-hoc, not deciding how much code to write upfront (Ladder) or listing what to delete (Over-engineering Review/Audit). Treat it as a balance check on the other two, not a fourth independent engine.
