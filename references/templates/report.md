# Review Report Template

## Output Modes

Two output formats are available:

| Mode | When to Use | Content |
|------|-------------|---------|
| **Detailed** | Full review, PR feedback | All issues with full context |
| **Concise** | Quick check, CI integration | Critical/High issues only |

---

## Output Format (Detailed)

Use this structure when reporting:

---

```markdown
## 🔍 Code Review Report

**Scope**: `<files or PR description>`  
**Language**: `<detected language(s)>`  
**Date**: `<today>`

---

### Summary

| Dimension | Issues Found | Highest Severity |
|---|---|---|
| 🔐 Security | N | 🔴 Critical / 🟠 High / etc. |
| ⚡ Performance | N | — |
| 🧹 Quality | N | — |
| 🏗️ Architecture | N | — |
| ✨ Simplification | N | — |
| **Total** | **N** | |

**Overall Score**: N / 100  
**Verdict**: ✅ Approved / ⚠️ Changes Requested / ❌ Rejected

---

### Issues

#### 🔴 Critical (N)

---

**[CRIT-001]** `src/auth.py:45` — SQL Injection  
**Confidence**: 97 | **Dimension**: Security

**Problem**: User input is directly concatenated into a SQL query without sanitization or parameterization. An attacker can manipulate the query to read, modify, or delete arbitrary data.

```python
# ❌ Vulnerable
query = "SELECT * FROM users WHERE name = '" + username + "'"
cursor.execute(query)
```

**Fix**:
```python
# ✅ Safe — use parameterized query
cursor.execute("SELECT * FROM users WHERE name = %s", (username,))
```

**Reference**: OWASP A03:2021 Injection, CWE-89

---

#### 🟠 High (N)

---

**[HIGH-001]** `src/processor.py:88-140` — O(n²) Nested Loop  
**Confidence**: 88 | **Dimension**: Performance

**Problem**: For each item in `orders` (n), you iterate over all `products` (m). For realistic data sizes (10k orders × 5k products = 50M iterations), this will cause severe latency spikes.

```python
# ❌ O(n × m)
for order in orders:
    for product in all_products:
        if order.product_id == product.id:
            ...
```

**Fix**:
```python
# ✅ O(n + m) — index products first
product_map = {p.id: p for p in all_products}
for order in orders:
    product = product_map.get(order.product_id)
    ...
```

---

#### 🟡 Medium (N)

*(same format as above)*

#### 🔵 Low (N)

*(same format as above)*

#### 🔎 Needs Verification (N)

Candidates grounded in real code but blocked on one decisive fact. Formal output — **no severity, no score deduction, no impact on the verdict**. Each entry must carry the exact missing fact and a verification plan.

---

**[NEEDS-001]** `src/queue.py:120` — Possible race condition in job claim  
**Blocker**: concurrency model unconfirmed — a single-worker deployment would make the interleaving impossible  
**Verification Plan**: confirm worker concurrency in the deployment config; if multi-worker, add a deterministic interleaving test against the claim path

---

#### 🗄️ Rejected (archived) (N)

Candidates disproven during this review, archived with the falsification reason so the same issue is not re-reported in later rounds. Not defects — do not act on these.

---

**[REJ-001]** `src/api.py:33` — "Missing auth check"  
**Reason**: auth is enforced by router-level middleware (`src/middleware.py:12`), which covers this route

---

### Recommendations

1. **Immediate** (before any merge): Fix all 🔴 Critical issues
2. **This sprint**: Address 🟠 High issues
3. **Backlog**: 🟡 Medium and 🔵 Low items

---

### Verdict

- [ ] ✅ **Approved** — No blocking issues found
- [x] ⚠️ **Changes Requested** — Fix Critical / High before merge
- [ ] ❌ **Rejected** — Major rework required

---

### Coverage

- **Reviewed**: `<files / modules>` — sampling strategy: `<how reviewed paths were chosen>`
- **Not covered**: `<paths>` — reason: `<why excluded>`
- **Explicit negatives**: checked `<X>` — no findings
```

---

## Score Calculation

```
Base score: 100
Deductions:
  Critical issues: -15 each
  High issues:     -8 each
  Medium issues:   -3 each
  Low issues:      -1 each

Floor: 0 (cannot go negative)
```

## Verdict Criteria

| Verdict | Condition |
|---------|-----------|
| ✅ Approved | Score ≥ 85, no Critical or High issues |
| ⚠️ Changes Requested | Score 60–84, or any Critical/High issues present |
| ❌ Rejected | Score < 60, or systemic security vulnerabilities |

## Issue ID Convention

| Prefix | Severity |
|--------|----------|
| `CRIT-` | Critical |
| `HIGH-` | High |
| `MED-` | Medium |
| `LOW-` | Low |
| `INFO-` | Info |
| `NEEDS-` | Needs Verification (no severity) |
| `REJ-` | Rejected, archived (no severity) |

Sequential numbering: `CRIT-001`, `CRIT-002`, `HIGH-001`, etc.

---

## Output Format (Concise)

Use this format for quick checks or CI integration — Critical and High issues only:

```markdown
## 🔍 Code Review Report (Concise)

**Scope**: `<files or PR description>`  
**Score**: N / 100 | **Verdict**: ⚠️ Changes Requested

---

### Blocking Issues (2)

| ID | Location | Issue | Confidence |
|---|---|---|---|
| CRIT-001 | src/auth.py:45 | SQL Injection | 97 |
| HIGH-001 | src/processor.py:88 | O(n²) Nested Loop | 88 |

---

**Fix Critical/High issues before merge.**
```

---

## Related

- [review-workflow.md](../review-workflow.md)
- [commands/security.md](../commands/security.md)
