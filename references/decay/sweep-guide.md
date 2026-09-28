# Decay Diagnosis — Full Sweep Guide

Sequential autonomous pipeline: **review → test → debt → audit**. Fix findings in place,
iterate until clean or cap is hit, run a coverage critic, report residuals. One interaction point:
Step 0 (pre-flight consent) — once approved, the pipeline runs unattended through Step 9.

Every finding follows the Iron Law: **Symptom → Source → Consequence → Remedy**.

---

### Step 0 — Pre-Flight Consent Gate

**Goal:** Upfront statement of scope, cost, and irreversibility; obtain one-time explicit consent
so subsequent steps don't need to ask again.

0a. If in a git repo, estimate file count with `git ls-files | wc -l`; otherwise
   use `find . -type f -not -path '*/.git/*' -not -path '*/node_modules/*' -not -path '*/.venv/*' -not -path '*/build/*' -not -path '*/dist/*' -not -path '*/vendor/*' -not -path '*/target/*' | wc -l`. Order of magnitude is sufficient.

0b. Display this notification verbatim with the estimate filled in. Do not reword —
   the user is consenting to this exact scope.

   ```
   ⚠️  Full Sweep mode — Full Repository Sweep & Auto-Fix

   Scope:    Four analysis dimensions run in sequence — PR code decay (R1–R6),
             test quality (T1–T6), tech debt, architecture. Edits are made in
             place inside the detected project scope.
   Estimated files in scope: ~N

   Order:    PR-review → test-quality → tech-debt → architecture-audit.
             Each dimension scans, queues, and fixes before the next starts.

   Autonomy: Fully autonomous. Safe single-file fixes apply directly. Multi-file
             fixes that have test coverage AND do not break a public interface
             also apply directly. High-risk fixes (public API break, cross-module
             structural change, or no test coverage) are NOT applied — they are
             recorded in the residual report for human review.

   Iteration: After each dimension pass, modified files + same-module + static
             consumers are re-scanned. A finding that fails to fix 3 times is
             retired to the unresolvable set and never re-queued. Non-critical
             rounds cap at 3 iterations; critical findings iterate until
             resolved or retired.

   Git impact: The pipeline edits files. It does NOT commit, push, or amend.
             If you have uncommitted work you want to preserve, commit or stash
             first.

   Proceed with full autonomous sweep? [Y/n]
   ```

0c. Parse the reply (first-match wins, rules evaluated in order):
   1. **Hard no** (`no`, `n`, `abort`, `cancel`): abort and output "Aborted before scan — no files modified."
   2. **Consent** (`Y`, `yes`, `ok`, `sure`, `proceed`, `go`, `continue`): proceed to Step 1.
   3. **Soft pause** (`wait`, `hold on`, `let me`): one-line acknowledgment ("Understood, waiting"), then wait for the user's next message and re-evaluate from Rule 1.
   4. **Question**: answer the question, then display the notification verbatim again and wait for the next reply. If the next reply is not consent (Rule 2) — whether a second question, another pause, or anything else — abort and output "Aborted — did not receive consent after clarification."

0d. After consent, ask no more questions until Step 9.

---

### Step 1 — Scope Enumeration and State Initialization

1a. If the user hasn't specified files or directories, apply Auto Scope Detection from `common.md`.
   Otherwise respect the user's explicit scope.

1b. If `.decay-review.yaml` exists in the project root, read it. Apply `disable`,
   `severity`, `ignore`, `focus`, and `custom_risks` per common.md. Record the applied config values and reuse them across all iteration rounds — do not re-read in Step 6 even if files are modified.

1c. Initialize pipeline state (persisted across all rounds):

   - **`unresolvable`** (set): findings retired after 3 failed attempts — keyed by `(file, line_range, risk_code)`; `signature` for tiebreaking. Never re-queued.
   - **`non_critical_rounds`** (int, 0): incremented each round that produces Warning/Suggestion findings; reset on a clean round.
   - **`critic_passes`** (int, 0): incremented each time the Step 7 Coverage Critic dispatches the pipeline back to 6a; hard budget of 2 dispatches per sweep — without it, a critic-triggered clean round would reset `non_critical_rounds` and the iteration cap could never be reached again. When the budget blocks a dispatch, Step 7 goes to Step 8 with no coverage verdict — the Step 9 report must state `budget exhausted` in its Coverage critic line; an exhausted budget is never evidence of complete coverage.
   - **`fix_log`** (list): each fix entry contains file, line range, risk code, description, and result (`applied` / `reverted` / `retired`).

1d. Record the final scope file list in the Step 9 Fix Report output buffer.

---

### Step 2 — PR-Review Pass (R1–R6 Code Decay)

Scan every file in scope against all R-series risks defined in `decay-risks.md`.

