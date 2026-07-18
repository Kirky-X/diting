# Remedy Guide — Executable Fix Mode

When `--fix` is active, enhance each finding's Remedy field to make it directly executable:

## Fix Enhancement Rules

For each finding, the Remedy must contain:
1. **Target**: exact file path and function/class name
2. **Action**: a specific refactoring operation (e.g., "extract lines 45–67 into a new function `calculateShippingCost(items, config)`")
3. **Rationale**: one sentence explaining why this particular fix was chosen (not just "refactor")

## Fixability Classification

After writing the enhanced Remedy, classify each finding:

| Tier | Criteria | Report Label |
|------|----------|-------------|
| Quick Fix | Single-file, mechanical operation: rename, extract constant, reorder imports | `[quick-fix]` |
| Guided Fix | Requires design choices: where to split, what the interface shape should be | `[guided]` |
| Manual Fix | Cross-module, requires domain knowledge or team discussion | `[manual]` |

Append the label to the finding title: `**R1 — Long function in OrderService [quick-fix]**`

## Output Addition

After the standard report, add a **Fix Summary** section:

| Finding | Tier | Target File | Action |
|---------|------|-------------|--------|
| R1 — Long function | quick-fix | src/order.ts:45 | Extract `calculateTotal()` |
| R5 — Circular dep | manual | src/models/ ↔ src/services/ | Introduce interface boundary |

## What Not to Do
- Do not modify any files. Phase 1 is diagnosis + executable plan only.
- Do not generate diffs or code blocks. The Remedy text itself is the deliverable.
- Do not rescore. The Health Score reflects current state, not target state.
