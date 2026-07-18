# Simplification Review Command

Simplification Review Mode — improve readability, eliminate redundancy, reduce cognitive load

## Usage

```bash
review simplification [target-path]
```

## Core Principle

**Simplification = reducing cognitive load while preserving behavior.**
Never change what the code does. Only change how it does it.
Always verify tests still pass.

---

## Checklist

### Readability

```
□ Variable names clearly describe their content
□ Function names clearly describe their behavior (verb phrases)
□ No non-universal abbreviations (mgr vs manager)
□ Complex expressions extracted into named variables
□ Magic literals replaced with named constants
□ Boolean expressions free of unnecessary inversions (if !(!a) → if a)
```

### Structure

```
□ Functions do one thing (single responsibility)
□ Nesting depth ≤ 3 (use guard clauses/early returns to flatten)
□ No deeply nested ternaries (extract to if-else or separate functions)
□ Loop logic extracted into named functions (filterActiveUsers vs inline lambda)
□ Related code grouped, unrelated code separated
```

### Duplication

```
□ No copy-pasted code blocks (≥ 3 occurrences → extract function)
□ Similar logic in different locations generalized (parameterize differences)
□ No extractable repeated conditional checks
□ Utility functions not re-implemented (use standard library)
```

### Dead Code

```
□ No unreachable code (after return/throw/break)
□ No unused variables, parameters, imports
□ No commented-out code (use version control)
□ No TODO/FIXME older than 6 months without issue references
□ No permanently enabled/disabled feature flags
```

### Modern Idioms (Language-Specific)

**Python**
```python
# ❌ Verbose
result = []
for item in items:
    if item.active:
        result.append(item.name)

# ✅ Pythonic
result = [item.name for item in items if item.active]

# ❌ Manual None check
if value is not None:
    return value
return default

# ✅ Using walrus / or
return value or default
```

**TypeScript / JavaScript**
```typescript
// ❌ Nested ternary
const label = isAdmin ? 'Admin' : isMod ? 'Moderator' : 'User'

// ✅ Map or function
const ROLE_LABELS = { admin: 'Admin', mod: 'Moderator' }
const label = ROLE_LABELS[role] ?? 'User'

// ❌ Manual array flattening
const flat = arr.reduce((acc, curr) => acc.concat(curr), [])

// ✅ Built-in
const flat = arr.flat()
```

**Java**
```java
// ❌ Imperative collection processing
List<String> names = new ArrayList<>();
for (User user : users) {
    if (user.isActive()) {
        names.add(user.getName());
    }
}

// ✅ Stream
List<String> names = users.stream()
    .filter(User::isActive)
    .map(User::getName)
    .collect(toList());
```

**Go**
```go
// ❌ Error checked but ignored with blank identifier
result, _ := riskyOperation()

// ✅ Always handle errors
result, err := riskyOperation()
if err != nil {
    return fmt.Errorf("riskyOperation failed: %w", err)
}
```

---

## Simplification Techniques

### Guard Clauses (Flatten Nesting)

```python
# ❌ Arrow code
def process(user, order):
    if user:
        if user.active:
            if order:
                if order.valid:
                    do_work(user, order)

# ✅ Guard clauses
def process(user, order):
    if not user: return
    if not user.active: return
    if not order: return
    if not order.valid: return
    do_work(user, order)
```

### Extract Variables

```python
# ❌ Opaque condition
if user.created_at > datetime.now() - timedelta(days=30) and user.plan == 'trial':
    ...

# ✅ Named expressions
is_new_user = user.created_at > datetime.now() - timedelta(days=30)
is_trial = user.plan == 'trial'
if is_new_user and is_trial:
    ...
```

### Replace Conditionals with Polymorphism

```python
# ❌ Type switch
def get_area(shape):
    if shape.type == 'circle': return pi * shape.r ** 2
    if shape.type == 'rect': return shape.w * shape.h

# ✅ Polymorphism
class Circle:
    def area(self): return pi * self.r ** 2

class Rectangle:
    def area(self): return self.w * self.h
```

---

## When Not to Simplify

- Code is performance-critical with benchmarks proving it (don't optimize away)
- Complex algorithms are correct and well-tested (add comments explaining, don't simplify)
- Simplification would break backward compatibility
- Team unfamiliar with resulting idiom (clarity > cleverness)

---

## References

- [simplification-guidelines.md](../simplification/simplification-guidelines.md) — full guide
- [refactoring-patterns.md](../simplification/refactoring-patterns.md) — refactoring catalog

## Related Commands

- [security.md](security.md)
- [performance.md](performance.md)
- [quality.md](quality.md)
- [architecture.md](architecture.md)
