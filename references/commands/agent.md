# Agent Code Review — 12-Factor Agents Audit

Agent Code Review Mode — audits LLM agent code against 12-factor agents architecture principles.

## Usage

```bash
review agent [target-path]      # 全量 aggregate 审计（默认）：F1·F4, F2, F3, F5, F7, F8, F9
review agent <factor> [target]  # 单 factor 精细审计，<factor> 见下表
```

| `<factor>` 别名 | 对应检测器 | 类型 |
| --------------- | ---------- | ---- |
| `tool-calls`/f1 | `processes/tool-calls.md` | detect |
| `prompts`/f2 | `processes/prompts.md` | detect |
| `context`/f3 | `processes/context.md` | detect |
| `structured-outputs`/f4 | `processes/structured-outputs.md` | detect |
| `state`/f5 | `processes/state.md` | detect |
| `pause-resume`/f6 | `processes/pause-resume.md` | reference-only |
| `contact-humans`/f7 | `processes/contact-humans.md` | detect |
| `control-flow`/f8 | `processes/control-flow.md` | detect (core) |
| `errors`/f9 | `processes/errors.md` | detect |
| `scope`/f10 | `processes/scope.md` | reference-only |
| `triggers`/f11 | `processes/triggers.md` | reference-only |
| `reducer`/f12 | `processes/reducer.md` | reference-only |

单 factor 调用时，读对应 `agent-factors/processes/<factor>.md` 执行；reference 型 factor（F6/F10/F11/F12）无静态信号，只输出说明不产生发现。全量 aggregate 审计（无 factor 参数）执行下方 Detection Methods 的检测逻辑。

## Scope and Overlap

This dimension audits LLM agent code against 12-factor agents architecture principles. It does **not overlap** with general dimensions
(security / performance / quality / architecture / correctness / …):
those check general software properties and contain no agent-specific checks. `agent` checks
agent-specific architecture and reliability patterns — control-flow ownership, prompt ownership, context
serialization, intent dispatch, error compaction, human-as-tool, state unification. If a finding
applies equally to non-agent code, route it to a general dimension; do not duplicate reports here.

**Activation Threshold**: only applies when the target imports an agent framework
(`langgraph` / `crewai` / `autogen` / `llama_index.agent` / OpenAI Agents SDK
/ equivalent) or hand-written LLM loops (`while True` + LLM call + tool dispatch).
Silently skip for non-agent code — do not force applicability.

## Detection Methods

### F08: Control-Flow Ownership Audit

- **Core Idea**: agent must own its control loop — hand-written `while True` + explicit
  `continue` / `break` / `return`. Strong anti-pattern is delegating the loop to framework graph orchestration
  (`langgraph.StateGraph` / `crewai.Crew.run` / `autogen.GroupChatManager`),
  where no explicit loop is visible in user code.
- **Detection Signals**:
  - `import langgraph` / `from langgraph.graph import StateGraph` /
    `from crewai import Crew` / `from autogen import …` appears
  - **and** agent's own source code has no `while True:` / `while running:` /
    `while not done:` literal loop
  - Uses `graph.add_node` + `graph.add_edge` + `add_conditional_edges` to express
    iteration (indicating the loop has been taken over by the framework)
- **Severity**: **HIGH** (strong anti-pattern, spec F08 explicitly requires the agent to own the loop)
- **Source**: 12-factor-agents spec.md F08
- **Fix**: replace framework graph orchestration with hand-written loops
  ```python
  while True:
      intent = classify_intent(llm, context)
      if isinstance(intent, Done):
          return context
      result = dispatch(intent, context)
      context = reduce(context, result)
  ```
- **Finding Format**:
  `[F08-HIGH] <file:line> — control flow delegated to <framework> graph; per spec F08 the agent must own the loop. Fix: hand-written while True + switch(intent) + continue/return.`

### F02: Prompt Ownership Audit

- **Core Idea**: agent must own its prompt template, not rely on framework black-box instantiation.
  Framework black boxes hide prompt construction inside
  `Agent(role=…)` / `Crew(agents=…, tasks=…)` /
  `Task(expected_output=…)`, making prompts unauditable and non-evolvable.
- **Detection Signals**:
  - `Agent(role="…", goal="…", backstory="…")` (crewai)
  - `Crew(agents=[…], tasks=[…])` (crewai)
  - `Task(description=…, expected_output=…)` (crewai)
  - `AssistantAgent(name=…, system_message=…)` where system_message is a literal string
    (autogen)
  - `initialize_agent(llm=…, agent_kwargs={…})` (legacy langchain agent)
  - Any instantiation pattern that delegates prompt assembly to the framework
