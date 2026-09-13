# F7 — Contact Humans with Tools (detect, medium)

**Principle**: Don't make the LLM gamble its first token between "return plaintext"
vs "return structured tool". Make it always output JSON, and express "contact human"
/ "done" as intent tools (`request_human_input`, `done_for_now`).

## Detect (grep the target)

Good signal — structured human-contact intent:
- `request_human_input` / `class RequestHumanInput`
- `intent: "request_human_input"`
- `notify_human` / `human_input_requested` / `response_from_human`
- `request_human_approval`

Bad signal — plaintext human interaction:
- relying on a first-token (`|JSON>` vs natural language) to decide human contact
- agent returning free text to signal "I need a human"

## Anti-pattern
Using plaintext output to express "I need to ask a human", forcing a fragile
first-token gamble instead of a dedicated intent tool.

## Ref
`../content/factor-07-contact-humans-with-tools.md` §"7. Contact humans with tool calls"

## Finding level
MID on absence (no `request_human_input`-style intent). HIGH only if a fragile
first-token / plaintext human-contact pattern is clearly present.
