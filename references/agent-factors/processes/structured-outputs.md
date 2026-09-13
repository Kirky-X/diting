# F4 — Tools Are Structured Outputs (detect, weak; shares intent detection with F1)

**Principle**: A tool is just structured JSON the LLM emits, parsed by deterministic
code. The LLM decides "what", your code controls "how". Tools are NOT 1:1 fixed
functions that must run identically every call.

## Detect (grep the target)

Good signal — typed intent classes + dispatch:
- `class CreateIssue:` / `class SearchIssues:` with an `intent: "..."` field
- `nextStep.intent ==` dispatch switch / `next_step.intent ==`
- union of tool/intent classes

Bad signal — rigid 1:1 tool binding:
- assumption that "LLM called tool X" → must run function X identically every time

## Anti-pattern
Treating tools as fixed functions the framework auto-executes, rather than as
structured intents your code interprets.

## Ref
`../content/factor-04-tools-are-structured-outputs.md` §"4. Tools are just structured outputs"

## Finding level
Shares intent-dispatch detection with F1. In `audit`, run it ONCE and emit under
`[F01/F04-...]`. As a single-factor call, report MID on absence.
