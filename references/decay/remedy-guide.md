# 修复指南 — 可执行修复模式

当 `--fix` 激活时，增强每条发现的 Remedy 字段使其直接可执行：

## 修复增强规则

对于每条发现，Remedy 必须包含：
1. **目标**：确切文件路径和函数/类名
2. **行动**：具体的重构操作（例如，"将 45-67 行抽取为新函数 `calculateShippingCost(items, config)`"）
3. **理由**：一句话解释为何采用此特定修复（不只是"重构"）

## 可修复性分类

写完增强的 Remedy 后，对每条发现分类：

| 层级 | 标准 | 报告标签 |
|------|---------|-------------|
| 快速修复 | 单文件、机械操作：重命名、抽取常量、重排 import | `[quick-fix]` |
| 引导修复 | 需要设计选择：在哪里拆分、接口形状如何 | `[guided]` |
| 手动修复 | 跨模块、需要领域知识或团队讨论 | `[manual]` |

将标签追加到发现标题：`**R1 — Long function in OrderService [quick-fix]**`

## 输出附加

在标准报告之后，添加 **Fix Summary** 部分：

| 发现 | 层级 | 目标文件 | 行动 |
|---------|------|------------|--------|
| R1 — Long function | quick-fix | src/order.ts:45 | 抽取 `calculateTotal()` |
| R5 — Circular dep | manual | src/models/ ↔ src/services/ | 引入接口边界 |

## 不应做的事
- 不要修改任何文件。阶段 1 仅诊断 + 可执行计划。
- 不要生成 diff 或代码块。Remedy 文本本身就是交付物。
- 不要重新评分。Health Score 反映当前状态，不是预期状态。
