# 审查工作流 —— 完整审查流程

## 概述

全面代码审查：多维度并行分析 + 置信度评分 + 统一报告。

提供两种审查模式：
- **并行分析** —— AI Agent 自动化流程，快速且一致
- **三遍审查** —— 人工审查者系统化扫描，全面且深入

---

## 工作流模式

| 模式 | 适用场景 | 优势 | 参考 |
|---|---|---|---|
| 并行分析 | AI Agent、自动化流程 | 快速、一致 | 本文档 |
| 三遍审查 | 人工审查者、学习过程 | 全面、系统 | [workflow/three-pass-review.md](workflow/three-pass-review.md) |

### 组合使用

```
1. AI 并行分析生成初始报告
2. 人工三遍审查确认并补充
3. 合并输出最终审查报告
```

---

## 阶段 1：审查前清单

```
□ 识别语言和运行时
□ 阅读 CLAUDE.md / .editorconfig / lint 配置了解项目标准
□ 确定变更范围（PR diff 还是完整代码库）
□ 检查是否存在测试（影响置信度评分）
□ 记录任何明确声明的约束或优先级
```

---

## 阶段 2：并行分析（5 个 Agent）

独立执行全部 5 个维度，然后合并发现项：

| Agent | 关注点 | 关键参考 |
|---|---|---|
| **安全** | OWASP Top 10 (2021)、CWE、认证、加密、密钥 | [commands/security.md](commands/security.md) |
| **性能** | Big-O、数据库查询、缓存、异步、Web Vitals | [commands/performance.md](commands/performance.md) |
| **质量** | 代码坏味、SOLID、复杂度、测试覆盖率 | [commands/quality.md](commands/quality.md) |
| **架构** | 模式、耦合、内聚、依赖 | [commands/architecture.md](commands/architecture.md) |
| **简化** | 可读性、重复、死代码、命名 | [commands/simplification.md](commands/simplification.md) |

---

## 阶段 3：评分与过滤

对每个发现项：

```
1. 分配严重度：Critical / High / Medium / Low / Info
2. 评分置信度：0–100
3. 过滤：丢弃 < 80 的项
4. 去重：合并指向同一根因的发现项
5. 排序：Critical 优先，然后 High、Medium、Low、Info
```

### 置信度校准

评分时使用以下锚点：

| 场景 | 置信度 |
|---|---|
| 代码中硬编码密码 | 98 |
| 用户输入直接拼接 SQL 字符串 | 95 |
| 大数据集上的 O(n²) 嵌套循环 | 85 |
| 缺少 null 检查（语言无 null 安全） | 80 |
| 方法 60 行（阈值 50） | 75 —— 边界 |
| 可能的竞态条件（并发模型不明确） | 55 —— 上下文确认前跳过 |
| 命名可以改进 | 40 —— 跳过 |

---

## 阶段 4：生成报告

遵循 [templates/report.md](templates/report.md) 中的模板。

### 报告必须包含

1. **执行摘要** —— 评分、文件数、按严重度统计的问题数
2. **问题表** —— ID、file:line、严重度、置信度、简要描述
3. **单问题详情** —— 问题说明、风险、带代码的具体修复建议
4. **结论** —— 通过 / 需要修改 / 拒绝

---

## 审查优先级

```
1. 安全         → 始终最高。绝不跳过。
2. 正确性       → 功能性 bug、数据完整性
3. 性能         → 仅显著影响（≥ High 严重度）
4. 质量         → 可维护性、测试覆盖率
5. 简化         → 最低。时间紧张时跳过。
```

---

## 误报减少

报告问题前，验证：

- [ ] 项目是否已在其他地方处理？（如中间件认证、ORM 转义）
- [ ] 是否存在抑制它的 lint 规则或注解？
- [ ] CLAUDE.md 是否明确允许此模式？
- [ ] 此代码路径是否实际可达 / 被执行？
- [ ] 该项目的资深开发者是否会认同这是真实问题？

---

## 特殊场景

### PR / Diff 审查
- 仅关注变更行
- 考虑周围未变更代码的上下文
- 检查测试是否覆盖新代码路径

### 单文件审查
- 全面分析所有维度
- 记录缺失项（测试、类型、错误处理）

### 完整代码库审查
- 每模块抽样代表性文件
- 关注架构和横切关注点
- 报告系统性模式而非个别出现

---

## 相关

- [commands/security.md](commands/security.md)
- [commands/performance.md](commands/performance.md)
- [commands/quality.md](commands/quality.md)
- [commands/architecture.md](commands/architecture.md)
- [commands/simplification.md](commands/simplification.md)
- [templates/report.md](templates/report.md)
