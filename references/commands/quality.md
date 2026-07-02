# 质量审查命令

质量审查模式 —— 代码坏味、复杂度、可维护性、测试覆盖

## 用法

```bash
review quality [target-path]
```

## 复杂度阈值

| 指标                     | 目标            | 审查    | 重构      |
| ------------------------ | --------------- | ------- | --------- |
| 圈复杂度（Cyclomatic）   | ≤ 7             | 8–10    | > 10      |
| 认知复杂度（Cognitive）  | ≤ 10            | 11–15   | > 15      |
| 方法/函数长度            | ≤ 30 行         | 31–50   | > 50      |
| 类/模块长度              | ≤ 200 行        | 200–300 | > 300     |
| 参数个数                 | ≤ 3             | 4       | > 4       |
| 嵌套深度                 | ≤ 3             | 4       | > 4       |
| 重复                     | < 3 次出现      | —       | ≥ 3       |

---

## 检查内容

### 代码坏味（高优先级）

```
□ 长方法（Long Method）—— 方法 > 50 行，或做多件事
□ 大类（Large Class）—— 类 > 300 行，或有多个不相关职责
□ 长参数列表 —— 函数 > 4 个参数（考虑参数对象）
□ 重复代码 —— 相同逻辑出现 ≥ 2 处
□ 深嵌套 —— if/for/while 嵌套 > 3 层（用 guard 子句）
□ 特性依恋（Feature Envy）—— 方法更多使用其他类的数据
□ 死代码 —— 不可达代码、未使用变量、未使用导入
□ 魔法数字/字符串 —— 未解释的字面量（用命名常量）
□ Switch/If-Else 链 —— 重复类型检查（考虑多态）
□ 过早泛化 —— 只有一个具体子类的抽象基类
```

### SOLID 原则

```
□ SRP：每个类/函数只有一个变更理由
□ OCP：通过添加代码扩展行为，而非修改已有
□ LSP：子类可替换父类而不破坏行为
□ ISP：接口小而聚焦；无客户端不需要的方法
□ DIP：高层模块依赖抽象，而非具体实现
```

### 错误处理

```
□ 异常具体（捕获 ValueError，而非 Exception）
□ 错误不被静默吞掉（至少记录日志）
□ 资源清理（try/finally 或 context manager/using/defer）
□ 错误信息有助于调试（含上下文，不仅是 "error occurred"）
□ 返回类型表明失败可能（Result<T>、Optional<T>、error return）
```

### 错误传播

```
□ 异步错误被捕获（await 周围 try/catch、promise 的 .catch()）
□ Promise 不被静默吞掉（总是 await 或 return）
□ 重新抛出时保留错误上下文（包装原始错误）
□ 错误边界正确设置（React、exception handler）
□ 重试逻辑有限制（最大次数、指数退避）
□ 超时错误显式处理
□ 网络错误与应用错误区分
```

### 状态一致性

```
□ 多步修改是事务性的
□ 部分失败可回滚
□ 重试幂等性保证
□ 并发更新冲突处理（乐观/悲观锁）
□ 需要时补偿最终一致性
□ 状态转换校验（状态机模式）
□ 孤立状态清理（后台任务、死信）
```

### 命名

```
□ 变量：描述其内容（userCount 而非 uc 或 n）
□ 函数/方法：动词短语描述其行为（getUserById，而非 getUser）
□ 布尔变量/函数：is/has/can 前缀（isActive、hasPermission）
□ 无脱离明确上下文的单字母变量（循环索引 i、坐标 x/y 除外）
□ 文件/模块内命名约定一致（camelCase vs snake_case）
□ 无误导性命名（doNothing 函数实际做事）
```

### 测试

```
□ 核心业务逻辑有单元测试
□ 测试描述行为，而非实现（测什么不测怎么）
□ 测试独立（测试间无共享可变状态）
□ 测试名描述性（test_user_registration_rejects_duplicate_email）
□ 边界条件覆盖（空输入、null/None、最大值、错误路径）
□ 外部依赖用 Mock（DB、HTTP、文件系统）
□ 新代码覆盖率 ≥ 80%
```

### 文档

```
□ 公共 API（函数、类、模块）有 docstring / JSDoc
□ 复杂算法有内联注释解释为什么（而非是什么）
□ TODO 有上下文：谁、为什么、可选工单引用
□ README 覆盖：安装、使用、如何运行测试
```

---

## 语言专属检查

### Python

- 函数签名有类型注解（PEP 484）
- f-string 优于 `.format()` 或 `%` 格式化
- 有公共 API 的模块定义 `__all__`
- 结构化数据用 dataclass 或 attrs，而非纯 dict

### TypeScript / JavaScript

- 严格 TypeScript 配置（`strict: true`）
- 无显式理由不使用 `any` 类型
- `const` 优于 `let` 优于 `var`
- 可选链 `?.` 和空值合并 `??` 优于冗长 null 检查

### Java

- `Optional<T>` 代替返回 null
- 纯数据类用 Record（Java 14+）
- 集合转换优先用 Stream
- 明显类型用 `var`（Java 10+）

### Go

- 错误处理：总是检查错误，不用 `_`
- 命名返回值有意使用，而非默认
- 接口在消费包中定义（依赖倒置）
- 可取消操作用 `context.Context` 作为首个参数

---

## 参考

- [code-smells.md](../quality/code-smells.md) — 完整代码坏味目录
- [quality-standards.md](../quality/quality-standards.md) — 命名和格式标准
- [design-pattern-review.md](../architecture/design-pattern-review.md) — GoF 模式 + 选择指南 + code-smell→pattern 反向查找
- [security-checklist.md](../quality/security-checklist.md) — 安全质量检查清单

## 相关命令

- [security.md](security.md)
- [performance.md](performance.md)
- [architecture.md](architecture.md)
- [simplification.md](simplification.md)
