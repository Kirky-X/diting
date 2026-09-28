# Review Workflow — Complete Review Process

## Overview

Comprehensive code review: multi-dimensional parallel analysis + confidence scoring + adversarial verification + unified report.

Two review modes available:
- **Parallel Analysis** — AI Agent automated workflow, fast and consistent
- **Three-Pass Review** — Human reviewer systematic scan, comprehensive and thorough

---

## Workflow Modes

| Mode | Use Case | Advantages | Reference |
|---|---|---|---|
| Parallel Analysis | AI Agent, automated workflow | Fast, consistent | This document |
| Three-Pass Review | Human reviewer, learning process | Comprehensive, systematic | [workflow/three-pass-review.md](workflow/three-pass-review.md) |

### Combined Usage

```
1. AI parallel analysis generates initial report
2. Human three-pass review confirms and supplements
3. Merge to produce final review report
```

---

## Phase 1: Pre-Review Checklist

```
□ Identify language and runtime
□ Read CLAUDE.md / .editorconfig / lint config to understand project standards
□ Determine change scope (PR diff or full codebase)
□ Check if tests exist (affects confidence scoring)
□ Note any explicitly stated constraints or priorities
```

---

## Phase 2: Parallel Analysis (5 Agents)

Execute all 5 dimensions independently, then merge findings:

| Agent | Focus | Key Reference |
|---|---|---|
| **Security** | OWASP Top 10 (2021), CWE, authentication, encryption, keys | [commands/security.md](commands/security.md) |
| **Performance** | Big-O, database queries, caching, async, Web Vitals | [commands/performance.md](commands/performance.md) |
| **Quality** | Code smells, SOLID, complexity, test coverage | [commands/quality.md](commands/quality.md) |
| **Architecture** | Patterns, coupling, cohesion, dependencies | [commands/architecture.md](commands/architecture.md) |
| **Simplification** | Readability, duplication, dead code, naming | [commands/simplification.md](commands/simplification.md) |

---

## Phase 3: Scoring and Adjudication

For each finding:

```
1. Assign severity: Critical / High / Medium / Low / Info
2. Score confidence: 0–100
3. Adjudicate: confirmed / needs-verification / rejected — low-confidence candidates are reported, not silently discarded (see Three-State Adjudication)
4. Deduplicate: merge findings pointing to the same root cause
5. Variant Search: for each confirmed Critical/High root cause, hunt same-root-cause variants in the remaining scope (see Variant Search)
6. Sort: Critical first, then High, Medium, Low, Info
```

### Three-State Adjudication

Findings are never silently discarded at a confidence cliff. Every candidate is adjudicated into exactly one of three states:

| State | Enters When | Report Treatment |
|---|---|---|
| **confirmed** | Confidence ≥ 80 and it survives False Positive Reduction | Severity assigned, score deducted, may drive verdict |
| **needs-verification** | Confidence 55–79: grounded in real code, but one decisive fact is unconfirmed | Formal output — **no severity, no score deduction, no verdict impact**; must carry a **Blocker** (the exact missing fact) and a **Verification Plan** (how to resolve it) |
| **rejected** | Falsified by False Positive Reduction or the Verification Pass | Archived with the falsification reason so the same issue is not re-reported in later rounds |

Typical blockers: concurrency model unclear (possible race condition), a deployment-only control absent from the repo (proxy rate limit, WAF), runtime behavior not derivable from source. A needs-verification candidate is promoted to confirmed only when the missing fact is resolved within this review; otherwise it stays in the report's **Needs Verification** section — it is never upgraded to a scored finding by assumption.

---

### Confidence Calibration

Use the following anchors when scoring:

| Scenario | Confidence |
|---|---|
| Hardcoded password in code | 98 |
| User input directly concatenated into SQL string | 95 |
| O(n²) nested loop on large dataset | 85 |
| Missing null check (language has no null safety) | 80 |
| Method 60 lines (threshold 50) | 75 — needs-verification (borderline) |
| Possible race condition (concurrency model unclear) | 55 — needs-verification; blocker: concurrency model unconfirmed |
| Naming could be improved | 40 — below candidate floor: not a candidate, no report entry |

Below 55 the candidate floor is not met: not a candidate — no report entry. The Three-State Adjudication above applies from 55 up; the floor itself is a judgment call, not a discard cliff, so a sub-55 observation that matters for other reasons is raised in prose, not as a scored finding.

---

### Variant Search

After a Critical/High root cause is confirmed (post-deduplication), actively hunt the remaining in-scope code for variants of the same root cause across three classes:

