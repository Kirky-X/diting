# Agent 代码审查 —— 12-Factor Agents 审计

Agent 代码审查模式 —— 按 12-factor agents 架构原则审计 LLM agent 代码。

## 用法

```bash
review agent [target-path]
```

## 范围与重叠

本维度按 12-factor agents 架构原则审计 LLM agent 代码。它与通用维度
（security / performance / quality / architecture / correctness / …）
**不重叠**：那些检查通用软件属性，都不含 agent 专属检查。`agent` 检查
agent 专属的架构和可靠性模式 —— 控制流所有权、prompt 所有权、context
序列化、intent 分发、错误压缩、人即工具、状态统一。如果某个发现项
对非 agent 代码同样适用，路由到通用维度；不要在此重复报告。

**激活门槛**：仅当目标导入了 agent 框架
（`langgraph` / `crewai` / `autogen` / `llama_index.agent` / OpenAI Agents SDK
/ 等价物）或手写 LLM 循环（`while True` + LLM 调用 + 工具分发）时才应用。
对非 agent 代码静默跳过 —— 不要强行套用。

## 检测方法

### F08: Control-Flow Ownership Audit（控制流所有权审核）

- **核心思想**: agent 必须自有控制循环——手写 `while True` + 显式
  `continue` / `break` / `return`。强反模式是把循环交给框架 graph 编排
  （`langgraph.StateGraph` / `crewai.Crew.run` / `autogen.GroupChatManager`），
  用户代码里看不到任何显式循环。
- **检测信号**:
  - `import langgraph` / `from langgraph.graph import StateGraph` /
    `from crewai import Crew` / `from autogen import …` 出现
  - **且** agent 自有源码中没有 `while True:` / `while running:` /
    `while not done:` 字面循环
  - 用 `graph.add_node` + `graph.add_edge` + `add_conditional_edges` 表达
    迭代（说明循环被框架接管）
- **严重度**: **HIGH**（强反模式，spec F08 明确要求 agent own the loop）
- **判据来源**: 12-factor-agents spec.md F08
- **修复建议**: 用手写循环替代框架 graph 编排
  ```python
  while True:
      intent = classify_intent(llm, context)
      if isinstance(intent, Done):
          return context
      result = dispatch(intent, context)
      context = reduce(context, result)
  ```
- **finding 格式**:
  `[F08-HIGH] <file:line> — control flow delegated to <framework> graph; per spec F08 the agent must own the loop. Fix: hand-written while True + switch(intent) + continue/return.`

### F02: Prompt Ownership Audit（Prompt 所有权审核）

- **核心思想**: agent 必须自有 prompt 模板，不能依赖框架黑盒实例化。框架黑盒
  会把 prompt 构造藏在 `Agent(role=…)` / `Crew(agents=…, tasks=…)` /
  `Task(expected_output=…)` 内部，导致 prompt 不可审计、不可演进。
- **检测信号**:
  - `Agent(role="…", goal="…", backstory="…")` (crewai)
  - `Crew(agents=[…], tasks=[…])` (crewai)
  - `Task(description=…, expected_output=…)` (crewai)
  - `AssistantAgent(name=…, system_message=…)` 且 system_message 是字面字符串
    (autogen)
  - `initialize_agent(llm=…, agent_kwargs={…})` (legacy langchain agent)
  - 任何把 prompt 拼装委派给框架的实例化模式
- **严重度**: **HIGH**（强信号，spec F02）
- **判据来源**: 12-factor-agents spec.md F02
- **修复建议**: 自定义 prompt 模板（string template / f-string / jinja2），
  显式拼装后传入 LLM；不使用框架的 role/backstory/expected_output 字段
- **finding 格式**:
  `[F02-HIGH] <file:line> — framework black-box instantiation (<pattern>) hides prompt construction; per spec F02 agents must own their prompts. Fix: inline prompt template, pass rendered string to the LLM call directly.`

### F03: Context Window Serialization Audit（Context 序列化审核）

