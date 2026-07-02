# Feedback Examples

Good and bad feedback examples to help reviewers provide valuable comments

---

## Feedback Principles

1. **Specific** — Point to exact line numbers, explain the issue
2. **Explain Why** — Describe risks or consequences, not just rules
3. **Suggest Fix** — Provide concrete alternatives or code snippets
4. **Ask Don't Command** — Use questions for subjective matters
5. **Acknowledge Good Work** — Praise good solutions
6. **Distinguish Blocking Level** — Use severity level tags

---

## Security Examples

### Bad Feedback

> This is insecure. Fix it.

### Good Feedback

> `[CRITICAL]` `src/auth.py:45` — SQL Injection Vulnerability
>
> **Issue**: User input is directly concatenated into SQL query string. Attackers can manipulate queries to read, modify, or delete arbitrary data.
>
> ```python
> # Vulnerable
> query = "SELECT * FROM users WHERE name = '" + username + "'"
> cursor.execute(query)
> ```
>
> **Fix**:
> ```python
> # Safe — Use parameterized query
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
> **Issue**: For each element in `orders` (n), iterate all `products` (m). Actual data volume (10k orders × 5k products = 50M iterations) will cause severe delay.
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
> # O(n + m) — Index products first
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
> **Issue**: Check-then-act pattern is not atomic. Between check and act, another process may have already modified state.
>
> ```python
> # Non-atomic operation
> if not file.exists():
>     file.write(data)  # May have been created by another process
> ```
>
> **Fix**:
> ```python
> # Use atomic operation
> try:
>     with open(path, 'xb') as f:  # Exclusive create
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
> Could add edge case tests for zero quantity and negative price to prevent regression?
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

> I would have done this differently.

### Good Feedback

> `[NIT]` This implementation is correct.
>
> Another approach is extracting retry logic into a shared `withRetry()` wrapper — but this is optional and can be a future optimization.

---

## Accessibility Examples

### Bad Feedback

> Fix the accessibility.

### Good Feedback

> `[MAJOR]` `src/components/Modal.tsx:23` — Missing Focus Management
>
> **Issue**: Focus is not moved into modal when opened, and not restored when closed. Keyboard users may be trapped outside or inside the modal.
>
> **Fix**:
> ```tsx
> // Move focus in when opened
> useEffect(() => {
>   if (isOpen) {
>     firstFocusableRef.current?.focus();
>   }
> }, [isOpen]);
>
> // Restore focus when closed
> const handleClose = () => {
>   triggerElementRef.current?.focus();
>   onClose();
> };
> ```

---

## Severity Labels Quick Reference

| Tag | Meaning | Block Merge? |
|------|------|-----------|
| `[CRITICAL]` | Security vulnerability, data loss, production crash | Yes |
| `[MAJOR]` | Bug, logic error, severe performance issue | Yes |
| `[MINOR]` | Improvement suggestion, reduced maintenance cost | No |
| `[NIT]` | Style preference, naming suggestion, minor cleanup | No |

---

## What to Avoid

| Anti-Pattern | Example | Alternative |
|--------|------|----------|
| Vague | "This is wrong" | Explain specific issue and consequences |
| No Solution | "Fix this" | Provide fix suggestion or code |
| Subjective Command | "Don't do this" | "What do you think about...?" |
| Emotional | "This is terrible" | Comment on code, not person |
| Over-Generalized | "Add tests" | Specify scenarios needing tests |

---

## References

- [report.md](report.md) — Report template
- [../anti-patterns.md](../anti-patterns.md) — Review anti-patterns