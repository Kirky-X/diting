# 测试衰退风险参考

导致测试套件退化的六种模式。对每条发现应用铁律。

---

## 风险 T1：Test Obscurity

**诊断问题：** 理解这个测试验证了什么需要多少努力？

不清晰的测试意图滋生不信任、遗漏的失败和重复 — 距离被废弃的套件仅一步之遥。

### 症状

- Assertion Roulette：多个断言没有消息字符串 — 当一个失败时，
  不阅读每个断言就无法确定哪个行为被破坏
- Mystery Guest：测试依赖外部状态（文件、数据库行、共享 fixture）
  而这些在测试体中不可见
- 不表达场景和预期结果的测试名称
  （例如，`test1`、`shouldWork`、`testLogin`、`testUserService`）
- General Fixture：被不相关测试共享的过大 setUp 或 beforeEach，使
  每个测试的前置条件不可见
- 测试体需要阅读生产代码才能理解正在验证什么

### 来源

| 症状 | 书籍 | 原则 / 坏味 |
|---------|------|-------------------|
| Assertion Roulette | Meszaros — xUnit Test Patterns | Assertion Roulette (p.224) |
| Mystery Guest | Meszaros — xUnit Test Patterns | Mystery Guest (p.411) |
| General Fixture | Meszaros — xUnit Test Patterns | General Fixture (p.316) |
| Test naming | Osherove — The Art of Unit Testing | method_scenario_expected naming convention |

### 严重度指南

- 🔴 Critical：文件中没有测试名称描述被测试的行为；所有断言缺少消息
- 🟡 Warning：多个 Mystery Guest；几个模糊的测试名称
- 🟢 Suggestion：轻微的命名问题；孤立的 General Fixture

### 不应标记

- 当多个断言描述一个连贯行为并以清晰故事失败时是可接受的
- 当每个初始化值与几乎每个测试相关时共享设置是可接受的
- 如果场景和预期结果仍然明显，简洁的测试名称是可接受的

---

## 风险 T2：Test Brittleness

**诊断问题：** 在不改变行为的情况下重构时测试会破坏吗？

脆弱的测试惩罚重构 — 最终开发者停止重构，代码库为了保护套件而停滞。

### 症状

- 测试断言私有方法结果、内部状态或实现细节
  而非可观察行为
- Eager Test：一个测试方法验证多个不相关行为；任何单个变更
  无论触及哪个行为都会导致它失败
- 过度规范：断言强制 mock 调用顺序或与
  被测试行为无关的确切参数值
- 重命名或抽取方法导致 5 个或更多测试失败，即使没有行为变更
- Erratic Test：测试在没有任何生产代码变更的情况下跨运行产生不同结果
  — 由竞态条件、时间依赖逻辑、随机数据或
  测试间的共享可变状态引起

### 来源

| 症状 | 书籍 | 原则 / 坏味 |
|---------|------|-------------------|
| Eager Test | Meszaros — xUnit Test Patterns | Eager Test (p.228) |
| Erratic Test | Meszaros — xUnit Test Patterns | Erratic Test |
| Implementation coupling | Osherove — The Art of Unit Testing | Test isolation principle |
| Orthogonality violation | Hunt & Thomas — The Pragmatic Programmer | Ch. 2: Orthogonality |

### 严重度指南

- 🔴 Critical：无行为变更的重构导致测试失败；> 5 个测试耦合到单个实现细节
- 🟡 Warning：Eager Test 在套件中普遍；中度实现细节断言
- 🟢 Suggestion：非关键测试中孤立的过度规范

### 不应标记

- 验证外部可观察事件或发出的命令不是实现耦合
- 当所有断言支持一个行为主张时，一个测试有几个断言是可接受的
- 如果测试仍断言行为而非布线，fake 或内存适配器不是脆弱性

---

## 风险 T3：Test Duplication

**诊断问题：** 同一个测试场景是否在多处表达？

重复的测试必须在多处变更，并在没有测试独特行为的情况下制造虚假信心。

### 症状

- Test Code Duplication：相同的设置或断言逻辑跨多个测试复制粘贴
  而未抽取到共享 helper
- Lazy Test：多个测试验证相同行为，输入、
  状态或预期输出无差异
- 同一边界条件在单元、集成和 E2E 层级相同测试
  — 三份副本且无层级差异
- 测试 helper 函数或 fixture 在测试文件间重复而非共享

### 来源

| 症状 | 书籍 | 原则 / 坏味 |
|---------|------|-------------------|
| Test Code Duplication | Meszaros — xUnit Test Patterns | Test Code Duplication (p.213) |
| Lazy Test | Meszaros — xUnit Test Patterns | Lazy Test (p.232) |
| DRY violation in tests | Hunt & Thomas — The Pragmatic Programmer | DRY: Don't Repeat Yourself |

### 严重度指南

- 🔴 Critical：核心业务场景在所有三个测试层完全重复且无差异
- 🟡 Warning：常见场景设置在 5 个或更多测试中重复而未抽取
- 🟢 Suggestion：轻微的 helper 重复；孤立的 Lazy Test

### 不应标记

- 当每个层级验证不同风险时，同一场景可以在单元和集成层级出现
- 小的本地设置重复可能比过度抽象的 fixture 迷宫更清晰
- 对不同领域规则的类似断言如果业务意图不同则不是 Lazy Test

---

## 风险 T4：Mock Abuse

**诊断问题：** 测试是否比它测试的行为更复杂？

