# 安全设计模式

> 安全专属模式目录（架构 / 设计 / 实现三层）。
> 关于"GoF 模式加安全包装"（Secure Singleton、Secure
> Factory 模板等）见 [pattern-classification.md](pattern-classification.md)
> —— 这是不同的维度。本文件是独立的安全模式
> 体系（Single Access Point、Check Point、Pathname Canonicalization、RAII…）。

## 三层一览

| 层级               | 关注点                                     | 模式                                                                                                                      |
| ------------------ | ------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------- |
| **架构**   | 信任边界、系统拓扑           | Single Access Point、Check Point、Distrustful Decomposition、Separation of Privilege、Defer to Kernel                         |
| **设计**         | 组件交互、职责拆分 | Secure Factory、Secure Policy Factory、Secure Chain of Responsibility、Secure State Machine、Secure Visitor、Protection Proxy |
| **实现** | 单点防御、代码细节           | Input Validation、Secure Logging、Clear Sensitive Information、Pathname Canonicalization、Secure Directory、RAII              |

经验法则：高层失败无法由低层补偿 ——
架构缺口不能靠添加输入验证修复。

---

## 架构层模式

### Single Access Point（单一访问点）

- **意图**：所有外部访问流经一个可监控的入口。
- **何时使用**：系统有多条入口路径（HTTP + CLI + 队列 + cron）
  且需强制一致的认证/审计/限流。
- **审查信号**：认证检查在多个 controller 重复；某入口路径
  绕过日志；`@login_required` 散落于每个 handler 而非
  网关/过滤器。
- **反信号**："我们加了新内部端点却忘了保护。"

### Check Point（检查点）

- **意图**：在定义良好的交互点插入安全检查，而非
  散落于业务逻辑。
- **何时使用**：横切关注点（认证、限流、输入验证、
  审计）须在 handler 前按已知顺序运行。
- **审查信号**：安全逻辑混入业务方法；"受信任"内部调用跳过
  检查；顺序依赖的检查（认证在限流前？）
  无强制排序。

### Distrustful Decomposition（不信任分解）

- **意图**：将系统拆分为互不信任的组件；
  一个组件被攻破不会级联。
- **何时使用**：处理不可信输入与特权操作并存；解析器、
  网络监听器、插件宿主。
- **审查信号**："低信任"组件持有与
  核心相同的凭据；解析器失败冒泡为特权操作；同一进程的
  前端与后端间无特权边界。

### Separation of Privilege（特权分离）

- **意图**：安全关键操作需两个或更多组件/角色
  共同同意；无单点控制。
- **何时使用**：敏感操作 —— 资金转账、密钥释放、特权
  授予、生产部署。
- **审查信号**：一个服务/账户可独立完成整个敏感操作；
  "admin" 角色将所有强大权限捆绑在一次授予中。
- **注意**：与最小权限配对 —— Separation 拆分权限，Least
  Privilege 最小化每份权限。

### Defer to Kernel（推迟到内核）

- **意图**：对于检查时/使用时（TOCTOU）与访问控制
  决策，委托给 OS 内核而非在应用代码中模拟。
- **何时使用**：按用户身份访问文件、setuid 式特权、
  验证后重新打开文件。
- **审查信号**：应用代码先 `access(path, R_OK)` 再 `open(path)` ——
  经典 TOCTOU；手搓内核已强制的权限检查。

---

## 设计层模式

### Secure Factory（安全工厂）

- **意图**：以受控方式创建安全相关对象，使
  半配置或不一致的实例无法存在。
- **何时使用**：构造加密上下文、认证策略链、策略
  对象 —— 配置错误本身即漏洞。
- **审查信号**：安全配置在调用方代码中逐字段拼装
  （`ctx.setAlgorithm(...); ctx.setKey(...)` —— 漏掉一个怎么办？）。

### Secure Policy Factory（安全策略工厂）

