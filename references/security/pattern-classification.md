# Security Design Pattern Classification Reference

## Creational Patterns

### Singleton Pattern

**Core Purpose**: Ensure a class has only one instance and provide a global access point

**Security-Related Applications**:
- Security configuration manager
- Encryption key manager
- Audit log service
- Permission verification service

**Security Implementation Requirements**:
| Requirement | Description | Risk Level |
|------|------|----------|
| Thread Safety | Use double-checked locking or enum | High |
| Private Constructor | Prevent external instantiation | High |
| Serialization Safe | Implement readResolve to prevent deserialization attacks | Medium |
| Clone Safe | Throw CloneNotSupportedException | Medium |

**Secure Singleton Template** (Java):
- `private static volatile` instance; private constructor throws `IllegalStateException` if already instantiated
- `getInstance()` uses double-checked locking (`synchronized` + null check)
- Implement `readResolve()` to return `getInstance()` — prevents deserialization attacks

### Factory Pattern

**Core Purpose**: Separate object creation from usage

**Security-Related Applications**:
- Security context factory (different environments)
- Encryption service factory
- Authentication strategy factory

**Secure Factory Template** (Java):
- `SecurityFactory.create(Class<T>, String environment)` dispatches to `SecurityLevel` enum
- `SecurityLevel` enum maps PRODUCTION/DEVELOPMENT/TESTING → `Supplier<SecurityPolicy>` (e.g., `StrictSecurityPolicy::new`)
- Callers never instantiate security components directly

### Builder Pattern

**Core Purpose**: Build complex objects step by step

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
[ ] Perform authorization check before accessing real object
[ ] Log audit trail of all access operations
[ ] Require higher privilege level for sensitive operations
[ ] Validate and sanitize all input data
[ ] Encrypt/mask sensitive data
[ ] Implement proper error handling without exposing internal information
```

### Decorator Pattern

**Core Purpose**: Dynamically add responsibilities

**Security Decorator Composition**:
```
InputValidator -> Encryption -> Compression -> Audit -> BaseProcessor
```

**Decorator Order Principles**:
1. Validate first (prevent malicious input)
2. Then encrypt (protect data)
3. Then audit (log operations)

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
- Third-party library security wrapper
- Protocol conversion

**Secure Adapter Template**:
```java
public class SecurityAdapter implements SecureTarget {
    private final LegacySource legacySource;
    private final SecurityContext securityContext;

    @Override
    public void secureOperation(Request request) {
        // 1. Authorization check
        if (!securityContext.authorize(request)) {
            throw new SecurityException("Unauthorized");
        }
        // 2. Input validation
        validateInput(request);
        // 3. Data conversion
        LegacyRequest legacyRequest = convert(request);
        // 4. Call legacy system
        LegacyResponse response = legacySource.operation(legacyRequest);
        // 5. Output validation
        return convertAndSanitize(response);
    }
}
```

### Facade Pattern

**Core Purpose**: Unified interface

**Security Applications**:
- Security service unified entry point
- Simplify complex security operations
- Hide security implementation details

## Behavioral Patterns

### Observer Pattern

**Core Purpose**: Publish-subscribe

**Security Event Types**:
```java
enum SecurityEventType {
    // Authentication related
    LOGIN_SUCCESS, LOGIN_FAILURE, LOGOUT, SESSION_TIMEOUT,

    // Authorization related
    UNAUTHORIZED_ACCESS, PRIVILEGE_ESCALATION,

    // Data related
    DATA_BREACH_ATTEMPT, SENSITIVE_DATA_ACCESS,

    // Configuration related
    CONFIG_CHANGE, POLICY_VIOLATION,

    // Attack related
    BRUTE_FORCE_ATTEMPT, SQL_INJECTION_DETECTED,
    XSS_ATTEMPT, PATH_TRAVERSAL_ATTEMPT
}
```

**Security Observer Implementation**:
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
| Strategy Type | Example | Configuration Points |
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

**Core Purpose**: State transition behavior

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
        // Normal login flow
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
            return ValidationResult.failure("Pre-validation failed");
        }
        if (!doValidate(request)) {
            return ValidationResult.failure("Validation failed");
        }
        if (!postValidate(request)) {
            return ValidationResult.failure("Post-validation failed");
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
| Access control | Proxy pattern | Strategy + Chain of Responsibility |
| Input validation | Decorator pattern | Chain of Responsibility |
| Event monitoring | Observer pattern | Publish-Subscribe |
| Algorithm switching | Strategy pattern | Factory pattern |
| Multi-layer checks | Chain of Responsibility | Decorator combination |
| Legacy system integration | Adapter pattern | Facade pattern |
| Security configuration management | Singleton pattern | Factory pattern |
| Environment isolation | Factory pattern | Abstract Factory |