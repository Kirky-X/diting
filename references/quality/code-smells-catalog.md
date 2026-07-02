# 代码坏味目录

> 代码坏味详细目录：Dispensables、Couplers、Other Smells、检测工具与优先级。分类总览详见 [code-smells.md](code-smells.md)。

## Dispensables（多余物）

应删除的不必要代码。

### 注释（Comments）

**检测标准**
- 解释代码做什么的注释
- 可以作为方法名的注释
- 注释掉的代码
- 过期的 TODO 注释

**示例**
```python
# 检查用户是否有效且活跃
if user.is_valid() and user.is_active():
    # 处理订单
    process_order()
```

**重构**：提取方法、重命名方法、删除注释代码

### 重复代码（Duplicate Code）

**检测标准**
- 多处存在相同代码结构
- 略有变化的相似代码
- 稍作修改的复制粘贴

**检测方法**
```
1. 基于令牌的检测
2. 基于 AST 的检测
3. 语义克隆检测
```

**重构**：提取方法、上拉方法、形成模板方法

### 死代码（Dead Code）

**检测标准**
- 未使用的变量
- 不可达代码
- 从未调用的方法
- 从未使用的参数

**检测工具**
```bash
# Python
vulture script.py
pylint --disable=all --enable=unused-variable

# JavaScript
eslint --no-eslintrc --rule 'no-unused-vars: error'
```

**重构**：删除代码

### 投机性通用性（Speculative Generality）

**检测标准**
- 未使用的抽象类
- 未使用的参数
- 空实现的方法
- 未使用的"未来"功能

**示例**
```python
class AbstractProcessor:  # 只有一个实现存在
    def process(self):
        raise NotImplementedError

class ConcreteProcessor(AbstractProcessor):
    def process(self):
        # 实际实现
```

**重构**：折叠继承体系、内联类、移除参数

## Couplers（耦合器）

类之间过度耦合。

### 依恋情结（Feature Envy）

**检测标准**
- 方法更多地使用另一个类的特性
- 方法频繁访问另一个类的数据
- 方法应属于另一个类

**示例**
```python
class Order:
    def get_customer_discount(self):
        return self.customer.get_discount_rate() * self.customer.get_loyalty_factor()
```

**重构**：移动方法、提取方法

### 不当亲密（Inappropriate Intimacy）

**检测标准**
- 类访问彼此的私有成员
- 类之间过于了解对方
- 类之间紧耦合

**重构**：移动方法、提取方法、双向关联改单向

### 消息链（Message Chains）

**检测标准**
- 长方法调用链
- 通过多个对象导航
- a.b().c().d().e()

**示例**
```python
discount = order.get_customer().get_membership().get_discount().get_rate()
```

**重构**：隐藏委托、提取方法

### 中间人（Middle Man）

**检测标准**
- 类将大部分工作委托给另一个类
- 方法只是调用其他方法
- 类无实际功能

**示例**
```python
class OrderManager:
    def get_total(self, order):
        return order.get_total()
    
    def get_items(self, order):
        return order.get_items()
```

**重构**：移除中间人、内联方法

## 其他坏味（Other Smells）

### 不完整的库类（Incomplete Library Class）

**检测标准**
- 库类缺少所需方法
- 无法修改库代码
- 变通方案散布于代码中

**重构**：引入外部方法、引入本地扩展

### 基本类型偏执（Primitive Obsession）

**检测标准**
- 使用基本类型而非小对象
- 多个相同基本类型的参数
- 在基本类型中编码信息

**示例**
```python
def set_coordinates(lat: float, lon: float):
    pass  # 应使用 Coordinate 对象

def process_phone(phone: str):
    pass  # 应使用 PhoneNumber 对象
```

**重构**：以对象替代数据值、引入参数对象

### 过长消息链（Long Message Chain）

**检测标准**
- 方法调用链超过 3 个
- 暴露对象结构知识
- 对变更脆弱

**重构**：隐藏委托

## 检测工具

### 静态分析

| 语言 | 工具 | 检测坏味 |
|----------|------|-----------------|
| Python | Pylint、Flake8、Radon | 全部类别 |
| JavaScript | ESLint、SonarJS | 全部类别 |
| Java | PMD、SpotBugs、SonarQube | 全部类别 |
| Go | Staticcheck、Golint | 全部类别 |

### 复杂度指标

| 指标 | 工具 | 阈值 |
|--------|------|-----------|
| 圈复杂度 | Radon、ESLint | < 10 |
| 认知复杂度 | SonarQube | < 15 |
| Halstead 容量 | 多种 | < 1000 |
| 可维护性指数 | Radon | > 20 |

## 代码坏味优先级

| 优先级 | 坏味 | 影响 |
|----------|-------|--------|
| 1 | 重复代码 | 维护噩梦 |
| 2 | 过长方法 | 难以理解 |
| 3 | 过大类 | 多职责 |
| 4 | 过长参数列表 | 接口混乱 |
| 5 | Switch 语句 | 错过多态 |
| 6 | 死代码 | 造成混乱 |
| 7 | 注释 | 代码坏味指示 |
| 8 | 依恋情结 | 职责错误 |
