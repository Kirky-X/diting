# Quality Command

Quality review mode — code smells, complexity, maintainability, test coverage

## Usage

```bash
review quality [target-path]
```

## Complexity Thresholds

| Metric                   | Target          | Review  | Refactor |
| ------------------------ | --------------- | ------- | -------- |
| Cyclomatic Complexity    | ≤ 7             | 8–10    | > 10     |
| Cognitive Complexity     | ≤ 10            | 11–15   | > 15     |
| Method / Function Length | ≤ 30 lines      | 31–50   | > 50     |
| Class / Module Length    | ≤ 200 lines     | 200–300 | > 300    |
| Parameter Count          | ≤ 3             | 4       | > 4      |
| Nesting Depth            | ≤ 3             | 4       | > 4      |
| Duplication              | < 3 occurrences | —       | ≥ 3      |

---

## What to Check

### Code Smells (High Priority)

```
□ Long Method — method > 50 lines, or does more than one thing
□ Large Class — class > 300 lines, or has multiple unrelated responsibilities
□ Long Parameter List — function takes > 4 params (consider parameter object)
□ Duplicated Code — same logic appears in ≥ 2 places
□ Deep Nesting — if/for/while nested > 3 levels (use guard clauses)
□ Feature Envy — method uses another class's data more than its own
□ Dead Code — unreachable code, unused variables, unused imports
□ Magic Numbers/Strings — unexplained literals (use named constants)
□ Switch/If-Else Chains — repeated type checks (consider polymorphism)
□ Premature Generalization — abstract base classes with one concrete subclass
```

### SOLID Principles

```
□ SRP: each class/function has one reason to change
□ OCP: extend behavior by adding code, not modifying existing
□ LSP: subclass can replace parent without breaking behavior
□ ISP: interfaces are small and focused; no method no client needs
□ DIP: high-level modules depend on abstractions, not concretions
```

### Error Handling

```
□ Exceptions are specific (catch ValueError, not Exception)
□ Errors are not silently swallowed (at minimum logged)
□ Resources cleaned up (try/finally or context managers/using/defer)
□ Error messages useful for debugging (include context, not just "error occurred")
□ Return types indicate failure possibility (Result<T>, Optional<T>, error return)
```

### Error Propagation

```
□ Async errors are caught (try/catch around await, .catch() on promises)
□ Promises are not silently swallowed (always await or return)
□ Error context preserved when re-throwing (wrap original error)
□ Error boundaries correctly set (React, exception handlers)
□ Retry logic has limits (max attempts, exponential backoff)
□ Timeout errors handled explicitly
□ Network errors distinguished from application errors
```

### State Consistency

```
□ Multi-step mutations are transactional
□ Partial failures can be rolled back
□ Idempotency guaranteed for retries
□ Concurrent update conflicts handled (optimistic/pessimistic locking)
□ Eventual consistency compensated when needed
□ State transitions validated (state machine patterns)
□ Orphaned state cleaned up (background jobs, dead letters)
```

### Naming

```
□ Variables: describe what they hold (userCount not uc or n)
□ Functions/methods: verb phrase describing what they do (getUserById, not getUser)
□ Boolean variables/functions: is/has/can prefix (isActive, hasPermission)
□ No single-letter variables outside of well-understood contexts (loop index i, coords x/y)
□ Consistent naming convention within file/module (camelCase vs snake_case)
□ No misleading names (doNothing function that actually does something)
```

### Testing

```
□ Core business logic has unit tests
□ Tests describe behavior, not implementation (test what not how)
□ Tests are independent (no shared mutable state between tests)
□ Test names are descriptive (test_user_registration_rejects_duplicate_email)
□ Edge cases covered (empty input, null/None, max values, error paths)
□ Mocks used for external dependencies (DB, HTTP, filesystem)
□ Coverage ≥ 80% for new code
```

### Documentation

```
□ Public API (functions, classes, modules) has docstrings / JSDoc
□ Complex algorithms have inline comments explaining the why (not the what)
□ TODOs have context: who, why, and optionally a ticket reference
□ README covers: setup, usage, and how to run tests
```

---

## Language-Specific Checks

### Python

- Type hints on function signatures (PEP 484)
- f-strings preferred over `.format()` or `%` formatting
- `__all__` defined in modules with public API
- Dataclasses or attrs instead of plain dicts for structured data

### TypeScript / JavaScript

- Strict TypeScript config (`strict: true`)
- No `any` type without explicit justification
- `const` over `let` over `var`
- Optional chaining `?.` and nullish coalescing `??` over verbose null checks

### Java

- `Optional<T>` instead of returning null
- Records for pure data classes (Java 14+)
- Streams preferred for collection transformations
- `var` for obvious types (Java 10+)

### Go

- Error handling: always check errors, never `_`
- Named return values used intentionally, not by default
- Interfaces defined in consuming package (dependency inversion)
- `context.Context` as first parameter for cancellable operations

---

## References

- [code-smells.md](../quality/code-smells.md) — Full code smell catalog
- [quality-standards.md](../quality/quality-standards.md) — Naming and format standards
- [design-pattern-review.md](../architecture/design-pattern-review.md) — GoF patterns + selection guide + code-smell→pattern reverse lookup
- [security-checklist.md](../quality/security-checklist.md) — Security quality checklist

## Related Commands

- [security.md](security.md)
- [performance.md](performance.md)
- [architecture.md](architecture.md)
- [simplification.md](simplification.md)
