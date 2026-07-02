# 衰退风险参考

导致软件退化的六种模式。对每条发现应用铁律。

---

## 风险 1：Cognitive Overload (R1)

**诊断问题：** 人类理解这个需要多少心智努力？

超过工作记忆的认知负荷会导致错误、回避，并阻碍本可修复它的重构。

### 症状

- 函数超过 20 行且混合了多个抽象层次
- 嵌套深度超过 3 层
- 参数列表超过 4 个参数
- 魔法数字或未解释的常量
- 需要阅读实现才能理解的变量名（例如 `d`、`tmp2`、`flag`）
- 3 个或更多条件组合的布尔表达式
- 火车残骸链：`a.getB().getC().doD()`
- 代码名称与业务对同一概念的称呼不匹配
- 标志参数：一个布尔参数使函数根据其值执行两种根本不同的事情 — 表明函数有两个职责
- 基本类型偏执：领域概念用原始类型表示（`String email`、`int orderId`、`double money`）而非专门构造的值类型 — 强迫调用者知道哪个字符串是邮箱、哪个是姓名
- 浅模块：组件的接口或文档相对于其提供的功能更复杂

### 来源

| 症状 | 书籍 | 原则 / 坏味 |
|---------|------|-------------------|
| Long Method | Fowler — Refactoring | Long Method |
| Long Parameter List | Fowler — Refactoring | Long Parameter List |
| Message Chains | Fowler — Refactoring | Message Chains |
| Flag Arguments | Fowler — Refactoring | Flag Arguments |
| Primitive Obsession | Fowler — Refactoring | Primitive Obsession |
| Function length and nesting | McConnell — Code Complete | Ch. 7: High-Quality Routines |
| Variable naming | McConnell — Code Complete | Ch. 11: The Power of Variable Names |
| Magic numbers | McConnell — Code Complete | Ch. 12: Fundamental Data Types |
| Domain name mismatch | Evans — Domain-Driven Design | Ubiquitous Language |
| Shallow Module | Ousterhout — A Philosophy of Software Design | Ch. 4: Modules Should Be Deep |

### 严重度指南

- 🔴 Critical：函数 > 50 行，嵌套 > 5，或几乎没有有意义的名称
- 🟡 Warning：函数 20–50 行，嵌套 4–5，一些不清晰的名称
- 🟢 Suggestion：轻微的命名问题，1–2 个魔法数字，孤立的火车残骸链

### 不应标记

- 带有清晰名称和守卫子句的线性代码不自动归为高认知负荷
- 隐藏在深度、简单模块边界背后的内部实现细节不是浅模块问题
- 领域特定术语如果与专家实际说话方式匹配则不应被标记

---

## 风险 2：Change Propagation (R2)

**诊断问题：** 改变一件事会破坏多少不相关的东西？

每次变更波及不相关模块，拖慢速度并成倍增加回归风险。

### 症状

- 修改一个功能需要触及不相关模块中超过 3 个文件
- 一个类因多个不同的业务原因变更（例如 `UserService` 因计费逻辑和通知逻辑和资料逻辑而变更）
- 一个方法从另一个类使用的数据多于从自己类使用的数据
- 两个类直接知道彼此的内部状态
- 修改一个模块需要重新编译或重新测试许多不相关的模块
- **Hyrum's Law**：如果有足够的调用者，每个可观察行为 — 包括实现细节、错误消息文本、偶然的调用顺序和未记录的副作用 — 都会成为调用者依赖的隐式契约，即使声明 API 从未保证过
- **正交性违反**：改变功能的一个维度迫使在不相关维度中编辑 — 添加新支付类型不应要求触及日志、缓存或通知代码，但在非正交设计中却需要
- 信息泄漏：一个设计决策（例如文件格式、协议细节或数据形状）被编码在多个模块中，因此修改它需要在多处协调编辑，即使只有一个模块"拥有"该概念

### 来源

| 症状 | 书籍 | 原则 / 坏味 |
|---------|------|-------------------|
| Shotgun Surgery | Fowler — Refactoring | Shotgun Surgery |
| Divergent Change | Fowler — Refactoring | Divergent Change |
| Feature Envy | Fowler — Refactoring | Feature Envy |
| Inappropriate Intimacy | Fowler — Refactoring | Inappropriate Intimacy |
| Orthogonality violation | Hunt & Thomas — The Pragmatic Programmer | Ch. 2: Orthogonality |
| DIP violation | Martin — Clean Architecture | Dependency Inversion Principle |
| High change propagation radius | Brooks — The Mythical Man-Month | Ch. 2: Brooks's Law (communication overhead) |
| Hyrum's Law | Winters et al. — Software Engineering at Google | Ch. 1: Hyrum's Law |
| Information Leakage | Ousterhout — A Philosophy of Software Design | Ch. 5: Information Hiding and Leakage |

