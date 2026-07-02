# 架构审计指南 — 模式 2

**目的：** 分析系统的模块和依赖结构，识别架构层面的衰退风险。每条发现必须遵循铁律：
Symptom → Source → Consequence → Remedy。

**单体仓库注意：** 将每个可部署的服务或库视为顶层模块。在服务之间绘制依赖关系，而不是在它们的内部包之间。在服务所有权层面应用康威定律检查。在单个服务内部，应用标准的模块级分析。

---

## 分析流程

按顺序完成以下六个步骤。

### 步骤 0：收集代码库上下文

在绘制任何内容之前，先确认你能看到什么。

**如果用户提供了完整的目录树或粘贴了相关文件内容：** 跳过下面的主动阅读，直接进入步骤 1。

**否则，使用以下工具主动阅读项目：**

1. **顶层结构** — 通过 glob 顶层两级来识别模块边界：
   ```
   Glob: **/*(depth 2, directories only)
   ```
2. **入口点** — 阅读包清单或主配置文件（例如 `package.json`、`go.mod`、`pom.xml`、`Cargo.toml`、`pyproject.toml`），确认语言、框架和声明的依赖。
3. **依赖边** — 通过 grep import 语句发现模块间调用。每种语言运行一次；限制为前 200 个匹配以避免 token 超限：
   ```
   Grep: "^\s*(import|from|require\(|use )" across *.ts|*.py|*.go|*.rs|*.java
   ```
4. **大型模块** — 对于任何文件数 > 10 的顶层目录，阅读匹配 `index.*`、`main.*` 或 `__init__.*` 的文件，理解其声明的职责。

**当你能回答以下三个问题时停止：**
- 顶层模块有哪些（名称和数量）？
- 哪些模块从哪些其他模块导入？
- 哪个模块的扇入或扇出最高？

如果项目有 > 100 个顶层文件或 > 4 层嵌套，记录哪些区域是采样而非推断的，并在报告范围行中标注。

### 步骤 1：绘制模块依赖图（Mermaid）

在评估任何风险之前，将依赖关系映射为 Mermaid 图。使用以下格式：

````mermaid
graph TD
  subgraph UI
    WebApp
    MobileApp
  end

  subgraph Domain
    AuthService
    OrderService
    PaymentService
  end

  subgraph Infrastructure
    Database
    MessageQueue
  end

  WebApp --> AuthService
  WebApp --> OrderService
  MobileApp --> AuthService
  MobileApp --> OrderService
  OrderService --> PaymentService
  OrderService --> Database
  OrderService --> MessageQueue
  PaymentService --> Database
  AuthService -.->|circular| OrderService

  classDef critical fill:#ff6b6b,stroke:#c92a2a,color:#fff
  classDef warning fill:#ffd43b,stroke:#e67700
  classDef clean fill:#51cf66,stroke:#2b8a3e,color:#fff

  class PaymentService critical
  class OrderService warning
  class Database,MessageQueue,AuthService,WebApp,MobileApp clean
````

先绘制图结构 — 节点、子图和边 — 不带任何 `classDef` 或 `class` 行。在完成步骤 2-4 的风险扫描之前，你无法分配颜色。

**完成步骤 4 后**，回到此图，根据发现添加 `classDef` 和 `class` 行。上面的示例展示了最终着色输出。

规则：
1. **节点** — 使用顶层目录或服务作为节点，而不是单个文件
2. **分组** — 每个架构层或顶层目录一个 `subgraph`（例如 UI、Domain、Infrastructure）
3. **边** — 实线箭头（`-->`）从依赖模块指向被依赖模块；循环依赖使用带标签的虚线箭头（`-.->|circular|`）。如果没有循环依赖，只使用实线箭头
4. **节点数量上限** — 图中最多约 50 个节点；如有需要，将低风险叶子模块合并到其父模块
5. **扇出** — 对于任何扇出 > 5 的节点，使用描述性标签：`HighFanOutModule["ModuleName (fan-out: 7)"]`
6. **颜色** — 在完成步骤 2-4 之后应用 `classDef` 颜色：`critical`（红色 `#ff6b6b`）表示有 Critical 发现的节点，`warning`（黄色 `#ffd43b`）表示有 Warning 发现的节点，`clean`（绿色 `#51cf66`）表示没有发现或只有 Suggestion 的节点。如果完全没有发现，将所有节点分类为 `clean`
7. **方向** — 默认使用 `graph TD`（自上而下）；仅当架构明显是从左到右的管道时才使用 `graph LR`

