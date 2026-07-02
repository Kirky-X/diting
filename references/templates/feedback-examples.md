# 反馈示例

好与坏的反馈示例，帮助审查者提供有价值的评论

---

## 反馈原则

1. **具体** —— 指出确切行号，解释问题
2. **解释原因** —— 描述风险或后果，而非仅规则
3. **建议修复** —— 提供具体替代方案或代码片段
4. **提问而非命令** —— 对主观事项使用提问
5. **认可好的工作** —— 表扬好的方案
6. **区分阻塞级别** —— 使用严重度标签

---

## 安全示例

### 糟糕反馈

> 这不安全。修一下。

### 良好反馈

> `[CRITICAL]` `src/auth.py:45` —— SQL 注入漏洞
>
> **问题**：用户输入直接拼接到 SQL 查询字符串。攻击者可操纵查询读取、修改或删除任意数据。
>
> ```python
> # 有漏洞
> query = "SELECT * FROM users WHERE name = '" + username + "'"
> cursor.execute(query)
> ```
>
> **修复**：
> ```python
> # 安全 —— 使用参数化查询
> cursor.execute("SELECT * FROM users WHERE name = %s", (username,))
> ```
>
> **参考**：OWASP A03:2021 Injection、CWE-89

---

## 性能示例

### 糟糕反馈

> 这很慢。

### 良好反馈

> `[MAJOR]` `src/processor.py:88-140` —— O(n²) 嵌套循环
>
> **问题**：对 `orders` 中每个元素（n），遍历所有 `products`（m）。实际数据量（10k 订单 × 5k 产品 = 50M 次迭代）会造成严重延迟。
>
> ```python
> # O(n × m)
> for order in orders:
>     for product in all_products:
>         if order.product_id == product.id:
>             ...
> ```
>
> **修复**：
> ```python
> # O(n + m) —— 先索引产品
> product_map = {p.id: p for p in all_products}
> for order in orders:
>     product = product_map.get(order.product_id)
>     ...
> ```

---

## 正确性示例

### 糟糕反馈

> 这可能有 bug。

### 良好反馈

> `[MAJOR]` `src/batch.py:52` —— 潜在竞态条件
>
> **问题**：检查-然后-执行模式不是原子的。在检查与执行之间，另一个进程可能已修改状态。
>
> ```python
> # 非原子操作
> if not file.exists():
>     file.write(data)  # 可能已被另一个进程创建
> ```
>
> **修复**：
> ```python
> # 使用原子操作
> try:
>     with open(path, 'xb') as f:  # 排他性创建
>         f.write(data)
> except FileExistsError:
>     handle_conflict()
> ```

---

## 质量示例

### 糟糕反馈

> 你为什么没加测试？

### 良好反馈

> `[MINOR]` `src/discount.py:15-30` —— `calculateDiscount()` 有多个分支路径
>
> 能否为零数量和负价格添加边界测试以防回归？
>
> ```python
> def test_calculate_discount_zero_quantity():
>     assert calculateDiscount(0, 100) == 0
>
> def test_calculate_discount_negative_price():
>     with pytest.raises(ValueError):
>         calculateDiscount(5, -10)
> ```

---

## 架构示例

### 糟糕反馈

> 我会用另一种方式做。

### 良好反馈

> `[NIT]` 这个实现是正确的。
>
> 另一种方式是把重试逻辑提取为共享的 `withRetry()` 包装器 —— 但这是可选的，可作为未来优化。

---

## 可访问性示例

### 糟糕反馈

> 修一下可访问性。

### 良好反馈

> `[MAJOR]` `src/components/Modal.tsx:23` —— 缺少焦点管理
>
> **问题**：模态框打开时焦点未移入，关闭时未恢复。键盘用户可能被困在模态框外或内。
>
> **修复**：
> ```tsx
> // 打开时移入焦点
> useEffect(() => {
>   if (isOpen) {
>     firstFocusableRef.current?.focus();
>   }
> }, [isOpen]);
>
> // 关闭时恢复焦点
> const handleClose = () => {
>   triggerElementRef.current?.focus();
>   onClose();
> };
> ```

---

## 严重度标签快速参考

| 标签 | 含义 | 是否阻塞合并？ |
|------|------|-----------|
| `[CRITICAL]` | 安全漏洞、数据丢失、生产崩溃 | 是 |
| `[MAJOR]` | bug、逻辑错误、严重性能问题 | 是 |
| `[MINOR]` | 改进建议、降低维护成本 | 否 |
| `[NIT]` | 风格偏好、命名建议、小清理 | 否 |

---

## 应避免的行为

| 反模式 | 示例 | 替代做法 |
|--------|------|----------|
| 模糊 | "这不对" | 解释具体问题与后果 |
| 无方案 | "修一下" | 提供修复建议或代码 |
| 主观命令 | "不要这样做" | "你觉得...怎么样？" |
| 情绪化 | "这太糟糕了" | 评论代码不评论人 |
| 过度泛化 | "加测试" | 指明需要测试的场景 |

---

## 参考

- [report.md](report.md) —— 报告模板
- [../anti-patterns.md](../anti-patterns.md) —— 审查反模式