### 严重度指南

- 🔴 Critical：一次变更触及 > 5 个文件，或存在结构性依赖倒置（领域依赖基础设施）
- 🟡 Warning：一次变更触及 3–5 个文件，模块间轻度耦合
- 🟢 Suggestion：轻微耦合，易于隔离

### 不应标记

- 装配根装配具体依赖本身不是 DIP 违反
- 具有有意支持行为的稳定公共 API 不自动归为 Hyrum's Law 债务
- 一个限界上下文内的相似编辑可能是正常的协调变更，不是霰弹式修改

---

## 风险 3：Knowledge Duplication (R3)

**诊断问题：** 同一个决策是否在多处表达？

多份副本会悄然分道扬镳。DRY 是关于决策，不是代码行。

### 症状

- 相同逻辑跨多个文件或函数复制粘贴
- 同一概念在代码库不同部分有不同命名
  （例如 `user`、`account`、`member`、`customer` 都指向同一领域实体）
- 必须同步变更的并行类层次
  （例如，添加新支付类型需要在 3 个不同层次中添加类）
- 配置值作为字面量在多处重复
- 两个模块独立实现相同算法

### 来源

| 症状 | 书籍 | 原则 / 坏味 |
|---------|------|-------------------|
| Code duplication | Fowler — Refactoring | Duplicate Code |
| Parallel Inheritance | Fowler — Refactoring | Parallel Inheritance Hierarchies |
| DRY violation | Hunt & Thomas — The Pragmatic Programmer | DRY: Don't Repeat Yourself |
| Inconsistent naming | Evans — Domain-Driven Design | Ubiquitous Language |
| Alternative Classes | Fowler — Refactoring | Alternative Classes with Different Interfaces |

### 严重度指南

- 🔴 Critical：核心业务逻辑跨模块重复，或同一领域概念以 3+ 种不同方式命名
- 🟡 Warning：工具代码重复，子系统内命名不一致
- 🟢 Suggestion：轻微字面量重复，单一命名不一致

### 不应标记

- 跨独立限界上下文的重复不自动归为知识重复
- 在积极抽取或迁移期间的临时重复不一定是债务
- 在显式边界处重复的共享协议常量，当本地所有权更清晰时可能是可接受的

---

## 风险 4：Accidental Complexity (R4)

**诊断问题：** 代码是否比它解决的问题更复杂？

偶然复杂性一次添加一次地累积，直到开发者与脚手架搏斗多于解决问题。

### 症状

- "为未来使用"构建的抽象没有当前消费者
  （例如，为只有一种已知实现的用例构建的插件系统）
- 仅勉强证明其存在合理性的类（包装单个方法调用）
- 只委托给另一个类而不添加行为的类（纯粹的中间人）
- 系统的第二次尝试明显比第一次更复杂，
  为尚不存在的需求添加通用性
- 表示缺少多态性的 switch 语句
- 从未从默认值更改过的配置选项
- 框架代码大于其驱动的应用程序
- 在持续战术捷径下增长的代码：每个变通方法看似微小，
  但累积的捷径意味着每个新功能都需要与现有结构搏斗

### 来源

| 症状 | 书籍 | 原则 / 坏味 |
|---------|------|-------------------|
| Speculative Generality | Fowler — Refactoring | Speculative Generality |
| Lazy Class | Fowler — Refactoring | Lazy Class |
| Middle Man | Fowler — Refactoring | Middle Man |
| Switch Statements | Fowler — Refactoring | Switch Statements |
| Second System Effect | Brooks — The Mythical Man-Month | Ch. 5: The Second-System Effect |
| YAGNI violations | McConnell — Code Complete | Ch. 5: Design in Construction |
| Over-engineering | Hunt & Thomas — The Pragmatic Programmer | Topic 4: Good-Enough Software |
| Tactical programming debt | Ousterhout — A Philosophy of Software Design | Ch. 3: Strategic vs. Tactical Programming |

### 严重度指南

- 🔴 Critical：围绕投机需求构建的整个子系统，或框架开销主导领域逻辑
- 🟡 Warning：几个不必要的抽象或包装类，未使用的配置系统
- 🟢 Suggestion：非关键路径中一两个惰性类或中间人模式

### 不应标记

- 对外部协议、线格式或封闭枚举的 switch 不自动归为缺少多态性
- 吸收供应商变动或隐藏不稳定性的薄包装可能是合理的
- 较大的第二版除非添加的通用性超过当前需求，否则不是第二系统效应

---

## 风险 5：Dependency Disorder (R5)

**诊断问题：** 依赖是否沿一致、可预测的方向流动？

当业务逻辑依赖基础设施时，基础设施变更会级联到领域变更。循环阻止隔离。

### 症状

