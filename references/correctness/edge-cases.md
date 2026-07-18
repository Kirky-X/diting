# Edge Case Handling Guide

Edge case handling patterns — Systematic identification and handling of boundary conditions

## Overview

Edge cases are among the most easily overlooked areas in a system, yet they often cause the most severe problems. This document provides systematic patterns for identifying and handling edge cases.

---

## 1. Collection Edge Cases

### Empty Collections

| Scenario | Incorrect Handling | Correct Handling |
|----------|-------------------|------------------|
| Iterating empty collection | No issue | Direct iteration, loop body will not execute |
| Getting first element | `items[0]` throws exception | `items[0] if items else default` |
| Sum/Average | `sum([])` = 0, `mean([])` throws exception | Check beforehand or return default value |
| Max/Min | `max([])` throws exception | `max(items, default=0)` |

### Single-Element Collections

```python
# May expect a list but get a single element
result = api.get_items()  # May return [item] or item

# Defensive handling
items = result if isinstance(result, list) else [result]
```

### Nested Collections

```python
# Risk of deep access
value = data.get('a', {}).get('b', {}).get('c')

# Safer alternative
from functools import reduce
def safe_get(d, *keys, default=None):
    return reduce(lambda d, k: d.get(k, {}) if isinstance(d, dict) else default, keys, d) or default
```

---

## 2. Numeric Edge Cases

### Zero Values

| Operation | Risk | Handling |
|-----------|------|----------|
| Division | Division by zero exception | Check or use try-except |
| Logarithm | `log(0)` undefined | `log(max(x, epsilon))` |
| Modulo | `x % 0` exception | Check divisor first |
| Exponentiation | `0 ** -1` exception | Boundary check |

### Negative Values

```python
# Negative square root
import math
result = math.sqrt(max(0, value))

# Negative modulo
-7 % 3  # Result is 2 in Python, but may differ in other languages
```

### Overflow

```python
# Integer overflow (not an issue in Python, but be careful in other languages)
# C/Java: INT_MAX + 1 = INT_MIN

# Floating-point overflow
import math
if not math.isfinite(result):
    raise OverflowError("Computation result overflowed")
```

### Floating-Point Precision

```python
# Don't use == to compare floats
0.1 + 0.2 == 0.3  # False!

# Use epsilon comparison
def approx_equal(a, b, epsilon=1e-9):
    return abs(a - b) < epsilon

# Use Decimal for currency calculations
from decimal import Decimal
price = Decimal('19.99')
tax = price * Decimal('0.08')
```

---

## 3. String Edge Cases

### Empty Strings

```python
# Empty after trim
username = input.strip()
if not username:
    raise ValidationError("Username cannot be empty")

# Distinguish empty string from null
value = data.get('name')  # None vs "" vs "  "
if value is None:
    # Missing
elif not value.strip():
    # Whitespace only
```

### Unicode Edge Cases

```python
# String length (bytes vs characters vs code points)
text = "hello"
len(text)                    # 5 (characters)
len(text.encode('utf-8'))    # 5 (bytes)

# Unicode normalization
import unicodedata
text = unicodedata.normalize('NFC', text)  # Unified representation

# Zero-width characters
invisible = text.strip('\u200b\ufeff')  # Remove zero-width characters
```

### Encoding Issues

```python
# Always explicitly declare encoding
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# Handle encoding errors
with open(path, 'r', encoding='utf-8', errors='replace') as f:
    content = f.read()
```

---

## 4. Time Edge Cases

### Timezone Boundaries

```python
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

# Always store in UTC
dt = datetime.now(timezone.utc)

# Convert on display
local = dt.astimezone(ZoneInfo('Asia/Shanghai'))
```

### Daylight Saving Time

```python
# Avoid time calculations at DST boundaries
# Use UTC or timezone-naive dates
from datetime import date
d = date(2024, 3, 10)  # No timezone issues
```

### Leap Years/Leap Seconds

```python
import calendar

# Leap year check
calendar.isleap(2024)  # True

# Days in February
days_in_feb = calendar.monthrange(2024, 2)[1]  # 29
```

---

## 5. Boundary Value Checklist

### Input Validation

```
Null values (null, None, undefined)
Empty strings ("" and "   ")
Empty collections ([] and {} and set())
Zero values (0 and 0.0 and 0j)
Negative values (-1 and -0.001)
Maximum values (INT_MAX and FLT_MAX)
Minimum values (INT_MIN and FLT_MIN)
Boundary values (exactly equal to threshold)
Special characters (< and > and & and " and ')
Unicode characters (emoji and CJK and zero-width)
```

### Index Boundaries

```
First element (index 0)
Last element (index len-1)
Out of bounds (index len and index -len-1)
Negative index (index -1)
Empty slice (arr[0:0])
Full slice (arr[:])
```

---

## 6. Edge Case Testing Template

```python
import pytest

@pytest.mark.parametrize("input,expected", [
    (None, "default"),
    ("", "default"),
    ("   ", "default"),
    ("valid", "valid"),
    ("a" * 1000, "too_long"),
])
def test_edge_cases(input, expected):
    result = process(input)
    assert result == expected
```

---

## References

- [concurrency.md](concurrency.md) — Concurrency edge cases
- [../commands/correctness.md](../commands/correctness.md) — Correctness review commands