- **核心思想**: agent 必须有显式的 context 序列化器（`to_prompt` /
  `serializeForLLM` / `pack` 之类），把业务状态结构转成 LLM 可消费的
  字符串。缺序列化器通常意味着 context 是隐式拼装的（脆弱、难演进）。
- **检测信号**:
  - 搜索 `to_prompt` / `serializeForLLM` / `pack` / `to_messages` /
    `render_context` 方法定义
  - 缺失 = 弱信号（不一定是 bug，但 spec F03 要求显式序列化）
- **严重度**: **MID**（弱信号缺失只报 MID，不报 HIGH，避免误报——有些
  简单 agent 用 list[dict] 直接传 messages 也是合规的）
- **判据来源**: 12-factor-agents spec.md F03
- **修复建议**: 实现一个显式的 context 序列化方法，把 Thread/Events
  序列化为 prompt 文本或 messages 数组
- **finding 格式**:
  `[F03-MED] <file:line> — no explicit context serializer found; per spec F03 the agent should own context-to-prompt serialization. Fix: add a to_prompt()/to_messages() method on the Thread/State type.`

### F05: State Unification Audit（状态统一性审核）

- **核心思想**: agent 必须用 event-sourced `Thread{events: []}` 统一执行
  状态与业务状态。反模式是把 `retry_count` / `current_step` /
  `next_step` / `last_intent` 等执行状态独立持久化为顶层字段或独立表，
  导致状态分裂、难以重放。
- **检测信号**:
  - 反模式（强信号）: 搜索 `retry_count` / `current_step` /
    `next_step` / `last_intent` / `turn_count` 作为独立持久化字段
    （DB column / top-level dataclass field / redis key）
  - 正模式: `Thread{events: []}` / `Event[]` / `events.append(…)` /
    `reduce(events)` 出现
- **严重度**: **MID**（弱信号——独立状态字段不一定是 bug，但偏离 spec F05
  的 event-sourced 模型）
- **判据来源**: 12-factor-agents spec.md F05
- **修复建议**: 把执行状态字段折叠进 `Thread{events: []}` 的 event 流，
  通过 reducer 派生 `retry_count` 等运行时视图
- **finding 格式**:
  `[F05-MED] <file:line> — execution state (<field>) persisted independently rather than derived from an event stream; per spec F05 unify state under Thread{events:[]}. Fix: append a StateUpdated event, derive <field> in the reducer.`

### F07: Human-as-Tool Audit（人即工具审核）

- **核心思想**: 联系人类必须通过结构化的 human-input intent 类
  （`RequestHumanInput` / `RequestHumanApproval` / `ClarificationRequest`），
  由 agent 主动 emit 并在循环中处理。禁止用 `interrupt()` / `input()` /
  抛 `NeedHumanHelp` 异常来联系人类——这把控制流交给了语言运行时而非
  agent 自己。
- **检测信号**:
  - 正模式（缺失也是弱信号）: 搜索 `request_human_input` /
    `request_human_approval` / `ClarificationRequest` / `HumanInputRequest`
    intent 类定义
  - 反模式（强信号）: `input(…)` / `interrupt()` /
    `raise NeedHumanApproval(…)` / `raise HumanHelpRequired(…)` 在 agent
    循环内部
- **严重度**:
  - 反模式命中 = **HIGH**（控制流外泄给运行时）
  - 正模式缺失 = **MID**（弱信号）
- **判据来源**: 12-factor-agents spec.md F07
- **修复建议**: 定义 typed intent 类，agent 在循环里 emit 它，由外部
  dispatcher 实际暂停/恢复执行
- **finding 格式**:
  - 反模式:
    `[F07-HIGH] <file:line> — human contact via <interrupt()/input()/exception>; per spec F07 humans must be a tool the agent calls, not a control-flow hijack. Fix: emit a RequestHumanInput intent, handle in the dispatch loop.`
  - 缺失:
    `[F07-MED] <file:line> — no structured human-input intent class found; per spec F07 model human contact as a typed intent. Fix: add a RequestHumanInput/ClarificationRequest intent class.`

