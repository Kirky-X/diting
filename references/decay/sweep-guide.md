# 衰退诊断 — 全量扫描指南

顺序自主管道：**review → test → debt → audit**。原地修复发现，
迭代至干净或达上限，报告残留项。一个交互点：
步骤 0（预飞行同意） — 获批准后管道无人值守运行直至步骤 8。

每条发现遵循铁律：**Symptom → Source → Consequence → Remedy**。

---

### 步骤 0 — 预飞行同意门

**目标：** 前置陈述范围、成本和不可逆性；获得一次性明确同意，
以便后续步骤无需再询问。

0a. 如果在 git 仓库中使用 `git ls-files | wc -l` 估算文件数量，否则
   使用 `find . -type f -not -path '*/.git/*' -not -path '*/node_modules/*' -not -path '*/.venv/*' -not -path '*/build/*' -not -path '*/dist/*' -not -path '*/vendor/*' -not -path '*/target/*' | wc -l`。数量级足够。

0b. 原样显示此通知并填入估算值。不要改写 —
   用户同意的是此确切范围。

   ```
   ⚠️  Full Sweep mode — Full Repository Sweep & Auto-Fix

   Scope:    Four analysis dimensions run in sequence — PR code decay (R1–R6),
             test quality (T1–T6), tech debt, architecture. Edits are made in
             place inside the detected project scope.
   Estimated files in scope: ~N

   Order:    PR-review → test-quality → tech-debt → architecture-audit.
             Each dimension scans, queues, and fixes before the next starts.

   Autonomy: Fully autonomous. Safe single-file fixes apply directly. Multi-file
             fixes that have test coverage AND do not break a public interface
             also apply directly. High-risk fixes (public API break, cross-module
             structural change, or no test coverage) are NOT applied — they are
             recorded in the residual report for human review.

   Iteration: After each dimension pass, modified files + same-module + static
             consumers are re-scanned. A finding that fails to fix 3 times is
             retired to the unresolvable set and never re-queued. Non-critical
             rounds cap at 3 iterations; critical findings iterate until
             resolved or retired.

   Git impact: The pipeline edits files. It does NOT commit, push, or amend.
             If you have uncommitted work you want to preserve, commit or stash
             first.

   Proceed with full autonomous sweep? [Y/n]
   ```

0c. 解析回复（首次匹配获胜，按顺序评估规则）：
   1. **硬否定**（`no`、`n`、`abort`、`cancel`、`取消`、`不要`）：中止并输出 "Aborted before scan — no files modified."
   2. **同意**（`Y`、`yes`、`ok`、`sure`、`proceed`、`go`、`continue`、`好`、`好的`、`行`、`可以`）：进入步骤 1。
   3. **软暂停**（`wait`、`hold on`、`等一下`、`等我`、`let me`）：一行确认（"Understood, waiting"），然后等待用户下一条消息并从规则 1 重新评估。
   4. **提问**：回答问题，然后再次原样显示通知并等待下一条回复。如果下一条回复不是同意（规则 2） — 无论是第二个问题、另一次暂停还是任何其他内容 — 中止并输出 "Aborted — did not receive consent after clarification."

0d. 同意后，在步骤 8 之前不再提问。

---

### 步骤 1 — 范围枚举和状态初始化

1a. 如果用户未指定文件或目录，应用 `common.md` 中的 Auto Scope Detection。
   否则尊重用户的显式范围。

1b. 如果项目根目录存在 `.decay-review.yaml`，读取它。根据 common.md 应用 `disable`、
   `severity`、`ignore`、`focus` 和 `custom_risks`。记录应用的配置值并在所有迭代轮次中复用 — 即使文件被修改也不要在步骤 6 中重新读取。

1c. 初始化管道状态（在所有轮次中持久化）：

   - **`unresolvable`**（集合）：3 次失败尝试后退役的发现 — 以 `(file, line_range, risk_code)` 为键；`signature` 用于打破平局。永不重新入队。
   - **`non_critical_rounds`**（int, 0）：每轮产生 Warning/Suggestion 时递增；干净轮次时重置。
   - **`fix_log`**（列表）：每次修复包含文件、行范围、风险代码、描述和结果（`applied` / `reverted` / `retired`）。

