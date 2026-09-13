# F11 — Trigger from Anywhere (reference — no static detection)

**Principle**: Let users trigger the agent from any channel (slack / email / sms)
and respond on the same channel. Agents can also be triggered by non-humans
(cron / event / outage) — the key is they contact humans when needed.

## Why reference only
The original is narrative + diagrams with no code markers. Do NOT emit findings.

## Guidance (when asked)
- multi-channel inbound triggers + same-channel responses
- support outer-loop triggers (cron / event), not just human → agent
- use a fast multi-human loop-in for high-stakes tools

## Ref
`../content/factor-11-trigger-from-anywhere.md` §"11. Trigger from anywhere, meet users where they are"
