# 代码坏味检测指南

> 代码坏味分类总览。详细目录（Dispensables/Couplers/Other/检测工具/优先级）详见 [code-smells-catalog.md](code-smells-catalog.md)。

## 代码坏味分类

### 膨胀者（Bloaters）

代码、方法或类过度膨胀。

#### 过长方法（Long Method）

**检测标准**
- 方法超过 50 行
- 方法名包含 "And" 或 "Or"
- 多层缩进
- 需要注释解释各部分

**指标**
| 行数 | 状态 |
|-------|--------|
| 1-10 | 良好 |
| 11-30 | 可接受 |
| 31-50 | 需审查 |
| >50 | 需重构 |

**示例**
```python
def process_order(order):
    # 验证订单
    if not order.items:
        raise ValueError("空订单")
    for item in order.items:
        if item.quantity <= 0:
            raise ValueError("无效数量")
    
    # 计算合计
    subtotal = 0
    for item in order.items:
        subtotal += item.price * item.quantity
    
    # 应用折扣
    if order.customer.is_vip:
        discount = subtotal * 0.1
    elif subtotal > 1000:
        discount = subtotal * 0.05
    else:
        discount = 0
    
    # ... 还有 50 行
```

**重构**：提取方法（Extract Method）

#### 过大类（Large Class）

**检测标准**
- 类超过 300 行
- 超过 10 个实例变量
- 方法按不同关注点分组
- 类中有多个"部分"

**指标**
| 行数 | 实例变量 | 状态 |
|-------|-------------------|--------|
| <150 | <5 | 良好 |
| 150-300 | 5-10 | 需审查 |
| >300 | >10 | 需重构 |

**重构**：提取类、提取子类

#### 过长参数列表（Long Parameter List）

**检测标准**
- 超过 4 个参数
- 布尔参数
- 相同类型参数连续出现
- 需要查阅参数含义

**指标**
| 参数数 | 状态 |
|------------|--------|
| 1-3 | 良好 |
| 4 | 可接受 |
| >4 | 需重构 |

**示例**
```python
def create_user(name, email, age, address, phone, country, timezone, language):
    # 参数过多
```

**重构**：引入参数对象、保持完整对象

#### 数据泥团（Data Clumps）

**检测标准**
- 相同的变量组经常一起出现
- 变量经常一起传递
- 相似的变量名（start/end、min/max）

**示例**
```python
def find_in_range(start_date, end_date, start_time, end_time):
    pass

def schedule(start_date, end_date, start_time, end_time):
    pass
```

**重构**：提取类

### 面向对象滥用者（Object-Orientation Abusers）

未充分利用面向对象能力的解决方案。

#### Switch 语句（Switch Statements）

**检测标准**
- switch/case 或 if-else 链
- 相同 switch 在多处重复
- 用条件判断类型

**示例**
```python
def calculate_pay(employee):
    if employee.type == 'ENGINEER':
        return employee.monthly_salary
    elif employee.type == 'SALESMAN':
        return employee.monthly_salary + employee.commission
    elif employee.type == 'MANAGER':
        return employee.monthly_salary + employee.bonus
```

**重构**：以多态替代条件、以策略替代类型码

#### 临时字段（Temporary Field）

**检测标准**
- 实例变量仅在特定情况下使用
- 对象有时有空字段
- 字段仅在特定操作中设置

**示例**
```python
class Order:
    def __init__(self):
        self.items = []
        self.discount = None  # 仅用于 VIP 订单
        self.gift_wrap = None  # 仅用于礼品
```

**重构**：提取类、引入空对象

#### 拒绝继承（Refused Bequest）

**检测标准**
- 子类不使用继承的方法
- 子类用空方法体覆盖方法
- 子类对父类方法抛出 "NotImplemented"

**重构**：以委托替代继承、下推方法

#### 接口不同的替代类（Alternative Classes with Different Interfaces）

**检测标准**
- 不同类做相同的事但方法名不同
- 功能相似但签名不同

**示例**
```python
class CustomerRepository:
    def find_by_id(self, id):
        pass

class ClientStore:
    def get(self, client_id):
        pass
```

**重构**：重命名方法、提取超类

### 变更阻碍者（Change Preventers）

使修改变得困难的代码。

#### 发散式变更（Divergent Change）

**检测标准**
- 一个类因多种原因被修改
- 不同类型的变更影响同一类
- 类有多种职责

**示例**
```python
class User:
    def update_profile(self):  # 用户管理
        pass
    
    def send_email(self):  # 邮件功能
        pass
    
    def generate_report(self):  # 报表
        pass
```

**重构**：提取类

#### 霰弹式修改（Shotgun Surgery）

**检测标准**
- 一次修改需要改动多个类
- 小变更散布于代码库各处
- 难以找到所有受影响的位置

**重构**：移动方法、移动字段、内联类

#### 平行继承体系（Parallel Inheritance Hierarchies）

**检测标准**
- 在一个继承体系中创建子类需要在另一个中创建
- 不同体系间命名模式相似

**示例**
```
Customer -> VIPCustomer
CustomerExporter -> VIPCustomerExporter
CustomerValidator -> VIPCustomerValidator
```

**重构**：移动方法、合并继承体系