- 模块或包之间的循环依赖
- 高层业务逻辑直接从低层基础设施导入
  （例如，领域服务从特定数据库驱动导入）
- 稳定的、广泛使用的组件依赖不稳定的、频繁变更的组件
- 抽象组件依赖具体实现
- 迪米特法则违反：`order.getCustomer().getAddress().getCity()`
- 模块扇出大于 5（从超过 5 个其他模块导入）
- 模块实现接口但只使用其方法子集，或必须为其不需要的方法提供存根实现（ISP 违反：胖接口强迫调用者接受不需要的依赖）
- 系统感觉像是"不是一个头脑设计的" — 不同模块使用不兼容的架构模式，没有清晰的规则说明何处用何者
- 对传递包的直接版本固定依赖（菱形依赖风险）；
  升级一个库需要协调多个不相关的团队或仓库

### 来源

| 症状 | 书籍 | 原则 / 坏味 |
|---------|------|-------------------|
| Dependency cycles | Martin — Clean Architecture | Acyclic Dependencies Principle (ADP) |
| DIP violation | Martin — Clean Architecture | Dependency Inversion Principle (DIP) |
| Instability direction | Martin — Clean Architecture | Stable Dependencies Principle (SDP) |
| Abstraction mismatch | Martin — Clean Architecture | Stable Abstractions Principle (SAP) |
| ISP violation | Martin — Clean Architecture | Interface Segregation Principle (ISP) |
| Conceptual integrity | Brooks — The Mythical Man-Month | Ch. 4: Conceptual Integrity |
| Law of Demeter | Hunt & Thomas — The Pragmatic Programmer | Ch. 5: Decoupling and the Law of Demeter |
| SOLID violations | Martin — Clean Architecture | Single Responsibility, Open/Closed Principles |
| Diamond dependency / upgrade blockage | Winters et al. — Software Engineering at Google | Ch. 21: Dependency Management |

### 严重度指南

- 🔴 Critical：存在依赖循环，或领域层直接依赖基础设施层
- 🟡 Warning：几个 SDP 或 DIP 违反但无循环；跨模块的概念不一致
- 🟢 Suggestion：轻微迪米特法则违反，孤立模块中略高的扇出

### 不应标记

- 编排层或装配根中的高扇出不自动归为紊乱
- 适配器模块在显式跨边界翻译时可以同时依赖领域和基础设施
- 如果依赖策略清晰，覆盖许多叶子依赖的稳定外观可能是健康的

---

## 风险 6：Domain Model Distortion (R6)

**诊断问题：** 代码是否忠实地表示了它正在解决的问题？

代码与业务语言不匹配会迫使心智翻译。久而久之它建模的是模式而非领域，逻辑渗入服务层。

### 症状

- 业务逻辑分散在服务层，而领域对象只有 getter 和 setter
  （贫血领域模型）
- 代码变量、类或方法名称与业务干系人对该概念的称呼不匹配
- 唯一目的是持有数据而无行为的类（纯粹数据袋）
- 忽略或覆盖大部分父类行为的子类（拒绝继承）
- 限界上下文边界在没有任何翻译或防腐层的情况下被跨越
- 对另一个类的数据比对自身类数据更感兴趣的方法
  （领域逻辑在错误的位置）
- 子类以不兼容行为覆盖大多数父类方法，或在父类契约保证成功处抛出异常
  （LSP 违反：替换破坏调用者）
- 值对象被视为实体：完全由属性定义的概念（例如 Money、
  Email、Address）被赋予可变 ID 和生命周期，而不是在变更时被替换

### 来源

| 症状 | 书籍 | 原则 / 坏味 |
|---------|------|-------------------|
| Anemic Domain Model | Evans — Domain-Driven Design | Domain Model pattern |
| Ubiquitous Language drift | Evans — Domain-Driven Design | Ubiquitous Language |
| Bounded context violation | Evans — Domain-Driven Design | Bounded Context |
| Data Class | Fowler — Refactoring | Data Class |
| Refused Bequest | Fowler — Refactoring | Refused Bequest |
| Feature Envy | Fowler — Refactoring | Feature Envy |
| LSP violation | Martin — Clean Architecture | Liskov Substitution Principle (LSP) |

### 严重度指南

- 🔴 Critical：领域逻辑完全在服务层，领域对象是毫无行为的纯粹数据袋
- 🟡 Warning：部分贫血，代码与领域语言之间一些命名不一致
- 🟢 Suggestion：非核心区域的轻微命名漂移，孤立的 Feature Envy 案例

### 不应标记

- CRUD 密集的工作流可能合法地使用事务脚本而非丰富的领域对象
- DTO、持久化记录和 API 负载模型可以是纯数据的
- 共享基础设施语言不应被误认为是领域漂移，如果业务模型本身简单
