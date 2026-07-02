---
name: diting
description: "代码质量审查套件。触发：review/audit/tech debt/over-engineering/simplify/agent 审计；或任意 write/add/refactor/fix 任务"
license: MIT
---

# 代码审查套件 — 三个引擎，一个 Skill

本 skill 融合了三个原本独立的工具包。每个引擎保留自己的分析方法（它们解决不同的问题，强制统一格式会丢失信息），但共享一个入口、一个模式表，以及 — 默认全量审查场景下 — 一份合并报告。

| 引擎                            | 回答的问题                                              | 输出风格                                                                                                                                              | 来源                                                                                                           |
| ------------------------------- | ------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------- |
| **A. 维度审查 (Dimensional)**   | "代码是否正确、安全、快速、设计良好？"                  | 严重度+置信度评分问题列表，100 分制评分，Approved/Changes/Rejected 裁决                                                                               | `references/commands/*`, `references/{security,performance,quality,architecture,correctness,simplification}/*` |
| **B. 腐化诊断 (Decay)**         | "为什么这段代码维护痛苦？哪条书本原则能解释？"          | Symptom → Source → Consequence → Remedy 发现项，Health Score，模块依赖图                                                                              | `references/decay/*`                                                                                           |
| **C. 简化与精炼 (Simplicity)**  | "代码是否超出问题所需？是否足够清晰？"                  | Ladder（写代码前，最小优先）· 删除清单（`tag: what to cut`，仅报告）· 精炼 pass（事后清晰度编辑，保留行为）                                            | `references/simplicity/*`                                                                                      |

只读取某个模式所需的 reference 文件 — 不要预加载全部三个引擎。

**TL;DR 路由**：审查/报告代码 → Engine A（指定维度）或 Engine B（全代码库/腐化框架）或融合的 Full Review（未指定维度）。写/编辑代码 → 写时用 Ladder，之后用 Refinement Pass。只想要删除清单、不编辑 → Over-engineering Review/Audit。完整细节见下文。

## 步骤 1 — 路由请求

