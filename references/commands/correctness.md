# 正确性审查命令

正确性审查模式 —— 边界条件、null 处理、竞态条件、数据完整性

## 用法

```bash
review correctness [target-path]
```

## 检查内容

### 1. 边界条件处理

```
空数组 / 空集合 → 返回默认值或空结果？
空字符串 → trim 后仍有效？
零值 → 触发除零或特殊逻辑？
负数 → 有业务含义？
最大值 → 溢出？
空集合 vs null → 语义是否区分？
```

### 2. Null 安全

```
可空值在访问属性前已检查
使用可选链（?.）或 guard 语句
返回 Optional<T> / Result<T> / Maybe<T> 而非 null
Null 传播显式（Kotlin ?.、Rust ?）
数据库 NULL 正确映射到应用层 null
```

### 3. 差一错误

```
循环边界：< vs <=
数组切片：[start:end] 是否包含 end？
分页偏移：offset = (page - 1) * size
日期范围：start 包含，end 不包含？
区间计算：length = end - start + 1？
```

### 4. 竞态条件

```
共享状态使用锁/事务/原子操作
双重检查锁定正确实现
并发集合使用正确
读-改-写是原子的
乐观锁版本检查
分布式锁超时和续期
```

### 5. 时区和日期

```
日期以 UTC 存储
显示转换在展示层进行
时区信息不丢失
夏令时边界处理
跨时区计算正确
时长使用 Duration 类型而非时间戳差值
```

### 6. 字符串和编码

```
字符串操作处理多字节字符（UTF-8）
字符串长度：字节 vs 字符 vs 码点
Unicode 规范化（NFC/NFD）
文件编码显式声明
数据库连接编码已设置
```

### 7. 数值精度

```
货币使用 Decimal/BigDecimal
浮点数比较使用 epsilon
大整数使用 BigInt
序列化精度不丢失
数据库数值类型匹配
```

### 8. 错误传播

```
异步调用错误被捕获
Promise 不被静默吞掉
错误上下文足以调试
错误边界正确设置
重试逻辑不会无限循环
```

### 9. 状态一致性

```
多步修改是事务性的
部分失败可回滚
幂等性保证
最终一致性补偿机制
并发更新冲突处理
```

---

## 语言专属检查

### Python
- 访问属性前检查 `None`
- `dict.get(key, default)` 避免 KeyError
- `try/except/finally` 用于资源清理

### TypeScript
- `strictNullChecks: true`
- 可选链 `?.` 和空值合并 `??`
- 未知类型用 `unknown` 而非 `any`

### Java
- `Optional<T>` 代替返回 null
- `@Nullable` / `@NonNull` 注解
- try-with-resources 资源管理

### Go
- 显式错误检查 `if err != nil`
- 多返回值处理
- defer 资源清理

### Rust
- `Option<T>` 和 `Result<T, E>` 处理
- `?` 操作符错误传播
- 所有权系统防止竞态

---

## 严重度映射

| 问题类型 | 严重度级别 |
|----------|----------|
| 数据丢失/损坏 | Critical |
| 竞态条件导致不一致 | High |
| 空指针异常 | High |
| 未处理的边界条件 | Medium |
| 时区处理不当 | Medium |
| 精度丢失 | Medium |
| 差一错误 | Medium |

---

## 常见模式

### Null 安全模式

```typescript
// 使用可选链和空值合并
const name = user?.profile?.name ?? 'Unknown';

// 使用 Result 类型
function divide(a: number, b: number): Result<number, string> {
  if (b === 0) return Err('Division by zero');
  return Ok(a / b);
}
```

### 事务一致性

```python
with transaction.atomic():
    order = Order.objects.create(...)
    inventory = Inventory.objects.select_for_update().get(...)
    inventory.quantity -= order.quantity
    inventory.save()
```

### 幂等性保证

```python
def process_payment(payment_id: str):
    payment = Payment.objects.select_for_update().get(id=payment_id)
    if payment.status == 'completed':
        return  # 幂等：已处理
    # ... 处理支付
    payment.status = 'completed'
    payment.save()
```

---

## 参考

- [correctness/edge-cases.md](../correctness/edge-cases.md)
- [correctness/concurrency.md](../correctness/concurrency.md)
- [quality.md](quality.md)

## 相关命令

- [security.md](security.md)
- [quality.md](quality.md)
- [testing.md](testing.md)
