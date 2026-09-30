# Receiving Review Feedback

Guidance for the side that receives a diting report — the author of the reviewed code, human or agent. diting's internal machinery (three-state adjudication, Verification Pass) governs how findings get produced; this file governs how they should be consumed. Load it when responding to a diting report, or hand it to the agent that will.

## Core Principle

A review report is input to a technical decision, not a work order to obey blindly — and not an invitation to perform agreement either. Verify before implementing; ask before assuming.

## 1. Read the Whole Report Before Acting

- Read every finding — including Needs Verification, Rejected, and minor notes — before touching code or replying.
- Never respond finding-by-finding while still reading. Findings may share a root cause or contradict each other; fixing item 1 can invalidate item 4, or make it mandatory.
- If any finding is unclear (claim, location, or requested change), pause the entire response and clarify the unclear items first. Do not implement the subset you understood — partial understanding of an interleaved list is how the wrong half gets fixed.

## 2. Verify Findings Against This Codebase

Applies to every finding you did not help produce. For each substantive finding, check:

- Is the claim technically true **for this codebase** — its framework versions, build targets, deployment assumptions?
- Would the proposed fix break existing behavior, callers, or documented guarantees?
- Why does the current implementation exist? Check history and commit messages before assuming it is accidental.
- Does the claim hold on all supported platforms and versions, not just the one in front of you?
- Does the reviewer hold the full context, or only the diff?

If a check cannot be completed cheaply, say exactly what is missing and ask — do not implement on faith, and do not silently skip.

## 3. YAGNI Check Before "Completing" a Feature

When a finding amounts to "implement this properly" or "extend this" (metrics, config surface, an abstraction), search the codebase for actual callers first:

- No callers → the finding is an argument for deleting the code, not growing it. Propose removal instead.
- Real callers exist → evaluate the extension on its merits.

## 4. Push Back With Grounds

Pushback is expected — not rude — when a finding:

- breaks existing functionality or a documented behavior,
- rests on context the reviewer lacked (deployment shape, callers, prior incidents),
- adds a feature nothing calls (YAGNI, per above),
- contradicts the project's own standards (`CLAUDE.md` / `AGENTS.md` / ADRs), or
- conflicts with a deliberate architectural decision on record.

State the specific ground plus its evidence (file:line, doc path, commit). Objection without evidence is not pushback — it is friction. In PR reviews, diting adjudicates rebuttals against exactly these grounds: see Author Pushback Adjudication in [commands/pr-review.md](../commands/pr-review.md).

## 5. When Pushback Fails, Concede in One Sentence

If the adjudication rules against you: state the corrected fact and implement. No apology tour, no re-litigating why you pushed back originally. A wrong rebuttal checked and dropped is normal review traffic, not an event.

## 6. No Performative Agreement

Accepting a correct finding looks like: "Fixed — [what changed, where]." Starting the work directly also counts. Absolute-agreement openers ("absolutely right!", "great catch!") and gratitude rituals add no information; state the fix — the diff already shows you heard it.

## 7. Implementation Order for Accepted Findings

1. Blocking items first — Critical/High findings that survived adjudication
2. Small mechanical fixes next
3. Larger refactors last

One fix at a time; verify each (test, build, or targeted check) and confirm no regression before starting the next.

## 8. GitHub Inline Replies

Reply to inline review comments inside the original thread (`gh api repos/{owner}/{repo}/pulls/{pr}/comments/{id}/replies`), never as fresh top-level PR comments — each finding's evidence and resolution should stay in one place.

## Related

- [commands/pr-review.md](../commands/pr-review.md) — where author pushback is adjudicated and outcomes are archived into the three-state records
- [report.md](report.md) — the report format this guidance responds to
