# F1 — Natural Language to Tool Calls (detect, weak)

**Principle**: Convert natural language atomically into a structured tool call
(function + args), then dispatch via deterministic code — never let the LLM drive
side effects straight off free text.

## Detect (grep the target)

Good signal — intent dispatch owned by your code:
- `determineNextStep` / `determine_next_step`
- `nextStep.function` / `nextStep.parameters`
- `nextStep.intent ==` / `if nextStep.intent` switch dispatch
- typed intent classes (`class CreateIssue`, `class SearchIssues`)

Bad signal — LLM drives side effects straight from text:
- LLM output consumed as free text that directly triggers actions
- no structured-output parsing before action

## Anti-pattern
`agent.run("create a payment link for $50")` — free text in, side effects out,
no structured intermediate.

## Ref
`../content/factor-01-natural-language-to-tool-calls.md` §"1. Natural Language to Tool Calls"

## Finding level
- HIGH if no structured dispatch exists at all (free-text → action)
- MID if dispatch exists but is shallow
Shares its intent-dispatch detection with F4 — in `audit`, emit once under `[F01/F04]`.
