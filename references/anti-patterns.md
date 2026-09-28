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

## Output Quality Anti-Patterns

### 9. 🎈 Severity Inflation

**Description**: Rating issues above what the demonstrated damage supports — treating lint-level findings as High

**Symptoms**:
- Style or hygiene issues labeled Critical/High
- Severity assigned without stating the concrete damage
- Unverified leads carrying final severity ratings

**Consequences**:
- Triage attention diverted from real defects
- Authors dispute ratings instead of fixing issues
- Trust in the severity scale erodes

**Alternative**: Severity follows demonstrated impact — state the concrete damage, or lower the rating

---

### 10. 🛡️ Defense-in-Depth Without Reachable Consequence

**Description**: Reporting hardening advice as findings when no reachable path demonstrates harm

**Symptoms**:
- "Consider adding validation here" as a top finding
- Best-practice suggestions with no demonstrated violation
- Hardening notes counted toward the finding total

**Consequences**:
- Findings list padded with non-defects
- Authors dismiss the entire report
- Real defects buried in noise

**Alternative**: Keep hardening notes separate; findings require a reachable, demonstrated consequence

---

### 11. 🎭 Inventing Findings to Fill the Report

**Description**: Fabricating or stretching findings so the report never comes back empty

**Symptoms**:
- Marginal observations stretched into LOW findings
- Known or previously-reported issues re-reported as new
- Confidence scores pumped up to pass the reporting threshold

**Consequences**:
- False positives erode trust in every finding
- Authors waste effort chasing non-issues
- Signal-to-noise of the report collapses

**Alternative**: Zero findings is a legitimate result — state it with coverage limits instead of inventing findings

---

### 12. 📢 Effect Stronger Than Observed

**Description**: Describing an issue in stronger terms than what was actually observed

**Symptoms**:
- "Could lead to full compromise" when only a parser anomaly was shown
- Hypothetical impact chains written as demonstrated fact
- Reproduction output contradicting the finding's wording

**Consequences**:
- Readers misjudge the actual risk
- Credibility collapses when reproduction shows less
- Effort misallocated to overstated issues

**Alternative**: Report exactly the observed effect; label anything beyond it as unproven hypothesis

---

### 13. 📜 Prose-Only Results

**Description**: Emitting findings as free-form prose that cannot be deduplicated or verified

**Symptoms**:
- Issues described only in narrative paragraphs
- The same issue reported twice in different words
- No structured location or evidence fields to check against

**Consequences**:
- Duplicates accumulate across reviewers and passes
- Claims cannot be verified or reconciled
- Tooling cannot consume or count the results

**Alternative**: Emit structured records — location, evidence, confidence, severity — not narrative prose

---

### 14. 📝 Report Before Verification

**Description**: Writing the report before candidates are verified, or letting prose disagree with the records

**Symptoms**:
- Report drafted while findings are still unverified candidates
- Prose claims counts or severities the records do not support
- Rejected candidates still described as findings

**Consequences**:
- Report asserts results that verification would refute
- Readers cannot tell whether prose or records are true
- Verification forces a rewrite of the finished report

**Alternative**: Verify first, then derive the report from the final verified records

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
| Severity Inflation | Lint-level rated High | ✅ | Severity follows demonstrated damage |
| Defense-in-Depth | Hardening advice as finding | — | Keep hardening notes separate |
| Inventing Findings | Zero-finding report padded | ✅ | Report zero findings as legitimate |
| Effect Stronger Than Observed | Claimed more than observed | ✅ | Report the observed effect only |
| Prose-Only Results | Cannot deduplicate or verify | — | Emit structured records |
| Report Before Verification | Report drafted before checking | ✅ | Verify first, derive report from records |

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
□ If I found nothing, did I report zero findings as a legitimate result instead of inventing findings?
```

---

## References

- [templates/feedback-examples.md](templates/feedback-examples.md) — Feedback examples
- [workflow/three-pass-review.md](workflow/three-pass-review.md) — Three-pass review workflow
