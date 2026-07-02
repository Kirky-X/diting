# 健康仪表板指南 — 模式 5

**目的：** 为代码库生成跨维度的健康仪表板。
每条发现必须遵循铁律：Symptom → Source → Consequence → Remedy。

---

## 分析流程

### 步骤 1：跨四个维度运行轻量级扫描

对于每个维度，使用 `_shared/` 中的 decay-risks 定义运行简化扫描。
不要阅读单个模式指南文件 — 使用下方的简化清单。每个维度最多 3 条发现；
对于 Debt：每个风险代码最多 2 条，所有风险代码合计最多 3 条。

**PR 维度（如果存在变更）：**
- 应用 Auto Scope Detection（common.md）
- 在 diff 中扫描 R2（Change Propagation）和 R1（Cognitive Overload）

**架构维度：**
- 收集代码库上下文：阅读顶层结构、入口点、import 语句
- 绘制 Mermaid 依赖图（遵循 common.md 中的标准图规则）
- 扫描 R5（Dependency Disorder）：循环依赖、向上流动、扇出 > 5
- 在输出中包含 Mermaid 图

**债务维度：**
- 跨代码库扫描所有六种衰退风险（R1-R6）
- 跳过 Pain × Spread 评分（仅使用严重度层级）

**测试维度：**
- 构建 Test Suite Map（单元/集成/E2E 计数）
- 在测试文件中扫描 T1（Test Obscurity）和 T2（Test Brittleness）

### 步骤 2：计算仪表板分数

每个维度有自己的 Health Score（基础 100，扣分规则同 common.md）。
综合分数 = 维度分数的加权平均：

| 维度 | 权重 | 理由 |
|-----------|--------|-----------|
| PR（代码质量） | 0.25 | 仅在存在变更时适用；无 diff 时跳过 |
| Architecture | 0.30 | 结构性问题具有最高爆炸半径 |
| Debt | 0.25 | 系统性但移动较慢 |
| Test | 0.20 | 支持性信号 |

如果 PR 维度被跳过（无变更），将其 0.25 权重按比例重新分配到其余三个维度，
每个剩余权重除以 (1 − 0.25) = 0.75。动态计算重新分配 — 不要硬编码值。

**重新分配的权重（PR 被跳过时）：**

| 维度 | 基础权重 | 重新分配权重 |
|-----------|------------|---------------------|
| Architecture | 0.30 | 0.30 / 0.75 = 0.40 |
| Debt | 0.25 | 0.25 / 0.75 = 0.33 |
| Test | 0.20 | 0.20 / 0.75 = 0.27 |

**评分规则（必须是确定性的 — 同一代码库的两次运行必须一致）：**

- 每个维度的分数从仪表板中显示的**已封顶**发现集计算
  （步骤 1 的封顶既限制显示内容也限制扣分 — 不要为超出封顶的发现扣分）。
- 在加权**之前**将每个维度分数下限设为 0。
- 没有发现的维度得 **100** 分 — 永远不跳过。**唯一**会被省略的维度是 PR，
  且仅当没有 diff 时（其权重随后被重新分配）。
- 将加权综合分数四舍五入到最接近的整数（半数向上）。

### 步骤 3：输出仪表板

使用下方的仪表板报告模板，而非标准的 common.md 模板。

---

## 仪表板报告模板

````markdown
# Decay Diagnosis — Health Dashboard

**Mode:** Health Dashboard
**Scope:** [project name or directory]
**Composite Score:** XX/100

| Dimension | Score | Top Finding |
|-----------|-------|------------|
| Code Quality | XX/100 | [one-line summary or "Clean"] |
| Architecture | XX/100 | [one-line summary or "Clean"] |
| Tech Debt | XX/100 | [one-line summary or "Clean"] |
| Test Quality | XX/100 | [one-line summary or "Clean"] |

## Module Dependency Graph
[Mermaid graph from architecture scan]

## Top Findings (max 5 across all dimensions)
[Standard Iron Law format, sorted by severity]

## Recommendation
[One paragraph: what to fix first, which dimension needs the most attention,
 suggest running the full individual skill for the worst dimension]
````
