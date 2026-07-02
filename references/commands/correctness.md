# Correctness Command

Correctness review mode — edge cases, null handling, race conditions, data integrity

## Usage

```bash
review correctness [target-path]
```

## What to Check

### 1. Edge Case Handling

```
Empty array / empty collection → return default or empty result?
Empty string → still valid after trim?
Zero value → triggers division by zero or special logic?
Negative numbers → have business meaning?
Maximum values → overflow?
Empty collection vs null → semantics distinguished?
```

### 2. Null Safety

```
Nullable values checked before accessing properties
Use optional chaining (?.) or guard statements
Return Optional<T> / Result<T> / Maybe<T> instead of null
Null propagation explicit (Kotlin ?., Rust ?)
Database NULL mapped correctly to application layer null
```

### 3. Off-by-One Errors

```
Loop boundaries: < vs <=
Array slicing: [start:end] does it include end?
Pagination offset: offset = (page - 1) * size
Date ranges: start inclusive, end exclusive?
Interval calculation: length = end - start + 1?
```

### 4. Race Conditions

```
Shared state uses locks/transactions/atomic operations
Double-checked locking correctly implemented
Concurrent collections used correctly
Read-modify-write is atomic
Optimistic locking version check
Distributed lock timeout and renewal
```

### 5. Timezone and Dates

```
Dates stored in UTC
Display conversion at presentation layer
Timezone information not lost
Daylight saving time boundary handling
Cross-timezone calculations correct
Duration uses Duration type not timestamp difference
```

### 6. Strings and Encoding

```
String operations handle multi-byte characters (UTF-8)
String length: bytes vs characters vs code points
Unicode normalization (NFC/NFD)
File encoding explicitly declared
Database connection encoding set
```

### 7. Numeric Precision

```
Currency uses Decimal/BigDecimal
Floating point comparison uses epsilon
Large integers use BigInt
Serialization precision not lost
Database numeric types match
```

### 8. Error Propagation

```
Async call errors caught
Promises not silently swallowed
Error context sufficient for debugging
Error boundaries correctly set
Retry logic doesn't infinite loop
```

### 9. State Consistency

```
Multi-step mutations are transactional
Partial failures can be rolled back
Idempotency guaranteed
Eventual consistency compensation mechanism
Concurrent update conflict handling
```

---

## Language-Specific Checks

### Python
- Check `None` before accessing attributes
- `dict.get(key, default)` to avoid KeyError
- `try/except/finally` for resource cleanup

### TypeScript
- `strictNullChecks: true`
- Optional chaining `?.` and nullish coalescing `??`
- `unknown` instead of `any` for unknown types

### Java
- `Optional<T>` instead of returning null
- `@Nullable` / `@NonNull` annotations
- Try-with-resources resource management

### Go
- Explicit error check `if err != nil`
- Multiple return value handling
- defer resource cleanup

### Rust
- `Option<T>` and `Result<T, E>` handling
- `?` operator error propagation
- Ownership system prevents races

---

## Severity Mapping

| Issue Type | Severity Level |
|----------|----------|
| Data loss/corruption | Critical |
| Race condition causing inconsistency | High |
| Null pointer exception | High |
| Unhandled edge cases | Medium |
| Improper timezone handling | Medium |
| Precision loss | Medium |
| Off-by-one errors | Medium |

---

## Common Patterns

### Null Safety Pattern

```typescript
// Use optional chaining and nullish coalescing
const name = user?.profile?.name ?? 'Unknown';

// Use Result type
function divide(a: number, b: number): Result<number, string> {
  if (b === 0) return Err('Division by zero');
  return Ok(a / b);
}
```

### Transaction Consistency

```python
with transaction.atomic():
    order = Order.objects.create(...)
    inventory = Inventory.objects.select_for_update().get(...)
    inventory.quantity -= order.quantity
    inventory.save()
```

### Idempotency Guarantee

```python
def process_payment(payment_id: str):
    payment = Payment.objects.select_for_update().get(id=payment_id)
    if payment.status == 'completed':
        return  # Idempotent: already processed
    # ... process payment
    payment.status = 'completed'
    payment.save()
```

---

## References

- [correctness/edge-cases.md](../correctness/edge-cases.md)
- [correctness/concurrency.md](../correctness/concurrency.md)
- [quality.md](quality.md)

## Related Commands

- [security.md](security.md)
- [quality.md](quality.md)
- [testing.md](testing.md)