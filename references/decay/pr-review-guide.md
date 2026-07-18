# PR Review Guide — Mode 1

**Purpose:** Analyze a code diff or specific files, identifying decay risks directly visible in changed code. Every finding must follow the Iron Law: Symptom → Source → Consequence → Remedy.

---

## Before You Start

**Auto-generated files:** If the diff contains generated files (protobuf stubs, OpenAPI clients, ORM migrations, lock files, minified bundles), skip these entirely. Generated code reflects tool choices, not developer decisions. Note in the report which files were skipped and why.

**Scope calibration:** Adjust analysis depth based on PR size before starting.

| PR Size | Approach |
|---------|----------|
| < 50 lines | Focus only on Steps 1–3; run Step 6a only if imports changed; run Step 6b only if any class, method, or variable was renamed or introduced |
| 50–300 lines | Full flow, all steps |
| > 300 lines | Full flow; note in Scope line that the review is sampled — covering highest-risk areas rather than every file |

For PRs > 500 lines: note in Summary that a PR of this size is itself a Change Propagation signal. Changes that can't be reviewed in one pass imply entangled responsibilities.

---

## Analysis Flow

Complete the following seven steps in order. Do not skip steps.

### Step 1: Understand the Scope

Read the diff or files and answer:
- What is the stated purpose of this change?
- Which files were modified?
- If the PR modifies more than 10 unrelated files — flag immediately — this is itself a
  🟡 Warning: Change Propagation (a PR touching many unrelated things is
  a signal of entangled responsibilities).

### Step 2: Scan for Change Propagation

*Scan this first — it's the most visible risk in a diff.*

Look for:
- Does this change touch files in modules that have no conceptual connection to its stated purpose?
- Is any modified class being changed in this diff for multiple business reasons?
- Does any method use data from another class more than from its own class?

If the diff shows no cross-module changes beyond what the feature requires → skip, no finding.

### Step 3: Scan for Cognitive Overload

Look for:
- Are any newly added or modified functions over 20 lines?
- Is there nesting deeper than 3 levels in new or modified code?
- Are there more than 4 parameters in any new function signature?
- Are there magic numbers or unexplained constants in the new code?
- Do new variable or function names require reading the implementation to understand?
- Are there train wreck chains (3+ method call chains)?

### Step 4: Scan for Knowledge Duplication

Look for:
- Does this change introduce logic that already exists in the codebase?
- Does this change introduce a new name for a concept that already has a name?
- Does this change add a class to a hierarchy that has a parallel counterpart in another module?

### Step 5: Scan for Accidental Complexity

Look for:
- Does this change add an abstraction with only a single concrete use?
- Does this change add a class that only wraps another class or delegates everything?
- Does this change add configuration options or extension points that don't serve current needs?

### Step 6a: Scan for Dependency Disorder

- Does any new import create a dependency from a high-level module to a low-level module?
  (e.g., a domain service now importing a database driver or HTTP client)
- Does any new import introduce a cycle between modules?
- Does any new interface force callers to depend on methods they don't use?

If there are no new imports and no structural changes → skip, no finding.

### Step 6b: Scan for Domain Model Distortion

- Do new class or variable names match the language the business uses for the same concept?
- Does any new class hold data with no behavior (pure data bag) when behavior was expected?
- Does any new method place logic in a service or utility layer that belongs in the domain?

---

## Severity Calibration

Apply the Iron Law format from `common.md`. Each risk in `decay-risks.md` has its own Severity
Guide with numeric thresholds — use those as the primary reference. When a finding sits at the boundary between two tiers, use the following as a tiebreaker:
- 🔴 Critical — actively breaking velocity or creating production risk today
- 🟡 Warning — will happen if not addressed in the next few features
- 🟢 Suggestion — worth fixing when nearby, not urgent

When there are multiple findings, list Critical items first. If there are more than 5 findings,
add a "Recommended fix order" line at the end of the Findings section.

---

## Step 7: Quick Test Check

*Run this last. Just three signals — this is not a full Mode 4 review.*

If the diff contains only generated files, config, or docs with no production logic changes → skip Step 7 entirely.

**Signal 1: Is the changed behavior tested?**

- Does the diff modify production code?
- Does the diff include corresponding test file changes?
- If new public behavior was added but no new tests:
  → 🟡 Warning: Coverage Illusion — new behavior untested
  → Source: Feathers — Working Effectively with Legacy Code, Ch. 1
- If the change is a pure refactor and existing tests cover the behavior → no finding.

**Signal 2: Quick Mock Abuse sniff**

Only check if the diff includes test file changes.

- Is mock setup code in new/modified tests clearly longer than the test logic?
- Is the primary assertion `expect(mock).toHaveBeenCalledWith(...)` with no behavioral verification?
- Does the diff add methods to production classes that are only called from test files?

If any of the above is true:
  → 🟡 Warning: Mock Abuse — test complexity exceeds behavioral complexity
  → Source: Osherove — The Art of Unit Testing, mock usage guidelines

**Signal 3: Quick Test Obscurity sniff**

Only check if the diff includes test file changes.

- Do new test names express the scenario and expected outcome?
  (Pattern: `methodName_scenario_expectedResult` or equivalent)
- Do any new tests contain multiple assertions without a message string on any of them?

If test names are vague or assertions lack messages:
  → 🟢 Suggestion: Test Obscurity — test intent unclear from test name or assertions
  → Source: Meszaros — xUnit Test Patterns, Assertion Roulette (p.224)

**Output rules:**

If all three signals are clean → do not write test findings. Proceed directly to the report.

If findings exist → add them to the Findings section using the standard Iron Law format.
Label risks with their test decay risk names (e.g. "Coverage Illusion", "Mock Abuse",
"Test Obscurity").

> **Note:** Step 7 is a quick check, not a full test audit. When systematic test issues are found,
> note in the Summary: "Consider running the `Test Quality Review mode` for a full test quality diagnosis."

---

## Output

Use the standard report template in `common.md`.
Mode: PR Review
Scope: list the files reviewed (excluding skipped generated files).
