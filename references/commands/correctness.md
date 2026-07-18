# Correctness Review Command

Correctness Review Mode — boundary conditions, null handling, race conditions, data integrity

## Usage

```bash
review correctness [target-path]
```

## Checklist

### 1. Boundary Condition Handling

```
Empty array / empty collection → return default value or empty result?
Empty string → still valid after trim?
Zero value → triggers divide-by-zero or special logic?
Negative numbers → have business meaning?
Maximum value → overflow?
Empty collection vs null → semantically distinguished?
```

### 2. Null Safety

```
Nullable values checked before accessing properties
Use optional chaining (?.) or guard statements
Return Optional<T> / Result<T> / Maybe<T> instead of null
Null propagation is explicit (Kotlin ?., Rust ?)
Database NULL correctly mapped to application-layer null
```

### 3. Off-by-One Errors

```
Loop boundaries: < vs <=
Array slicing: [start:end] — does it include end?
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
Optimistic lock version checking
Distributed lock timeout and renewal
```

### 5. Timezone and Dates

```
Dates stored in UTC
Display conversion in presentation layer
Timezone information not lost
Daylight saving time boundary handling
Cross-timezone calculations correct
Duration uses Duration type, not timestamp differences
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
Floating-point comparison uses epsilon
Large integers use BigInt
Serialization precision not lost
Database numeric types match
```

### 8. Error Propagation

```
Async call errors caught
Promises not silently swallowed
Error context sufficient for debugging
Error boundaries correctly configured
Retry logic does not loop infinitely
```

### 9. State Consistency

```
Multi-step modifications are transactional
Partial failures can be rolled back
Idempotency guarantees
Eventual consistency compensation mechanism
Concurrent update conflict handling
```

---

## Language-Specific Checks

### Python
- Check for `None` before accessing properties
- `dict.get(key, default)` to avoid KeyError
- `try/except/finally` for resource cleanup

### TypeScript
- `strictNullChecks: true`
- Optional chaining `?.` and nullish coalescing `??`
- Use `unknown` instead of `any` for unknown types

### Java
- `Optional<T>` instead of returning null
- `@Nullable` / `@NonNull` annotations
- try-with-resources for resource management

### Go
- Explicit error checking `if err != nil`
- Multiple return value handling
- defer for resource cleanup

### Rust
- `Option<T>` and `Result<T, E>` handling
- `?` operator for error propagation
- Ownership system prevents race conditions

---

## Severity Mapping

| Issue Type | Severity Level |
|------------|---------------|
| Data loss/corruption | Critical |
| Race condition causing inconsistency | High |
| Null pointer exception | High |
| Unhandled boundary condition | Medium |
| Improper timezone handling | Medium |
| Precision loss | Medium |
| Off-by-one error | Medium |

---

## Common Patterns

### Null Safety Patterns

```typescript
// Using optional chaining and nullish coalescing
const name = user?.profile?.name ?? 'Unknown';

// Using Result type
function divide(a: number, b: number): Result<number, string> {
  if (b === 0) return Err('Division by zero');
  return Ok(a / b);
}
```

### Transactional Consistency

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
