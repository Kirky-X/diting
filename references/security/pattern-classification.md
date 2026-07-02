# 安全设计模式分类参考

## 创建型模式

### 单例模式（Singleton Pattern）

**核心目的**：确保一个类只有一个实例，并提供全局访问点

**安全相关应用**：
- 安全配置管理器
- 加密密钥管理器
- 审计日志服务
- 权限验证服务

**安全实现要求**：
| 要求 | 描述 | 风险等级 |
|------|------|----------|
| 线程安全 | 使用双重检查锁定或枚举 | 高 |
| 私有构造函数 | 防止外部实例化 | 高 |
| 序列化安全 | 实现 readResolve 防止反序列化攻击 | 中 |
| 克隆安全 | 抛出 CloneNotSupportedException | 中 |

**安全单例模板**（Java）：
- `private static volatile` 实例；私有构造函数在已实例化时抛出 `IllegalStateException`
- `getInstance()` 使用双重检查锁定（`synchronized` + null 检查）
- 实现 `readResolve()` 返回 `getInstance()` —— 防止反序列化攻击

### 工厂模式（Factory Pattern）

**核心目的**：将对象创建与使用分离

**安全相关应用**：
- 安全上下文工厂（不同环境）
- 加密服务工厂
- 认证策略工厂

**安全工厂模板**（Java）：
- `SecurityFactory.create(Class<T>, String environment)` 分发到 `SecurityLevel` 枚举
- `SecurityLevel` 枚举将 PRODUCTION/DEVELOPMENT/TESTING 映射到 `Supplier<SecurityPolicy>`（如 `StrictSecurityPolicy::new`）
- 调用方永不直接实例化安全组件

### 建造者模式（Builder Pattern）

**核心目的**：逐步构建复杂对象

**安全相关应用**：
- 安全配置构建器
- 防火墙规则构建器
- 访问控制列表构建器

## 结构型模式

### 代理模式（Proxy Pattern）

**核心目的**：控制对对象的访问

**代理类型**：
| 类型 | 目的 | 安全应用 |
|------|------|----------|
| 远程代理（Remote Proxy） | 隐藏网络通信 | 安全 API 网关 |
| 虚代理（Virtual Proxy） | 延迟加载 | 敏感数据访问控制 |
| 保护代理（Protection Proxy） | 访问控制 | 权限验证 |
| 智能引用（Smart Reference） | 附加操作 | 审计日志 |

**代理模式安全清单**：
```
[ ] 访问真实对象前执行授权检查
[ ] 记录所有访问操作的审计轨迹
[ ] 敏感操作要求更高权限级别
[ ] 验证并清理所有输入数据
[ ] 加密/脱敏敏感数据
[ ] 实施适当的错误处理，不暴露内部信息
```

### 装饰器模式（Decorator Pattern）

**核心目的**：动态添加职责

**安全装饰器组合**：
```
InputValidator -> Encryption -> Compression -> Audit -> BaseProcessor
```

**装饰器顺序原则**：
1. 先验证（防止恶意输入）
2. 再加密（保护数据）
3. 最后审计（记录操作）

**安全装饰器模板**：
```java
public abstract class SecurityDecorator implements SecureComponent {
    protected final SecureComponent wrapped;

    public SecurityDecorator(SecureComponent wrapped) {
        this.wrapped = wrapped;
    }
}
```

### 适配器模式（Adapter Pattern）

**核心目的**：接口转换

**安全应用场景**：
- 遗留系统安全适配
- 第三方库安全包装
- 协议转换

**安全适配器模板**：
```java
public class SecurityAdapter implements SecureTarget {
    private final LegacySource legacySource;
    private final SecurityContext securityContext;

    @Override
    public void secureOperation(Request request) {
        // 1. 授权检查
        if (!securityContext.authorize(request)) {
            throw new SecurityException("未授权");
        }
        // 2. 输入验证
        validateInput(request);
        // 3. 数据转换
        LegacyRequest legacyRequest = convert(request);
        // 4. 调用遗留系统
        LegacyResponse response = legacySource.operation(legacyRequest);
        // 5. 输出验证
        return convertAndSanitize(response);
    }
}
```

