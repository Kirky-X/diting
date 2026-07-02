# Review Anti-Patterns

Avoid these common review traps — they waste time and damage team trust

---

## The 8 Anti-Patterns

### 1. 🛑 Rubber-Stamping

**Description**: Approving without reading the code

**Symptoms**:
- Approving all PRs regardless of content
- Commenting "LGTM" without checking
- Assuming someone else will review

**Consequences**:
- False confidence, letting bugs through
- Review process becomes meaningless
- Diffusion of responsibility

**Alternative**: Read every line, or clearly state review scope and limitations

---

### 2. 🚲 Bikeshedding

**Description**: Spending lots of time arguing about trivial details while ignoring important issues

**Symptoms**:
- 30 minutes debating variable names
- Endless formatting discussions
- Ignoring race conditions or security issues

**Consequences**:
- Critical issues overlooked
- PR cycles extended
- Reviewer fatigue

**Alternative**: Prioritize: Security > Correctness > Performance > Style

---

### 3. 🎨 Blocking on Style

**Description**: Refusing to approve for formatting issues that should be handled by linter/formatter

**Symptoms**:
- "This indentation is wrong" blocking merge
- Requiring manual fixes for issues linter can auto-fix
- Treating personal preferences as team standards

**Consequences**:
- Wastes human time
- Reduces review efficiency
- Discourages contributors

**Alternative**: Configure automation tools, review logic only

---

### 4. 🚧 Gatekeeping

**Description**: Demanding personal preferences rather than accepting correct but different solutions

**Symptoms**:
- "I would have implemented it differently"
- Refusing approval until rewritten your way
- Over-engineering requirements

**Consequences**:
- Trust damaged
- Contributors lose ownership
- Knowledge sharing blocked

**Alternative**: Accept multiple correct solutions unless there's a clear standard violation

---

### 5. 🚗 Drive-by Reviews

**Description**: Leaving a vague comment and disappearing

**Symptoms**:
- "This doesn't look right"
- Not following up on discussions
- Contributor cannot get clarification

**Consequences**:
- No closure
- Contributor confused
- PR blocked

**Alternative**: Follow up until resolved, or explicitly hand off to another reviewer

---

### 6. 📈 Scope Creep Reviews

**Description**: Requesting refactoring unrelated to the current PR

**Symptoms**:
- "While you're at it, refactor this module"
- "Since you're here, also fix..."
- Requesting improvements beyond PR scope

**Consequences**:
- PR never ends
- Change set bloats
- Regression risk increases

**Alternative**: Record as follow-up PR or Issue, don't block current one

---

### 7. 🕰️ Stale Reviews

**Description**: Letting PRs sit for days without review

**Symptoms**:
- PR waiting over 24 hours
- Reviewer assigned but unresponsive
- Frequent reminders needed

**Consequences**:
- Blocks delivery
- Context switching cost
- Team friction

**Alternative**: Review within 24 hours, or explicitly hand off to others

---

### 8. 💬 Emotional Language

**Description**: Using aggressive or dismissive language

**Symptoms**:
- "This is terrible"
- "Obviously wrong"
- "How could you write this"

**Consequences**:
- Team relationships deteriorate
- Psychological safety reduced
- People afraid to submit code

**Alternative**: Comment on code, not the person; assume good intent

---

## Quick Reference Table

| Anti-Pattern | One-Liner | Blocking? | Alternative |
|--------|-----------|--------|----------|
| Rubber-Stamping | Approve without reading | — | Read every line or state scope |
| Bikeshedding | Argue details, miss key issues | — | Prioritize by importance |
| Blocking on Style | Format issues block merge | ✅ | Automate with linter |
| Gatekeeping | Demand personal preferences | ✅ | Accept multiple correct solutions |
| Drive-by | Comment and disappear | ✅ | Follow up or hand off |
| Scope Creep | Request unrelated refactoring | ✅ | Create follow-up Issue |
| Stale Reviews | Over 24 hours | ✅ | Set SLA or hand off |
| Emotional Language | Aggressive language | — | Comment on code, not person |

---

## Self-Check Before Submitting Review

```
□ Did I read every changed line?
□ Are my issues prioritized?
□ For format issues, did I suggest linter instead of manual fix?
□ Did I accept correct but different solutions?
□ Will I follow up until resolved?
□ Are my requests within PR scope?
□ Will I respond within 24 hours?
□ Is my language objective and professional?
```

---

## References

- [templates/feedback-examples.md](templates/feedback-examples.md) — Feedback examples
- [workflow/three-pass-review.md](workflow/three-pass-review.md) — Three-pass review workflow