| Class | What to Look For |
|---|---|
| **Lexical** | Same unsafe API or pattern spelled differently (`exec` vs `execute`, `query` vs `rawQuery`) |
| **Structural** | Same construction in a different shape (string-concatenated SQL inline vs inside a shared helper) |
| **Logical** | Same flaw reached through a different mechanism (the same missing authz check enforced at another layer) |

Same root cause merges into one finding, but each variant's trigger conditions and impact are confirmed independently — a variant that cannot establish its own conditions and impact is not counted. Variants found here enter the same Three-State Adjudication as any other finding.

---

## Phase 4: Verification Pass

Run after Phase 3, before the report's verdict is produced. Every **Critical** and **High** finding that would drive the verdict is re-checked adversarially by an independent verifier that did not produce the finding (a fresh subagent, or a fresh context pass scoped to that one finding). The verifier's goal is refutation, not confirmation. Open the verifier prompt with:

```
You did not write this candidate. Try to refute it.
```

Verifier checklist:

- [ ] **Reachability trace** — the entry point is actually reachable and the path reaches the claimed sink (not just a textual match)
- [ ] **Compensating controls** — no upstream validation, framework guard, middleware, or ORM layer already neutralizes it (re-derived independently, not trusted from the finder)
- [ ] **Peer comparison** — comparable modules or baselines sharing the same pattern are noted as calibration, never as grounds to dismiss
- [ ] **Severity match** — the claimed impact holds at the claimed severity

Outcomes:

| Verifier Result | Action |
|---|---|
| Finding survives | Stays confirmed; drives the verdict |
| Finding materially replaced (severity, location, or root cause changed) | Hand the replacement to a **new** independent verifier before it drives the verdict |
| Finding refuted | Moves to rejected — archived with the falsification reason; verdict is recomputed without it |

Needs-verification candidates never drive the verdict and do not enter this pass. Scope: applies to Full Review and single-dimension reviews; [commands/pr-review.md](commands/pr-review.md) runs under its own fixed subagent budget (hard cap 11) and is not extended by this pass.

---

## Phase 5: Generate Report

Follow the template in [templates/report.md](templates/report.md).

### Report Must Include

Same sections, in the same order, as the [templates/report.md](templates/report.md) Detailed format:

1. **Executive Summary** — score, file count, issue counts by severity
2. **Issue Table** — ID, file:line, severity, confidence, brief description
3. **Per-Issue Details** — issue explanation, risk, specific fix recommendation with code
4. **Needs Verification** — candidates with blocker + verification plan; no severity, no score deduction, no verdict impact
5. **Rejected (archived)** — falsified candidates with the falsification reason, so the same issue is not re-reported in later rounds
6. **Recommendations** — immediate / this sprint / backlog
7. **Verdict** — Approved / Changes Requested / Rejected
8. **Coverage** — reviewed paths + sampling strategy, uncovered paths + reasons, explicit "checked X — no findings" statements

---

## Review Priority

```
1. Security        → Always highest. Never skip.
2. Correctness     → Functional bugs, data integrity
3. Performance     → Only significant impact (≥ High severity)
4. Quality         → Maintainability, test coverage
5. Simplification  → Lowest. Skip when time is tight.
```

---

## False Positive Reduction

Before reporting an issue, verify:

- [ ] Is the project already handling this elsewhere? (e.g., middleware auth, ORM escaping)
- [ ] Is there a lint rule or annotation that suppresses it?
- [ ] Does CLAUDE.md explicitly allow this pattern?
- [ ] Is this code path actually reachable / executed?
- [ ] Would a senior developer on this project agree this is a real issue?

A candidate falsified here (or by the Verification Pass) moves to **rejected** — archived with the falsification reason so the same issue is not re-reported in later rounds; it is not silently dropped.

---

## Special Scenarios

### PR / Diff Review
- Focus only on changed lines
- Consider context from surrounding unchanged code
- Check if tests cover new code paths

### Single File Review
- Comprehensive analysis across all dimensions
- Note missing items (tests, types, error handling)

### Full Codebase Review
- Sample representative files per module
- Focus on architecture and cross-cutting concerns
- Report systemic patterns rather than individual occurrences
- Hard requirement: sampling review is partial by definition — the report's Coverage section must state which paths were reviewed (with the sampling strategy) and which were not, with reasons (see [templates/report.md](templates/report.md))

---

## Related

- [commands/security.md](commands/security.md)
- [commands/performance.md](commands/performance.md)
- [commands/quality.md](commands/quality.md)
- [commands/architecture.md](commands/architecture.md)
- [commands/simplification.md](commands/simplification.md)
- [templates/report.md](templates/report.md)
