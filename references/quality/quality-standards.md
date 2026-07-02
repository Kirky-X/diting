# 代码质量标准

## 1. 命名规范

### 变量命名

| 类型 | 风格 | 示例 |
|------|------|------|
| 局部变量 | 小写带下划线 | `user_name`、`total_count` |
| 常量 | 大写下划线 | `MAX_RETRIES`、`DEFAULT_TIMEOUT` |
| 实例变量 | 小写下划线或驼峰 | `user_id` / `userId` |
| 类变量 | 小写下划线 | `_cache`、`instances` |

### 函数/方法命名

- 以动词开头：`get_user()`、`create_order()`、`validate_input()`
- 布尔值使用 `is_`、`has_`、`can_` 前缀：`is_valid()`、`has_permission()`
- 避免无意义名称：`do_stuff()`、`process_data()`

### 类命名

- 帕斯卡命名：`UserService`、`OrderProcessor`、`PaymentGateway`
- 避免过度使用后缀：`Manager`、`Handler`、`Utils`（仅在必要时使用）

### 文件命名

| 语言 | 风格 | 示例 |
|------|------|------|
| Python | 小写下划线 | `user_service.py` |
| JavaScript | 驼峰或短横线 | `userService.js` / `user-service.js` |
| Java | 帕斯卡 | `UserService.java` |
| Go | 小写下划线 | `user_service.go` |

## 2. 代码格式

### 缩进

- **Python**：4 空格
- **JavaScript/TypeScript**：2 空格
- **Java/Go/Rust**：4 空格或 2 空格（项目内保持一致）
- **禁止使用 Tab 字符**

### 行长度

- **最大 120 字符**
- 理想情况不超过 80 字符

### 空格

- 运算符两侧加空格：`a + b` 而非 `a+b`
- 逗号后加空格：`func(a, b)` 而非 `func(a,b)`
- 括号内不加空格：`func(a)` 而非 `func( a )`

### 空行

- 类之间：2 空行
- 方法之间：1 空行
- 逻辑段之间：1 空行

## 3. 注释标准

### 必需注释

- **复杂算法**：解释算法思路
- **业务规则**：描述业务背景
- **临时方案**：解释为何如此处理
- **未完成工作**：使用 TODO 标记

### 注释风格

```python
# 单行注释（Python）
def calculate_tax(amount):
    # 税率根据收入水平动态计算
    if amount > 100000:
        return amount * 0.2
    return amount * 0.1
```

```java
// 单行注释（Java）
public class TaxCalculator {
    /**
     * 计算税额
     * @param amount 金额
     * @return 税额
     */
    public double calculate(double amount) {
        // 超过 10 万的金额适用 20% 税率
        if (amount > 100000) {
            return amount * 0.2;
        }
        return amount * 0.1;
    }
}
```

### 禁止的注释

- 解释显而易见的代码：`i++ // i 自增`
- 过期注释
- 注释掉的代码（使用版本控制）
- 以注释替代好代码

## 4. 函数标准

### 参数数量

- **最多 4 个参数**
- 超过 4 个应封装为对象或使用选项对象

### 返回值

- **单一出口**：减少多个 return
- **明确返回类型**：避免混合返回类型
- **错误处理**：使用异常或返回 Result 类型

### 函数长度

| 复杂度 | 行数范围 | 描述 |
|--------|----------|------|
| 简单 | 1-10 | 原子操作 |
| 中等 | 10-30 | 单一职责 |
| 复杂 | 30-50 | 需要审查 |
| 过长 | >50 | 需要重构 |

## 5. 错误处理

### 异常原则

- **使用具体异常**：避免捕获 `Exception`
- **不要吞掉异常**：至少记录日志
- **清理资源**：使用 try-finally 或 with 语句
- **暴露异常接口**：转换内部异常

### 错误示例

```python
# 错误示例
try:
    data = json.loads(body)
except:
    pass  # 静默失败

# 正确示例
try:
    data = json.loads(body)
except json.JSONDecodeError as e:
    logger.error(f"JSON 解析失败: {e}")
    raise ValidationError("无效的 JSON 格式")
```

## 6. 测试要求

### 测试覆盖率

| 组件 | 最低覆盖率 | 推荐覆盖率 |
|------|------------|------------|
| 核心业务逻辑 | 80% | 90% |
| 新功能 | 70% | 85% |
| Bug 修复 | 100% | 100% |

### 测试原则

- **测试行为而非实现**
- **使用描述性测试名**
- **保持测试快速**
- **隔离外部依赖**
- **使用 Given-When-Then 模式**

### 测试示例

```python
def test_user_registration_with_valid_input():
    # Given（前置条件）
    user_data = {"email": "test@example.com", "password": "secure123"}

    # When（执行操作）
    result = UserService.register(user_data)

    # Then（验证结果）
    assert result.status == "success"
    assert result.user.email == "test@example.com"
    assert mock_email.called
```

## 7. Git 提交标准

### 提交信息格式

```
<类型>(<范围>): <描述>

[可选正文]

[可选页脚]
```

### 类型标准

| 类型 | 描述 | 示例 |
|------|------|------|
| feat | 新功能 | feat(user): 添加用户注册 |
| fix | Bug 修复 | fix(auth): 修复登录漏洞 |
| docs | 文档更新 | docs: 更新 README |
| style | 代码格式 | style: 格式化代码 |
| refactor | 重构 | refactor(payment): 重构支付逻辑 |
| test | 测试 | test: 添加单元测试 |
| chore | 构建/工具 | chore: 更新依赖 |

### 提交示例

```
feat(auth): 实现双因素认证

- 添加 TOTP 验证
- 生成恢复码
- 更新用户设置页

Closes #123
```

## 8. 代码审查标准

### 必须通过

- [ ] 所有测试通过
- [ ] 无严重安全问题
- [ ] 代码风格遵循规范
- [ ] 必要的文档更新
- [ ] 不破坏现有功能

### 应包含

- [ ] 有意义的测试
- [ ] 无显著性能回退
- [ ] 考虑边界情况
- [ ] 完整的错误处理

### 审查重点

1. **正确性**：代码是否正确解决问题？
2. **安全性**：是否存在安全风险？
3. **可读性**：代码是否易于理解？
4. **可维护性**：未来修改是否方便？
5. **测试**：是否有充分的测试？