### 步骤 2：扫描依赖紊乱

*最具架构影响力的风险 — 优先扫描。*

寻找：
- 循环依赖（上图中的任何 `-.->|circular|` 边）
- 向上流动的箭头（高层领域依赖低层基础设施）
- 稳定的、被广泛依赖的模块从频繁变更的模块导入
- 扇出 > 5 的模块
- 缺乏清晰的分层规则（对"什么依赖什么"没有一致的答案）

### 步骤 3：扫描领域模型扭曲

寻找：
- 模块名称是否匹配业务领域词汇？
- 是否存在一个名为"services"的层包含所有业务逻辑，而领域对象只是纯粹的数据结构？
- 是否有模块跨越了限界上下文边界（例如，用户模块中包含计费逻辑）？
- 外部系统与领域接口处是否有防腐层？

### 步骤 4：扫描其余四种风险

依次检查：

**知识重复：**
- 是否有多个模块独立实现相同的概念？
- 同一领域概念是否在不同模块中以不同名称出现？

**偶然复杂性：**
- 架构中是否存在不增加价值的整层？
- 是否有模块的职责无法用一句话陈述？

**变更传播：**
- 哪些模块是"爆炸半径热点"？（此处的一个变更需要许多其他模块的变更）
- 依赖图是否揭示了某些功能开发缓慢的原因？

**认知过载：**
- 每个模块的职责能否仅从其名称用一句话陈述？
- 新开发者是否会知道应将新功能添加到哪个模块？

### 步骤 5：可测试性接缝评估

*接缝*是架构中可以在不编辑源代码的情况下改变行为的位置 — 通常是接口、配置点或依赖注入边界。接缝密度是可测试性和可演进性的代理指标。

扫描：
- **基础设施边界处没有接缝**：你能否在不编辑被测模块的情况下，用测试替身替换真实的数据库、文件系统或 HTTP 客户端？如果不能，架构在单元测试即可胜任的地方强制使用集成测试。
- **接缝坍塌**：曾经可独立测试的模块其接缝已被移除（例如，直接构造函数实例化取代了依赖注入点，或全局单例取代了注入的协作者）。
- **遗留区域缺少接缝**：没有明显注入点或接口边界的模块 — 任何变更都需要触及整个调用栈以替换行为。

如果所有模块在基础设施边界处都有清晰的接缝 → 无发现。

如果接缝缺失或坍塌：标记为 🟡 Warning，Remedy 指向具体模块以及需要恢复或引入的注入点。

Source: Feathers — Working Effectively with Legacy Code, Ch. 4: The Seam Model

### 步骤 6：康威定律检查

完成六风险扫描后，评估架构与团队结构之间的关系：

- 模块/服务结构是否反映团队结构？
  （康威定律："组织设计出的系统其结构会映射组织的沟通结构"）
- 如果是：这是有意设计还是偶然耦合？
- 导致每个功能都需要跨团队协调开销的不匹配是 🔴 Critical。
- 理论上存在但尚未造成痛苦的不匹配是 🟡 Warning。
- 如果团队结构未知，将其记录为上下文缺失并跳过检查。

**校准示例：**
- 🔴 Critical：Payments 模块由团队 A 拥有，但包含团队 B 拥有的认证逻辑 — 每次 Payments 变更都需要与团队 B 召开同步会议
- 🟡 Warning：两个不同的团队分别拥有 `utils/` 和 `helpers/` 目录，它们做相同的事情 — 理论上痛苦但尚未造成发布协调问题
- 不是发现：单个团队拥有包含多个逻辑模块的单体仓库 — 康威定律错位需要*不同的团队*才有意义

---

## 输出

使用 `common.md` 中的标准报告模板。Mode：Architecture Audit。

将 Mermaid 依赖图放在"Module Dependency Graph"下的最前面。在发现中引用相关节点名称。最后添加 `classDef` 颜色分配，在所有发现识别完毕之后。
