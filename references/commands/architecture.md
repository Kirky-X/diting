# 架构审查命令

架构审查模式 —— 系统设计、模式应用、耦合、微服务合规性

## 用法

```bash
review architecture [target-path]
```

## 检查内容

### 模块结构与边界

```
□ 清晰的职责分离（展示层 / 业务逻辑 / 数据 / 基础设施）
□ 模块边界与领域边界匹配（DDD 对齐）
□ 模块间无循环依赖
□ 公共 API 表面是有意且最小的
□ 内部实现细节不泄露给调用方
□ 依赖方向：高层 → 低层（不反向）
```

### 耦合与内聚

| 指标                             | 目标            | 说明                                       |
| -------------------------------- | --------------- | ------------------------------------------ |
| 入向耦合（Ca）                   | 越低越好        | 多少模块依赖此模块                         |
| 出向耦合（Ce）                   | 越低越好        | 此模块依赖多少模块                         |
| 不稳定性（I = Ce / (Ca + Ce)）   | 0.0–1.0         | 0 = 稳定，1 = 不稳定                       |
| 内聚                             | 高              | 相关事物分组，无关事物分离                 |

**危险信号：**

- 上帝对象：一个类/模块被到处引用
- 霰弹手术：一次修改需要触碰 10+ 文件
- 平行类层次结构总是同步增长

### 设计模式应用

| 场景                        | 推荐模式                        |
| --------------------------- | ------------------------------- |
| 对象创建复杂或条件化        | Factory / Builder               |
| 需要单一共享实例            | Singleton（优先用 DI 容器）     |
| 不修改类添加行为            | Decorator                       |
| 控制访问/添加安全层         | Proxy                           |
| 解耦事件发送者与处理者      | Observer / Event Bus            |
| 多个可互换算法              | Strategy                        |
| 多步校验/处理链             | Chain of Responsibility         |
| 简化复杂子系统              | Facade                          |
| 分布式事务                  | Saga                            |

**优先级信号**：缺失模式本身就是发现项 —— 超过 3 种类型的 `if/elif` 链、≥ 3× 重复算法、或一个类有 > 6 个不相关职责，每项默认 **High** 严重度。完整阈值和 code-smell→pattern 反向查找见 [design-pattern-review.md](../architecture/design-pattern-review.md)。

### 需检测的反模式

```
□ 上帝对象（God Object）—— 一个类负责一切
□ 贫血领域模型（Anemic Domain Model）—— 领域对象只是 getter/setter 集合
□ 分布式单体（Distributed Monolith）—— 微服务但通过同步调用紧密耦合
□ 硬编码依赖 —— `new ServiceImpl()` 而非注入接口
□ 意大利面式依赖（Spaghetti Dependencies）—— 无清晰分层，任意调用任意
□ 过早微服务（Premature Microservices）—— 微服务开销但无收益
```

### 微服务（如适用）

```
□ 每个服务拥有一个业务能力
□ 每服务一库（服务间无共享数据库）
□ 通信：非关键路径优先异步（事件）而非同步
□ 所有服务间调用配置熔断器
□ 服务可独立部署，无需协调发布
□ 健康端点暴露（/health 或 /readyz）
□ 可观测性：结构化日志、分布式追踪、指标
□ API Gateway 处理横切关注点：认证、限流、路由
```

### 依赖管理

```
□ 无循环导入/循环依赖
□ 外部依赖抽象为接口（易于替换）
□ 第三方库未在代码库中直接使用（adapter/wrapper）
□ 依赖版本锁定；lock 文件已提交
□ 无废弃或有漏洞的依赖
```

### 可扩展性与可靠性

```
□ 无状态服务（会话状态在共享存储，而非内存）
□ 幂等操作（可安全重试）
□ 优雅降级（部分失败 ≠ 全面故障）
□ 瞬时失败的重试 + 指数退避
□ 所有外部调用配置超时
□ 资源池化（DB 连接、HTTP 客户端）
```

---

## 架构决策快速指南

### 何时使用哪种模式

```
简单应用（1-3 名开发者）：
  → 分层架构（展示层 / 业务层 / 数据层）

增长中的代码库（多团队、清晰领域边界）：
  → 模块化单体 + DDD 聚合

高规模、独立扩展需求、大型组织：
  → 微服务（仅当团队能支撑运维开销时）

复杂业务逻辑、多状态转换：
  → 领域驱动设计（聚合、值对象、领域事件）

读写比差异大：
  → CQRS + 读模型
```

---

## 参考

- [architect-guide.md](../architecture/architect-guide.md) — 完整架构师参考
- [system-architecture.md](../architecture/system-architecture.md) — 架构质量属性
- [design-pattern-review.md](../architecture/design-pattern-review.md) — GoF 模式审查
- [microservices-compliance.md](../architecture/microservices-compliance.md) — 微服务检查清单
- [dependency-analysis.md](../architecture/dependency-analysis.md) — 依赖分析指南

## 相关命令

- [security.md](security.md)
- [performance.md](performance.md)
- [quality.md](quality.md)
- [simplification.md](simplification.md)
