# Refinement Pass

A proactive clarity pass for code Claude just wrote or modified in this session. Unlike the other two simplification perspective modes: the ladder decides how much code to write before writing (minimum first); the over-engineering review/audit lists what to remove but doesn't touch code. This mode edits already-written code to improve clarity and consistency — and explicitly guards against the ladder's own failure mode: over-compressing at the expense of readability.

## When to Run

Run silently after completing any write/add/refactor/fix task, unasked — targeting the code just touched, not the entire file or repo, unless asked. Also run on explicit request: "clean this up", "make this more readable/consistent", "refine this code", "polish".

Do not run on files the user didn't modify in this session unless they explicitly ask — that's the over-engineering audit's job (report only) or a full-dimension review, not this pass.

## Rules

1. **Preserve behavior exactly.** Change how code works, never what it does — same inputs, same outputs, same side effects, same edge cases. If a "simplification" changes behavior, it's a bug fix, not refinement — flag it separately rather than quietly folding it in.
2. **Follow project standards first.** Read `CLAUDE.md` / linter config / existing sibling files to understand naming, module, and error-handling conventions before applying generic style preferences. Project-specific conventions always win over generic ones below.
3. **Reduce incidental complexity**: unnecessary nesting, redundant abstractions, unclear names, comments that restate what the code obviously does, duplicated logic that could be consolidated into one place.
4. **Clarity over brevity.** Fewer lines is not the goal — an explicit if/else chain beats a nested ternary; a named intermediate variable beats a dense one-liner nobody can read at 2 AM. If the shorter version is harder to follow, keep the longer, clearer one.
5. **Don't over-simplify.** Never merge truly separate concerns into one function/component just to save lines, never remove abstractions that earn their existence (more than one caller, or one caller today but the task itself clearly has a second incoming — not speculative), never make code harder to step through in a debugger for density's sake.

## Output

If there's nothing to refine, say nothing — when running proactively, don't report "nothing found" as its own message. If you refined something, log only the changes that affect understanding (e.g. "renamed `x` to `retryCount` for clarity" or "flattened nested if into guard clauses") in one or two lines, not a walkthrough. When running on explicit request with real findings, a short before/after diff is enough — this is not a scorecard report like the other engines, no severity/confidence numbers.

## Boundaries

Scope: clarity, consistency, and maintainability of code that exists or was just written. Does not replace other simplification perspective modes (deletion candidates, dependency count) or dimension reviews (bugs, security, performance) — route those requests to the matching mode rather than trying to cover them here.
