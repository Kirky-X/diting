# Security Design Pattern Code Examples

> 安全设计模式代码案例主索引。完整案例已按安全域拆分为子文件。

## 子文件导航

| 子文件 | 内容 | 适用场景 |
|------|------|---------|
| [examples-injection.md](examples-injection.md) | 代理/装饰器/责任链模式 | 注入防御、输入校验、XSS/SQL注入 |
| [examples-auth-config.md](examples-auth-config.md) | 观察者/策略模式、配置管理 | 认证授权、加密策略、配置管理 |
| [examples-owasp.md](examples-owasp.md) | 纵深防御、审计系统、告警 | OWASP 防御、审计日志、入侵检测 |

## 1. Complete Security System Architecture

```java
public class SecureSystem {
    private final SecurityContext securityContext;
    private final SecurityProxy resourceProxy;
    private final SecurityStrategyContext strategyContext;
    private final SecurityEventPublisher eventPublisher;

    public SecureSystem(String environment) {
        this.securityContext = SecurityContextFactory.getContext(environment);
        this.strategyContext = new SecurityStrategyContext();
        this.strategyContext.setStrategy(environment);
        this.eventPublisher = new SecurityEventPublisher();

        SensitiveResource realResource = new RealSensitiveResource();
        this.resourceProxy = new SecurityProxy(realResource, securityContext);
        setupObservers();
    }

    private void setupObservers() {
        SecurityEventManager manager = SecurityEventManager.getInstance();
        manager.registerObserver(new LoggingObserver());
        if (!"testing".equals(System.getProperty("env"))) {
            manager.registerObserver(new AlertObserver(new EmailService()));
            manager.registerObserver(new BruteForceDetector());
        }
    }

    public boolean authenticate(String username, String password) {
        boolean success = securityContext.authenticate(username, password);
        if (success) {
            eventPublisher.publishLoginSuccess(username, "SecureSystem");
        } else {
            eventPublisher.publishLoginFailure(username, "SecureSystem");
        }
        return success;
    }

    public String processData(String user, String data) {
        if (!securityContext.authorize("process", user)) {
            eventPublisher.publishUnauthorizedAccess(user, "data-processing", "process");
            throw new SecurityException("Unauthorized");
        }
        DataProcessor processor = new AuditDecorator(
            new EncryptionDecorator(
                new InputValidationDecorator(new BasicDataProcessor())
            )
        );
        return processor.process(data);
    }

    public String accessResource(String user, String resource) {
        try {
            return resourceProxy.readData(user);
        } catch (SecurityException e) {
            eventPublisher.publishDataBreachAttempt(user, "resource-access", e.getMessage());
            throw e;
        }
    }
}

// Event publisher
class SecurityEventPublisher {
    private final SecurityEventManager eventManager;

    public SecurityEventPublisher() {
        this.eventManager = SecurityEventManager.getInstance();
    }

    public void publishLoginSuccess(String user, String source) {
        eventManager.notifyObservers(
            new SecurityEvent(SecurityEventType.LOGIN_SUCCESS, user, source, "Successful login")
        );
    }

    public void publishLoginFailure(String user, String source) {
        eventManager.notifyObservers(
            new SecurityEvent(SecurityEventType.LOGIN_FAILURE, user, source, "Failed login")
        );
    }

    public void publishUnauthorizedAccess(String user, String resource, String action) {
        eventManager.notifyObservers(
            new SecurityEvent(SecurityEventType.UNAUTHORIZED_ACCESS, user, resource,
                "Attempted to " + action)
        );
    }

    public void publishDataBreachAttempt(String user, String method, String details) {
        eventManager.notifyObservers(
            new SecurityEvent(SecurityEventType.DATA_BREACH_ATTEMPT, user, method, details)
        );
    }
}
```

## 2. Complete Comprehensive Demo

```java
public class ComprehensiveSecurityDemo {
    public static void main(String[] args) {
        // Setup environment
        System.setProperty("env", "production");

        // Create security system
        SecureSystem system = new SecureSystem("production");

        System.out.println("=== Security System Demo ===");

        // 1. Authentication
        System.out.println("\n1. User Authentication:");
        boolean authResult = system.authenticate("alice", "password123");
        System.out.println("Authentication result: " + authResult);

        // 2. Data Processing
        System.out.println("\n2. Data Processing:");
        try {
            String processed = system.processData("alice", "Sensitive Data");
            System.out.println("Processing result: " + processed);
        } catch (Exception e) {
            System.err.println("Processing failed: " + e.getMessage());
        }

        // 3. Resource Access
        System.out.println("\n3. Resource Access:");
        try {
            String resource = system.accessResource("alice", "user-data");
            System.out.println("Resource content: " + resource);
        } catch (Exception e) {
            System.err.println("Access failed: " + e.getMessage());
        }

        // 4. Simulate Attack
        System.out.println("\n4. Simulate Attack Scenario:");
        try {
            system.processData("attacker", "<script>alert('xss')</script>");
        } catch (SecurityException e) {
            System.err.println("Attack blocked: " + e.getMessage());
        }

        // 5. Unauthorized Access
        System.out.println("\n5. Unauthorized Access:");
        try {
            system.authenticate("bob", "wrongpass");
            system.accessResource("bob", "admin-data");
        } catch (SecurityException e) {
            System.err.println("Unauthorized access blocked: " + e.getMessage());
        }

        System.out.println("\n=== Demo Complete ===");
    }
}
```

