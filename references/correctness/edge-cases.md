# 边界情况处理指南

边界情况处理模式 —— 系统化识别与处理边界条件

## 概述

边界情况是系统中最容易被忽视的区域，但往往导致最严重的问题。本文档提供系统化的边界情况识别与处理模式。

---

## 1. 集合边界情况

### 空集合

| 场景 | 错误处理 | 正确处理 |
|------|----------|----------|
| 迭代空集合 | 无问题 | 直接迭代，循环体不会执行 |
| 取第一个元素 | `items[0]` 抛异常 | `items[0] if items else default` |
| 求和/平均 | `sum([])` = 0，`mean([])` 抛异常 | 提前检查或返回默认值 |
| 最大/最小值 | `max([])` 抛异常 | `max(items, default=0)` |

### 单元素集合

```python
# 可能期望列表但得到单个元素
result = api.get_items()  # 可能返回 [item] 或 item

# 防御性处理
items = result if isinstance(result, list) else [result]
```

### 嵌套集合

```python
# 深层访问的风险
value = data.get('a', {}).get('b', {}).get('c')

# 更安全的替代方案
from functools import reduce
def safe_get(d, *keys, default=None):
    return reduce(lambda d, k: d.get(k, {}) if isinstance(d, dict) else default, keys, d) or default
```

---

## 2. 数值边界情况

### 零值

| 操作 | 风险 | 处理 |
|------|------|------|
| 除法 | 除零异常 | 检查或使用 try-except |
| 对数 | `log(0)` 未定义 | `log(max(x, epsilon))` |
| 取模 | `x % 0` 异常 | 先检查除数 |
| 幂运算 | `0 ** -1` 异常 | 边界检查 |

### 负值

```python
# 负数平方根
import math
result = math.sqrt(max(0, value))

# 负数取模
-7 % 3  # Python 中结果为 2，但其他语言可能不同
```

### 溢出

```python
# 整数溢出（Python 中不是问题，但其他语言需注意）
# C/Java: INT_MAX + 1 = INT_MIN

# 浮点数溢出
import math
if not math.isfinite(result):
    raise OverflowError("计算结果溢出")
```

### 浮点精度

```python
# 不要用 == 比较浮点数
0.1 + 0.2 == 0.3  # False！

# 使用 epsilon 比较
def approx_equal(a, b, epsilon=1e-9):
    return abs(a - b) < epsilon

# 货币计算使用 Decimal
from decimal import Decimal
price = Decimal('19.99')
tax = price * Decimal('0.08')
```

---

## 3. 字符串边界情况

### 空字符串

```python
# trim 后为空
username = input.strip()
if not username:
    raise ValidationError("用户名不能为空")

# 区分空字符串与 null
value = data.get('name')  # None vs "" vs "  "
if value is None:
    # 缺失
elif not value.strip():
    # 仅空白
```

### Unicode 边界情况

```python
# 字符串长度（字节 vs 字符 vs 码点）
text = "你好"
len(text)                    # 2（字符）
len(text.encode('utf-8'))    # 6（字节）

# Unicode 规范化
import unicodedata
text = unicodedata.normalize('NFC', text)  # 统一表示

# 零宽字符
invisible = text.strip('\u200b\ufeff')  # 移除零宽字符
```

### 编码问题

```python
# 始终显式声明编码
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# 处理编码错误
with open(path, 'r', encoding='utf-8', errors='replace') as f:
    content = f.read()
```

---

## 4. 时间边界情况

### 时区边界

```python
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

# 始终以 UTC 存储
dt = datetime.now(timezone.utc)

# 显示时转换
local = dt.astimezone(ZoneInfo('Asia/Shanghai'))
```

### 夏令时

```python
# 避免在 DST 边界做时间计算
# 使用 UTC 或无时区日期
from datetime import date
d = date(2024, 3, 10)  # 无时区问题
```

### 闰年/闰秒

```python
import calendar

# 闰年检查
calendar.isleap(2024)  # True

# 二月天数
days_in_feb = calendar.monthrange(2024, 2)[1]  # 29
```

---

## 5. 边界值清单

### 输入验证

```
Null 值（null、None、undefined）
空字符串（""、"   "）
空集合（[]、{}、set()）
零值（0、0.0、0j）
负值（-1、-0.001）
最大值（INT_MAX、FLT_MAX）
最小值（INT_MIN、FLT_MIN）
边界值（恰好等于阈值）
特殊字符（<、>、&、"、'）
Unicode 字符（emoji、CJK、零宽）
```

### 索引边界

```
第一个元素（索引 0）
最后一个元素（索引 len-1）
越界（索引 len、索引 -len-1）
负索引（索引 -1）
空切片（arr[0:0]）
全切片（arr[:]）
```

---

## 6. 边界情况测试模板

```python
import pytest

@pytest.mark.parametrize("input,expected", [
    (None, "default"),
    ("", "default"),
    ("   ", "default"),
    ("valid", "valid"),
    ("a" * 1000, "too_long"),
])
def test_edge_cases(input, expected):
    result = process(input)
    assert result == expected
```

---

## 参考

- [concurrency.md](concurrency.md) —— 并发边界情况
- [../commands/correctness.md](../commands/correctness.md) —— 正确性审查命令
