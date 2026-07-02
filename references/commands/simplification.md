# Simplification Command

Simplification review mode — improve readability, eliminate redundancy, reduce cognitive load

## Usage

```bash
review simplification [target-path]
```

## Core Principle

**Simplification = reduce cognitive load, preserve behavior.**  
Never change what code does. Only change how it does it.  
Always verify tests still pass.

---

## What to Check

### Readability

```
□ Variable names clearly describe what they hold
□ Function names clearly describe what they do (verb phrase)
□ No abbreviations that aren't universally understood (mgr vs manager)
□ Complex expressions extracted to named variables
□ Magic literals replaced with named constants
□ Boolean expressions not inverted unnecessarily (if !(!a) → if a)
```

### Structure

```
□ Functions do one thing (single responsibility)
□ Nesting depth ≤ 3 (use guard clauses / early returns to flatten)
□ No deeply nested ternaries (extract to if-else or separate function)
□ Loop logic extracted to named functions (filterActiveUsers vs inline lambda)
□ Related code grouped together, unrelated code separated
```

### Duplication

```
□ No copy-paste code blocks (≥ 3 duplications → extract function)
□ Similar logic in different places generalized (parameterize the difference)
□ No repeated conditional checks that could be hoisted
□ Utility functions not re-implemented (use standard library)
```

### Dead Code

```
□ No unreachable code (after return/throw/break)
□ No unused variables, parameters, imports
□ No commented-out code (use version control instead)
□ No TODO/FIXME older than 6 months with no issue reference
□ No feature flags that are permanently enabled/disabled
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

// ❌ Manual array flatten
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

// ✅ Streams
List<String> names = users.stream()
    .filter(User::isActive)
    .map(User::getName)
    .collect(toList());
```

**Go**
```go
// ❌ Error checked but ignored via blank identifier
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
# ❌ Arrow-shaped code
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

### Extract Variable

```python
# ❌ Opaque condition
if user.created_at > datetime.now() - timedelta(days=30) and user.plan == 'trial':
    ...

# ✅ Named expression
is_new_user = user.created_at > datetime.now() - timedelta(days=30)
is_trial = user.plan == 'trial'
if is_new_user and is_trial:
    ...
```

### Replace Conditional with Polymorphism

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

## When NOT to Simplify

- Code is performance-critical with proven benchmarks (don't optimize away)
- Complex algorithm is correct and well-tested (add a comment explaining it instead)
- Simplification would break backward compatibility
- The team is unfamiliar with the resulting idiom (clarity > cleverness)

---

## References

- [simplification-guidelines.md](../simplification/simplification-guidelines.md) — Full guideline
- [refactoring-patterns.md](../simplification/refactoring-patterns.md) — Refactoring catalog

## Related Commands

- [security.md](security.md)
- [performance.md](performance.md)
- [quality.md](quality.md)
- [architecture.md](architecture.md)
