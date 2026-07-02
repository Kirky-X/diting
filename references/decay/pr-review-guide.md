# PR Review 指南 — 模式 1

**目的：** 分析代码 diff 或特定文件，识别变更代码中直接可见的衰退风险。每条发现必须遵循铁律：Symptom → Source → Consequence → Remedy。

---

## 开始之前

**自动生成的文件：** 如果 diff 包含生成文件（protobuf 桩、OpenAPI 客户端、ORM 迁移、lock 文件、压缩 bundle），完全跳过这些文件。生成代码反映工具选择，不是开发者决策。在报告中记录哪些文件被跳过及原因。

**范围校准：** 开始前根据 PR 大小调整分析深度。

| PR 大小 | 方法 |
|---------|----------|
| < 50 行 | 仅关注步骤 1–3；仅在 import 变更时运行步骤 6a；如果任何类、方法或变量被重命名或引入则运行步骤 6b |
| 50–300 行 | 完整流程，所有步骤 |
| > 300 行 | 完整流程；在 Scope 行中记录审查为采样 — 覆盖最高风险区域而非每个文件 |

对于 > 500 行的 PR：在 Summary 中标记此大小的 PR 本身就是一个 Change Propagation 信号。无法一次性审查的变更暗示职责纠缠。

---

## 分析流程

按顺序完成以下七个步骤。不要跳过步骤。

### 步骤 1：理解范围

阅读 diff 或文件并回答：
- 此变更的声明目的是什么？
- 修改了哪些文件？
- 如果 PR 修改超过 10 个不相关文件 — 立即标记 — 这本身是一个
  🟡 Warning：Change Propagation（触及许多不相关事情的 PR 是
  职责纠缠的信号）。

### 步骤 2：扫描 Change Propagation

*首先扫描此项 — 它是 diff 中最可见的风险。*

寻找：
- 此变更是否触及与声明目的没有概念联系的模块中的文件？
- 任何被修改的类是否在此 diff 中因多个业务原因而变更？
- 任何方法是否从另一个类使用的数据多于从自己类使用的数据？

如果 diff 没有显示超出功能所需的跨模块变更 → 跳过，无发现。

### 步骤 3：扫描 Cognitive Overload

寻找：
- 任何新增或修改的函数是否超过 20 行？
- 新增或修改代码中是否有超过 3 层的嵌套？
- 任何新函数签名中是否有超过 4 个参数？
- 新代码中是否有魔法数字或未解释的常量？
- 新的变量或函数名是否需要阅读实现才能理解？
- 是否有火车残骸链（3+ 方法调用链）？

### 步骤 4：扫描 Knowledge Duplication

寻找：
- 此变更是否引入了代码库中已存在的逻辑？
- 此变更是否为已有名称的概念引入了新名称？
- 此变更是否在某个层次中添加了一个类，而该层次在另一个模块中有并行对应？

### 步骤 5：扫描 Accidental Complexity

寻找：
- 此变更是否添加了只有一个具体用途的抽象？
- 此变更是否添加了只包装另一个类或委托一切的类？
- 此变更是否添加了不服务于当前需求的配置选项或扩展点？

### 步骤 6a：扫描 Dependency Disorder

- 任何新 import 是否创建了从高层模块到低层模块的依赖？
  （例如，领域服务现在 import 了数据库驱动或 HTTP 客户端）
- 任何新 import 是否在模块间引入了循环？
- 任何新接口是否强迫调用者依赖他们不使用的方法？

如果没有新 import 且没有结构性变更 → 跳过，无发现。

### 步骤 6b：扫描 Domain Model Distortion

- 新的类或变量名是否与业务对同一概念使用的语言匹配？
- 任何新类是否只持有数据而无行为（纯粹数据袋），而原本预期有行为？
- 任何新方法是否将本应属于领域的逻辑放在了服务或工具层？

---

## 严重度校准

应用 `common.md` 中的 Iron Law 格式。`decay-risks.md` 中每个风险都有自己的 Severity
Guide 及数值阈值 — 使用这些作为主要参考。当发现处于两个层级边界时，使用以下作为决策依据：
- 🔴 Critical — 今天正在积极破坏速度或造成生产风险
- 🟡 Warning — 如果在接下来几个功能中不解决就会发生
- 🟢 Suggestion — 在附近时值得修复，不紧急

当存在多个发现时，先列出 Critical 项。如果有超过 5 个发现，
在 Findings 部分末尾添加一行"Recommended fix order"。

---

## 步骤 7：快速测试检查

*最后运行此项。仅三个信号 — 这不是完整的模式 4 审查。*

如果 diff 只包含生成文件、配置或文档，没有生产逻辑变更 → 完全跳过步骤 7。

**信号 1：变更的行为是否有测试？**

- diff 是否修改了生产代码？
- diff 中是否包含相应的测试文件变更？
- 如果添加了新的公共行为但没有新测试：
  → 🟡 Warning：Coverage Illusion — 新行为未测试
  → Source: Feathers — Working Effectively with Legacy Code, Ch. 1
- 如果变更是纯重构且现有测试覆盖了行为 → 无发现。

**信号 2：快速 Mock Abuse 嗅探**

仅在 diff 包含测试文件变更时检查。

- 新增/修改测试中的 mock 设置代码是否明显长于测试逻辑？
- 主要断言是否是 `expect(mock).toHaveBeenCalledWith(...)` 而无行为验证？
- diff 是否向生产类添加了仅从测试文件调用的方法？

如果以上任一为真：
  → 🟡 Warning：Mock Abuse — 测试复杂度超过行为复杂度
  → Source: Osherove — The Art of Unit Testing, mock usage guidelines

**信号 3：快速 Test Obscurity 嗅探**

仅在 diff 包含测试文件变更时检查。

- 新测试名称是否表达了场景和预期结果？
  （模式：`methodName_scenario_expectedResult` 或等效）
- 是否有新测试包含多个断言但其中任何一个都没有消息字符串？

如果测试名称模糊或断言缺少消息：
  → 🟢 Suggestion：Test Obscurity — 测试意图从测试名或断言中不清晰
  → Source: Meszaros — xUnit Test Patterns, Assertion Roulette (p.224)

**输出规则：**

如果所有三个信号都干净 → 不写测试发现。直接进入报告。

如果存在发现 → 使用标准 Iron Law 格式将它们添加到 Findings 部分。
将风险标记为测试衰退风险名称（例如 "Coverage Illusion"、"Mock Abuse"、
"Test Obscurity"）。

> **注意：** 步骤 7 是快速检查，不是完整的测试审计。当发现系统性测试问题时，
> 在 Summary 中记录："考虑运行 `Test Quality Review 模式` 以获取完整的测试质量诊断。"

---

## 输出

使用 `common.md` 中的标准报告模板。
Mode：PR Review
Scope：列出审查的文件（排除跳过的生成文件）。
