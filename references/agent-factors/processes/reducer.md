# F12 — Make Your Agent a Stateless Reducer (reference — no static detection)

**Principle**: Model the agent as a stateless reducer — `foldl` over events. All
state lives in the thread passed in.

## Why reference only
The original is two sentences + two diagrams, no code, no grep markers.
Do NOT emit findings.

## Guidance (when asked)
- agent = pure function of (thread, event) → thread
- keep the agent itself stateless; state is the event list
- this is the conceptual capstone of F5 (unified state)

## Ref
`../content/factor-12-stateless-reducer.md` §"12. Make your agent a stateless reducer"
