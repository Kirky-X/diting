# F-audit — Aggregate Audit

Default subcommand. Run the detect factors in order, collect findings.

## Scope

Confirm target file/dir with the user. Read agent code; skip tests/configs/docs
unless the user asks for them.

## Run order

1. F1·F4 intent-dispatch — run the shared detection from `tool-calls.md` / `structured-outputs.md` ONCE, emit under `[F01/F04-...]`
2. F2 prompts — `prompts.md`
3. F3 context — `context.md`
4. F5 state — `state.md`
5. F7 contact-humans — `contact-humans.md`
6. F8 control-flow — `control-flow.md`
7. F9 errors — `errors.md`

F6 (pause-resume), F10 (scope), F11 (triggers), F12 (reducer) are reference-only.
Do NOT run them in audit.

## Output

Aggregate all findings, sorted HIGH → MID. Report header: `12-Factor Agents Audit`.
End with a one-line tally: `N findings (H HIGH, M MID) across <target>`.
If zero findings: say so explicitly — do not default to success wording.