Mock 滥用产生的测试在什么都不验证的情况下通过 — 只要 mock 接好了，
生产代码可以完全坏掉。

### 症状

- Mock 设置代码长于测试逻辑本身
- 主要断言是 `expect(mock).toHaveBeenCalledWith(...)` — 测试验证
  mock 被调用了，而非任何真实行为发生了
- 为测试中的生命周期管理向生产类添加仅测试方法
- 单个单元测试使用超过 3 个 mock
- Incomplete Mock：mock 对象缺少下游代码将访问的字段，
  导致仅在集成中可见的静默失败
- Hard-Coded Test Data：测试数据与真实数据形状或约束
  无相似之处

### 来源

| 症状 | 书籍 | 原则 / 坏味 |
|---------|------|-------------------|
| Mock count > 3 | Osherove — The Art of Unit Testing | Mock usage guidelines |
| Testing mock behavior | Meszaros — xUnit Test Patterns | Behavior Verification (p.544) |
| Test-only production methods | Feathers — Working Effectively with Legacy Code | Ch. 3: Sensing and Separation |
| Hard-Coded Test Data | Meszaros — xUnit Test Patterns | Hard-Coded Test Data (p.534) |
| Incomplete Mock | Osherove — The Art of Unit Testing | Mock completeness requirement |

### 严重度指南

- 🔴 Critical：mock 设置 > 测试代码的 50%；生产类有仅从测试调用的方法
- 🟡 Warning：mock 一致地每测试 > 3 个；主要断言是 mock 调用验证
- 🟢 Suggestion：孤立的 Incomplete Mock；轻微的 Hard-Coded Test Data

### 不应标记

- 当断言仍验证行为时，围绕非确定性依赖的少量 mock 是可接受的
- 用于观察状态转换的 fake 和 spy 默认不是 mock 滥用
- 当交互本身就是被测行为时，一个交互断言可能是合适的

---

## 风险 T5：Coverage Illusion

**诊断问题：** 测试套件是否实际防止了重要的失败？

覆盖衡量执行，而非验证。90% 的行覆盖仍可能错过每个关键失败模式 — 团队停止查看因为数字显示"已覆盖"。

### 症状

- 高行覆盖但错误处理分支、边界条件和异常路径
  没有相应测试
- 仅 Happy-path：没有 sad path，没有 null/empty/zero 输入，没有并发边缘案例
- 遗留代码区域正在被积极修改但没有测试存在
  （Feathers："遗留代码是没有测试的代码"）
- 覆盖百分比被视为签收标准；关键变更路径仍未测试
- 测试断言返回值但不断言重要的副作用如数据库写入、
  事件发布或状态转换

### 来源

| 症状 | 书籍 | 原则 / 坏味 |
|---------|------|-------------------|
| Legacy code = no tests | Feathers — Working Effectively with Legacy Code | Ch. 1: "Legacy code is code without tests" |
| Change coverage vs line coverage | Google — How Google Tests Software | Ch. 11: Testing at Google Scale |
| Happy-path only | Osherove — The Art of Unit Testing | Test completeness principle |

### 严重度指南

- 🔴 Critical：遗留代码区域被积极修改且无测试；错误处理路径完全缺失
- 🟡 Warning：覆盖 > 80% 但边缘和异常路径系统性缺失
- 🟢 Suggestion：一些非关键路径缺少 sad-path 测试

### 不应标记

- 高行覆盖在配有分支、边界和变更路径覆盖时是有用的
- 新模块如果仍是私有且低风险，早期可能有有限覆盖
- 副作用断言可能存在于集成测试而非单元测试中，不暗示缺口

---

## 风险 T6：Architecture Mismatch

**诊断问题：** 测试套件结构是否反映系统实际的风险概况？

错误的套件形状缓慢且昂贵 — 不是因为坏测试，而是因为在错误层级使用了错误类型。

### 症状

- 倒置测试金字塔：E2E 或集成测试计数超过单元测试计数，
  导致缓慢且脆弱的套件
- 没有接缝点的遗留代码：不存在接口、依赖注入或接缝，
  使其无法在不修改生产代码的情况下隔离测试
- 被修改的遗留区域没有 Characterization Tests 来捕获当前行为
  在变更之前
- 完整套件执行时间超过 10 分钟（表示架构问题，
  而非性能问题 — 太多慢测试）
- 高风险和低风险路径以相同密度测试；
  测试分布中没有基于风险的优先级

### 来源

| 症状 | 书籍 | 原则 / 坏味 |
|---------|------|-------------------|
| Inverted pyramid | Google — How Google Tests Software | 70:20:10 unit:integration:E2E ratio |
| No seam points | Feathers — Working Effectively with Legacy Code | Ch. 4: Seam Model |
| Missing Characterization Tests | Feathers — Working Effectively with Legacy Code | Ch. 13: Characterization Tests |
| Suite execution time | Meszaros — xUnit Test Patterns | Slow Tests (p. 253) |

### 严重度指南

- 🔴 Critical：被修改的遗留代码没有接缝且没有特征化测试；金字塔完全倒置
- 🟡 Warning：套件执行 > 10 分钟；集成/E2E 计数超过单元测试
- 🟢 Suggestion：局部金字塔比例偏差；几个遗留区域缺少特征化测试

### 不应标记

- 偏离 70:20:10 可由平台约束或产品风险证明合理
- 重的集成测试套件如果反馈快速且有目的地分层仍可以是健康的
- 少量关键路径 E2E 测试是可取的，不是坏味
