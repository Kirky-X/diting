# Feedback Examples

Examples of good and bad feedback to help reviewers provide valuable comments

---

## Feedback Principles

1. **Be specific** — point to the exact line, explain the issue
2. **Explain the why** — describe the risk or consequence, not just the rule
3. **Suggest a fix** — provide a concrete alternative or code snippet
4. **Ask, don't command** — use questions for subjective matters
5. **Acknowledge good work** — praise well-done solutions
6. **Distinguish blocking level** — use severity labels

---

## Security Examples

### Bad Feedback

> This isn't secure. Fix it.

### Good Feedback

> `[CRITICAL]` `src/auth.py:45` — SQL Injection Vulnerability
>
> **Problem**: User input is directly concatenated into a SQL query string. An attacker can manipulate the query to read, modify, or delete arbitrary data.
>
> ```python
> # Vulnerable
> query = "SELECT * FROM users WHERE name = '" + username + "'"
> cursor.execute(query)
> ```
>
> **Fix**:
> ```python
> # Safe — use parameterized query
> cursor.execute("SELECT * FROM users WHERE name = %s", (username,))
> ```
>
> **Reference**: OWASP A03:2021 Injection, CWE-89

---

## Performance Examples

### Bad Feedback

> This is slow.

### Good Feedback

> `[MAJOR]` `src/processor.py:88-140` — O(n²) Nested Loop
>
> **Problem**: For each element in `orders` (n), you iterate over all `products` (m). At realistic data volumes (10k orders × 5k products = 50M iterations), this will cause severe latency.
>
> ```python
> # O(n × m)
> for order in orders:
>     for product in all_products:
>         if order.product_id == product.id:
>             ...
> ```
>
> **Fix**:
> ```python
> # O(n + m) — index products first
> product_map = {p.id: p for p in all_products}
> for order in orders:
>     product = product_map.get(order.product_id)
>     ...
> ```

---

## Correctness Examples

### Bad Feedback

> This might have a bug.

### Good Feedback

> `[MAJOR]` `src/batch.py:52` — Potential Race Condition
>
> **Problem**: The check-then-act pattern is not atomic. Between the check and the act, another process may have modified the state.
>
> ```python
> # Non-atomic operation
> if not file.exists():
>     file.write(data)  # may have been created by another process
> ```
>
> **Fix**:
> ```python
> # Use atomic operation
> try:
>     with open(path, 'xb') as f:  # exclusive creation
>         f.write(data)
> except FileExistsError:
>     handle_conflict()
> ```

---

## Quality Examples

### Bad Feedback

> Why didn't you add tests?

### Good Feedback

> `[MINOR]` `src/discount.py:15-30` — `calculateDiscount()` has multiple branch paths
>
> Could you add boundary tests for zero quantity and negative price to guard against regressions?
>
> ```python
> def test_calculate_discount_zero_quantity():
>     assert calculateDiscount(0, 100) == 0
>
> def test_calculate_discount_negative_price():
>     with pytest.raises(ValueError):
>         calculateDiscount(5, -10)
> ```

---

## Architecture Examples

### Bad Feedback

> I would have done it differently.

### Good Feedback

> `[NIT]` This implementation is correct.
>
> An alternative would be to extract the retry logic into a shared `withRetry()` wrapper — but this is optional, could be a future optimization.

---

## Accessibility Examples

### Bad Feedback

> Fix the accessibility.

### Good Feedback

> `[MAJOR]` `src/components/Modal.tsx:23` — Missing Focus Management
>
> **Problem**: Focus is not moved into the modal when opened or restored when closed. Keyboard users may get trapped outside or inside the modal.
>
> **Fix**:
> ```tsx
> // Move focus in on open
> useEffect(() => {
>   if (isOpen) {
>     firstFocusableRef.current?.focus();
>   }
> }, [isOpen]);
>
> // Restore focus on close
> const handleClose = () => {
>   triggerElementRef.current?.focus();
>   onClose();
> };
> ```

---

## Severity Labels Quick Reference

| Label | Meaning | Blocks Merge? |
|-------|---------|---------------|
| `[CRITICAL]` | Security vulnerability, data loss, production crash | Yes |
| `[MAJOR]` | Bug, logic error, severe performance issue | Yes |
| `[MINOR]` | Improvement suggestion, reduced maintenance cost | No |
| `[NIT]` | Style preference, naming suggestion, minor cleanup | No |

---

## Anti-Patterns to Avoid

| Anti-Pattern | Example | Better Approach |
|--------------|---------|-----------------|
| Vague | "This is wrong" | Explain the specific issue and consequence |
| No proposal | "Fix it" | Provide a suggested fix or code |
| Subjective command | "Don't do it this way" | "What do you think about...?" |
| Emotional | "This is terrible" | Critique the code, not the person |
| Over-generalization | "Add tests" | Specify which scenarios need testing |

---

## References

- [report.md](report.md) — Report template
- [../anti-patterns.md](../anti-patterns.md) — Review anti-patterns
