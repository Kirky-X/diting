# Review Anti-Patterns

Avoid these common review pitfalls — they waste time and damage team trust

---

## Eight Major Anti-Patterns

### 1. 🛑 Rubber-Stamp Review

**Description**: Approving without reading the code

**Symptoms**:
- Approving all PRs regardless of content
- Commenting "LGTM" without checking
- Assuming someone else will review

**Consequences**:
- False confidence, letting bugs slip through
- Review process becomes meaningless
- Diffusion of responsibility

**Alternative**: Read every line, or explicitly state the review scope and limitations

---

### 2. 🚲 Bike-Shedding

**Description**: Arguing over trivial details while ignoring important issues

**Symptoms**:
- Spending 30 minutes debating variable names
- Endless formatting discussions
- Ignoring race conditions or security issues

**Consequences**:
- Critical issues get overlooked
- PR cycle time extends
- Reviewer fatigue

**Alternative**: Prioritize: security > correctness > performance > style

---

### 3. 🎨 Blocking on Style

**Description**: Rejecting approval over formatting issues that linter/formatter should handle

**Symptoms**:
- "This indentation is wrong" blocking merge
- Requiring manual fixes for issues linter can auto-fix
- Treating personal preferences as team standards

**Consequences**:
- Wasted effort
- Reduced review efficiency
- Discourages contributors

**Alternative**: Configure automation tools, only review logic

---

### 4. 🚧 Gatekeeping Review

**Description**: Requiring personal preferences rather than accepting correct but different approaches

**Symptoms**:
- "I would implement it differently"
- Refusing approval until rewritten your way
- Over-engineering requirements

**Consequences**:
- Damaged trust
- Contributors lose ownership
- Knowledge sharing hindered

**Alternative**: Accept multiple correct approaches unless there is a clear standards violation

---

### 5. 🚗 Drive-By Review

**Description**: Leaving vague comments and disappearing

**Symptoms**:
- "This doesn't look right"
- Not following up on discussion
- Contributor cannot get clarification

**Consequences**:
- No closure
- Contributor confusion
- PR blocked

**Alternative**: Follow up until resolved, or explicitly hand off to another reviewer

---

### 6. 📈 Scope Creep Review

**Description**: Requesting refactoring unrelated to the current PR

**Symptoms**:
- "While you're at it, refactor this module too"
- "Since you're here, also fix..."
- Requesting improvements beyond PR scope

**Consequences**:
- PR never ends
- Change set inflates
- Regression risk increases

**Alternative**: File as follow-up PR or Issue, do not block current PR

---

### 7. 🕰️ Stale Review

**Description**: Letting PRs sit unreviewed for days

**Symptoms**:
- PR waiting over 24 hours
- Reviewer assigned but unresponsive
- Frequent reminders needed

**Consequences**:
- Delivery blocked
- Context-switching cost
- Team friction

**Alternative**: Review within 24 hours, or explicitly hand off to others

---

### 8. 💬 Emotional Language

**Description**: Using aggressive or dismissive language

**Symptoms**:
- "This is terrible"
- "Obviously wrong"
- "How could you write this code"

**Consequences**:
- Team relationships deteriorate
- Psychological safety decreases
- People become afraid to submit code

**Alternative**: Comment on code, not the person; assume good intent

---

## Quick Reference Table

| Anti-Pattern | One-Liner | Blocking? | Alternative |
|--------|-----------|--------|----------|
| Rubber-Stamp | Approve without reading | — | Read every line or state scope |
| Bike-Shedding | Argue details, miss critical | — | Prioritize by importance |
| Blocking on Style | Formatting blocks merge | ✅ | Automate with linter |
| Gatekeeping | Require personal preference | ✅ | Accept multiple correct approaches |
| Drive-By | Comment then disappear | ✅ | Follow up or hand off |
| Scope Creep | Request unrelated refactoring | ✅ | Create follow-up Issue |
| Stale Review | Over 24 hours | ✅ | Set SLA or hand off |
| Emotional Language | Aggressive language | — | Comment on code not person |

---

## Pre-Submission Self-Check

```
□ Did I read every line of changes?
□ Are my comments prioritized by importance?
□ For formatting issues, did I suggest using linter instead of manual fixes?
□ Did I accept correct but different approaches?
□ Will I follow up until resolved?
□ Are my requests within PR scope?
□ Will I respond within 24 hours?
□ Is my language objective and professional?
```

---

## References

- [templates/feedback-examples.md](templates/feedback-examples.md) — Feedback examples
- [workflow/three-pass-review.md](workflow/three-pass-review.md) — Three-pass review workflow
