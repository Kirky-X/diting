# Code Smells Catalog

> Detailed code smells catalog: Dispensables, Couplers, Other Smells, detection tools, and priorities. See [code-smells.md](code-smells.md) for the classification overview.

## Dispensables

Unnecessary code that should be removed.

### Comments

**Detection Criteria**
- Comments that explain what the code does
- Comments that could be method names
- Commented-out code
- Stale TODO comments

**Example**
```python
# Check if user is valid and active
if user.is_valid() and user.is_active():
    # Process order
    process_order()
```

**Refactoring**: Extract method, rename method, delete commented code

### Duplicate Code

**Detection Criteria**
- Same code structure in multiple places
- Similar code with slight variations
- Copy-paste with minor modifications

**Detection Methods**
```
1. Token-based detection
2. AST-based detection
3. Semantic clone detection
```

**Refactoring**: Extract method, pull up method, form template method

### Dead Code

**Detection Criteria**
- Unused variables
- Unreachable code
- Methods never called
- Parameters never used

**Detection Tools**
```bash
# Python
vulture script.py
pylint --disable=all --enable=unused-variable

# JavaScript
eslint --no-eslintrc --rule 'no-unused-vars: error'
```

**Refactoring**: Delete code

### Speculative Generality

**Detection Criteria**
- Unused abstract classes
- Unused parameters
- Methods with empty implementations
- Unused "future" functionality

**Example**
```python
class AbstractProcessor:  # Only one implementation exists
    def process(self):
        raise NotImplementedError

class ConcreteProcessor(AbstractProcessor):
    def process(self):
        # Actual implementation
```

**Refactoring**: Collapse inheritance hierarchy, inline class, remove parameter

## Couplers

Excessive coupling between classes.

### Feature Envy

**Detection Criteria**
- Method uses more features of another class
- Method frequently accesses another class's data
- Method should belong to another class

**Example**
```python
class Order:
    def get_customer_discount(self):
        return self.customer.get_discount_rate() * self.customer.get_loyalty_factor()
```

**Refactoring**: Move method, extract method

### Inappropriate Intimacy

**Detection Criteria**
- Classes access each other's private members
- Classes know too much about each other
- Tight coupling between classes

**Refactoring**: Move method, extract method, change bidirectional association to unidirectional

### Message Chains

**Detection Criteria**
- Long method call chains
- Navigating through multiple objects
- a.b().c().d().e()

**Example**
```python
discount = order.get_customer().get_membership().get_discount().get_rate()
```

**Refactoring**: Hide delegate, extract method

### Middle Man

**Detection Criteria**
- Class delegates most of its work to another class
- Methods just call other methods
- Class has no actual functionality

**Example**
```python
class OrderManager:
    def get_total(self, order):
        return order.get_total()
    
    def get_items(self, order):
        return order.get_items()
```

**Refactoring**: Remove middle man, inline method

## Other Smells

### Incomplete Library Class

**Detection Criteria**
- Library class missing required methods
- Cannot modify library code
- Workarounds scattered throughout code

**Refactoring**: Introduce local extension, introduce foreign method

### Primitive Obsession

**Detection Criteria**
- Using primitives instead of small objects
- Multiple parameters of the same primitive type
- Encoding information in primitives

**Example**
```python
def set_coordinates(lat: float, lon: float):
    pass  # Should use a Coordinate object

def process_phone(phone: str):
    pass  # Should use a PhoneNumber object
```

**Refactoring**: Replace data value with object, introduce parameter object

### Long Message Chain

**Detection Criteria**
- Method call chain longer than 3
- Exposes knowledge of object structure
- Fragile to changes

**Refactoring**: Hide delegate

## Detection Tools

### Static Analysis

| Language | Tool | Detects |
|----------|------|---------|
| Python | Pylint, Flake8, Radon | All categories |
| JavaScript | ESLint, SonarJS | All categories |
| Java | PMD, SpotBugs, SonarQube | All categories |
| Go | Staticcheck, Golint | All categories |

### Complexity Metrics

| Metric | Tool | Threshold |
|--------|------|-----------|
| Cyclomatic complexity | Radon, ESLint | < 10 |
| Cognitive complexity | SonarQube | < 15 |
| Halstead volume | Various | < 1000 |
| Maintainability index | Radon | > 20 |

## Code Smell Priorities

| Priority | Smell | Impact |
|----------|-------|--------|
| 1 | Duplicate Code | Maintenance nightmare |
| 2 | Long Method | Hard to understand |
| 3 | Large Class | Multiple responsibilities |
| 4 | Long Parameter List | Confusing interface |
| 5 | Switch Statements | Missed polymorphism |
| 6 | Dead Code | Creates confusion |
| 7 | Comments | Indicator of code smells |
| 8 | Feature Envy | Wrong responsibility |
