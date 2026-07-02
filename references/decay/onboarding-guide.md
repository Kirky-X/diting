# 代码库入职指南

**目的：** 生成对新人友好的代码库导览。这不是诊断报告 — 没有 Health Score，没有 Iron Law 发现。专注于解释和导向。

---

## 流程

### 步骤 1：绘制领域地图

- 阅读顶层结构（同 architecture-guide 步骤 0）
- 输出：每个顶层模块做什么的通俗语言概述（每个一句话）
- 按层分组："用户交互的东西"、"业务逻辑"、"基础设施"

### 步骤 2：绘制依赖地图

绘制与架构审计步骤 1 相同的 Mermaid 依赖图，但按**推荐阅读顺序**着色节点，
使用与严重度调色板（使用红/黄/绿）不同的调色板
以避免混淆"红色 = 危险"和"红色 = 最后读"：

- 🔵 蓝色（`#339af0`）：从这里开始 — 入口点、核心领域
- 🟣 紫色（`#9775fa`）：接下来读 — 支持模块
- ⚪ 灰色（`#ced4da`）：最后读 — 基础设施、生成代码、工具

添加编号标签：`CoreModule["1. CoreModule"]`

```
classDef start fill:#339af0,color:#fff
classDef next fill:#9775fa,color:#fff
classDef last fill:#ced4da
```

### 步骤 3：突出关键约定

识别并记录代码库遵循的模式：
- 命名约定（文件命名、类命名、变量命名）
- 目录组织模式（基于功能？基于层？混合？）
- 错误处理模式（异常？结果类型？错误码？）
- 测试约定（共置？独立目录？命名模式？）
- 依赖注入模式（如果有）

### 步骤 4：标记危险区

对于每个已知复杂性或耦合问题的模块，添加简短警告：
- "OrderService：高复杂度，仅在完整测试套件运行时修改"
- "legacy/：无测试，修改前使用 Characterization Tests"

不要使用 Iron Law 格式 — 使用普通警告。这是导向，不是诊断。

### 步骤 5：构建领域词汇表

从代码中提取 10-15 个关键领域术语（类名、方法名、常量）并映射到通俗语言定义。这应用了 Evans 的 Ubiquitous Language 作为文档。

### 步骤 6：建议首批任务

基于依赖图，建议 2-3 个新开发者可以做出首次贡献的低风险区域：
测试覆盖良好、边界清晰、低耦合的模块。

---

## 输出模板

```
# Codebase Tour: [Project Name]

## Overview
[2-3 sentence summary of what the project does and its tech stack]

## Module Map
[Mermaid graph with reading-order colors]

## Module Guide
[One paragraph per top-level module: what it does, what it depends on, key files to read]

## Conventions
[Bullet list of patterns this codebase follows]

## Danger Zones
[Bullet list of areas to be careful with, or "None identified" if the codebase is clean]

## Domain Glossary
| Term | Meaning |
|------|---------|

## Suggested First Tasks
[2-3 concrete suggestions for a new developer's first PR]
```