1d. 在步骤 8 的 Fix Report 输出缓冲区中记录最终范围文件列表。

---

### 步骤 2 — PR-review 通行（R1–R6 代码衰退）

针对 `decay-risks.md` 中定义的所有 R 系列风险扫描范围内的每个文件。

2a. 对于每个 R 风险，应用其症状清单。将每个命中记录为发现，
   包含：风险代码、文件 + 大致行范围、Symptom、Source、
   Consequence、Remedy、Severity（Critical / Warning / Suggestion），以及
   **Fix-Class**（见步骤 2b）。

2b. 为每个发现分配 Fix-Class：

   | 类 | 标准 |
   |-------|----------|
   | **Safe** | 单文件且完全本地：重命名非导出符号、抽取常量、移除死代码、在叶子处添加空守卫、为未测试的纯函数添加测试脚手架。任何修改或移除导出符号的变更即使在一个文件中也不是 Safe。 |
   | **Extended-Safe** | 多文件但 (a) 存在项目测试命令且修复前通过，AND (b) 变更不重命名、移除或更改任何公开导出符号的签名，AND (c) 此轮触及 ≤ 5 个文件。 |
   | **Residual** | 公共 API 破坏、跨服务边界变更、无测试覆盖可回退，或修复方案模糊。不应用 — 进入步骤 8 残留报告。 |

2c. 跳过任何匹配 `unresolvable` 集合中条目的发现。

2d. 在此维度中应用每个 Safe 和 Extended-Safe 修复，每个严重度层级内最低风险
   优先。对于每个修复：Edit 或 Write，然后向 `fix_log` 追加一行，结果为 `applied`。如果两个修复触及同一文件中重叠的行范围，
   先应用更高严重度的，重新读取文件，然后应用下一个。

2e. 此维度所有修复完成后，如果存在项目测试/lint 命令则运行
   （`package.json` 脚本、`pytest`、`cargo test`、`go test ./...` 等）。
   如果测试失败：按相反顺序一次一个地从此维度回退修复，
   每次回退后重新运行测试命令，直到测试通过。
   在 `fix_log` 中将每个回退的修复标记为结果 `reverted`，并将发现
   提升为 **Residual**。如果未找到测试命令，在报告中记录一次并继续。

2f. 记录维度摘要：N 个已扫描、M 个 Safe 已应用、K 个 Extended-Safe 已应用、
   R 个已回退、P 个 Residual。

---

### 步骤 3 — test-quality 通行（T1–T6 测试衰退）

针对 `test-decay-risks.md` 中定义的 T 系列风险扫描测试文件（和未测试的生产代码）。

遵循与步骤 2 相同的子步骤（分类 → 应用 → 验证 → 摘要），
使用 T 前缀风险代码。对于完全没有测试覆盖的生产文件，
记录为 T5（Coverage Illusion）。添加纯函数测试的测试脚手架是
**Safe**；添加需要新测试基础设施的测试是 **Residual**。

---

### 步骤 4 — tech-debt 通行（技术债务累积）

通过债务视角重新分类 R 发现 — 同样症状在累积规模上：
重复的重复、分层的变通方法、过期的 `TODO`/`FIXME` 簇、死
标志。用 **Pain (1–3) × Spread (1–3)** 评分；总计 7–9 = Critical，
4–6 = Warning，1–3 = Suggestion。对模式级
出现应用严重度提升（孤立 Suggestion → 4+ 模块 Warning）。

遵循与步骤 2 相同的子步骤。债务发现通常跨多个文件，
更可能落入 Extended-Safe 或 Residual 而非 Safe。

---

### 步骤 5 — architecture-audit 通行（架构完整性）

扫描全范围以发现架构级问题。依赖方向
症状（倒置依赖、循环 import、跨领域耦合）在
`decay-risks.md` 风险 5 中定义 — 使用该清单。步骤 5
还涵盖 R5 不涉及的架构关注：缺少
抽象层、God 模块、领域代码内泄漏的基础设施、
和接缝边界违反。

大多数架构发现按定义是 **Residual** — 它们需要人类对
模块边界的判断。少数是 Extended-Safe（例如，将 3+ 模块中使用的共享
常量抽取到尚未被任何东西 import 的新模块中）。
不要自动重构模块布局、重命名包或更改公共导出。

遵循与步骤 2 相同的子步骤。

