# Code Simplification Guidelines

## Core Principles

### 1. Preserve Functionality

**Rule**: Never change what the code does - only how it does it.

```
Before: Returns list of users
After: Returns list of users (same behavior, cleaner code)
```

**Verification**
- All tests pass
- Same outputs for same inputs
- Same side effects
- Same error handling

### 2. Apply Project Standards

Follow established conventions from CLAUDE.md:
- Import sorting and extensions
- Function keyword over arrow functions (when appropriate)
- Explicit return type annotations
- Proper error handling patterns
- Consistent naming conventions

### 3. Enhance Clarity

**Priorities**
1. Reduce unnecessary complexity and nesting
2. Eliminate redundant code and abstractions
3. Improve readability through clear naming
4. Consolidate related logic
5. Remove unnecessary comments

**Balance Point**
- Explicit code over clever code
- Readability over brevity
- Maintainability over optimization

### 4. Maintain Balance

**Avoid Over-Simplification**
- Don't reduce code clarity
- Don't create overly clever solutions
- Don't combine too many concerns
- Don't prioritize "fewer lines" over readability

## Simplification Techniques

### 1. Extract Method

**Before**
```python
def process_order(order):
    if order.status == 'pending':
        if order.items:
            total = 0
            for item in order.items:
                total += item.price * item.quantity
            if total > 1000:
                order.discount = total * 0.1
            order.total = total - order.discount
            order.status = 'processed'
            save(order)
            notify(order.user)
```

**After**
```python
def process_order(order):
    if not _can_process(order):
        return
    _apply_discount(order)
    _finalize(order)

def _can_process(order):
    return order.status == 'pending' and order.items

def _apply_discount(order):
    total = _calculate_total(order)
    if total > 1000:
        order.discount = total * 0.1
    order.total = total - order.discount

def _calculate_total(order):
    return sum(item.price * item.quantity for item in order.items)

def _finalize(order):
    order.status = 'processed'
    save(order)
    notify(order.user)
```

### 2. Replace Nested Conditional with Guard Clauses

**Before**
```python
def get_user_permission(user, resource):
    if user is not None:
        if user.is_active:
            if user.has_permission(resource):
                if not resource.is_locked:
                    return 'allowed'
    return 'denied'
```

**After**
```python
def get_user_permission(user, resource):
    if user is None:
        return 'denied'
    if not user.is_active:
        return 'denied'
    if not user.has_permission(resource):
        return 'denied'
    if resource.is_locked:
        return 'denied'
    return 'allowed'
```

### 3. Replace Magic Numbers with Named Constants

**Before**
```python
if status == 3:
    process()
    
if hours > 40:
    overtime = hours - 40
```

**After**
```python
STATUS_COMPLETED = 3
STANDARD_WORK_WEEK = 40

if status == STATUS_COMPLETED:
    process()
    
if hours > STANDARD_WORK_WEEK:
    overtime = hours - STANDARD_WORK_WEEK
```

### 4. Consolidate Duplicate Conditional Fragments

**Before**
```python
if is_special_customer:
    total = calculate_total()
    apply_discount(total, 0.15)
    send_receipt(total)
else:
    total = calculate_total()
    send_receipt(total)
```

**After**
```python
total = calculate_total()
if is_special_customer:
    apply_discount(total, 0.15)
send_receipt(total)
```

### 5. Replace Conditional with Polymorphism

**Before**
```python
def calculate_area(shape):
    if shape.type == 'circle':
        return 3.14159 * shape.radius ** 2
    elif shape.type == 'rectangle':
        return shape.width * shape.height
    elif shape.type == 'triangle':
        return 0.5 * shape.base * shape.height
```

**After**
```python
class Circle:
    def calculate_area(self):
        return 3.14159 * self.radius ** 2

class Rectangle:
    def calculate_area(self):
        return self.width * self.height

class Triangle:
    def calculate_area(self):
        return 0.5 * self.base * self.height

def calculate_area(shape):
    return shape.calculate_area()
```

### 6. Decompose Conditional

**Before**
```python
if date.before(SUMMER_START) or date.after(SUMMER_END):
    charge = quantity * winter_rate + winter_service_charge
else:
    charge = quantity * summer_rate
```

**After**
```python
if is_winter(date):
    charge = winter_charge(quantity)
else:
    charge = summer_charge(quantity)

def is_winter(date):
    return date.before(SUMMER_START) or date.after(SUMMER_END)

def winter_charge(quantity):
    return quantity * winter_rate + winter_service_charge

def summer_charge(quantity):
    return quantity * summer_rate
```

### 7. Replace Nested Ternary with If-Else or Switch

**Before**
```javascript
const status = user 
  ? user.isActive 
    ? user.hasPermission 
      ? 'allowed' 
      : 'no-permission'
    : 'inactive'
  : 'no-user';
```

**After**
```javascript
function getStatus(user) {
  if (!user) return 'no-user';
  if (!user.isActive) return 'inactive';
  if (!user.hasPermission) return 'no-permission';
  return 'allowed';
}
```

### 8. Remove Assignments to Parameters

Don't mutate parameters; accumulate results in a local. Example: `discount(value, is_vip, is_new)` — track a `multiplier` local instead of reassigning `result = result * 0.9`.

### 9. Replace Method with Method Object

For long methods with many locals, turn the method into a class: each parameter/locals becomes a field, each step becomes a private method. Use when Extract Method is blocked by shared local variables.

### 10. Introduce Parameter Object

When a method takes > 4 params (e.g., `create_user(name, email, age, address, phone, country)`), group related params into a `@dataclass UserParams` and pass the object. Reduces call-site churn when params evolve.

## Code Smells to Address

> 完整的坏味分类、检测信号与解决方案详见 [code-smells.md](code-smells.md)。

**优先级速查**：High（Long Method >50 行 / Deep Nesting >4 层 / Large Class >300 行 / Long Params >4 / Duplicated Code）→ Medium（Dead Code / Magic Numbers / Speculative Generality / Feature Envy）→ Low（Comments / Inconsistent Naming / Unused Parameters）。

## Simplification Checklist

### Structure
- [ ] Methods under 50 lines
- [ ] Nesting under 4 levels
- [ ] Parameters under 4
- [ ] Single responsibility per method/class

### Clarity
- [ ] Descriptive names
- [ ] No magic numbers
- [ ] Clear control flow
- [ ] Minimal comments needed

### Duplication
- [ ] No copy-paste code
- [ ] Common logic extracted
- [ ] Similar code consolidated

### Complexity
- [ ] Cyclomatic complexity < 10
- [ ] Cognitive complexity < 15
- [ ] No deeply nested conditionals
- [ ] Clear algorithm structure

## When NOT to Simplify

**Leave as-is**: backward-compat breaks / perf-critical benchmarked paths / well-tested complex business logic / external constraints / regression risk > benefit.
**Document instead**: complex algorithms / intricate business rules / regulatory requirements / unfamiliar domain.