## 3. Pattern Application Guide

### When to Use Which Pattern

| Pattern | Applicable Scenarios | Security Benefits |
|------|----------|----------|
| Singleton Pattern | Security managers, configuration managers, encryption services | Unified management of shared resources, prevent duplicate creation |
| Factory Pattern | Security context creation, encryption algorithm selection | Isolate security strategies across different environments |
| Proxy Pattern | Resource access control, remote service calls | Centralized security checks and auditing |
| Decorator Pattern | Security feature stacking (validation, encryption, auditing) | Flexible combination of security features |
| Observer Pattern | Security event monitoring, alert systems | Real-time response to security events |
| Strategy Pattern | Encryption algorithm switching, access policies | Flexible adjustment of security levels |

### Typical Security Architecture Combination

```mermaid
flowchart TD
    SS["Security System"]
    SS --> SP["Singleton Pattern: SecurityManager (unified management)"]
    SS --> FP["Factory Pattern: SecurityContextFactory (environment isolation)"]
    SS --> PP["Proxy Pattern: SecurityProxy (access control)"]
    SS --> DP["Decorator Pattern: SecurityDecorator (feature stacking)"]
    SS --> OP["Observer Pattern: SecurityEventManager (event monitoring)"]
    SS --> STP["Strategy Pattern: EncryptionStrategy (algorithm switching)"]
```

## 4. Security Checklist

### Implementation Phase Checklist

**Authentication and Authorization**
- [ ] Use secure authentication mechanism (avoid hardcoded credentials)
- [ ] Implement least privilege principle
- [ ] Session management uses secure cookies (HttpOnly, Secure, SameSite)
- [ ] Implement password hashing (bcrypt/Argon2)

**Input Validation**
- [ ] Validate all user input
- [ ] Check input length limits
- [ ] Filter dangerous characters (`< > " ' & ;`)
- [ ] Prevent SQL injection (use parameterized queries)
- [ ] Prevent XSS (output encoding)
- [ ] Prevent path traversal

**Encryption Processing**
- [ ] Use strong encryption algorithms (AES-256, RSA-2048+)
- [ ] Secure key management (no hardcoding, key rotation)
- [ ] Encrypt sensitive data at rest
- [ ] Enforce HTTPS with TLS 1.2+

**Error Handling**
- [ ] Don't expose sensitive information in error messages
- [ ] Unified error handling, avoid information leakage
- [ ] Log security-related errors

**Multi-threading Safety**
- [ ] Use synchronization mechanisms for shared resources
- [ ] Use thread-safe data structures
- [ ] Singleton pattern uses double-checked locking

### Review Phase Checklist

**Architecture Review**
- [ ] Security boundaries clearly defined
- [ ] Sensitive data has protection measures
- [ ] Audit logs fully recorded
- [ ] Security components configurable

**Code Review**
- [ ] No hardcoded passwords/keys
- [ ] Validate all external input
- [ ] Sensitive operations have authorization checks
- [ ] Exceptions handled correctly
- [ ] Use secure design patterns

**Testing Verification**
- [ ] Unit tests cover security logic
- [ ] Integration tests verify authentication/authorization
- [ ] Penetration test vulnerabilities fixed

## 5. Security Coding Principles

1. **Defense in Depth**: Multiple layers of security measures, each layer can independently provide protection
2. **Least Privilege**: Grant only necessary permissions
3. **Secure by Default**: Default configuration should be secure
4. **Fail Secure**: Deny access by default when operations fail
5. **Open/Closed**: Open for extension, closed for modification

## 6. Common Security Vulnerabilities and Corresponding Patterns

| Vulnerability Type | Design Pattern Solution |
|----------|------------------|
| Privilege Escalation | Proxy pattern + least privilege check |
| SQL Injection | Decorator pattern + parameterized queries |
| XSS Attack | Decorator pattern + output encoding |
| Session Hijacking | Strategy pattern + secure cookie policy |
| Brute Force | Observer pattern + rate limiting |
| Sensitive Information Leakage | Decorator pattern + encryption |
| Path Traversal | Chain of Responsibility pattern + path validation |
