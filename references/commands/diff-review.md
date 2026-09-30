# Diff Review

PR diff-specific review.

## Checklist

### Change Scope
- Is the change too large — bands from [workflow/three-pass-review.md](../workflow/three-pass-review.md): <100 lines good · 100–400 reviewable · 400–1000 large, propose a split · >1000 recommend splitting before any review can be meaningful
- Can it be split — propose the concrete split (stacked changes, shared foundation first, refactor separated from feature), not just "too big"
- Related files modified together
- Small diff, big file — a few added lines that push an already-large file further still count against size; judge the resulting structure, not the diff size
- Mixed intent — refactoring plus new behavior in one change: flag it and recommend landing as two changes

### Code Quality
- Follows project conventions
- Test coverage
- Comment completeness

### Security
- No sensitive information leakage
- Dependency security
- Input validation

### Performance
- No obvious performance issues
- Resource cleanup

### Maintainability
- Code readability
- Clear naming
- No duplicate code
