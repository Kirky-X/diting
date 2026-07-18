# Code Smells Detection Guide

> Code smells classification overview. See [code-smells-catalog.md](code-smells-catalog.md) for the detailed catalog (Dispensables/Couplers/Other/Detection Tools/Priorities).

## Code Smell Categories

### Bloaters

Code, methods, or classes that have grown excessively.

#### Long Method

**Detection Criteria**
- Method exceeds 50 lines
- Method name contains "And" or "Or"
- Multiple levels of indentation
- Requires comments to explain sections

**Metrics**
| Lines | Status |
|-------|--------|
| 1-10 | Good |
| 11-30 | Acceptable |
| 31-50 | Needs review |
| >50 | Needs refactoring |

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
    
    # Apply discount
    if order.customer.is_vip:
        discount = subtotal * 0.1
    elif subtotal > 1000:
        discount = subtotal * 0.05
    else:
        discount = 0
    
    # ... another 50 lines
```

**Refactoring**: Extract Method

#### Large Class

**Detection Criteria**
- Class exceeds 300 lines
- More than 10 instance variables
- Methods grouped by different concerns
- Class has multiple "parts"

**Metrics**
| Lines | Instance Variables | Status |
|-------|-------------------|--------|
| <150 | <5 | Good |
| 150-300 | 5-10 | Needs review |
| >300 | >10 | Needs refactoring |

**Refactoring**: Extract Class, Extract Subclass

#### Long Parameter List

**Detection Criteria**
- More than 4 parameters
- Boolean parameters
- Consecutive parameters of the same type
- Need to look up parameter meanings

**Metrics**
| Parameter Count | Status |
|-----------------|--------|
| 1-3 | Good |
| 4 | Acceptable |
| >4 | Needs refactoring |

**Example**
```python
def create_user(name, email, age, address, phone, country, timezone, language):
    # Too many parameters
```

**Refactoring**: Introduce Parameter Object, Preserve Whole Object

#### Data Clumps

**Detection Criteria**
- Same group of variables always appears together
- Variables frequently passed together
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

Solutions that don't fully leverage object-oriented capabilities.

#### Switch Statements

**Detection Criteria**
- switch/case or if-else chains
- Same switch duplicated in multiple places
- Type checking via conditionals

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
- Instance variable used only in certain circumstances
- Object sometimes has empty fields
- Field only set during specific operations

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
- Subclass overrides methods with empty bodies
- Subclass throws "NotImplemented" for parent methods

**Refactoring**: Replace Inheritance with Delegation, Push Down Method

#### Alternative Classes with Different Interfaces

**Detection Criteria**
- Different classes doing the same thing with different method names
- Similar functionality but different signatures

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

Code that makes modifications difficult.

#### Divergent Change

**Detection Criteria**
- One class modified for multiple reasons
- Different types of changes affect the same class
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
- One change requires modifications in multiple classes
- Small changes scattered throughout the codebase
- Hard to find all affected locations

**Refactoring**: Move Method, Move Field, Inline Class

#### Parallel Inheritance Hierarchies

**Detection Criteria**
- Creating a subclass in one hierarchy requires creating one in another
- Similar naming patterns across hierarchies

**Example**
```
Customer -> VIPCustomer
CustomerExporter -> VIPCustomerExporter
CustomerValidator -> VIPCustomerValidator
```

**Refactoring**: Move Method, Collapse Hierarchy
