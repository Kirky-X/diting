# Code Smells Catalog

> 代码坏味详细目录：Dispensables、Couplers、Other Smells、检测工具与优先级。分类总览详见 [code-smells.md](code-smells.md)。

## Dispensables

Unnecessary code that should be removed.

### Comments

**Detection Criteria**
- Comments explaining what code does
- Comments that could be method names
- Commented-out code
- TODO comments that are old

**Example**
```python
# Check if user is valid and active
if user.is_valid() and user.is_active():
    # Process the order
    process_order()
```

**Refactoring**: Extract Method, Rename Method, Delete commented code

### Duplicate Code

**Detection Criteria**
- Same code structure in multiple places
- Similar code with minor variations
- Copy-paste with slight modifications

**Detection Methods**
```
1. Token-based detection
2. AST-based detection
3. Semantic clone detection
```

**Refactoring**: Extract Method, Pull Up Method, Form Template Method

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

**Refactoring**: Delete the code

### Speculative Generality

**Detection Criteria**
- Unused abstract classes
- Unused parameters
- Methods that do nothing
- "Future" features not used

**Example**
```python
class AbstractProcessor:  # Only one implementation exists
    def process(self):
        raise NotImplementedError

class ConcreteProcessor(AbstractProcessor):
    def process(self):
        # actual implementation
```

**Refactoring**: Collapse Hierarchy, Inline Class, Remove Parameter

## Couplers

Excessive coupling between classes.

### Feature Envy

**Detection Criteria**
- Method uses more features of another class
- Method accesses other class's data frequently
- Method belongs in another class

**Example**
```python
class Order:
    def get_customer_discount(self):
        return self.customer.get_discount_rate() * self.customer.get_loyalty_factor()
```

**Refactoring**: Move Method, Extract Method

### Inappropriate Intimacy

**Detection Criteria**
- Classes access each other's private members
- Classes know too much about each other
- Tight coupling between classes

**Refactoring**: Move Method, Extract Method, Change Bidirectional to Unidirectional

### Message Chains

**Detection Criteria**
- Long chain of method calls
- Object navigation through multiple objects
- a.b().c().d().e()

**Example**
```python
discount = order.get_customer().get_membership().get_discount().get_rate()
```

**Refactoring**: Hide Delegate, Extract Method

### Middle Man

**Detection Criteria**
- Class delegates most work to another
- Methods just call other methods
- No real functionality in class

**Example**
```python
class OrderManager:
    def get_total(self, order):
        return order.get_total()
    
    def get_items(self, order):
        return order.get_items()
```

**Refactoring**: Remove Middle Man, Inline Method

## Other Smells

### Incomplete Library Class

**Detection Criteria**
- Library class missing needed methods
- Can't modify library code
- Workarounds scattered in code

**Refactoring**: Introduce Foreign Method, Introduce Local Extension

### Primitive Obsession

**Detection Criteria**
- Using primitives instead of small objects
- Multiple parameters of same primitive type
- Encoding information in primitives

**Example**
```python
def set_coordinates(lat: float, lon: float):
    pass  # Should use Coordinate object

def process_phone(phone: str):
    pass  # Should use PhoneNumber object
```

**Refactoring**: Replace Data Value with Object, Introduce Parameter Object

### Long Message Chain

**Detection Criteria**
- Chain of method calls > 3
- Knowledge of object structure exposed
- Fragile to changes

**Refactoring**: Hide Delegate

## Detection Tools

### Static Analysis

| Language | Tool | Smells Detected |
|----------|------|-----------------|
| Python | Pylint, Flake8, Radon | All categories |
| JavaScript | ESLint, SonarJS | All categories |
| Java | PMD, SpotBugs, SonarQube | All categories |
| Go | Staticcheck, Golint | All categories |

### Complexity Metrics

| Metric | Tool | Threshold |
|--------|------|-----------|
| Cyclomatic Complexity | Radon, ESLint | < 10 |
| Cognitive Complexity | SonarQube | < 15 |
| Halstead Volume | Various | < 1000 |
| Maintainability Index | Radon | > 20 |

## Code Smell Priority

| Priority | Smell | Impact |
|----------|-------|--------|
| 1 | Duplicate Code | Maintenance nightmare |
| 2 | Long Method | Hard to understand |
| 3 | Large Class | Multiple responsibilities |
| 4 | Long Parameter List | Confusing interfaces |
| 5 | Switch Statements | Missed polymorphism |
| 6 | Dead Code | Confusion |
| 7 | Comments | Code smell indicator |
| 8 | Feature Envy | Wrong responsibility |
