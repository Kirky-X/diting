# F5 — Unify Execution State (detect, weak)

**Principle**: Unify execution state (current step / waiting / retry counts) with
business state (messages, tool results) into a single source — ideally the thread /
context window alone. Extend state by adding event types, not separate fields.

## Detect (grep the target)

Good signal — event-sourced single source:
- `class Thread` with `events: list`
- single serializable thread as the only state
- `save_thread` / `load_state` over the same structure

Weak/absent signal — scattered execution state:
- `retry_count` / `current_step` / `next_step` as independent persisted fields
- step / retry / messages tracked in separate places

## Anti-pattern
Tracking `current_step`, `next_step`, `waiting`, `retry_count` as separate persisted
fields divorced from the message/tool-result thread.

## Ref
`../content/factor-05-unify-execution-state.md` §"5. Unify execution state and business state"

## Finding level
MID only — signal is weak (the factor is architectural, the original has no code
example). Report scattered state fields as a hint, not proof.