| 用户说…                                                                        | 模式                                 | 引擎   | 参考                                                                                                                                            |
| ------------------------------------------------------------------------------ | ------------------------------------ | ------ | ----------------------------------------------------------------------------------------------------------------------------------------------- |
| `review`（无参数）                                                             | **Full Review**（融合）              | A+B+C  | 见下文 "Full Review"                                                                                                                             |
| `review security`                                                              | Security                             | A      | [commands/security.md](references/commands/security.md)                                                                                         |
| `review performance`                                                           | Performance                          | A      | [commands/performance.md](references/commands/performance.md)                                                                                   |
| `review quality`                                                               | Quality                              | A      | [commands/quality.md](references/commands/quality.md)                                                                                           |
| `review architecture`                                                          | Architecture                         | A      | [commands/architecture.md](references/commands/architecture.md)                                                                                 |
| `review simplification`                                                        | Simplification                       | A      | [commands/simplification.md](references/commands/simplification.md)                                                                             |
| `review api`                                                                   | API                                  | A      | [commands/api.md](references/commands/api.md)                                                                                                   |
| `review database`                                                              | Database                             | A      | [commands/database.md](references/commands/database.md)                                                                                         |
| `review testing`                                                               | Testing                              | A      | [commands/testing.md](references/commands/testing.md)                                                                                           |
| `review documentation`                                                         | Documentation                        | A      | [commands/documentation.md](references/commands/documentation.md)                                                                               |
| `review i18n`                                                                  | i18n                                 | A      | [commands/i18n.md](references/commands/i18n.md)                                                                                                 |
| `review accessibility`                                                         | Accessibility                        | A      | [commands/accessibility.md](references/commands/accessibility.md)                                                                               |
| `review correctness`                                                           | Correctness                          | A      | [commands/correctness.md](references/commands/correctness.md)                                                                                   |
| `review agent`                                                                 | Agent（12-factor 审计）              | A      | [commands/agent.md](references/commands/agent.md)                                                                                               |
| `review diff`                                                                  | Diff Review                          | A      | [commands/diff-review.md](references/commands/diff-review.md)                                                                                   |
| `review pre-commit`                                                            | Pre-commit                           | A      | [commands/pre-commit.md](references/commands/pre-commit.md)                                                                                     |
| `review batch`                                                                 | Batch Review                         | A      | [commands/batch-review.md](references/commands/batch-review.md)                                                                                 |
| "audit this codebase"、"does this follow clean architecture"、"codebase tour"   | Architecture Audit                   | B      | [decay/architecture-guide.md](references/decay/architecture-guide.md)（+ [onboarding-guide.md](references/decay/onboarding-guide.md) 用于 tour） |
| "tech debt"、"what should we fix first"、"refactoring roadmap"                  | Tech Debt Assessment                 | B      | [decay/debt-guide.md](references/decay/debt-guide.md)                                                                                           |
| "our tests keep breaking"、"too many mocks"、test-suite review                  | Test Quality Review                  | B      | [decay/test-guide.md](references/decay/test-guide.md)                                                                                           |
| "how healthy is this codebase"、"run all the checks"                            | Health Dashboard                     | B      | [decay/health-guide.md](references/decay/health-guide.md)                                                                                       |
| "fix everything"、"sweep the codebase"、"auto-fix all issues"                   | Full Sweep & Auto-Fix ⚠️ 写代码       | B      | [decay/sweep-guide.md](references/decay/sweep-guide.md)                                                                                         |
| "review for over-engineering"、"what can we delete"、"is this over-engineered"  | Over-engineering Review（diff）      | C      | [simplicity/overengineering-review.md](references/simplicity/overengineering-review.md)                                                         |
| "audit for over-engineering"、"find bloat"、repo-wide                           | Over-engineering Audit               | C      | [simplicity/overengineering-audit.md](references/simplicity/overengineering-audit.md)                                                           |
| "what did we mark to do later"、"list the shortcuts"                            | Debt Ledger（`lazy:` 注释）          | C      | [simplicity/debt-ledger.md](references/simplicity/debt-ledger.md)                                                                               |
| "clean this up"、"make this more readable/consistent"、"refine/polish this"     | Refinement Pass                      | C      | [simplicity/refinement-pass.md](references/simplicity/refinement-pass.md)                                                                       |
| "be lazy"、"minimal solution"、"yagni"、写/编辑代码                             | Simplicity Lens（ambient）           | C      | [simplicity/ladder.md](references/simplicity/ladder.md)                                                                                         |

**Fallback 与范围确认**：未知模式 / 无参数 → Full Review。模糊请求（"check this"）→ 询问：单文件 · PR diff · 全代码库。缺失目标路径 → 询问，绝不臆造。全代码库或批量扫描前，与用户确认目标路径 + 维度清单。

**"Simplify this" 歧义消解**（Engine C 的三个模式共享词汇 — 按用户想做什么消解，不按关键词）：

- 想要**待删除清单**、代码不动（"what can I delete"、"is this over-engineered"、"review for over-engineering"）→ Over-engineering Review/Audit。仅报告，从不编辑代码。
- 正在**写新代码**，或明确想要最简/最短方案（"be lazy"、"yagni"、"minimal solution"）→ Ladder（ambient）。直接编辑，偏向能用得起来的最少代码。
- 想要**已有/刚写的代码更清晰**，不一定更短（"clean this up"、"make this more readable/consistent"、"refine this"）→ Refinement Pass。直接编辑，但此处清晰度优先于简洁 — 与 Ladder 相反的偏向。
- 确实不清楚是哪个 → 问一行："想要待删除清单、最短版本，还是只是更清晰/更易读？"

**"Architecture" 歧义消解**（Engine A 和 Engine B 都覆盖架构，范围不同）：

- 范围限定于**当前 diff/PR**（"does this PR's design make sense"、`review architecture`）→ Engine A [commands/architecture.md](references/commands/architecture.md)。
- 范围是**整个代码库的模块结构**（"audit the architecture"、"why does everything depend on everything"、依赖图）→ Engine B [decay/architecture-guide.md](references/decay/architecture-guide.md)。
- 两者都请求，或小 diff 上范围不清 → 默认 Engine A（更便宜，匹配声明的范围）；将 Engine B 的全代码库审计作为后续选项提及，而非未请求就同时跑两个。