---

### 步骤 6 — 迭代循环

**目标：** 重新扫描修复触及的内容并收敛。在干净轮次、
达上限或无进展时停止。

6a. 构建重新扫描范围：
   - 当前轮次步骤 2–5 中修改的每个文件，加上
   - 与修改文件同模块的每个文件，加上
   - 静态 import 自修改文件的每个文件。

   不要重新扫描其依赖未被触及的文件。在
   "模块"可能跨越数百个文件的单体仓库中，将同模块桶缩小到 import 自或被修改文件 import 的文件（仅
   直接依赖图）。

6b. 在重新扫描范围上重新运行步骤 2–5。对于此轮次中的每个新发现：
   - 如果匹配 `unresolvable` 中的条目 → 跳过。
   - 否则如果是 🔴 Critical → 入队并修复；Critical 发现代迭代直至
     解决或退役（3 次失败尝试 → `unresolvable`）。
   - 否则 🟡 Warning / 🟢 Suggestion → 入队并修复，受下方上限约束。

6c. 在所有修复尝试后分类轮次：
   - **干净轮次**（`unresolvable` 之外无新发现）：管道
     收敛 → 进入步骤 7。
   - **仅 Critical 轮次**：不要递增 `non_critical_rounds`；返回
     6a。
   - **混合或非关键轮次**（产生任何 Warning / Suggestion）：
     将 `non_critical_rounds` 递增 1。如果达到上限（默认 3，
     或 `.decay-review.yaml` 中的 `sweep.max_iterations`），进入步骤 7，
     剩余的非关键发现记录为
     `"Unresolved — iteration cap reached"`。否则返回 6a。

6d. 修复重试规则：如果单个发现跨任何轮次组合
   验证（步骤 2e）失败 3 次，将其退役到 `unresolvable`，原因为
   `"3-retry budget exhausted"`，并停止尝试。

---

### 步骤 7 — 残留聚合

收集所有未原地修复的内容，去重：

- 步骤 2–5 的所有 Residual 类发现（首轮 + 重新扫描轮次）
- 所有 `unresolvable` 条目及其退役原因
- 步骤 6c 的所有迭代上限残留

按 Critical → Warning → Suggestion 排序。在每个严重度内，列出文件路径、
风险代码、Symptom（一行）、Remedy（一行），以及未应用的原因
（`public API break` / `no test coverage` / `3-retry budget` /
`iteration cap`）。

---

### 步骤 8 — 扫描报告

输出最终报告。使用 `common.md` 中的标准报告模板，并附加以下内容：

```
# Decay Diagnosis — Full Sweep Report
Mode: Full Sweep | Scope: <files or directory>
Config: .decay-review.yaml applied (N risks disabled, M paths ignored)   # omit if no config

## Dimension Summary
| Dimension | Scanned | Safe Applied | Extended Applied | Reverted | Residual |
|-----------|---------|--------------|------------------|----------|----------|
| Review (R1–R6) | ... | ... | ... | ... | ... |
| Test (T1–T6)   | ... | ... | ... | ... | ... |
| Debt           | ... | ... | ... | ... | ... |
| Audit          | ... | ... | ... | ... | ... |

## Iteration History
Round 1: <classification — clean / critical-only / mixed>, <N> new findings
Round 2: ...
Stopped at: clean round | iteration cap | no outstanding criticals

## Fix Log
| # | File | Lines | Risk | Outcome  | Change |
|---|------|-------|------|----------|--------|
| 1 | ...  | ...   | R2   | applied  | Extract repeated constant |
| 2 | ...  | ...   | T4   | reverted | Test regression; promoted to Residual |
...

## Health Score Delta
Before: <estimated score>/100  →  After: <estimated score>/100
(Re-run Health Dashboard mode for an exact recalculation.)

## Residual Items  (<K> not applied)
<Iron Law entries, sorted Critical → Suggestion, with "Not applied because: ..." line>

## Summary
- Total findings detected: <N>
- Fixed this sweep: <M>
- Residual (needs human review): <K>
- Unresolvable (3-retry exhausted): <U>
```

如果没有残留项且没有 unresolvable 条目，以以下结尾：
**"Sweep complete — codebase is clean."**

**报告中的 Mode 行：** `Full Sweep`
