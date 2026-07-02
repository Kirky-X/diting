# Refactoring Techniques

> 重构技法：方法调用简化、泛化处理、大型重构、工作流与优先级。模式目录详见 [refactoring-patterns.md](refactoring-patterns.md)。

## Making Method Calls Simpler

### Rename Method

```python
# Before
def get_num(self):
    return self.number

# After
def get_phone_number(self):
    return self.number
```

### Add Parameter

```python
# Before
def get_contact():
    return self.contact

# After
def get_contact(include_extension=False):
    if include_extension:
        return f"{self.contact} x{self.extension}"
    return self.contact
```

### Remove Parameter

```python
# Before
def get_order(order, customer):
    return order

# After
def get_order(order):
    return order
```

### Separate Query from Modifier

```python
# Before
def get_and_set_attribute(name, value):
    if attribute_exists(name):
        return get_attribute(name)
    set_attribute(name, value)
    return value

# After
def get_attribute(name):
    return attributes.get(name)

def set_attribute(name, value):
    attributes[name] = value

def attribute_exists(name):
    return name in attributes
```

### Parameterize Method

```python
# Before
def five_percent_raise():
    salary *= 1.05

def ten_percent_raise():
    salary *= 1.10

# After
def raise(percentage):
    salary *= (1 + percentage / 100)
```

## Dealing with Generalization

### Pull Up Method

```python
# Before (duplicate methods in subclasses)
class Engineer:
    def get_name(self):
        return self.name

class Manager:
    def get_name(self):
        return self.name

# After (method in parent class)
class Employee:
    def get_name(self):
        return self.name

class Engineer(Employee):
    pass

class Manager(Employee):
    pass
```

### Push Down Method

```python
# Before (method only relevant to subclass)
class Employee:
    def get_quota(self):
        return self.quota

class Engineer(Employee):
    pass  # doesn't use quota

class Salesman(Employee):
    pass  # uses quota

# After
class Employee:
    pass

class Engineer(Employee):
    pass

class Salesman(Employee):
    def get_quota(self):
        return self.quota
```

### Extract Subclass

```python
# Before
class JobItem:
    def __init__(self, unit_price, quantity, is_labor):
        self.unit_price = unit_price
        self.quantity = quantity
        self.is_labor = is_labor
    
    def get_total_price(self):
        if self.is_labor:
            return self.quantity * LABOR_RATE
        return self.quantity * self.unit_price

# After
class JobItem:
    def __init__(self, quantity):
        self.quantity = quantity
    
    def get_total_price(self):
        return self.quantity * self.get_unit_price()

class LaborItem(JobItem):
    def get_unit_price(self):
        return LABOR_RATE

class PartsItem(JobItem):
    def __init__(self, unit_price, quantity):
        super().__init__(quantity)
        self.unit_price = unit_price
    
    def get_unit_price(self):
        return self.unit_price
```

## Big Refactorings

### Convert Procedural Design to Objects

```python
# Before
def calculate_order_total(order):
    total = 0
    for item in order['items']:
        total += item['price'] * item['quantity']
    return total

def apply_discount(order, discount):
    order['total'] = calculate_order_total(order) * (1 - discount)

# After
class Order:
    def __init__(self, items):
        self.items = items
    
    def calculate_total(self):
        return sum(item.price * item.quantity for item in self.items)
    
    def apply_discount(self, discount):
        self.total = self.calculate_total() * (1 - discount)
```

### Separate Domain from Presentation

```python
# Before (mixed concerns)
class OrderView:
    def display_order(self, order_id):
        order = self.db.query(f"SELECT * FROM orders WHERE id = {order_id}")
        print(f"<h1>Order {order_id}</h1>")
        print(f"<p>Total: ${order.total}</p>")

# After (separated)
class Order:
    def __init__(self, order_id, db):
        self.data = db.query(f"SELECT * FROM orders WHERE id = {order_id}")
    
    @property
    def total(self):
        return self.data['total']

class OrderView:
    def display(self, order):
        print(f"<h1>Order {order.id}</h1>")
        print(f"<p>Total: ${order.total}</p>")
```

## Refactoring Workflow

### Step-by-Step Process

1. **Identify Code Smell**
   - Use detection criteria
   - Prioritize by impact

2. **Write Tests**
   - Ensure existing behavior is captured
   - Add tests for edge cases

3. **Apply Refactoring**
   - Make small, incremental changes
   - Run tests after each change

4. **Verify Behavior**
   - All tests pass
   - No regression

5. **Commit**
   - One refactoring per commit
   - Clear commit message

### Safety Checks

```
Before Refactoring:
[ ] Tests exist for affected code
[ ] Tests pass
[ ] Code coverage adequate

During Refactoring:
[ ] Small, focused changes
[ ] Tests run frequently
[ ] No behavior changes

After Refactoring:
[ ] All tests pass
[ ] Code is cleaner
[ ] No new complexity introduced
```

## Refactoring Priority Matrix

| Impact | Effort | Priority |
|--------|--------|----------|
| High | Low | Do Now |
| High | High | Plan |
| Low | Low | When Possible |
| Low | High | Skip |
