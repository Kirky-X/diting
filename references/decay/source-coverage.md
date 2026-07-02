---
books:
  - The Mythical Man-Month
  - Code Complete
  - Refactoring
  - Clean Architecture
  - The Pragmatic Programmer
  - Domain-Driven Design
  - A Philosophy of Software Design
  - Software Engineering at Google
  - xUnit Test Patterns
  - The Art of Unit Testing
  - Working Effectively with Legacy Code
  - How Google Tests Software
---

# 来源覆盖矩阵

在选择模式之后、写发现之前使用此文件。
它的存在是为了防止浅薄的"书名引用"式审查。

## 审查纪律

- 仅当观察到的症状实际匹配该书的原则时才引用书。
- 阈值跨越是提示，不是结论。检查上下文、意图和爆炸半径。
- 在将坏味标记为债务之前寻找合理的权衡。
- 优先选择具体的架构或领域后果而非抽象的风格抱怨。
- 如果两本书的方向不同，陈述权衡而不是假装没有张力。

---

## Frederick Brooks — *The Mythical Man-Month*

**当代体现**
- 变更传播作为沟通开销
- 第二系统效应
- 概念完整性

**不要忽略**
- 设计是否展示了单一连贯的想法还是竞争的局部优化
- 跨团队协调成本是否正在成为功能成本的一部分

**不要过度标记**
- 大型系统不自动归为第二系统
- 多模块设计在保留概念完整性时是可接受的

---

## Steve McConnell — *Code Complete*

**当代体现**
- 例程长度、嵌套、命名和魔法数字
- 构建阶段 YAGNI 检查
- 防御式编程和错误处理纪律（守卫子句、输入验证、
  显式错误路径、对不变量的断言）

**不要忽略**
- 低层可读性选择是否复合为运营风险
- 缺失的错误处理是否使失败模式对维护者不可见

**不要过度标记**
- 小而显式的守卫子句不是认知过载
- 长例程在它是线性的、命名良好且单一用途时可能是可接受的

---

## Martin Fowler — *Refactoring*

**当代体现**
- Long Method, Long Parameter List, Message Chains
- Shotgun Surgery, Divergent Change, Feature Envy, Inappropriate Intimacy
- Duplicate Code, Speculative Generality, Lazy Class, Middle Man, Data Class
- Flag Arguments：将函数拆分为两种行为的布尔参数
- Primitive Obsession：领域概念用原始类型而非值类型表示

**不要忽略**
- 代码坏味是局部的还是系统性的
- 重构目标在模型中是否有自然归属

**不要过度标记**
- 在积极抽取期间的临时重复不总是债务
- 数据聚焦结构在有意图地作为 DTO 或边界记录时是可接受的

---

## Robert C. Martin — *Clean Architecture*

**当代体现**
- DIP、ADP、SDP、SAP 和分层方向
- ISP：强迫调用者依赖他们不使用的方法的胖接口
- LSP：破坏父类型行为契约的子类
- SRP 和 OCP：有多个变更原因的类；对修改关闭但对扩展开放的模块
  （通过抽象）

**不要忽略**
- 策略与细节边界
- 依赖箭头是否保留可替换性和可测试性

**不要过度标记**
- 装配根可以按设计依赖具体基础设施
- 薄适配器层在显式作为边界胶水时可以双向 import

---

## Andrew Hunt & David Thomas — *The Pragmatic Programmer*

**当代体现**
- 正交性
- DRY
- 迪米特法则

**不要忽略**
- 知识重复是否真的是重复的决策制定
- 耦合是偶然的还是刻意的局部简化

**不要过度标记**
- 不同限界上下文中的相似代码不自动归为 DRY 违反
- 内聚聚合内的直接对象访问不总是迪米特问题

---

## Eric Evans — *Domain-Driven Design*

**当代体现**
- 统一语言
- 限界上下文
- 贫血领域模型
- Entity vs Value Object：具有身份和生命周期的对象 vs 完全由属性定义的对象
  （Money、Email、Address 应为不可变值类型，而非可变实体）
- 聚合根：谁拥有不变量边界；跨聚合访问仅通过根

**不要忽略**
- 聚合边界、不变量所有权和防腐层
- 名称是否与专家使用的业务语言匹配

**不要过度标记**
- CRUD 密集的工作流可能合法地使用事务脚本
- 当领域本身简单时薄实体是可接受的

---

## John Ousterhout — *A Philosophy of Software Design*

**当代体现**
- 深模块 vs 浅模块
- 战略式 vs 战术式编程
- 信息泄漏：编码在多个模块中的设计决策，即使模块间没有显式 import 也会创建
  变更耦合

**不要忽略**
- 接口复杂性相对于隐藏复杂性
- 重复的战术补丁是否在提高长期认知负荷
- "helper"是否暴露了调用者不应知道的内部设计决策

**不要过度标记**
- 当接口保持简单时内部实现复杂性是可接受的
- 当有意义地吸收波动性时小包装是可接受的

---

## Titus Winters, Tom Manshreck, Hyrum Wright — *Software Engineering at Google*

**当代体现**
- Hyrum's Law
- 依赖管理和升级阻塞
- 代码可持续性：代码是否能按书面形式在多年内维护、迁移和升级
  而无需英雄式努力
- 向后兼容性：API 变更是否保留现有调用者或强迫
  跨组织协调升级

**不要忽略**
- 由可观察行为创建的事实 API
- 暴露过多表面积的维护成本
- 依赖图是否允许随时间独立升级

**不要过度标记**
- 如果有意支持，稳定的公共 API 不是负债
- 当依赖策略显式且受治理时，仅扇出不构成紊乱

---

## Gerard Meszaros — *xUnit Test Patterns*

**当代体现**
- Assertion Roulette, Mystery Guest, General Fixture
- Eager Test, Lazy Test, Test Code Duplication, Behavior Verification
- Erratic Test：由于共享状态、时间依赖或测试间的顺序假设
  而产生非确定性结果的测试

**不要忽略**
- 测试失败是否可诊断
- 套件形状是否放大维护成本

**不要过度标记**
- 当多个断言表达一个行为和一个失败故事时是可接受的
- 当每个字段都与场景相关时共享 fixture 是可接受的

---

## Roy Osherove — *The Art of Unit Testing*

**当代体现**
- 测试命名纪律
- 测试隔离
- mock 使用指南
- 边缘路径测试完整性

**不要忽略**
- 测试是否验证行为而非布线
- 接缝是否用于简化测试，或生产代码是否为可测试性而被扭曲

**不要过度标记**
- 当依赖是非确定性的且断言仍验证行为时 mock 是可接受的
- 命名约定是指导；清晰才是目标

---

## Michael Feathers — *Working Effectively with Legacy Code*

**当代体现**
- 遗留代码作为没有测试的代码
- 感知与分离
- 接缝
- 特征化测试

**不要忽略**
- 团队今天是否能安全地变更风险区域
- 代码是否提供任何接缝用于在变更下隔离行为

**不要过度标记**
- 如果稳定且未在积极变更下，未测试的代码不自动归为遗留
- 特征化测试在修改不清晰的现有行为之前最重要

---

## Google Engineering — *How Google Tests Software*

**当代体现**
- 变更覆盖 vs 行覆盖
- 金字塔形状和套件组合经济学

**不要忽略**
- 套件是否反映业务风险，而非仅仅是百分比
- 昂贵的测试是否主导反馈循环

**不要过度标记**
- 在由平台约束或产品风险证明合理时，非 70:20:10 比例可以是健康的
- 高覆盖在配有意义的分支和变更保护时是有用的
