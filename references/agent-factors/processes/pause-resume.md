# F6 — Launch/Pause/Resume (reference — no static detection)

**Principle**: An agent is a program: launch / query / pause / resume / stop via
simple APIs. External triggers (webhooks) resume from the breakpoint without deep
coupling to an orchestrator — pause between tool selection and tool invocation.

## Why reference only
The original doc is narrative + diagrams with no code markers or API signatures.
There is no reliable static signal to grep. Do NOT emit findings.

## Guidance (when asked)
- prefer simple launch/pause/resume/stop APIs over orchestrator lock-in
- ensure you can pause between choosing a tool and executing it
- a webhook should resume from the breakpoint, not restart from scratch

## Ref
`../content/factor-06-launch-pause-resume.md` §"6. Launch/Pause/Resume with simple APIs"