### F09: Error Compaction Audit（错误压缩审核）

- **核心思想**: agent 必须把工具/LLM 错误回灌进 context（让后续 LLM 调用
  能看到错误信息），**且**实现 `consecutive_errors` 熔断三件套——计数 +
  阈值 + 触发后停止。否则 agent 会在同一个错误上无限重试。
- **检测信号**（三件套都要命中才算合规）:
  - 错误回灌: `except … as e: context.append({"role": "system",
    "content": f"Error: {e}"})` 或等价的把异常文本写回 context 的模式
  - 熔断计数: `consecutive_errors` / `error_count` / `errors_in_a_row`
    计数器
  - 熔断逻辑: `if consecutive_errors >= MAX: break` / `raise` /
    `return` 显式停止
- **严重度**:
  - 三件套全缺 = **HIGH**（强信号，spec F09 强制要求）
  - 部分缺失（有回灌但无熔断，或反之）= **MID**
- **判据来源**: 12-factor-agents spec.md F09
- **修复建议**: 把异常文本回灌进 context；维护一个
  `consecutive_errors` 计数；超过阈值时 emit `Failed` intent 退出循环
- **finding 格式**:
  `[F09-HIGH] <file:line> — no error-compaction trio (reinject + consecutive_errors + circuit-break); per spec F09 agent must feed errors back to context and trip a breaker. Fix: append error text to context, increment consecutive_errors, break when >= MAX.`

### F01/F04: Intent Dispatch Audit（Intent 分发审核，F1·F4 合并去重）

- **核心思想**: agent 必须用 typed intent class + 显式 dispatch 分发
  （`switch(intent)` / `match intent:` / `if isinstance(intent, …):`）。
  反模式是 `agent.run(raw_text)` 直接把用户原文喂给 LLM 让它自行决定
  下一步，没有任何结构化 intent。
- **检测信号**:
  - 正模式: typed intent class (`class Intent: …` / `class Done: …` /
    `class CallTool: …` / `@dataclass class RequestHumanInput`) +
    `match intent:` / `switch(intent)` / `isinstance(intent, …)` 分发
  - 反模式（强信号）: `agent.run(user_text)` / `agent.run(message)` /
    `agent.invoke({"input": raw_text})` 无前置 intent 分类
- **严重度**:
  - 反模式命中 = **HIGH**（与 F08 共享检测段——`agent.run(rawText)`
    通常也意味着控制流外泄）
  - typed intent 缺失但用了结构化 messages = **MID**（弱信号）
- **判据来源**: 12-factor-agents spec.md F01 + F04（合并去重：F01 要求
  typed intent，F04 要求显式 dispatch，二者检测段重合）
- **修复建议**: 先定义 intent 类型族（`Done` / `CallTool(name, args)` /
  `RequestHumanInput(question)` / `Respond(text)`），再写显式 dispatch
- **finding 格式**:
  - 反模式:
    `[F01F04-HIGH] <file:line> — agent.run(raw_text) with no typed intent layer; per spec F01+F04 dispatch must be on a typed intent, not raw user input. Fix: classify_intent() → typed intent class → switch(intent) dispatch.`
  - 缺失:
    `[F01F04-MED] <file:line> — no typed intent class hierarchy found; per spec F01 model agent steps as typed intents. Fix: introduce a small Intent union (Done/CallTool/RequestHumanInput/Respond).`

## Reference 型提示（不进 audit，仅作参考）

下列 factor 在 spec 中是叙述性 / 运行时概念，**没有可静态检测的代码
标志**，不产生 finding。仅当 reviewer 在人工评审中自然观察到时，可作为
散文提示写入报告的 "Observations" 部分，但不得计入 severity 评分或
finding ID。