2a. For each R risk, apply its symptom checklist. Record each hit as a finding,
   including: risk code, file + approximate line range, Symptom, Source,
   Consequence, Remedy, Severity (Critical / Warning / Suggestion), and
   **Fix-Class** (see Step 2b).

2b. Assign a Fix-Class to each finding:

   | Class | Criteria |
   |-------|----------|
   | **Safe** | Single-file and fully local: renaming non-exported symbols, extracting constants, removing dead code, adding null guards at leaves, adding test scaffolds for untested pure functions. Any change that modifies or removes an exported symbol is not Safe even in a single file. |
   | **Extended-Safe** | Multi-file but (a) a project test command exists and passes before the fix, AND (b) changes do not rename, remove, or alter the signature of any publicly exported symbol, AND (c) this round touches ≤ 5 files. |
   | **Residual** | Public API break, cross-service boundary change, no test coverage to roll back to, or ambiguous fix. Do not apply — goes to Step 9 residual report. |

2c. Skip any finding that matches an entry in the `unresolvable` set.

2d. Apply each Safe and Extended-Safe fix in this dimension, lowest risk within
   each severity tier first. For each fix: Edit or Write, then append a line to `fix_log` with result `applied`. If two fixes touch overlapping line ranges in the same file,
   apply the higher-severity one first, re-read the file, then apply the next.

2e. After all fixes in this dimension, run the project's test/lint command if one exists
   (`package.json` scripts, `pytest`, `cargo test`, `go test ./...`, etc.).
   If tests fail: revert fixes from this dimension one at a time in reverse order,
   re-running the test command after each revert until tests pass.
   Mark each reverted fix in `fix_log` with result `reverted` and promote the finding
   to **Residual**. If no test command was found, note it once in the report and continue.

2f. Record dimension summary: N scanned, M Safe applied, K Extended-Safe applied,
   R reverted, P Residual.

---

### Step 3 — Test-Quality Pass (T1–T6 Test Decay)

Scan test files (and untested production code) against T-series risks defined in `test-decay-risks.md`.

Follow the same sub-steps as Step 2 (classify → apply → verify → summarize),
using T-prefix risk codes. For production files with absolutely no test coverage,
record as T5 (Coverage Illusion). Adding test scaffolds for pure functions is
**Safe**; adding tests that require new test infrastructure is **Residual**.

---

### Step 4 — Tech-Debt Pass (Technical Debt Accumulation)

Re-classify R findings through the debt lens — same symptoms at accumulated scale:
repeated duplication, layered workarounds, stale `TODO`/`FIXME` clusters, dead
flags. Score with **Pain (1–3) × Spread (1–3)**; total 7–9 = Critical,
4–6 = Warning, 1–3 = Suggestion. Apply severity elevation for pattern-level
occurrence (isolated Suggestion → 4+ module Warning).

Follow the same sub-steps as Step 2. Debt findings typically span multiple files,
making them more likely to fall into Extended-Safe or Residual than Safe.

---

### Step 5 — Architecture-Audit Pass (Architectural Integrity)

Scan the full scope for architecture-level issues. Dependency direction
symptoms (inverted dependencies, circular imports, cross-domain coupling) are
defined in `decay-risks.md` Risk 5 — use that checklist. Step 5
also covers architectural concerns not addressed by R5: missing
abstraction layers, God modules, infrastructure leaking into domain code,
and seam boundary violations.

Most architecture findings are **Residual** by definition — they require human judgment on
module boundaries. A few are Extended-Safe (e.g., extracting a shared constant used in 3+ modules
into a new module that nothing imports yet).
Do not auto-refactor module layouts, rename packages, or change public exports.

Follow the same sub-steps as Step 2.

---

### Step 6 — Iteration Loop

**Goal:** Re-scan what fixes touched and converge. Stop on a clean round,
hitting the cap, or no progress.

6a. Build the re-scan scope:
   - Every file modified in Steps 2–5 of the current round, plus
   - Every file in the same module as a modified file, plus
   - Every file that statically imports from a modified file.

   Do not re-scan files whose dependencies were untouched. In a monorepo where
   "module" might span hundreds of files, narrow the same-module bucket to files that import from or are imported by modified files (direct dependency graph only).

6b. Re-run Steps 2–5 on the re-scan scope. For each new finding in this round:
   - If it matches an entry in `unresolvable` → skip.
   - Otherwise if it's 🔴 Critical → enqueue and fix; Critical findings iterate until
     resolved or retired (3 failed attempts → `unresolvable`).
   - Otherwise 🟡 Warning / 🟢 Suggestion → enqueue and fix, subject to the cap below.

