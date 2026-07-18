# Quality Review Command

Quality Review Mode — code smells, complexity, maintainability, test coverage

## Usage

```bash
review quality [target-path]
```

## Complexity Thresholds

| Metric                     | Target          | Review    | Refactor   |
| -------------------------- | --------------- | --------- | ---------- |
| Cyclomatic Complexity      | ≤ 7             | 8–10      | > 10       |
| Cognitive Complexity       | ≤ 10            | 11–15     | > 15       |
| Method/Function Length     | ≤ 30 lines      | 31–50     | > 50       |
| Class/Module Length         | ≤ 200 lines     | 200–300   | > 300      |
| Parameter Count            | ≤ 3             | 4         | > 4        |
| Nesting Depth              | ≤ 3             | 4         | > 4        |
| Duplication                | < 3 occurrences | —         | ≥ 3        |

---

## Checklist

### Code Smells (High Priority)

```
□ Long Method — method > 50 lines, or does multiple things
□ Large Class — class > 300 lines, or has multiple unrelated responsibilities
□ Long Parameter List — function > 4 parameters (consider parameter object)
□ Duplicated Code — same logic appears ≥ 2 times
□ Deep Nesting — if/for/while nesting > 3 levels (use guard clauses)
□ Feature Envy — method uses more data from another class
□ Dead Code — unreachable code, unused variables, unused imports
□ Magic Numbers/Strings — unexplained literals (use named constants)
□ Switch/If-Else Chains — repeated type checks (consider polymorphism)
□ Premature Generalization — abstract base class with only one concrete subclass
```

### SOLID Principles

```
□ SRP: each class/function has only one reason to change
□ OCP: extend behavior by adding code, not modifying existing
□ LSP: subclasses can substitute parent class without breaking behavior
□ ISP: interfaces are small and focused; no methods the client doesn't need
□ DIP: high-level modules depend on abstractions, not concrete implementations
```

### Error Handling

```
□ Exceptions are specific (catch ValueError, not Exception)
□ Errors are not silently swallowed (at least log them)
□ Resource cleanup (try/finally or context manager/using/defer)
□ Error messages aid debugging (contain context, not just "error occurred")
□ Return types indicate possible failure (Result<T>, Optional<T>, error return)
```

### Error Propagation

```
□ Async errors caught (try/catch around await, promise .catch())
□ Promises not silently swallowed (always await or return)
□ Error context preserved when re-throwing (wrap original error)
□ Error boundaries correctly configured (React, exception handler)
□ Retry logic has limits (max attempts, exponential backoff)
□ Timeout errors handled explicitly
□ Network errors distinguished from application errors
```

### State Consistency

```
□ Multi-step modifications are transactional
□ Partial failures can be rolled back
□ Retry idempotency guaranteed
□ Concurrent update conflict handling (optimistic/pessimistic locking)
□ Eventual consistency compensated when needed
□ State transition validation (state machine pattern)
□ Orphaned state cleanup (background tasks, dead letters)
```

### Naming

```
□ Variables describe their content (userCount not uc or n)
□ Functions/methods describe behavior as verb phrases (getUserById, not getUser)
□ Boolean variables/functions use is/has/can prefix (isActive, hasPermission)
□ No single-letter variables outside explicit context (loop indices i, coordinates x/y excepted)
□ Consistent naming convention within file/module (camelCase vs snake_case)
□ No misleading names (doNothing function that actually does something)
```

### Testing

```
□ Core business logic has unit tests
□ Tests describe behavior, not implementation (test what, not how)
□ Tests are independent (no shared mutable state between tests)
□ Test names are descriptive (test_user_registration_rejects_duplicate_email)
□ Boundary conditions covered (empty input, null/None, max values, error paths)
□ External dependencies mocked (DB, HTTP, filesystem)
□ New code coverage ≥ 80%
```

### Documentation

```
□ Public APIs (functions, classes, modules) have docstrings / JSDoc
□ Complex algorithms have inline comments explaining why (not what)
□ TODOs have context: who, why, optional ticket reference
□ README covers: installation, usage, how to run tests
```

---

## Language-Specific Checks

### Python

- Function signatures have type annotations (PEP 484)
- f-strings preferred over `.format()` or `%` formatting
- Modules with public APIs define `__all__`
- Structured data uses dataclass or attrs, not plain dicts

### TypeScript / JavaScript

- Strict TypeScript configuration (`strict: true`)
- No `any` type without explicit justification
- `const` preferred over `let` preferred over `var`
- Optional chaining `?.` and nullish coalescing `??` over verbose null checks

### Java

- `Optional<T>` instead of returning null
- Records for pure data classes (Java 14+)
- Stream preferred for collection transformations
- `var` for obvious types (Java 10+)

### Go

- Error handling: always check errors, don't use `_`
- Named return values used intentionally, not as defaults
- Interfaces defined in the consuming package (dependency inversion)
- `context.Context` as first parameter for cancellable operations

---

## References

- [code-smells.md](../quality/code-smells.md) — full code smell catalog
- [quality-standards.md](../quality/quality-standards.md) — naming and formatting standards
- [design-pattern-review.md](../architecture/design-pattern-review.md) — GoF patterns + selection guide + code-smell→pattern reverse lookup
- [security-checklist.md](../quality/security-checklist.md) — security quality checklist

## Related Commands

- [security.md](security.md)
- [performance.md](performance.md)
- [architecture.md](architecture.md)
- [simplification.md](simplification.md)
