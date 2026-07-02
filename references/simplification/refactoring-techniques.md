# 重构技法

> 重构技法：方法调用简化、泛化处理、大型重构、工作流与优先级。模式目录详见 [refactoring-patterns.md](refactoring-patterns.md)。

## 简化方法调用

### 重命名方法

```python
# 之前
def get_num(self):
    return self.number

# 之后
def get_phone_number(self):
    return self.number
```

### 添加参数

```python
# 之前
def get_contact():
    return self.contact

# 之后
def get_contact(include_extension=False):
    if include_extension:
        return f"{self.contact} x{self.extension}"
    return self.contact
```

### 移除参数

```python
# 之前
def get_order(order, customer):
    return order

# 之后
def get_order(order):
    return order
```

### 分离查询与修改

```python
# 之前
def get_and_set_attribute(name, value):
    if attribute_exists(name):
        return get_attribute(name)
    set_attribute(name, value)
    return value

# 之后
def get_attribute(name):
    return attributes.get(name)

def set_attribute(name, value):
    attributes[name] = value

def attribute_exists(name):
    return name in attributes
```

### 参数化方法

```python
# 之前
def five_percent_raise():
    salary *= 1.05

def ten_percent_raise():
    salary *= 1.10

# 之后
def raise(percentage):
    salary *= (1 + percentage / 100)
```

## 处理泛化

### 上拉方法

```python
# 之前（子类中重复方法）
class Engineer:
    def get_name(self):
        return self.name

class Manager:
    def get_name(self):
        return self.name

# 之后（方法在父类中）
class Employee:
    def get_name(self):
        return self.name

class Engineer(Employee):
    pass

class Manager(Employee):
    pass
```

### 下推方法

```python
# 之前（方法仅与子类相关）
class Employee:
    def get_quota(self):
        return self.quota

class Engineer(Employee):
    pass  # 不使用 quota

class Salesman(Employee):
    pass  # 使用 quota

# 之后
class Employee:
    pass

class Engineer(Employee):
    pass

class Salesman(Employee):
    def get_quota(self):
        return self.quota
```

### 提取子类

```python
# 之前
class JobItem:
    def __init__(self, unit_price, quantity, is_labor):
        self.unit_price = unit_price
        self.quantity = quantity
        self.is_labor = is_labor
    
    def get_total_price(self):
        if self.is_labor:
            return self.quantity * LABOR_RATE
        return self.quantity * self.unit_price

# 之后
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

## 大型重构

### 将过程式设计转为对象

```python
# 之前
def calculate_order_total(order):
    total = 0
    for item in order['items']:
        total += item['price'] * item['quantity']
    return total

def apply_discount(order, discount):
    order['total'] = calculate_order_total(order) * (1 - discount)

# 之后
class Order:
    def __init__(self, items):
        self.items = items
    
    def calculate_total(self):
        return sum(item.price * item.quantity for item in self.items)
    
    def apply_discount(self, discount):
        self.total = self.calculate_total() * (1 - discount)
```

### 分离领域与表示

```python
# 之前（关注点混合）
class OrderView:
    def display_order(self, order_id):
        order = self.db.query(f"SELECT * FROM orders WHERE id = {order_id}")
        print(f"<h1>Order {order_id}</h1>")
        print(f"<p>Total: ${order.total}</p>")

# 之后（已分离）
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

## 重构工作流

### 逐步流程

1. **识别代码坏味**
   - 使用检测标准
   - 按影响排序

2. **编写测试**
   - 确保现有行为被捕获
   - 添加边界情况测试

3. **应用重构**
   - 做小的增量变更
   - 每次变更后运行测试

4. **验证行为**
   - 所有测试通过
   - 无回归

5. **提交**
   - 每次重构一次提交
   - 清晰的提交信息

### 安全检查

```
重构前：
[ ] 受影响代码已有测试
[ ] 测试通过
[ ] 代码覆盖率充足

重构中：
[ ] 小而聚焦的变更
[ ] 频繁运行测试
[ ] 无行为变更

重构后：
[ ] 所有测试通过
[ ] 代码更干净
[ ] 未引入新复杂度
```

## 重构优先级矩阵

| 影响 | 工作量 | 优先级 |
|--------|--------|----------|
| 高 | 低 | 立即执行 |
| 高 | 高 | 计划执行 |
| 低 | 低 | 有空时做 |
| 低 | 高 | 跳过 |