6c. Classify the round after all fix attempts:
   - **Clean round** (no new findings outside `unresolvable`): pipeline
     converged → proceed to Step 7 (Coverage Critic).
   - **Critical-only round**: do not increment `non_critical_rounds`; return
     to 6a.
   - **Mixed or non-critical round** (produces any Warning / Suggestion):
     increment `non_critical_rounds` by 1. If cap is reached (default 3,
     or `sweep.max_iterations` in `.decay-review.yaml`), proceed to Step 7
     (Coverage Critic), recording remaining non-critical findings as
     `"Unresolved — iteration cap reached"`. Otherwise return to 6a.

6d. Fix retry rule: if a single finding fails validation (Step 2e) across any combination of
   rounds 3 times, retire it to `unresolvable` with reason
   `"3-retry budget exhausted"` and stop attempting.

---

### Step 7 — Coverage Critic

**Goal:** Fresh-eyes coverage check — the critic proposes coverage gaps, not findings.
Dispatched only at Step 6c's two exits — a clean round, or the iteration cap reached
with remaining non-critical findings (critical-only and below-cap mixed rounds return
to 6a without a critic) — and only while the budget lasts: if `critic_passes` already
equals 2, skip the dispatch and proceed to Step 8. Each dispatch is one fresh critic
subagent that took no part in any scan or fix of this sweep. Coverage is complete only
when a critic returns no accepted items; accepted items arriving at the iteration cap
(7c) are disclosed as residuals instead of opening another round.

7a. Brief the critic with the scope file list, dimension summaries, `fix_log`, and the
   `unresolvable` set — never the working notes of earlier rounds. The critic reads
   source code but does not edit or fix anything.

7b. The critic answers exactly two questions:
   - Which entry points, parallel paths, lifecycle patterns, and risk categories were
     not covered by any round?
   - Which units (scope areas, dimensions, rounds) were closed without recorded paths
     and checks?

7c. Route by verdict:
   - **No accepted items** → coverage complete → proceed to Step 8.
   - **Accepted items, cap not reached** (6c exited here from a clean round) →
     increment `critic_passes`, treat each item as additional re-scan scope
     and return to 6a; the next wrap-up dispatches a fresh critic again, while
     the budget lasts (`critic_passes` < 2, checked before dispatch).
   - **Accepted items, cap reached** (6c exited here at the iteration cap) →
     do not open a new round; record each item as a residual collected in
     Step 8 with reason `coverage gap disclosed by critic`. An iteration cap —
     or an exhausted critic budget — is never evidence of complete coverage.

---

### Step 8 — Residual Aggregation

Collect everything not fixed in place, deduplicated:

- All Residual-class findings from Steps 2–5 (first pass + re-scan rounds)
- All `unresolvable` entries with their retirement reasons
- All iteration-cap residuals from Step 6c
- All Coverage Critic items recorded when the cap or the critic budget blocked a covering round (Step 7c)

Sort by Critical → Warning → Suggestion. Within each severity, list file path,
risk code, Symptom (one line), Remedy (one line), and reason not applied
(`public API break` / `no test coverage` / `3-retry budget` /
`iteration cap` / `coverage gap disclosed by critic`).

---

### Step 9 — Sweep Report

Output the final report. Use the standard report template from `common.md`, with these additions:

```
# Decay Diagnosis — Full Sweep Report
Mode: Full Sweep | Scope: <files or directory>
Config: .decay-review.yaml applied (N risks disabled, M paths ignored)   # omit if no config

## Dimension Summary
| Dimension | Scanned | Safe Applied | Extended Applied | Reverted | Residual |
|-----------|---------|--------------|------------------|----------|----------|
| Review (R1–R6) | ... | ... | ... | ... | ... |
| Test (T1–T6)   | ... | ... | ... | ... | ... |
| Debt           | ... | ... | ... | ... | ... |
| Audit          | ... | ... | ... | ... | ... |

## Iteration History
Round 1: <classification — clean / critical-only / mixed>, <N> new findings
Round 2: ...
Stopped at: clean round | iteration cap | no outstanding criticals
Coverage critic: complete (no accepted items) | residuals (accepted items at the iteration cap) | budget exhausted after <N> passes — coverage check truncated, gaps beyond it undisclosed

## Fix Log
| # | File | Lines | Risk | Outcome  | Change |
|---|------|-------|------|----------|--------|
| 1 | ...  | ...   | R2   | applied  | Extract repeated constant |
| 2 | ...  | ...   | T4   | reverted | Test regression; promoted to Residual |
...

## Health Score Delta
Before: <estimated score>/100  →  After: <estimated score>/100
(Re-run Health Dashboard mode for an exact recalculation.)

## Residual Items  (<K> not applied)
<Iron Law entries, sorted Critical → Suggestion, with "Not applied because: ..." line>

## Summary
- Total findings detected: <N>
- Fixed this sweep: <M>
- Residual (needs human review): <K>
- Unresolvable (3-retry exhausted): <U>
```

If there are no residuals and no unresolvable entries, end with:
**"Sweep complete — codebase is clean."**

**Mode line in the report:** `Full Sweep`
