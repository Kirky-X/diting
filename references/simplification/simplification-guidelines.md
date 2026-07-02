# 代码简化指南

## 核心原则

### 1. 保持功能

**规则**：永不改变代码做什么 —— 只改变它怎么做。

```
之前：返回用户列表
之后：返回用户列表（相同行为，更干净的代码）
```

**验证**
- 所有测试通过
- 相同输入产生相同输出
- 相同副作用
- 相同错误处理

### 2. 应用项目标准

遵循 CLAUDE.md 中的既有约定：
- 导入排序与扩展名
- function 关键字优先于箭头函数（适当时）
- 显式返回类型注解
- 正确的错误处理模式
- 一致的命名约定

### 3. 增强清晰度

**优先级**
1. 减少不必要的复杂度和嵌套
2. 消除冗余代码和抽象
3. 通过清晰命名提升可读性
4. 合并相关逻辑
5. 移除不必要注释

**平衡点**
- 显式代码优先于巧妙代码
- 可读性优先于简洁
- 可维护性优先于优化

### 4. 保持平衡

**避免过度简化**
- 不降低代码清晰度
- 不创造过于巧妙的方案
- 不合并过多关注点
- 不以"更少行数"为由牺牲可读性

## 简化技法

### 1. 提取方法

**之前**
```python
def process_order(order):
    if order.status == 'pending':
        if order.items:
            total = 0
            for item in order.items:
                total += item.price * item.quantity
            if total > 1000:
                order.discount = total * 0.1
            order.total = total - order.discount
            order.status = 'processed'
            save(order)
            notify(order.user)
```

**之后**
```python
def process_order(order):
    if not _can_process(order):
        return
    _apply_discount(order)
    _finalize(order)

def _can_process(order):
    return order.status == 'pending' and order.items

def _apply_discount(order):
    total = _calculate_total(order)
    if total > 1000:
        order.discount = total * 0.1
    order.total = total - order.discount

def _calculate_total(order):
    return sum(item.price * item.quantity for item in order.items)

def _finalize(order):
    order.status = 'processed'
    save(order)
    notify(order.user)
```

### 2. 以卫语句替代嵌套条件

**之前**
```python
def get_user_permission(user, resource):
    if user is not None:
        if user.is_active:
            if user.has_permission(resource):
                if not resource.is_locked:
                    return 'allowed'
    return 'denied'
```

**之后**
```python
def get_user_permission(user, resource):
    if user is None:
        return 'denied'
    if not user.is_active:
        return 'denied'
    if not user.has_permission(resource):
        return 'denied'
    if resource.is_locked:
        return 'denied'
    return 'allowed'
```

### 3. 以命名常量替代魔术数字

**之前**
```python
if status == 3:
    process()
    
if hours > 40:
    overtime = hours - 40
```

**之后**
```python
STATUS_COMPLETED = 3
STANDARD_WORK_WEEK = 40

if status == STATUS_COMPLETED:
    process()
    
if hours > STANDARD_WORK_WEEK:
    overtime = hours - STANDARD_WORK_WEEK
```

### 4. 合并重复条件片段

**之前**
```python
if is_special_customer:
    total = calculate_total()
    apply_discount(total, 0.15)
    send_receipt(total)
else:
    total = calculate_total()
    send_receipt(total)
```

**之后**
```python
total = calculate_total()
if is_special_customer:
    apply_discount(total, 0.15)
send_receipt(total)
```

### 5. 以多态替代条件

**之前**
```python
def calculate_area(shape):
    if shape.type == 'circle':
        return 3.14159 * shape.radius ** 2
    elif shape.type == 'rectangle':
        return shape.width * shape.height
    elif shape.type == 'triangle':
        return 0.5 * shape.base * shape.height
```

**之后**
```python
class Circle:
    def calculate_area(self):
        return 3.14159 * self.radius ** 2

class Rectangle:
    def calculate_area(self):
        return self.width * self.height

class Triangle:
    def calculate_area(self):
        return 0.5 * self.base * self.height

def calculate_area(shape):
    return shape.calculate_area()
```

### 6. 分解条件

**之前**
```python
if date.before(SUMMER_START) or date.after(SUMMER_END):
    charge = quantity * winter_rate + winter_service_charge
else:
    charge = quantity * summer_rate
```

**之后**
```python
if is_winter(date):
    charge = winter_charge(quantity)
else:
    charge = summer_charge(quantity)

def is_winter(date):
    return date.before(SUMMER_START) or date.after(SUMMER_END)

def winter_charge(quantity):
    return quantity * winter_rate + winter_service_charge

def summer_charge(quantity):
    return quantity * summer_rate
```

### 7. 以 if-else 或 switch 替代嵌套三元

**之前**
```javascript
const status = user 
  ? user.isActive 
    ? user.hasPermission 
      ? 'allowed' 
      : 'no-permission'
    : 'inactive'
  : 'no-user';
```

**之后**
```javascript
function getStatus(user) {
  if (!user) return 'no-user';
  if (!user.isActive) return 'inactive';
  if (!user.hasPermission) return 'no-permission';
  return 'allowed';
}
```

### 8. 移除对参数的赋值

不要修改参数；在局部变量中累积结果。示例：`discount(value, is_vip, is_new)` —— 跟踪一个 `multiplier` 局部变量，而非重新赋值 `result = result * 0.9`。

### 9. 以方法对象替代方法

对于有大量局部变量的长方法，将方法转为类：每个参数/局部变量成为字段，每个步骤成为私有方法。当提取方法因共享局部变量而受阻时使用。

### 10. 引入参数对象

当方法接收 > 4 个参数时（如 `create_user(name, email, age, address, phone, country)`），将相关参数分组为 `@dataclass UserParams` 并传递该对象。减少参数演进时的调用点变更。

## 待处理的代码坏味

> 完整的坏味分类、检测信号与解决方案详见 [code-smells.md](code-smells.md)。

**优先级速查**：高（长方法 >50 行 / 深嵌套 >4 层 / 过大类 >300 行 / 长参数 >4 / 重复代码）→ 中（死代码 / 魔术数字 / 投机性通用性 / 依恋情结）→ 低（注释 / 不一致命名 / 未使用参数）。

## 简化清单

### 结构
- [ ] 方法不超过 50 行
- [ ] 嵌套不超过 4 层
- [ ] 参数不超过 4 个
- [ ] 每个方法/类单一职责

### 清晰度
- [ ] 描述性命名
- [ ] 无魔术数字
- [ ] 清晰的控制流
- [ ] 最少的必要注释

### 重复
- [ ] 无复制粘贴代码
- [ ] 公共逻辑已提取
- [ ] 相似代码已合并

### 复杂度
- [ ] 圈复杂度 < 10
- [ ] 认知复杂度 < 15
- [ ] 无深层嵌套条件
- [ ] 清晰的算法结构

## 何时不简化

**保持原样**：破坏向后兼容 / 性能关键已基准测试路径 / 充分测试的复杂业务逻辑 / 外部约束 / 回归风险 > 收益。
**改为文档化**：复杂算法 / 复杂业务规则 / 法规要求 / 不熟悉的领域。
