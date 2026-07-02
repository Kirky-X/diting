# 简化审查命令

简化审查模式 —— 提升可读性、消除冗余、降低认知负担

## 用法

```bash
review simplification [target-path]
```

## 核心原则

**简化 = 降低认知负担，保留行为。**
绝不改变代码做什么。只改变它怎么做。
总是验证测试仍通过。

---

## 检查内容

### 可读性

```
□ 变量名清晰描述其内容
□ 函数名清晰描述其行为（动词短语）
□ 无非通用缩写（mgr vs manager）
□ 复杂表达式提取为命名变量
□ 魔法字面量替换为命名常量
□ 布尔表达式无不必要反转（if !(!a) → if a）
```

### 结构

```
□ 函数只做一件事（单一职责）
□ 嵌套深度 ≤ 3（用 guard 子句/提前返回扁平化）
□ 无深嵌套三元（提取为 if-else 或独立函数）
□ 循环逻辑提取为命名函数（filterActiveUsers vs 内联 lambda）
□ 相关代码分组，无关代码分离
```

### 重复

```
□ 无复制粘贴代码块（≥ 3 次重复 → 提取函数）
□ 不同位置的相似逻辑泛化（参数化差异）
□ 无可提升的重复条件检查
□ 工具函数未重复实现（用标准库）
```

### 死代码

```
□ 无不可达代码（return/throw/break 之后）
□ 无未使用变量、参数、导入
□ 无注释掉的代码（用版本控制）
□ 无超过 6 个月且无 issue 引用的 TODO/FIXME
□ 无永久启用/禁用的 feature flag
```

### 现代惯用法（语言专属）

**Python**
```python
# ❌ 冗长
result = []
for item in items:
    if item.active:
        result.append(item.name)

# ✅ Pythonic
result = [item.name for item in items if item.active]

# ❌ 手动 None 检查
if value is not None:
    return value
return default

# ✅ 用 walrus / or
return value or default
```

**TypeScript / JavaScript**
```typescript
// ❌ 嵌套三元
const label = isAdmin ? 'Admin' : isMod ? 'Moderator' : 'User'

// ✅ Map 或函数
const ROLE_LABELS = { admin: 'Admin', mod: 'Moderator' }
const label = ROLE_LABELS[role] ?? 'User'

// ❌ 手动数组扁平化
const flat = arr.reduce((acc, curr) => acc.concat(curr), [])

// ✅ 内置
const flat = arr.flat()
```

**Java**
```java
// ❌ 命令式集合处理
List<String> names = new ArrayList<>();
for (User user : users) {
    if (user.isActive()) {
        names.add(user.getName());
    }
}

// ✅ Stream
List<String> names = users.stream()
    .filter(User::isActive)
    .map(User::getName)
    .collect(toList());
```

**Go**
```go
// ❌ 错误被检查但通过空白标识符忽略
result, _ := riskyOperation()

// ✅ 总是处理错误
result, err := riskyOperation()
if err != nil {
    return fmt.Errorf("riskyOperation failed: %w", err)
}
```

---

## 简化技法

### Guard 子句（扁平化嵌套）

```python
# ❌ 箭头型代码
def process(user, order):
    if user:
        if user.active:
            if order:
                if order.valid:
                    do_work(user, order)

# ✅ Guard 子句
def process(user, order):
    if not user: return
    if not user.active: return
    if not order: return
    if not order.valid: return
    do_work(user, order)
```

### 提取变量

```python
# ❌ 不透明条件
if user.created_at > datetime.now() - timedelta(days=30) and user.plan == 'trial':
    ...

# ✅ 命名表达式
is_new_user = user.created_at > datetime.now() - timedelta(days=30)
is_trial = user.plan == 'trial'
if is_new_user and is_trial:
    ...
```

### 用多态替换条件

```python
# ❌ 类型 switch
def get_area(shape):
    if shape.type == 'circle': return pi * shape.r ** 2
    if shape.type == 'rect': return shape.w * shape.h

# ✅ 多态
class Circle:
    def area(self): return pi * self.r ** 2

class Rectangle:
    def area(self): return self.w * self.h
```

---

## 何时不简化

- 代码是性能关键且有基准证明（不要优化掉）
- 复杂算法正确且测试充分（加注释解释而非简化）
- 简化会破坏向后兼容
- 团队不熟悉结果惯用法（清晰 > 聪明）

---

## 参考

- [simplification-guidelines.md](../simplification/simplification-guidelines.md) — 完整指南
- [refactoring-patterns.md](../simplification/refactoring-patterns.md) — 重构目录

## 相关命令

- [security.md](security.md)
- [performance.md](performance.md)
- [quality.md](quality.md)
- [architecture.md](architecture.md)
