Every intentional simplification shortcut is marked with a `lazy:` annotation, naming its upper bound and escalation path. This collects them into a ledger so that deferrals don't quietly become permanent.

## Scan

Grep the repo for annotation markers, skipping `node_modules`, `.git`, and build output:

`grep -rnE '(#|//) ?lazy:' .`  (add your own prefixes if your stack uses different comment styles)

Each hit is a ledger line. The comment prefix keeps prose that merely mentions the convention out of the ledger.

## Output

One line per marker, grouped by file:

`<file>:<line>, <what was simplified>. Upper bound: <named limit>. Escalation: <trigger for re-evaluation>.`

The convention is `lazy: <upper bound>, <escalation path>`, so extract the bound and trigger straight from the annotation. Want an owner on each line? Add `git blame -L<line>,<line>`.

Flag rot risk: any `lazy:` annotation without a named escalation path or trigger gets a `no-trigger` tag — these are the ones that quietly rot.

End with `<N> markers, <M> without triggers.` None found: `No lazy: debt. Ledger is clean.`

## Boundaries

Read and report only; do not change anything. To persist it, ask and write the ledger to a file (e.g. `SIMPLIFY-DEBT.md`). One-shot. "stop simplify-debt" or "normal mode" resumes.
