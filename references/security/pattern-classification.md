# Security Design Pattern Classification Reference

## Creational Patterns

### Singleton Pattern

**Core Purpose**: Ensure a class has only one instance and provide a global access point

**Security-Related Applications**:
- Security configuration manager
- Encryption key manager
- Audit logging service
- Permission verification service

**Security Implementation Requirements**:
| Requirement | Description | Risk Level |
|------|------|----------|
| Thread Safety | Use double-checked locking or enumeration | High |
| Private Constructor | Prevent external instantiation | High |
| Serialization Safety | Implement readResolve to prevent deserialization attacks | Medium |
| Clone Safety | Throw CloneNotSupportedException | Medium |

**Secure Singleton Template** (Java):
- `private static volatile` instance; private constructor throws `IllegalStateException` if already instantiated
- `getInstance()` uses double-checked locking (`synchronized` + null check)
- Implements `readResolve()` returning `getInstance()` — prevents deserialization attacks

### Factory Pattern

**Core Purpose**: Separate object creation from usage

**Security-Related Applications**:
- Security context factory (different environments)
- Encryption service factory
- Authentication strategy factory

**Secure Factory Template** (Java):
- `SecurityFactory.create(Class<T>, String environment)` dispatches to `SecurityLevel` enum
- `SecurityLevel` enum maps PRODUCTION/DEVELOPMENT/TESTING to `Supplier<SecurityPolicy>` (e.g., `StrictSecurityPolicy::new`)
- Callers never directly instantiate security components

### Builder Pattern

**Core Purpose**: Step-by-step construction of complex objects

**Security-Related Applications**:
- Security configuration builder
- Firewall rule builder
- Access control list builder

## Structural Patterns

### Proxy Pattern

**Core Purpose**: Control access to objects

**Proxy Types**:
| Type | Purpose | Security Application |
|------|------|----------|
| Remote Proxy | Hide network communication | Secure API gateway |
| Virtual Proxy | Lazy loading | Sensitive data access control |
| Protection Proxy | Access control | Permission verification |
| Smart Reference | Additional operations | Audit logging |

**Proxy Pattern Security Checklist**:
```
[ ] Perform authorization checks before accessing real objects
[ ] Record audit trails for all access operations
[ ] Sensitive operations require higher privilege levels
[ ] Validate and sanitize all input data
[ ] Encrypt/mask sensitive data
[ ] Implement proper error handling without exposing internal information
```

### Decorator Pattern

**Core Purpose**: Dynamically add responsibilities

**Secure Decorator Composition**:
```
InputValidator -> Encryption -> Compression -> Audit -> BaseProcessor
```

**Decorator Ordering Principles**:
1. First validate (prevent malicious input)
2. Then encrypt (protect data)
3. Finally audit (record operations)

**Secure Decorator Template**:
```java
public abstract class SecurityDecorator implements SecureComponent {
    protected final SecureComponent wrapped;

    public SecurityDecorator(SecureComponent wrapped) {
        this.wrapped = wrapped;
    }
}
```

### Adapter Pattern

**Core Purpose**: Interface conversion

**Security Application Scenarios**:
- Legacy system security adaptation
- Third-party library security wrapping
- Protocol conversion

**Secure Adapter Template**:
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

### Facade Pattern

**Core Purpose**: Unified interface

**Security Applications**:
- Unified security service entry point
- Simplify complex security operations
- Hide security implementation details

## Behavioral Patterns

### Observer Pattern

**Core Purpose**: Publish-subscribe

**Security Event Types**:
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

**Secure Observer Implementation**:
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

### Strategy Pattern

**Core Purpose**: Algorithm substitution

**Security Strategy Types**:
| Strategy Type | Example | Configuration Point |
|----------|------|----------|
| Encryption Strategy | AES, RSA, ChaCha20 | Key length, algorithm selection |
| Authentication Strategy | OAuth, SAML, JWT | Token expiry, signing algorithm |
| Compression Strategy | GZIP, Deflate | Compression level, security considerations |
| Hashing Strategy | bcrypt, scrypt, Argon2 | Work factor, memory cost |

### Chain of Responsibility Pattern

**Core Purpose**: Processing chain

**Security Check Chain Example**:
```
Request -> AuthenticationCheck -> AuthorizationCheck
                               -> InputValidation
                               -> RateLimitCheck
                               -> EncryptionCheck
                               -> AuditLog
                               -> Process
```

### State Pattern

**Core Purpose**: State-driven behavior

**Security State Example**:
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

### Template Method Pattern

**Core Purpose**: Algorithm skeleton

**Security Validation Template**:
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

## Pattern Selection Guide

| Requirement | Recommended Pattern | Alternative Pattern |
|------|----------|----------|
| Access Control | Proxy Pattern | Strategy + Chain of Responsibility |
| Input Validation | Decorator Pattern | Chain of Responsibility |
| Event Monitoring | Observer Pattern | Publish-Subscribe |
| Algorithm Switching | Strategy Pattern | Factory Pattern |
| Multi-Layer Checks | Chain of Responsibility | Decorator Composition |
| Legacy System Integration | Adapter Pattern | Facade Pattern |
| Security Configuration Management | Singleton Pattern | Factory Pattern |
| Environment Isolation | Factory Pattern | Abstract Factory |