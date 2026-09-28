# Health Dashboard Guide — Mode 5

**Purpose:** Generate a cross-dimensional health dashboard for a codebase.
Every finding must follow the Iron Law: Symptom → Source → Consequence → Remedy.

---

## Analysis Flow

### Step 1: Run Lightweight Scans Across Four Dimensions

For each dimension, run a simplified scan using the decay-risks definitions in `_shared/`.
Do not read the individual mode guide files — use the simplified checklists below. Max 3 findings per dimension;
for Debt: max 2 per risk code, max 3 total across all risk codes.

**PR dimension (if changes exist):**
- Apply Auto Scope Detection (common.md)
- Scan for R2 (Change Propagation) and R1 (Cognitive Overload) in the diff

**Architecture dimension:**
- Gather codebase context: read top-level structure, entry points, import statements
- Draw the Mermaid dependency graph (follow the standard graph rules in common.md)
- Scan for R5 (Dependency Disorder): circular dependencies, upward flow, fan-out > 5
- Include the Mermaid graph in the output

**Debt dimension:**
- Scan all six decay risks (R1–R6) across the codebase
- Skip Pain × Spread scoring (use severity tiers only)

**Test dimension:**
- Build a Test Suite Map (unit/integration/E2E counts)
- Scan for T1 (Test Obscurity) and T2 (Test Brittleness) in test files

### Step 2: Compute the Dashboard Score

Each dimension has its own Health Score (base 100, deduction rules same as common.md).
Composite score = weighted average of dimension scores:

| Dimension | Weight | Rationale |
|-----------|--------|-----------|
| PR (Code Quality) | 0.25 | Only applicable when changes exist; skipped when there's no diff |
| Architecture | 0.30 | Structural issues have the highest blast radius |
| Debt | 0.25 | Systemic but moves slower |
| Test | 0.20 | Supporting signal |

If the PR dimension is skipped (no changes), redistribute its 0.25 weight proportionally to the remaining three dimensions,
dividing each remaining weight by (1 − 0.25) = 0.75. Compute the redistribution dynamically — do not hardcode values.

**Redistributed weights (when PR is skipped):**

| Dimension | Base Weight | Redistributed Weight |
|-----------|------------|---------------------|
| Architecture | 0.30 | 0.30 / 0.75 = 0.40 |
| Debt | 0.25 | 0.25 / 0.75 = 0.33 |
| Test | 0.20 | 0.20 / 0.75 = 0.27 |

**Scoring rules (must be deterministic — two runs on the same codebase must agree):**

- Each dimension's score is computed from the **capped** finding set displayed in the dashboard
  (Step 1's capping limits both what is shown and what is deducted — do not deduct for findings beyond the cap).
- Floor each dimension score to 0 **before** weighting.
- A dimension with no findings scores **100** — never skip. The **only** dimension that may be omitted is PR,
  and only when there is no diff (its weight is then redistributed).
- Round the weighted composite score to the nearest integer (half-up).

### Step 3: Output the Dashboard

Before rendering, run one lightweight coverage critic pass: dispatch a fresh critic
subagent that took no part in the Step 1 scans and ask exactly two questions:
- Which dimension, entry point, or risk category did no scan touch?
- Which area was scored without any scanned path?

Accepted gaps are scanned once under the Step 1 caps and the
score recomputed; no accepted gaps → render as-is. One pass only — no loop.

Use the dashboard report template below instead of the standard common.md template.

---

## Dashboard Report Template

````markdown
# Decay Diagnosis — Health Dashboard

**Mode:** Health Dashboard
**Scope:** [project name or directory]
**Composite Score:** XX/100

| Dimension | Score | Top Finding |
|-----------|-------|------------|
| Code Quality | XX/100 | [one-line summary or "Clean"] |
| Architecture | XX/100 | [one-line summary or "Clean"] |
| Tech Debt | XX/100 | [one-line summary or "Clean"] |
| Test Quality | XX/100 | [one-line summary or "Clean"] |

## Module Dependency Graph
[Mermaid graph from architecture scan]

## Top Findings (max 5 across all dimensions)
[Standard Iron Law format, sorted by severity]

## Recommendation
[One paragraph: what to fix first, which dimension needs the most attention,
 suggest running the full individual skill for the worst dimension]
````
