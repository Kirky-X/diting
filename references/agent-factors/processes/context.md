# F3 — Own Your Context Window (detect, medium)

**Principle**: Don't default to the standard message-based format. Build the context
format that is most efficient for tokens and attention — even if that means packing
all history into a single user message.

## Detect (grep the target)

Good signal — custom serialization:
- `event_to_prompt` / `thread_to_prompt` / `to_prompt`
- `class Thread` / `class Event` with custom schema
- custom tags (`<slack_message>`, `<..._result>`)
- `stringifyToYaml` / custom packing

Weak/absent signal — likely raw standard messages:
- only `"role": "system"` / `"role": "user"` / `"role": "assistant"` dicts
- `"role": "tool"` + `tool_call_id` raw passthrough, no compaction

## Anti-pattern
Passing the raw OpenAI-style `messages` array (`role`/`tool_calls`/`tool_call_id`)
straight to the LLM with no compaction or custom format.

## Ref
`../content/factor-03-own-your-context-window.md` §"Standard vs Custom Context Formats"

## Finding level
MID — absence is weak evidence (a project may legitimately start simple).
Never HIGH on F3 alone. Note `"role": "tool"` raw passthrough as a MID hint, not proof.
