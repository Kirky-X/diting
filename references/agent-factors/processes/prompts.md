# F2 — Own Your Prompts (detect, strong)

**Principle**: Don't outsource prompt engineering to a framework's black-box
abstraction. Treat prompts as first-class code: write, test, iterate them yourself.

## Detect (grep the target)

Bad signal — framework black-box constructors (HIGH confidence, low false-positive):
- `Agent(role=` / `Agent(goal=` / `Agent(personality=` / `Agent(backstory=`
- `Crew(` / `Task(expected_output=` / `Task(instructions=`
- `agent.run(` as the whole execution

Good signal — prompt as code:
- explicit prompt template functions / `prompt #"` (BAML) / `_.role("system")`
- prompt tests or evals

## Anti-pattern
`agent = Agent(role=..., goal=..., personality=..., tools=...)` then
`result = agent.run(task)` — prompts buried in framework defaults you can't see or test.

## Ref
`../content/factor-02-own-your-prompts.md` §"2. Own your prompts"

## Finding level
HIGH on any `Agent(role=` / `Crew(` / `agent.run(` / `expected_output=` — these are
specific, low-false-positive black-box markers.