### 外观模式（Facade Pattern）

**核心目的**：统一接口

**安全应用**：
- 安全服务统一入口
- 简化复杂安全操作
- 隐藏安全实现细节

## 行为型模式

### 观察者模式（Observer Pattern）

**核心目的**：发布-订阅

**安全事件类型**：
```java
enum SecurityEventType {
    // 认证相关
    LOGIN_SUCCESS, LOGIN_FAILURE, LOGOUT, SESSION_TIMEOUT,

    // 授权相关
    UNAUTHORIZED_ACCESS, PRIVILEGE_ESCALATION,

    // 数据相关
    DATA_BREACH_ATTEMPT, SENSITIVE_DATA_ACCESS,

    // 配置相关
    CONFIG_CHANGE, POLICY_VIOLATION,

    // 攻击相关
    BRUTE_FORCE_ATTEMPT, SQL_INJECTION_DETECTED,
    XSS_ATTEMPT, PATH_TRAVERSAL_ATTEMPT
}
```

**安全观察者实现**：
```java
public interface SecurityObserver {
    void onSecurityEvent(SecurityEvent event);
}

public class SecurityEventDispatcher {
    private final List<SecurityObserver> observers = new CopyOnWriteArrayList<>();

    public void register(SecurityObserver observer) {
        observers.add(observer);
    }

    public void dispatch(SecurityEvent event) {
        observers.forEach(o -> o.onSecurityEvent(event));
    }
}
```

### 策略模式（Strategy Pattern）

**核心目的**：算法替换

**安全策略类型**：
| 策略类型 | 示例 | 配置点 |
|----------|------|----------|
| 加密策略 | AES、RSA、ChaCha20 | 密钥长度、算法选择 |
| 认证策略 | OAuth、SAML、JWT | 令牌过期、签名算法 |
| 压缩策略 | GZIP、Deflate | 压缩级别、安全考量 |
| 哈希策略 | bcrypt、scrypt、Argon2 | 工作因子、内存成本 |

### 责任链模式（Chain of Responsibility Pattern）

**核心目的**：处理链

**安全检查链示例**：
```
Request -> AuthenticationCheck -> AuthorizationCheck
                               -> InputValidation
                               -> RateLimitCheck
                               -> EncryptionCheck
                               -> AuditLog
                               -> Process
```

### 状态模式（State Pattern）

**核心目的**：状态转换行为

**安全状态示例**：
```java
public interface SecurityState {
    void handleLogin(LoginContext context);
    void handleLogout(LoginContext context);
    void handleViolation(LoginContext context);
}

public class NormalState implements SecurityState {
    @Override
    public void handleLogin(LoginContext context) {
        // 正常登录流程
    }
}

public class LockedState implements SecurityState {
    @Override
    public void handleLogin(LoginContext context) {
        throw new AccountLockedException();
    }
}
```

### 模板方法模式（Template Method Pattern）

**核心目的**：算法骨架

**安全验证模板**：
```java
public abstract class SecurityValidationTemplate {
    public final ValidationResult validate(SecurityRequest request) {
        if (!preValidate(request)) {
            return ValidationResult.failure("预验证失败");
        }
        if (!doValidate(request)) {
            return ValidationResult.failure("验证失败");
        }
        if (!postValidate(request)) {
            return ValidationResult.failure("后置验证失败");
        }
        return ValidationResult.success();
    }

    protected abstract boolean preValidate(SecurityRequest request);
    protected abstract boolean doValidate(SecurityRequest request);
    protected abstract boolean postValidate(SecurityRequest request);
}
```

## 模式选择指南

| 需求 | 推荐模式 | 备选模式 |
|------|----------|----------|
| 访问控制 | 代理模式 | 策略 + 责任链 |
| 输入验证 | 装饰器模式 | 责任链 |
| 事件监控 | 观察者模式 | 发布-订阅 |
| 算法切换 | 策略模式 | 工厂模式 |
| 多层检查 | 责任链 | 装饰器组合 |
| 遗留系统集成 | 适配器模式 | 外观模式 |
| 安全配置管理 | 单例模式 | 工厂模式 |
| 环境隔离 | 工厂模式 | 抽象工厂 |
