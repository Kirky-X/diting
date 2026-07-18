# Review Workflow — Complete Review Process

## Overview

Comprehensive code review: multi-dimensional parallel analysis + confidence scoring + unified report.

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

## Phase 3: Scoring and Filtering

For each finding:

```
1. Assign severity: Critical / High / Medium / Low / Info
2. Score confidence: 0–100
3. Filter: discard items < 80
4. Deduplicate: merge findings pointing to the same root cause
5. Sort: Critical first, then High, Medium, Low, Info
```

### Confidence Calibration

Use the following anchors when scoring:

| Scenario | Confidence |
|---|---|
| Hardcoded password in code | 98 |
| User input directly concatenated into SQL string | 95 |
| O(n²) nested loop on large dataset | 85 |
| Missing null check (language has no null safety) | 80 |
| Method 60 lines (threshold 50) | 75 — borderline |
| Possible race condition (concurrency model unclear) | 55 — skip until context confirmed |
| Naming could be improved | 40 — skip |

---

## Phase 4: Generate Report

Follow the template in [templates/report.md](templates/report.md).

### Report Must Include

1. **Executive Summary** — score, file count, issue counts by severity
2. **Issue Table** — ID, file:line, severity, confidence, brief description
3. **Per-Issue Details** — issue explanation, risk, specific fix recommendation with code
4. **Verdict** — Approved / Changes Requested / Rejected

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

---

## Related

- [commands/security.md](commands/security.md)
- [commands/performance.md](commands/performance.md)
- [commands/quality.md](commands/quality.md)
- [commands/architecture.md](commands/architecture.md)
- [commands/simplification.md](commands/simplification.md)
- [templates/report.md](templates/report.md)