- **Severity**: **HIGH** (strong signal, spec F02)
- **Source**: 12-factor-agents spec.md F02
- **Fix**: custom prompt templates (string template / f-string / jinja2),
  explicitly assembled and passed to the LLM; do not use the framework's role/backstory/expected_output fields
- **Finding Format**:
  `[F02-HIGH] <file:line> — framework black-box instantiation (<pattern>) hides prompt construction; per spec F02 agents must own their prompts. Fix: inline prompt template, pass rendered string to the LLM call directly.`

### F03: Context Window Serialization Audit

- **Core Idea**: agent must have an explicit context serializer (`to_prompt` /
  `serializeForLLM` / `pack` or similar) to convert business state structures into
  strings consumable by the LLM. A missing serializer typically means context is implicitly assembled (fragile, hard to evolve).
- **Detection Signals**:
  - Search for `to_prompt` / `serializeForLLM` / `pack` / `to_messages` /
    `render_context` method definitions
  - Absence = weak signal (not necessarily a bug, but spec F03 requires explicit serialization)
- **Severity**: **MID** (weak signal absence reports MID, not HIGH, to avoid false positives — some
  simple agents use list[dict] to pass messages directly and are compliant)
- **Source**: 12-factor-agents spec.md F03
- **Fix**: implement an explicit context serialization method that serializes Thread/Events
  to prompt text or a messages array
- **Finding Format**:
  `[F03-MED] <file:line> — no explicit context serializer found; per spec F03 the agent should own context-to-prompt serialization. Fix: add a to_prompt()/to_messages() method on the Thread/State type.`

### F05: State Unification Audit

- **Core Idea**: agent must use event-sourced `Thread{events: []}` to unify
  execution state with business state. Anti-pattern is persisting `retry_count` / `current_step` /
  `next_step` / `last_intent` as independent top-level fields or separate tables,
  causing state fragmentation and replay difficulties.
- **Detection Signals**:
  - Anti-pattern (strong signal): search for `retry_count` / `current_step` /
    `next_step` / `last_intent` / `turn_count` as independent persisted fields
    (DB column / top-level dataclass field / redis key)
  - Positive pattern: `Thread{events: []}` / `Event[]` / `events.append(…)` /
    `reduce(events)` appears
- **Severity**: **MID** (weak signal — independent state fields are not necessarily bugs, but deviate from the spec F05
  event-sourced model)
- **Source**: 12-factor-agents spec.md F05
- **Fix**: fold execution state fields into the `Thread{events: []}` event stream,
  derive `retry_count` and similar runtime views via the reducer
- **Finding Format**:
  `[F05-MED] <file:line> — execution state (<field>) persisted independently rather than derived from an event stream; per spec F05 unify state under Thread{events:[]}. Fix: append a StateUpdated event, derive <field> in the reducer.`

### F07: Human-as-Tool Audit

- **Core Idea**: contacting humans must be through structured human-input intent classes
  (`RequestHumanInput` / `RequestHumanApproval` / `ClarificationRequest`),
  actively emitted by the agent and handled within the loop. Using `interrupt()` / `input()` /
  throwing `NeedHumanHelp` exceptions to contact humans is prohibited — this delegates control flow to the language runtime rather than
  the agent itself.
- **Detection Signals**:
  - Positive pattern (absence is also a weak signal): search for `request_human_input` /
    `request_human_approval` / `ClarificationRequest` / `HumanInputRequest`
    intent class definitions
  - Anti-pattern (strong signal): `input(…)` / `interrupt()` /
    `raise NeedHumanApproval(…)` / `raise HumanHelpRequired(…)` inside the
    agent loop
- **Severity**:
  - Anti-pattern hit = **HIGH** (control flow leaked to runtime)
  - Positive pattern absent = **MID** (weak signal)
- **Source**: 12-factor-agents spec.md F07
- **Fix**: define typed intent classes, agent emits them in the loop, handled by an external
  dispatcher that actually pauses/resumes execution
