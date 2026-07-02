# Refactoring Patterns

> 重构模式目录。技法与工作流详见 [refactoring-techniques.md](refactoring-techniques.md)。

## Catalog of Refactoring Patterns

### Composing Methods

#### Extract Method

**Problem**: Long method that's hard to understand

**Solution**: Turn the fragment into a method with a descriptive name

```python
# Before
def print_owing(amount):
    print_banner()
    print(f"name: {customer}")
    print(f"amount: {amount}")

# After
def print_owing(amount):
    print_banner()
    print_details(amount)

def print_details(amount):
    print(f"name: {customer}")
    print(f"amount: {amount}")
```

#### Inline Method

**Problem**: Method body is as clear as its name

**Solution**: Replace calls to the method with the method's content

```python
# Before
def get_rating():
    return more_than_five_late_deliveries() ? 2 : 1

def more_than_five_late_deliveries():
    return late_deliveries > 5

# After
def get_rating():
    return late_deliveries > 5 ? 2 : 1
```

#### Extract Variable

**Problem**: Expression is hard to understand

**Solution**: Place result in a temporary variable with descriptive name

```python
# Before
if platform.upper().index('MAC') > -1 and browser.upper().index('IE') > -1 and initialized:
    do_something()

# After
is_mac = platform.upper().index('MAC') > -1
is_ie = browser.upper().index('IE') > -1
if is_mac and is_ie and initialized:
    do_something()
```

#### Replace Temp with Query

**Problem**: Temporary variable holding result of expression

**Solution**: Replace with a method

```python
# Before
def calculate_total():
    base_price = quantity * item_price
    if base_price > 1000:
        return base_price * 0.95
    return base_price

# After
def calculate_total():
    if base_price() > 1000:
        return base_price() * 0.95
    return base_price()

def base_price():
    return quantity * item_price
```

### Organizing Data

#### Replace Magic Number with Symbolic Constant

```python
# Before
if potential_energy > 9.81:
    return True

# After
GRAVITY_ACCELERATION = 9.81

if potential_energy > GRAVITY_ACCELERATION:
    return True
```

#### Replace Type Code with Strategy Pattern

```python
# Before
def calculate_salary(employee):
    if employee.type == 'ENGINEER':
        return employee.monthly_salary
    elif employee.type == 'SALESMAN':
        return employee.monthly_salary + employee.commission
    elif employee.type == 'MANAGER':
        return employee.monthly_salary + employee.bonus

# After
class Engineer:
    def calculate_salary(self):
        return self.monthly_salary

class Salesman:
    def calculate_salary(self):
        return self.monthly_salary + self.commission

class Manager:
    def calculate_salary(self):
        return self.monthly_salary + self.bonus
```

### Simplifying Conditional Expressions

#### Decompose Conditional

```python
# Before
if date < SUMMER_START or date > SUMMER_END:
    charge = quantity * winter_rate + winter_service_charge
else:
    charge = quantity * summer_rate

# After
if is_winter(date):
    charge = winter_charge(quantity)
else:
    charge = summer_charge(quantity)
```

#### Consolidate Conditional Expression

```python
# Before
def disability_amount():
    if seniority < 2:
        return 0
    if months_disabled > 12:
        return 0
    if is_part_time:
        return 0
    # compute amount

# After
def disability_amount():
    if is_not_eligible():
        return 0
    # compute amount

def is_not_eligible():
    return seniority < 2 or months_disabled > 12 or is_part_time
```

#### Replace Nested Conditional with Guard Clauses

```python
# Before
def get_payment_amount():
    result = 0
    if is_dead:
        result = dead_amount()
    else:
        if is_separated:
            result = separated_amount()
        else:
            if is_retired:
                result = retired_amount()
            else:
                result = normal_amount()
    return result

# After
def get_payment_amount():
    if is_dead:
        return dead_amount()
    if is_separated:
        return separated_amount()
    if is_retired:
        return retired_amount()
    return normal_amount()
```

#### Introduce Null Object

```python
# Before
if customer is None:
    plan = BillingPlan.basic()
else:
    plan = customer.get_plan()

# After
class NullCustomer:
    def get_plan(self):
        return BillingPlan.basic()

customer = customer or NullCustomer()
plan = customer.get_plan()
```
