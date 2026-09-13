# F8 — Own Your Control Flow (detect, CORE)

**Principle**: Own the agent loop yourself — a `while True` with explicit dispatch —
not a framework. Some tool calls `break` (await human / long task), some `continue`
(re-feed the LLM). Insert summarization, LLM-as-judge, compaction, rate-limiting,
durable sleep as your code.

## Detect (grep the target)

Good signal — hand-owned loop:
- `while True:` with explicit dispatch inside
- `def handle_next_step` / `handle_next_step(`
- `next_step.intent == '...'` / `nextStep.intent ==` branching
- `break` after `save_thread` + human notification
- `continue` after appending tool result
- `request_human_approval` / `send_message_to_human`

Bad signal — framework owns the loop:
- `agent.run(` / compiled graph with no visible loop
- `while` + `sleep` busy-waiting in memory for long tasks (restart on crash)

## Anti-pattern
Handing control flow to a framework's opaque graph; or `while...sleep` busy-wait
that loses everything on process restart.

## Ref
`../content/factor-08-own-your-control-flow.md` §"8. Own your control flow"

## Finding level
HIGH if the only loop driver is a framework black-box (`agent.run(` / compiled graph)
with no hand-owned dispatch — this is the core 12-factor anti-pattern.
MID if a loop exists but lacks break/continue intent handling.
