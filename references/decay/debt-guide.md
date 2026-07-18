# Tech Debt Assessment Guide — Mode 3

**Purpose:** Identify, classify, and prioritize technical debt across the entire codebase.
Every finding must follow the Iron Law: Symptom → Source → Consequence → Remedy.

---

## Evidence Gathering

If there isn't enough evidence to assess the codebase, ask the user one question —
pick the one most relevant to what you already know:

1. "Which part of the codebase takes the longest to modify for typical features?"
2. "Which module are developers least willing to touch, and why?"
3. "Which parts of the system have the fewest tests but the most bugs?"
4. "Is there a module that only one person fully understands?"

Continue after getting one answer. Do not ask more than one question.
If the user refuses or says they don't know, continue with available evidence and note which areas could not be assessed.

---

## Analysis Flow

Complete the following four steps in order.

### Step 1: Full Decay Risk Scan

Scan the entire codebase for all six decay risks. List all findings before scoring any of them. This avoids anchoring on early findings and missing systemic patterns.

For each risk, look for:

**Cognitive Overload:** Are there widespread naming issues, deeply nested logic, or excessively long functions spanning multiple modules?

**Change Propagation:** Which modules cause the most cascade effects when changed?
Is there a module that everyone must modify when adding new features?

**Knowledge Duplication:** How many times has the same concept been independently implemented?
Is the domain vocabulary consistent across the codebase?

**Accidental Complexity:** Are there architecture layers or abstractions that add no value?
Is the infrastructure overhead proportional to the problem being solved?

**Dependency Disorder:** Are there dependency cycles? Does domain logic depend on infrastructure?
Are there modules with no clear layering position?

**Domain Model Distortion:** Is business logic in the correct layer?
Do code names match business names? Are domain objects anemic?

### Step 2: Score Each Finding with Pain × Spread

After listing all findings, score each one:

**Pain score (1–3):** How much does this slow down current development?
- 3: Developers actively avoid touching this area; it causes bugs in most changes
  *(e.g., "Nobody wants to touch the billing module because it always breaks something")*
- 2: Development in this area is noticeably slower than the rest of the codebase
  *(e.g., "Adding a field here takes 2–3x longer than elsewhere")*
- 1: This is a quality issue but isn't causing actual pain right now
  *(e.g., "Naming is inconsistent, but we always know what it means")*

**Spread score (1–3):** How many files, modules, or developers does this affect?
- 3: Affects 5+ modules or all developers on a team
  *(e.g., "Every new feature touches the God class in core/")*
- 2: Affects 2–4 modules or some team members
  *(e.g., "The auth and notification modules are tightly coupled")*
- 1: Limited to one module or one developer's area
  *(e.g., "A legacy parser only one person maintains")*

**Priority = Pain × Spread** (max 9)

| Priority | Classification | Action |
|----------|---------------|--------|
| 7–9 | Critical Debt | Resolve in the next iteration |
| 4–6 | Planned Debt | Plan within the quarter |
| 1–3 | Monitored Debt | Document and observe |

### Step 3: Classify Debt Intent

After scoring, classify each finding as intentional or accidental:

**Intentional debt** — Deliberate shortcuts taken to meet deadlines, with the expectation of paying them back later. The team knows it exists. It may be legitimate (strategic prototyping, known temporary workarounds during migration).

**Accidental debt** — Degradation that accumulated without deliberate decision: the team didn't choose it and may not even know it exists. This is what Ward Cunningham's original definition warned about — not a tactical trade-off, but structural erosion.

Label each finding in the Debt Summary table with `[intentional]` or `[accidental]`. Intentional debt without a visible repayment plan — no associated ticket, no code comment, no recorded decision — should be treated as accidental debt for prioritization purposes.
Focus remediation effort on accidental debt first; intentional debt at least has an owner.

### Step 4: Group by Decay Risk

Group findings in the report by risk type, not by file or module.
Grouping by risk reveals systemic patterns:
- "Change Propagation is systemic" → architectural intervention needed
- "Cognitive Overload is isolated" → local refactoring suffices

---

## Output

Use the standard report template in `common.md`. Mode: Tech Debt Assessment.

After Findings, append the Debt Summary table:

```
## Debt Summary
| Risk | Findings | Avg Priority | Classification | Intent |
|------|----------|-------------|----------------|--------|
| Cognitive Overload      | N | X.X | Monitored/Scheduled/Critical | intentional/accidental |
| Change Propagation      | N | X.X | ... | ... |
| Knowledge Duplication   | N | X.X | ... | ... |
| Accidental Complexity   | N | X.X | ... | ... |
| Dependency Disorder     | N | X.X | ... | ... |
| Domain Model Distortion | N | X.X | ... | ... |

**Recommended focus:** [risks with highest average priority]
```