- **意图**：基于上下文（环境、租户、角色）从封闭、已审查的集合
  选择安全策略 —— 绝不临时拼装。
- **何时使用**：生产/预发/测试不同策略，或每租户
  隔离规则。
- **审查信号**：策略由松散标志/字符串构造而非
  固定枚举；开发策略意外可用于生产。

### Secure Chain of Responsibility（安全责任链）

- **意图**：将安全检查排序为链，每阶段可拒绝；
  链是通往 handler 的唯一路径。
- **何时使用**：多阶段请求验证（认证 → 授权 → 输入检查 →
  限流 → 审计 → handler）。
- **审查信号**：任何检查可通过直接调用 handler
  绕过；顺序未强制（限流在认证前会泄露用户存在性）。

### Secure State Machine（安全状态机）

- **意图**：将安全相关生命周期（会话、账户、订单）建模为
  显式状态与受守卫的转换；不允许的转换抛异常。
- **何时使用**：带锁定的登录尝试、会话生命周期、支付
  状态、账户验证。
- **审查信号**：状态以松散布尔（`isLocked`、`isActive`、
  `isVerified`）持有，可组合成非法配置；无默认
  拒绝转换规则。

### Secure Visitor（安全访问者）

- **意图**：跨异构对象树应用安全操作
  而不污染每个元素的接口。
- **何时使用**：ACL 遍历、配置树审计、混合
  记录类型脱敏。
- **审查信号**：每个领域类有自己的 `checkPermission` /
  `redact` 方法 —— 安全逻辑涂抹在领域代码上。

### Protection Proxy（保护代理）

- **意图**：代理对象在委托给
  真实主题前强制访问控制。
- **何时使用**：敏感资源的延迟认证、每次调用授权、
  审计包装的访问。
- **审查信号**：客户端直接调用敏感对象；认证仅在
  构造时做但对象生命周期长于凭据。

---

## 实现层模式

### Input Validation（输入验证）

- **意图**：在每个信任边界验证；先拒绝再净化，绝不
  仅净化。
- **何时使用**：任何数据跨越信任边界（HTTP、文件、队列、IPC）。
- **审查信号**：仅在"正常"路径验证；`try/except: pass`
  包裹解析；可用白名单处无白名单。
- **边界规则**：边界处验证一次，内部信任 —— 不要
  在调用栈中重复验证同一值五次。

### Secure Logging（安全日志）

- **意图**：为审计/取证记录安全相关事件 —— 而不
  泄露密钥或可伪造。
- **何时使用**：认证事件、权限变更、拒绝访问、配置
  变更、可疑流量信号。
- **审查信号**：日志含密钥/PII（`password=...`、完整 token、PAN）；
  日志可被其审计的同一主体写入；审计日志无
  防篡改；成功未记录导致可抵赖。

### Clear Sensitive Information（清除敏感信息）

- **意图**：密钥不再需要时立即清零/覆盖 ——
  内存中、缓冲区中、日志中、错误消息中。
- **何时使用**：加密密钥、密码、token、解密明文、会话
  密钥。
- **审查信号**：密钥存于长期字段/字符串且从不
  清除；异常消息包含密钥；调试转储
  含凭据的请求体。

### Pathname Canonicalization（路径名规范化）

- **意图**：在任何白名单/前缀检查前将路径解析为
  规范绝对形式，以击败 `..`、符号链接与大小写
  技巧。
- **何时使用**：任何代码从用户影响的输入打开文件。
- **审查信号**：`if path.startswith(base_dir)` 未先 `realpath`/
  `canonicalize`；用户输入用字符串
  拼接进文件系统路径。

### Secure Directory（安全目录）

- **意图**：将敏感文件放在权限受限、由正确主体拥有的
  目录中，使无关用户无法读取
  或竞争。
- **何时使用**：临时文件、套接字、磁盘密钥、上传目的地。
- **审查信号**：临时文件在世界可读的 `/tmp`；`mktemp` 竞争；
  `chmod 777` "修复"权限错误。