- **Finding Format**:
  - Anti-pattern:
    `[F07-HIGH] <file:line> — human contact via <interrupt()/input()/exception>; per spec F07 humans must be a tool the agent calls, not a control-flow hijack. Fix: emit a RequestHumanInput intent, handle in the dispatch loop.`
  - Missing:
    `[F07-MED] <file:line> — no structured human-input intent class found; per spec F07 model human contact as a typed intent. Fix: add a RequestHumanInput/ClarificationRequest intent class.`

### F09: Error Compaction Audit

- **Core Idea**: agent must feed tool/LLM errors back into context (so subsequent LLM calls
  can see error messages), **and** implement a `consecutive_errors` circuit-breaker trio — counter +
  threshold + stop after trigger. Otherwise the agent will retry the same error infinitely.
- **Detection Signals** (all three must be present for compliance):
  - Error re-injection: `except … as e: context.append({"role": "system",
    "content": f"Error: {e}"})` or equivalent pattern writing exception text back to context
  - Circuit-breaker counter: `consecutive_errors` / `error_count` / `errors_in_a_row`
    counter
  - Circuit-breaker logic: `if consecutive_errors >= MAX: break` / `raise` /
    `return` explicit stop
- **Severity**:
  - All three missing = **HIGH** (strong signal, spec F09 mandatory)
  - Partially missing (has re-injection but no circuit-breaker, or vice versa) = **MID**
- **Source**: 12-factor-agents spec.md F09
- **Fix**: re-inject exception text into context; maintain a
  `consecutive_errors` counter; emit `Failed` intent to exit the loop when threshold is exceeded
- **Finding Format**:
  `[F09-HIGH] <file:line> — no error-compaction trio (reinject + consecutive_errors + circuit-break); per spec F09 agent must feed errors back to context and trip a breaker. Fix: append error text to context, increment consecutive_errors, break when >= MAX.`

### F01/F04: Intent Dispatch Audit (F1·F4 merged, deduplicated)

- **Core Idea**: agent must use typed intent class + explicit dispatch
  (`switch(intent)` / `match intent:` / `if isinstance(intent, …):`).
  Anti-pattern is `agent.run(raw_text)` feeding raw user text directly to the LLM to decide
  the next step, with no structured intent.
- **Detection Signals**:
  - Positive pattern: typed intent class (`class Intent: …` / `class Done: …` /
    `class CallTool: …` / `@dataclass class RequestHumanInput`) +
    `match intent:` / `switch(intent)` / `isinstance(intent, …)` dispatch
  - Anti-pattern (strong signal): `agent.run(user_text)` / `agent.run(message)` /
    `agent.invoke({"input": raw_text})` without prior intent classification
- **Severity**:
  - Anti-pattern hit = **HIGH** (shares detection segment with F08 — `agent.run(rawText)`
    typically also means control flow is leaked)
  - Typed intent missing but structured messages are used = **MID** (weak signal)
- **Source**: 12-factor-agents spec.md F01 + F04 (merged and deduplicated: F01 requires
  typed intent, F04 requires explicit dispatch, their detection segments overlap)
- **Fix**: first define an intent type family (`Done` / `CallTool(name, args)` /
  `RequestHumanInput(question)` / `Respond(text)`), then write explicit dispatch
- **Finding Format**:
  - Anti-pattern:
    `[F01F04-HIGH] <file:line> — agent.run(raw_text) with no typed intent layer; per spec F01+F04 dispatch must be on a typed intent, not raw user input. Fix: classify_intent() → typed intent class → switch(intent) dispatch.`
  - Missing:
    `[F01F04-MED] <file:line> — no typed intent class hierarchy found; per spec F01 model agent steps as typed intents. Fix: introduce a small Intent union (Done/CallTool/RequestHumanInput/Respond).`

## Reference-type Hints (not audited, for reference only)

The following factors are narrative/runtime concepts in the spec with **no statically detectable code
markers** and do not produce findings. They may appear as prose observations in a reviewer's
"Observations" section during manual review, but must not count toward severity scores or
finding IDs.

| Factor | Hint | Why Not Detected |
|--------|------|-----------------|
| F06 Pause/Resume | Agent should support `launch` / `pause` / `resume` APIs + webhook resume, enabling long tasks to pause and resume | Purely narrative, no static code markers (any function signature could or could not serve this purpose) |
| F10 Small Focused Agents | Agents should be small and focused, with limits on steps/responsibilities per agent | Requires runtime step counting; static scanning cannot measure this |
| F11 Trigger From Anywhere | Agent should be triggerable from multiple channels (webhook / cron / CLI / chat) | No static signal — entry point diversity is a deployment-time property |
| F12 Stateless Reducer | Reducer should be a pure function (no side effects, deterministic) | "Pure function" is a semantic concept with no reliable static criteria (requires a type system or formal verification) |

