# Review Workflow — Complete Review Workflow

## Overview

Comprehensive code review: multi-dimensional parallel analysis + confidence scoring + unified report.

Two review modes available:
- **Parallel Analysis** — AI Agent automated process, fast and consistent
- **Three-Pass Review** — Human reviewer systematic scan, comprehensive and thorough

---

## Workflow Modes

| Mode | Use Case | Advantages | Reference |
|---|---|---|---|
| Parallel Analysis | AI Agent, automated processes | Fast, consistent | This document |
| Three-Pass Review | Human reviewers, learning process | Comprehensive, systematic | [workflow/three-pass-review.md](workflow/three-pass-review.md) |

### Combined Usage

```
1. AI parallel analysis generates initial report
2. Human three-pass review confirms and supplements
3. Merge to output final review report
```

---

## Phase 1: Pre-Review Checklist

```
□ Identify language(s) and runtime
□ Read CLAUDE.md / .editorconfig / linting configs for project standards
□ Determine what changed (PR diff vs. full codebase)
□ Check if tests exist (affects confidence scoring)
□ Note any explicitly stated constraints or priorities
```

---

## Phase 2: Parallel Analysis (5 Agents)

Execute all 5 dimensions independently, then merge findings:

| Agent | Focus | Key Reference |
|---|---|---|
| **Security** | OWASP Top 10 (2021), CWE, auth, crypto, secrets | [commands/security.md](commands/security.md) |
| **Performance** | Big-O, DB queries, caching, async, Web Vitals | [commands/performance.md](commands/performance.md) |
| **Quality** | Code smells, SOLID, complexity, test coverage | [commands/quality.md](commands/quality.md) |
| **Architecture** | Patterns, coupling, cohesion, dependencies | [commands/architecture.md](commands/architecture.md) |
| **Simplification** | Readability, duplication, dead code, naming | [commands/simplification.md](commands/simplification.md) |

---

## Phase 3: Score & Filter

For each finding:

```
1. Assign severity: Critical / High / Medium / Low / Info
2. Score confidence: 0–100
3. Filter: discard anything < 80
4. Deduplicate: merge findings that refer to the same root cause
5. Prioritize: Critical first, then High, Medium, Low, Info
```

### Confidence Calibration

Use these anchors when scoring:

| Scenario | Confidence |
|---|---|
| Hardcoded password in code | 98 |
| SQL string concatenation with user input | 95 |
| O(n²) nested loop on potentially large dataset | 85 |
| Missing null check (language has no null safety) | 80 |
| Method is 60 lines (threshold is 50) | 75 — borderline |
| Possible race condition (unclear concurrency model) | 55 — skip unless context confirms |
| Naming could be improved | 40 — skip |

---

## Phase 4: Generate Report

Follow the template in [templates/report.md](templates/report.md).

### Report Must Include

1. **Executive Summary** — Score, file count, issue count by severity
2. **Issues table** — ID, file:line, severity, confidence, brief description
3. **Per-issue detail** — Problem explanation, risk, and concrete fix suggestion with code
4. **Verdict** — Approved / Changes Requested / Rejected

---

## Review Priorities

```
1. Security       → Always highest. Never skip.
2. Correctness    → Functional bugs, data integrity
3. Performance    → Significant impact only (≥ High severity)
4. Quality        → Maintainability, test coverage
5. Simplification → Lowest. Skip if time-constrained.
```

---

## False Positive Reduction

Before reporting an issue, verify:

- [ ] Does the project already handle this elsewhere? (e.g., middleware auth, ORM escaping)
- [ ] Is there an existing lint rule or annotation suppressing it?
- [ ] Does the CLAUDE.md explicitly allow this pattern?
- [ ] Is this code path actually reachable / exercised?
- [ ] Would a senior developer on this project agree this is a real issue?

---

## Special Cases

### PR / Diff Review
- Focus only on changed lines
- Consider context of surrounding unchanged code
- Check that tests cover the new code paths

### Single-File Review
- Full analysis, all dimensions
- Note what's missing (tests, types, error handling)

### Full Codebase Review
- Sample representative files per module
- Focus on architectural and cross-cutting concerns
- Report systemic patterns rather than individual occurrences

---

## Related

- [commands/security.md](commands/security.md)
- [commands/performance.md](commands/performance.md)
- [commands/quality.md](commands/quality.md)
- [commands/architecture.md](commands/architecture.md)
- [commands/simplification.md](commands/simplification.md)
- [templates/report.md](templates/report.md)
