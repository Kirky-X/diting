# 测试质量审查指南 — 模式 4

**目的：** 使用六种测试空间衰退风险诊断测试套件健康度。
每条发现必须遵循铁律：Symptom → Source → Consequence → Remedy。

---

## 开始之前：构建 Test Suite Map

在扫描任何风险之前，映射当前测试套件结构：

```
Unit tests:        X files, ~N tests
Integration tests: X files, ~N tests
E2E tests:         X files, ~N tests
Ratio:             Unit X%  :  Integration X%  :  E2E X%
Coverage areas:    [modules with tests] vs [modules without tests]
```

如果无法直接访问测试文件，向用户提**一个问题** — 选择
最相关的：
1. "哪个模块最难测试或覆盖最少？"
2. "当你做变更时，不相关的测试多久会破坏一次？"
3. "是否有一部分代码库你的团队避免触碰因为它没有测试？"

得到一个答案后继续。不要问超过一个问题。

---

## 分析流程

按顺序完成以下五个步骤。

### 步骤 1：扫描 Test Obscurity

*首先扫描此项 — 最可见的风险，决定套件是否
可维护。*

寻找：
- 随机阅读 5–10 个测试名称：每个能否在不打开测试体的情况下传达
  主题 + 场景 + 预期
  结果？
- 是否有测试在失败时毫无线索哪个行为被破坏（多个断言、
  无消息字符串）？
- 是否有任何测试依赖外部状态（文件、数据库行、环境变量、共享可变
  fixture）而从测试体内部不可见？
- 是否有单个巨大的 setUp 或 beforeEach 被每个测试继承，无论
  它实际需要什么？

如果所有测试名称清晰且设置最小 → 无发现。

### 步骤 2a：扫描 Test Brittleness

*脆弱的测试在不改变可观察行为的重构上破坏 — 它们测试
实现，而非契约。*

寻找：
- 询问（或检查 git 历史）：最近的任何重构是否导致测试失败但无
  行为变更？
- 是否有测试方法名称包含"and"或断言 3 个或更多
  不相关行为（Eager Test）？
- 断言是否指定与
  可观察行为无关的 mock 调用顺序或确切参数值？
- 测试是否直接耦合到私有方法或内部状态？

如果脆弱性是系统性的（文件中的大多数测试在重命名时破坏） → 🔴 Critical。
如果是孤立的（1–2 个脆弱测试） → 🟢 Suggestion。

### 步骤 2b：扫描 Mock Abuse

*Mock Abuse 产生的测试无论真实行为是否正确都会通过。
与脆弱性分开扫描此项 — 过度 mock 通常是脆弱性的原因，
但它是一个值得单独发现的独立问题。*

**为步骤 2a 和 2b 一起采样 3–5 个测试一次** — 阅读每个测试体并在
同一轮中检查脆弱性信号和 mock 设置比，然后如果两个问题都存在则写单独
发现。

寻找：
- 在采样的测试中 mock 设置代码是否长于断言逻辑？
- 主要断言是否是 `expect(mock).toHaveBeenCalledWith(...)` 而非
  对输出、状态或可观察事件的断言？
- 生产类中是否有仅从测试文件调用的方法
  （测试诱导的设计损害）？
- 是否有任何单个测试创建超过 3 个 mock 对象？

如果 mock 设置与断言比超过 3:1 → 🟡 Warning。
如果存在仅用于测试访问的生产方法 → 🔴 Critical（架构正被
测试套件扭曲）。

### 步骤 3：扫描 Test Duplication

寻找：
- 是否有相同的设置块（相同方式初始化的相同变量）跨
  5 个或更多测试文件重复而无共享 helper？
- 是否有多个测试传递相同输入并断言相同输出
  而无差异（Lazy Test）？
- 是否有相同业务场景在单元、集成和 E2E 层级覆盖而
  每个层级测试的内容无差异？

如果重复是系统性的（10 个或更多实例） → Critical。
如果是局部的（3–5 个实例） → Warning。

### 步骤 4：扫描 Coverage Illusion 和 Architecture Mismatch

寻找 Coverage Illusion：
- 选择最近修改的核心模块。其错误处理分支和
  null/边界输入是否被测试覆盖？
- 是否有遗留区域（旧函数、附近无测试文件）正在被积极
  变更？
- 测试是否断言副作用（DB 写入、发出的事件、状态转换）
  或仅断言返回值？

**Characterization Test 检查：** 如果遗留代码在没有现有测试的情况下被修改，
团队需要在做变更之前 — 而非之后 — 使用 Characterization Tests。
寻找此模式并在缺失时标记。

Characterization Test 锁定当前行为（无论对错），以便未来变更
不会静默回归它。模板：
```
test("characterize: [module].[method] given [input], returns [current output]") {
  // 用真实输入调用被测代码
  // 断言它当前返回的任何内容 — 即使你怀疑输出是错误的
  // 添加注释："这捕获当前行为，不一定是正确行为"
}
```
Source: Feathers — Working Effectively with Legacy Code, Ch. 13: Characterization Tests

寻找 Architecture Mismatch：
- 与开头的套件图比较：比例是否接近 70% 单元 / 20% 集成 / 10% E2E？
- 高风险模块是否以高于琐碎工具的密度测试？

**测试套件性能：** 慢的测试套件是一等可维护性风险 — 它
破坏快速反馈循环并导致开发者跳过本地运行测试。
- 如果完整套件运行时已知且 > 10 分钟 → 🟡 Warning
- 如果完整套件运行时 > 30 分钟或未知 → 🔴 Critical（未知套件时间
  意味着没人在定期运行它）
- 如果可以是单元测试的测试是集成测试，那是 Performance Mismatch：
  每个错误分类的测试增加几秒可避免的等待时间

Source: Meszaros — xUnit Test Patterns, Slow Tests (p. 253)

### 步骤 5：应用 Iron Law，输出报告

对每条发现应用 `common.md` 中的 Iron Law 格式。

使用标准报告模板。Mode：Test Quality Review。
将 Test Suite Map 作为代码块紧接在 `## Findings` 标题之前，标记为 "Test Suite Map"。