## 检查点

以下情况先询问再继续：

1. **Full Sweep** — 唯一会在整个代码库上未经提示就写文件的模式。展示 [decay/sweep-guide.md](references/decay/sweep-guide.md) Step 0 的事前同意提示，等待一次性批准，然后免手干预运行。
2. **全代码库或批量扫描**（任何其他模式）— 先确认目标路径和维度清单（见上方步骤 1 fallback）。
3. **确实模糊的路由** — "Simplify this" 或 "Architecture" 请求无法清晰映射到某个模式（见上方歧义消解）。

其他所有模式（Full Review、单维度审查、Ladder、Refinement Pass）只触碰用户本轮正在问的代码 — Full Sweep 之外不会有未经提示的全代码库编辑。

## 步骤 2 — 收集上下文（所有引擎）

1. 语言、项目类型（service / CLI / library / frontend / pipeline）
2. 范围：单文件、PR diff、或全代码库 — 用户未指定时见 [decay/common.md](references/decay/common.md) 的 Auto Scope Detection
3. 项目标准：`CLAUDE.md`、`.eslintrc`、`pyproject.toml`，以及 — 对 Engine B — `.decay-review.yaml` 配置（disable/severity/ignore/focus/strictness 覆盖，见 [decay/common.md](references/decay/common.md)）

## 步骤 3 — 执行

### 单维度 / 单引擎模式

直接跟随链接的 reference 文件；它是自包含的。Engine A 文件（`commands/*.md`）使用下方的置信度+严重度模型。Engine B 文件总是以 "Read `decay/common.md` for the Iron Law, config, report template, and Health Score" 开头 — 先做这个。Engine C 文件短且自包含。

### Full Review（默认，融合输出）

用户要求无维度名的普通审查时，跑全部三个引擎并合并为**一份**报告：

1. **Engine A** — 扫描 security、performance、quality、architecture、simplification（[review-workflow.md](references/review-workflow.md) 的五个默认维度），找具体、定位清晰的问题。用 Confidence（0–100，仅报告 ≥80）和 Severity（Critical/High/Medium/Low）逐项评分。
2. **Engine B** — 同范围内跑 PR-Review decay scan（[decay/pr-review-guide.md](references/decay/pr-review-guide.md)）：Six Decay Risks（R1–R6），每条写成 Symptom → Source → Consequence → Remedy。应用 [decay/common.md](references/decay/common.md) 的 Iron Law：禁止无诊断后果就陈述修复方案。
3. **Engine C** — 仅做一次过度工程 pass，使用 [simplicity/overengineering-review.md](references/simplicity/overengineering-review.md) 的 tag（`delete:` `stdlib:` `native:` `yagni:` `shrink:`）。范围受限 — correctness/security/performance 留在 Engine A，此处不重复。
4. **Merge**：用 [templates/report.md](references/templates/report.md) 的报告骨架作为外壳（Summary 表、Overall Score、Verdict），但给 Engine B 发现项单独开一个 `### 🧬 Decay Risks` 子章节（S→S→C→R 格式，不塞进 Engine A 的 Problem/Fix 格式 — 推理链才是重点），给 Engine C 发现项单独开一个 `### ✂️ Simplification Opportunities` 子章节（每条一行，结尾 `net: -N lines possible`）。
5. **Score**：按 [templates/report.md](references/templates/report.md) 计算 Engine A 的 Overall Score（100 − 扣分）作为头牌分数。Engine B 的 Health Score 作为第二个数字并列报告（两者权重不同 — Health Score 惩罚腐化风险，而非 bug — 不要平均它们）。Engine C 无独立分数；其 net-lines 数字单独呈现。
6. **Verdict**：仅由 Engine A 的 Critical/High 发现项驱动（按 [templates/report.md](references/templates/report.md) 的表格）。Decay risk 和 simplification opportunity 进入 Summary，但从不单独阻断 verdict — 它们是可维护性信号，不是缺陷。

### 写或编辑代码（非审查）

