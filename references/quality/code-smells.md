# Code Smells Detection Guide

> 代码坏味分类总览。详细目录（Dispensables/Couplers/Other/检测工具/优先级）详见 [code-smells-catalog.md](code-smells-catalog.md)。

## Code Smell Categories

### Bloaters

Code, methods, or classes that have grown too large.

#### Long Method

**Detection Criteria**
- Method exceeds 50 lines
- Method name contains "And" or "Or"
- Multiple levels of indentation
- Comments explaining sections

**Metrics**
| Lines | Status |
|-------|--------|
| 1-10 | Good |
| 11-30 | Acceptable |
| 31-50 | Review needed |
| >50 | Refactor |

**Example**
```python
def process_order(order):
    # Validate order
    if not order.items:
        raise ValueError("Empty order")
    for item in order.items:
        if item.quantity <= 0:
            raise ValueError("Invalid quantity")
    
    # Calculate totals
    subtotal = 0
    for item in order.items:
        subtotal += item.price * item.quantity
    
    # Apply discounts
    if order.customer.is_vip:
        discount = subtotal * 0.1
    elif subtotal > 1000:
        discount = subtotal * 0.05
    else:
        discount = 0
    
    # ... 50 more lines
```

**Refactoring**: Extract Method

#### Large Class

**Detection Criteria**
- Class exceeds 300 lines
- More than 10 instance variables
- Methods grouped by different concerns
- Multiple "sections" in class

**Metrics**
| Lines | Instance Variables | Status |
|-------|-------------------|--------|
| <150 | <5 | Good |
| 150-300 | 5-10 | Review |
| >300 | >10 | Refactor |

**Refactoring**: Extract Class, Extract Subclass

#### Long Parameter List

**Detection Criteria**
- More than 4 parameters
- Boolean parameters
- Parameters of same type in sequence
- Need to look up parameter meaning

**Metrics**
| Parameters | Status |
|------------|--------|
| 1-3 | Good |
| 4 | Acceptable |
| >4 | Refactor |

**Example**
```python
def create_user(name, email, age, address, phone, country, timezone, language):
    # Too many parameters
```

**Refactoring**: Introduce Parameter Object, Preserve Whole Object

#### Data Clumps

**Detection Criteria**
- Same group of variables appear together
- Variables often passed together
- Similar variable names (start/end, min/max)

**Example**
```python
def find_in_range(start_date, end_date, start_time, end_time):
    pass

def schedule(start_date, end_date, start_time, end_time):
    pass
```

**Refactoring**: Extract Class

### Object-Orientation Abusers

Solutions that don't fully utilize object-oriented capabilities.

#### Switch Statements

**Detection Criteria**
- Switch/case or if-else chains
- Same switch repeated in multiple places
- Type checking with conditional

**Example**
```python
def calculate_pay(employee):
    if employee.type == 'ENGINEER':
        return employee.monthly_salary
    elif employee.type == 'SALESMAN':
        return employee.monthly_salary + employee.commission
    elif employee.type == 'MANAGER':
        return employee.monthly_salary + employee.bonus
```

**Refactoring**: Replace Conditional with Polymorphism, Replace Type Code with Strategy

#### Temporary Field

**Detection Criteria**
- Instance variable only used in certain cases
- Object sometimes has null fields
- Fields set only during specific operations

**Example**
```python
class Order:
    def __init__(self):
        self.items = []
        self.discount = None  # Only used for VIP orders
        self.gift_wrap = None  # Only used for gifts
```

**Refactoring**: Extract Class, Introduce Null Object

#### Refused Bequest

**Detection Criteria**
- Subclass doesn't use inherited methods
- Subclass overrides methods with empty body
- Subclass throws "NotImplemented" for parent methods

**Refactoring**: Replace Inheritance with Delegation, Push Down Method

#### Alternative Classes with Different Interfaces

**Detection Criteria**
- Classes do the same thing with different method names
- Similar functionality, different signatures

**Example**
```python
class CustomerRepository:
    def find_by_id(self, id):
        pass

class ClientStore:
    def get(self, client_id):
        pass
```

**Refactoring**: Rename Method, Extract Superclass

### Change Preventers

Code that makes changes difficult.

#### Divergent Change

**Detection Criteria**
- One class changed for multiple reasons
- Different types of changes affect same class
- Class has multiple responsibilities

**Example**
```python
class User:
    def update_profile(self):  # User management
        pass
    
    def send_email(self):  # Email functionality
        pass
    
    def generate_report(self):  # Reporting
        pass
```

**Refactoring**: Extract Class

#### Shotgun Surgery

**Detection Criteria**
- One change requires modifying many classes
- Small changes scattered across codebase
- Hard to find all affected places

**Refactoring**: Move Method, Move Field, Inline Class

#### Parallel Inheritance Hierarchies

**Detection Criteria**
- Creating subclass in one hierarchy requires creating in another
- Similar naming patterns across hierarchies

**Example**
```
Customer -> VIPCustomer
CustomerExporter -> VIPCustomerExporter
CustomerValidator -> VIPCustomerValidator
```

**Refactoring**: Move Method, Combine hierarchies
