# 审查报告模板

## 输出模式

提供两种输出格式：

| 模式 | 使用场景 | 内容 |
|---|---|---|
| **详细** | 完整审查、PR 反馈 | 所有问题及完整上下文 |
| **简洁** | 快速检查、CI 集成 | 仅 Critical/High 问题 |

---

## 输出格式（详细）

报告时使用以下结构：

---

```markdown
## 🔍 Code Review Report

**Scope**: `<files or PR description>`  
**Language**: `<detected language(s)>`  
**Date**: `<today>`

---

### Summary

| Dimension | Issues Found | Highest Severity |
|---|---|---|
| 🔐 Security | N | 🔴 Critical / 🟠 High / etc. |
| ⚡ Performance | N | — |
| 🧹 Quality | N | — |
| 🏗️ Architecture | N | — |
| ✨ Simplification | N | — |
| **Total** | **N** | |

**Overall Score**: N / 100  
**Verdict**: ✅ Approved / ⚠️ Changes Requested / ❌ Rejected

---

### Issues

#### 🔴 Critical (N)

---

**[CRIT-001]** `src/auth.py:45` — SQL Injection  
**Confidence**: 97 | **Dimension**: Security

**Problem**: User input is directly concatenated into a SQL query without sanitization or parameterization. An attacker can manipulate the query to read, modify, or delete arbitrary data.

```python
# ❌ Vulnerable
query = "SELECT * FROM users WHERE name = '" + username + "'"
cursor.execute(query)
```

**Fix**:
```python
# ✅ Safe — use parameterized query
cursor.execute("SELECT * FROM users WHERE name = %s", (username,))
```

**Reference**: OWASP A03:2021 Injection, CWE-89

---

#### 🟠 High (N)

---

**[HIGH-001]** `src/processor.py:88-140` — O(n²) Nested Loop  
**Confidence**: 88 | **Dimension**: Performance

**Problem**: For each item in `orders` (n), you iterate over all `products` (m). For realistic data sizes (10k orders × 5k products = 50M iterations), this will cause severe latency spikes.

```python
# ❌ O(n × m)
for order in orders:
    for product in all_products:
        if order.product_id == product.id:
            ...
```

**Fix**:
```python
# ✅ O(n + m) — index products first
product_map = {p.id: p for p in all_products}
for order in orders:
    product = product_map.get(order.product_id)
    ...
```

---

#### 🟡 Medium (N)

*(same format as above)*

#### 🔵 Low (N)

*(same format as above)*

---

### Recommendations

1. **Immediate** (before any merge): Fix all 🔴 Critical issues
2. **This sprint**: Address 🟠 High issues
3. **Backlog**: 🟡 Medium and 🔵 Low items

---

### Verdict

- [ ] ✅ **Approved** — No blocking issues found
- [x] ⚠️ **Changes Requested** — Fix Critical / High before merge
- [ ] ❌ **Rejected** — Major rework required
```

---

## 评分计算

```
基础分：100
扣分：
  Critical 问题：每个 -15
  High 问题：    每个 -8
  Medium 问题：  每个 -3
  Low 问题：     每个 -1

下限：0（不能为负）
```

## 结论标准

| 结论 | 条件 |
|---|---|
| ✅ 通过 | 评分 ≥ 85，无 Critical 或 High 问题 |
| ⚠️ 需要修改 | 评分 60–84，或存在任何 Critical/High 问题 |
| ❌ 拒绝 | 评分 < 60，或系统性安全漏洞 |

## 问题 ID 约定

| 前缀 | 严重度 |
|---|---|
| `CRIT-` | Critical |
| `HIGH-` | High |
| `MED-` | Medium |
| `LOW-` | Low |
| `INFO-` | Info |

序号：`CRIT-001`、`CRIT-002`、`HIGH-001` 等

---

## 输出格式（简洁）

快速检查或 CI 集成时使用此格式 —— 仅 Critical 和 High 问题：

```markdown
## 🔍 Code Review Report (Concise)

**Scope**: `<files or PR description>`  
**Score**: N / 100 | **Verdict**: ⚠️ Changes Requested

---

### Blocking Issues (2)

| ID | Location | Issue | Confidence |
|---|---|---|---|
| CRIT-001 | src/auth.py:45 | SQL Injection | 97 |
| HIGH-001 | src/processor.py:88 | O(n²) Nested Loop | 88 |

---

**Fix Critical/High issues before merge.**
```

---

## 相关

- [review-workflow.md](../review-workflow.md)
- [commands/security.md](../commands/security.md)
