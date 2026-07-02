# 自定义风险加载指南

当 `.decay-review.yaml` 包含 `custom_risks` 映射时，本指南规定这些风险的加载和扫描方式。自定义风险使用 `Cx` 代码（C1、C2、…）— 与标准 R1–R6 和 T1–T6 命名空间不冲突。

---

## 加载

1. 对于 `custom_risks` 中的每个条目，验证其包含：
   - `name` — 非空字符串
   - `question` — 要询问的诊断问题
   - `symptoms` — 非空的症状模式列表
   - `severity` — 至少包含以下之一的映射：`critical`、`warning`、`suggestion`

2. 将每个有效条目注册为 `Cx` 代码，与 R1–R6 / T1–T6 并列。加载后，`Cx` 代码成为同一配置文件中 `disable`、`focus` 和 `severity` 字段的有效目标。

3. 将任何验证错误报告为配置警告（不要中止审查）：
   - 缺少必需字段：`"Config warning: C1 missing 'symptoms'"`
   - 无效代码格式（必须是 `C` 后跟数字）：跳过，记录错误
   - 代码与 R/T 命名空间冲突：跳过，记录错误

---

## 扫描

在分析过程中，将每个自定义风险视为标准流程之后的额外步骤：

- 使用 `question` 作为诊断问题
- 使用 `symptoms` 作为症状查找列表
- 使用 `severity` 映射进行分层分类
- 应用铁律：`Source` 字段应为 `"[Project-defined risk] — <risk name>"`
- 将自定义风险发现包含在 Health Score 中（扣分规则与 R/T 代码相同）
- 在报告中，自定义发现出现在标准发现之后的 **### Project-Specific Risks** 子标题下

---

## 配置验证补充

以下代码在 `disable`、`focus` 和 `severity` 中有效：
- 标准：`R1`–`R6`、`T1`–`T6`
- 自定义：在 `custom_risks` 中定义的任何 `Cx` 代码
- 任何其他代码：跳过并发出 `"Config warning: X is not a valid risk code"`