### RAII / Try-with-Resources（资源获取即初始化）

- **意图**：将资源生命周期绑定到作用域，使清理（关闭、清零、释放）
  不会被遗忘，即使异常。
- **何时使用**：文件句柄、套接字、加密上下文、锁、DB
  事务。
- **审查信号**：无 `finally`/上下文管理器的手动 `close()`；
  锁仅在正常路径释放；资源跨可抛异常的
  awaitable 持有。

---

## 安全原则 → 模式映射

| 原则                | 实现它的模式                                                     |
| ------------------------ | ---------------------------------------------------------------------------- |
| 最小权限          | Separation of Privilege、Check Point、Protection Proxy、Secure State Machine |
| 职责分离     | Distrustful Decomposition、Separation of Privilege                           |
| 纵深防御         | Single Access Point → Check Point → Input Validation（分层）               |
| 默认安全        | Secure State Machine（默认拒绝状态）、Clear Sensitive Information       |
| 失败安全              | Secure Chain of Responsibility（任何阶段可拒绝）、Secure State Machine  |
| 机制经济性     | Single Access Point、Secure Factory（更少误构建方式）                |
| 保护最弱链     | Secure Logging（使弱链可观测）                               |

## 威胁（STRIDE）→ 模式选择

| 威胁                     | 主要模式                                                         |
| -------------------------- | ------------------------------------------------------------------------ |
| **S**poofing（欺骗）               | Single Access Point + 认证 Check Point + Protection Proxy                |
| **T**ampering（篡改）              | Input Validation + Pathname Canonicalization + Secure State Machine      |
| **R**epudiation（抵赖）            | Secure Logging（写侧审计、防篡改）                        |
| **I**nformation Disclosure（信息泄露） | Clear Sensitive Information + Separation of Privilege + Secure Directory |
| **D**enial of Service（拒绝服务）      | Check Point（限流）+ Distrustful Decomposition（隔离）           |
| **E**levation of Privilege（权限提升） | Separation of Privilege + 最小权限 + Secure State Machine         |

## "本应使用此模式"审查信号（默认严重度）

| 审查中的代码坏味                                | 缺失模式                   | 严重度 |
| --------------------------------------------------- | --------------------------------- | -------- |
| 多个无守卫入口点、认证不一致  | Single Access Point / Check Point | High     |
| 安全配置逐字段拼装、可跳过 | Secure Factory                    | Medium   |
| 松散布尔形成非法安全状态      | Secure State Machine              | High     |
| `path.startswith(prefix)` 未规范化      | Pathname Canonicalization         | High     |
| 密钥存于长期字符串、从不清除   | Clear Sensitive Information       | High     |
| 临时文件在共享 `/tmp`                         | Secure Directory                  | Medium   |
| 审计日志可被审计主体写入         | Secure Logging                    | High     |
| 用户路径上 `access()` 再 `open()`               | Defer to Kernel                   | High     |
| 一个角色/账户可独立完成关键操作   | Separation of Privilege           | High     |

## 采用工作流（面向审查）

1. **识别威胁** —— 对每个信任边界/入口点做 STRIDE。
2. **匹配模式** —— 从上表选取；优先架构层
   先于实现层。
3. **集成** —— 模式在边界处，而非涂抹于业务逻辑。
4. **验证** —— 确认检查无法被替代路径绕过。
5. **监控** —— Secure Logging 覆盖模式所强制的内容。

## 参考

- [pattern-classification.md](pattern-classification.md) —— 带安全包装的 GoF 模式
  （Secure Singleton 模板、Secure Decorator 链等）
- [security-expert-guide.md](security-expert-guide.md) —— 威胁建模
  流程与完整审查工作流
- [security-fixes.md](security-fixes.md) —— 每类漏洞的具体修复配方
- [../quality/security-checklist.md](../quality/security-checklist.md) ——
  提交前安全清单
