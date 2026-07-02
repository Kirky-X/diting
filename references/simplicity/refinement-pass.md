# Refinement Pass

Proactive clarity pass for code Claude just wrote or modified in this session.
Distinct from the other two Simplicity Lens modes: the Ladder decides how much
code to write *before* writing it (minimal-first); Over-engineering Review/Audit
*lists* what to cut without touching code. This mode *edits* already-written
code for clarity and consistency — and explicitly guards against the Ladder's
own failure mode of over-compressing at the cost of readability.

## When to run

Run silently, without being asked, immediately after finishing any write/add/
refactor/fix task — on the code just touched, not the whole file or repo
unless asked. Also run on explicit request: "clean this up", "make this more
readable/consistent", "refine this code", "polish this".

Do not run standalone on an unmodified file the user hasn't touched this
session unless they explicitly ask — that is Over-engineering Audit's job
(report-only) or a full Dimensional Review, not this pass.

## Rules

1. **Preserve behavior exactly.** Only change *how* the code works, never
   *what* it does — same inputs, same outputs, same side effects, same edge
   cases. If a "simplification" would change behavior, it is a bug fix, not a
   refinement — call it out separately instead of folding it in silently.
2. **Follow project standards first.** Read `CLAUDE.md` / linter config /
   existing sibling files for naming, module, and error-handling conventions
   before applying generic style preferences. A project-specific convention
   always wins over a generic one below.
3. **Reduce accidental complexity**: unnecessary nesting, redundant
   abstractions, unclear names, obvious comments that restate the code,
   duplicated logic that could be one place.
4. **Clarity outranks brevity.** Fewer lines is not the goal — an explicit
   if/else chain beats a nested ternary; a named intermediate variable beats a
   dense one-liner nobody can read at 2am. If a shorter version is harder to
   follow, keep the longer, clearer one.
5. **Do not over-simplify.** Never collapse genuinely separate concerns into
   one function/component to save lines, never remove an abstraction that
   earns its keep (more than one caller, or one caller today with a second
   one clearly coming from the task itself — not speculative), never make
   code harder to step through in a debugger for the sake of density.

## Output

If nothing needs refining, say nothing — do not report "no issues found" as
its own message when this runs proactively. If something is refined, note
only the changes that affect understanding (e.g. "renamed `x` to
`retryCount` for clarity" or "flattened nested if into a guard clause") in one
or two lines, not a walkthrough. When run on explicit request with real
findings, a short before/after diff is enough — this is not a scored report
like the other engines and gets no severity/confidence numbers.

## Boundaries

Scope: clarity, consistency, and maintainability of code that exists or was
just written. Not a substitute for the other Simplicity Lens modes (deletion
candidates, dependency count) or Dimensional Review (bugs, security,
performance) — route those requests to the matching mode instead of trying to
cover them here.