按 [simplicity/ladder.md](references/simplicity/ladder.md) ambient 应用 Ladder：写代码前爬梯子（YAGNI → 复用 → 标准库 → 原生 → 现有依赖 → 一行 → 最简），用 `lazy:` 注释标记刻意捷径并命名天花板和升级触发条件，未请求的解释最多三行。无论是否请求审查都适用 — 它治理代码怎么写，不只是怎么打分。绝不简化掉输入验证、错误处理、安全或可访问性。退出开关："stop simplify" / "normal mode" 在剩余 session 禁用 Ladder；用 "simplify" 或点名级别（`lite`/`full`/`ultra`）重新启用。若用户说 "just fix this, don't refactor" 或类似，本轮跳过 Ladder 的重塑 — 只做要求的最小修复，不多做；Ladder 治理新代码，不是改写没人要求碰的工作代码的命令。

**然后，在呈现结果前**，静默对刚写的代码跑 Refinement Pass（[simplicity/refinement-pass.md](references/simplicity/refinement-pass.md)）— 检查命名、嵌套、项目惯例契合度，修值得修的。范围护栏：只触碰刚写或明确指向的行；若真实修复需要触碰无关的已有代码，点名它而非静默扩大 diff。这是唯一一个与 Ladder 反向的检查：Ladder 偏向最少代码，Refinement Pass 偏向最清晰代码，第二次 pass 能抓住第一次走过头的地方（一行密集到确实难读、合并了本应分开的关注点）。除非确实改了东西，否则不说。

## Reference 索引

```
references/
├── review-workflow.md, anti-patterns.md        — Engine A 共享工作流
├── commands/*.md                                — Engine A，16 个维度指南
├── security/ performance/ quality/ correctness/
│   architecture/ simplification/                — Engine A 深度材料
├── security/security-design-patterns.md         — 安全模式目录
│                                                    (arch/design/impl 层，STRIDE→pattern)
├── templates/report.md, feedback-examples.md    — Engine A + 融合报告外壳
├── workflow/three-pass-review.md                — Engine A 方法论
├── decay/common.md                              — Engine B 核心：Iron Law、配置、
│                                                    报告模板、Health Score、
│                                                    历史追踪、triage
├── decay/decay-risks.md, test-decay-risks.md,
│   source-coverage.md, custom-risks-guide.md,
│   remedy-guide.md                              — Engine B 风险定义
├── decay/{architecture,debt,pr-review,sweep,
│   health,test,onboarding}-guide.md             — Engine B 各模式流程
├── simplicity/ladder.md                         — Engine C：最小优先梯子
├── simplicity/overengineering-review.md         — Engine C：diff 范围删除清单
├── simplicity/overengineering-audit.md          — Engine C：repo 范围删除清单
├── simplicity/refinement-pass.md                — Engine C：事后清晰度编辑
└── simplicity/debt-ledger.md                    — Engine C：`lazy:` 注释账本

scripts/
├── analyzer.py           — 静态分析助手（Engine A）
├── security_check.py     — 基于模式的安全扫描（Engine A）
└── parallel_review.py    — fan-out 多维度审查（Engine A）；它按维度加载的
                             reference 路径在此次合并后仍然有效
```

## 备注

- Engine B 的 `.decay-review.yaml` 配置（disable/severity/ignore/focus/strictness）与 Ladder 的强度级别（`lite`/`full`/`ultra`）是独立设置 — 一个项目可以同时设置两者而不冲突。
- Engine B 的历史追踪（`.decay-review-history.json`）与 Engine C 的 debt ledger（`SIMPLIFY-DEBT.md`）是分开的产物；不要合并它们。
- Engine A 没有自己的配置文件，总是跑默认维度；Engine B 的 `.decay-review.yaml` 只作用于 Engine B。若项目在 `.decay-review.yaml` 中禁用了某个风险（如 architecture decay），但同一关注作为 Engine A 发现项出现（如 `review architecture`），在那里正常报告 — 配置只静音 Engine B 自己的发现项，不抑制 Engine A。
- Refinement Pass 是最新的 Engine C 模式：它在事后为清晰度编辑代码，而非事先决定写多少代码（Ladder）或列出删除什么（Over-engineering Review/Audit）。把它当作另外两个的平衡检查，不是第四个独立引擎。
