# 重构模式

> 重构模式目录。技法与工作流详见 [refactoring-techniques.md](refactoring-techniques.md)。

## 重构模式目录

### 方法重组

#### 提取方法（Extract Method）

**问题**：长方法难以理解

**解决方案**：将片段转为方法并赋予描述性名称

```python
# 之前
def print_owing(amount):
    print_banner()
    print(f"name: {customer}")
    print(f"amount: {amount}")

# 之后
def print_owing(amount):
    print_banner()
    print_details(amount)

def print_details(amount):
    print(f"name: {customer}")
    print(f"amount: {amount}")
```

#### 内联方法（Inline Method）

**问题**：方法体与其名称一样清晰

**解决方案**：用方法内容替换方法调用

```python
# 之前
def get_rating():
    return more_than_five_late_deliveries() ? 2 : 1

def more_than_five_late_deliveries():
    return late_deliveries > 5

# 之后
def get_rating():
    return late_deliveries > 5 ? 2 : 1
```

#### 提取变量（Extract Variable）

**问题**：表达式难以理解

**解决方案**：将结果放入具有描述性名称的临时变量

```python
# 之前
if platform.upper().index('MAC') > -1 and browser.upper().index('IE') > -1 and initialized:
    do_something()

# 之后
is_mac = platform.upper().index('MAC') > -1
is_ie = browser.upper().index('IE') > -1
if is_mac and is_ie and initialized:
    do_something()
```

#### 以查询替代临时变量（Replace Temp with Query）

**问题**：临时变量保存表达式结果

**解决方案**：用方法替代

```python
# 之前
def calculate_total():
    base_price = quantity * item_price
    if base_price > 1000:
        return base_price * 0.95
    return base_price

# 之后
def calculate_total():
    if base_price() > 1000:
        return base_price() * 0.95
    return base_price()

def base_price():
    return quantity * item_price
```

### 数据组织

#### 以符号常量替代魔术数字

```python
# 之前
if potential_energy > 9.81:
    return True

# 之后
GRAVITY_ACCELERATION = 9.81

if potential_energy > GRAVITY_ACCELERATION:
    return True
```

#### 以策略模式替代类型码

```python
# 之前
def calculate_salary(employee):
    if employee.type == 'ENGINEER':
        return employee.monthly_salary
    elif employee.type == 'SALESMAN':
        return employee.monthly_salary + employee.commission
    elif employee.type == 'MANAGER':
        return employee.monthly_salary + employee.bonus

# 之后
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

### 简化条件表达式

#### 分解条件

```python
# 之前
if date < SUMMER_START or date > SUMMER_END:
    charge = quantity * winter_rate + winter_service_charge
else:
    charge = quantity * summer_rate

# 之后
if is_winter(date):
    charge = winter_charge(quantity)
else:
    charge = summer_charge(quantity)
```

#### 合并条件表达式

```python
# 之前
def disability_amount():
    if seniority < 2:
        return 0
    if months_disabled > 12:
        return 0
    if is_part_time:
        return 0
    # 计算金额

# 之后
def disability_amount():
    if is_not_eligible():
        return 0
    # 计算金额

def is_not_eligible():
    return seniority < 2 or months_disabled > 12 or is_part_time
```

#### 以卫语句替代嵌套条件

```python
# 之前
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

# 之后
def get_payment_amount():
    if is_dead:
        return dead_amount()
    if is_separated:
        return separated_amount()
    if is_retired:
        return retired_amount()
    return normal_amount()
```

#### 引入空对象

```python
# 之前
if customer is None:
    plan = BillingPlan.basic()
else:
    plan = customer.get_plan()

# 之后
class NullCustomer:
    def get_plan(self):
        return BillingPlan.basic()

customer = customer or NullCustomer()
plan = customer.get_plan()
```