| Factor | 提示内容 | 不检测原因 |
|--------|---------|-----------|
| F06 Pause/Resume | agent 应支持 `launch` / `pause` / `resume` API + webhook resume，使长任务可暂停恢复 | 原文纯叙述，无静态代码标志（任何函数签名都可能或不可能服务于此目的） |
| F10 Small Focused Agents | agent 应小而聚焦，单 agent 步骤数 / 职责切分有上限 | 需运行时统计步数才能判断，静态扫描无法度量 |
| F11 Trigger From Anywhere | agent 应能从多渠道（webhook / cron / CLI / chat）触发 | 无静态信号——入口多样性是部署期属性 |
| F12 Stateless Reducer | reducer 应是纯函数（无副作用、确定性） | "纯函数" 是语义概念，无可靠静态判据（需类型系统或形式化验证） |

## 统一 finding 格式

所有 finding 使用同一前缀格式：

```
[FNN-<级别>] <file:line> — <一句话问题陈述>; per spec FNN <判据引用>. Fix: <一句话修复建议>.
```

字段约定:

| 字段 | 取值 | 说明 |
|------|------|------|
| `FNN` | `F01F04` / `F02` / `F03` / `F05` / `F07` / `F08` / `F09` | factor 编号；F01+F04 合并去重为 `F01F04` |
| `<级别>` | `HIGH` / `MED` | 见下方定级规则；不使用 `CRIT` / `LOW` / `INFO`（agent 维度只分两档） |
| `<file:line>` | `src/agent.py:42` 或 `src/agent.py:42-58` | 精确到行；多行反模式用范围 |
| `<判据引用>` | `spec F08 agents must own the loop` 等 | 引用 spec.md 中具体 factor 的判据段落，不要泛指 |
| `<修复建议>` | 一句话 | 与该 factor 的 "修复建议" 字段一致 |

定级规则（**严格遵守，避免误报**）:

| 信号类型 | 级别 | 理由 |
|---------|------|------|
| 强反模式命中（框架黑盒 / `agent.run(rawText)` / `interrupt()` 联系人类 / 错误三件套全缺） | `HIGH` | spec 明确禁止，命中即违规 |
| 弱信号缺失（无序列化器 / 无 intent 类 / 无 Thread{events} / 无 human-input intent） | `MID` | 可能是简单 agent 的合规简化，不强制 HIGH |
| Reference 型 factor（F06/F10/F11/F12） | 不报 | 无静态信号，不产生 finding |

**禁止**：弱信号缺失报 HIGH（误报率高）；强反模式报 MED（漏报风险）；
对非 agent 代码触发本维度（应直接跳过）。

## Severity Mapping

| Issue Type | Severity |
|------------|----------|
| 控制流外泄给框架 graph (F08) | High |
| 框架黑盒实例化隐藏 prompt (F02) | High |
| `agent.run(raw_text)` 无 intent 层 (F01F04) | High |
| `interrupt()`/异常联系人类 (F07) | High |
| 错误未回灌 + 无熔断 (F09) | High |
| 缺 context 序列化器 (F03) | Medium |
| 状态独立持久化非 event-sourced (F05) | Medium |
| 缺 human-input intent 类 (F07) | Medium |
| 缺 typed intent 层但用结构化 messages (F01F04) | Medium |

## References

- 12-factor-agents spec.md — F01, F02, F03, F04, F05, F06, F07, F08, F09,
  F10, F11, F12（外部规格，本维度判据来源）
- [review-workflow.md](../review-workflow.md) — Engine A 共享工作流
- [templates/report.md](../templates/report.md) — finding 报告外壳
  （本维度的 finding 嵌入 Engine A 报告的 Issues 段，前缀用 `[FNN-级别]`
  而非通用 `[HIGH-001]`）

## Related Commands

- [architecture.md](architecture.md) — 通用架构审核（耦合/模式/分层），
  与本维度无重叠：architecture 看模块边界，agent 看 LLM 循环所有权
- [quality.md](quality.md) — 通用质量审核（code smell / 复杂度），
  本维度不重复报通用质量问题
- [correctness.md](correctness.md) — 通用正确性审核（边界 / 并发），
  agent 循环本身的正确性 bug 走这里，agent 架构反模式走 agent 维度
- [security.md](security.md) — 通用安全审核；agent prompt 注入等
  安全问题归 security，不归 agent
