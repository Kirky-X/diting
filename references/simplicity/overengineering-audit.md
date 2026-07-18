Simplification audit, full-repo scope. Scan the entire tree, not just a diff. Rank findings by maximum potential removal.

## Tags

Same tags as diff-scoped review:

- `delete:` Dead code, unused flexibility, speculative features. Replacement: none.
- `stdlib:` Hand-rolled things that already exist in the standard library. Name the function.
- `native:` Dependency or code doing what the platform already does. Name the feature.
- `yagni:` Abstractions with a single implementation, config nobody sets, layers with a single caller.
- `shrink:` Same logic, fewer lines. Show the shorter form.

## What to Hunt

Dependencies already covered by stdlib or platform, interfaces with a single implementation, factories for a single product, wrappers that only delegate, files that export a single thing, dead flags and config, hand-rolled stdlib.

## Output

One line per finding, ranked: `<tag> What to remove. <Replacement>. [path]`.
End with `Net: -<N> lines, -<M> dependencies possible.` Nothing to remove: `Already lean. Ship it.`

## Boundaries

Scope: over-engineering and complexity only. Correctness bugs, security vulnerabilities, and performance are explicitly out of scope. Route them to the normal review process. List findings, do not apply anything. One-shot.
"stop simplify-audit" or "normal mode" resumes.