## Unified Finding Format

All findings use the same prefix format:

```
[FNN-<level>] <file:line> — <one-sentence problem statement>; per spec FNN <criterion reference>. Fix: <one-sentence fix suggestion>.
```

Field conventions:

| Field | Values | Description |
|-------|--------|-------------|
| `FNN` | `F01F04` / `F02` / `F03` / `F05` / `F07` / `F08` / `F09` | Factor number; F01+F04 merged and deduplicated as `F01F04` |
| `<level>` | `HIGH` / `MED` | See grading rules below; `CRIT` / `LOW` / `INFO` are not used (agent dimension only has two levels) |
| `<file:line>` | `src/agent.py:42` or `src/agent.py:42-58` | Precise to line; multi-line anti-patterns use range |
| `<criterion reference>` | `spec F08 agents must own the loop` etc. | Reference the specific factor's criterion paragraph in spec.md, not generic |
| `<fix suggestion>` | One sentence | Consistent with the "Fix" field for that factor |

Grading rules (**strictly followed to avoid false positives**):

| Signal Type | Level | Rationale |
|-------------|-------|-----------|
| Strong anti-pattern hit (framework black-box / `agent.run(rawText)` / `interrupt()` contacting humans / all three error components missing) | `HIGH` | Spec explicitly prohibits; hit = violation |
| Weak signal absence (no serializer / no intent class / no Thread{events} / no human-input intent) | `MID` | May be a compliant simplification for simple agents; HIGH not enforced |
| Reference-type factors (F06/F10/F11/F12) | Not reported | No static signals; do not produce findings |

**Prohibited**: reporting weak signal absence as HIGH (high false-positive rate); reporting strong anti-pattern as MED (missed detection risk);
triggering this dimension for non-agent code (should be silently skipped).

## Severity Mapping

| Issue Type | Severity |
|------------|----------|
| Control flow leaked to framework graph (F08) | High |
| Framework black-box instantiation hides prompt (F02) | High |
| `agent.run(raw_text)` with no intent layer (F01F04) | High |
| `interrupt()`/exception for human contact (F07) | High |
| Error not re-injected + no circuit-breaker (F09) | High |
| Missing context serializer (F03) | Medium |
| Independent state persistence, not event-sourced (F05) | Medium |
| Missing human-input intent class (F07) | Medium |
| Missing typed intent layer but using structured messages (F01F04) | Medium |

## References

- **Factor spec 原文**（权威引用）：`agent-factors/content/factor-01-natural-language-to-tool-calls.md` … `factor-12-stateless-reducer.md`（每个 factor 的完整原文，引用本维度准则时 cite 对应文件的具体小节）。另含 `appendix-13-pre-fetch.md`、`brief-history-of-software.md`。
- **单 factor 精细检测器**（`agent-factors/processes/`）：每个 factor 一份独立检测脚本（`audit.md` 汇总，`control-flow.md`/`prompts.md`/`context.md`/`state.md`/`contact-humans.md`/`errors.md`/`structured-outputs.md`/`tool-calls.md` 为 detect 型，`pause-resume.md`/`scope.md`/`triggers.md`/`reducer.md` 为 reference 型）。当用户要审计**单个 factor**（如 "只看 prompt ownership"、"审查控制流"）时，读对应 `processes/<factor>.md` 而非本文件的 aggregate 检测逻辑。
- [review-workflow.md](../review-workflow.md) — Engine A shared workflow
- [templates/report.md](../templates/report.md) — finding report shell
  (this dimension's findings are embedded in Engine A's Issues section, prefixed with `[FNN-level]`
  instead of the generic `[HIGH-001]`)

## Related Commands

- [architecture.md](architecture.md) — general architecture review (coupling/patterns/layering),
  no overlap with this dimension: architecture checks module boundaries, agent checks LLM loop ownership
- [quality.md](quality.md) — general quality review (code smells / complexity),
  this dimension does not duplicate general quality issues
- [correctness.md](correctness.md) — general correctness review (edge cases / concurrency),
  correctness bugs in the agent loop itself go here, agent architecture anti-patterns go to the agent dimension
- [security.md](security.md) — general security review; agent prompt injection and similar
  security issues belong to security, not agent
