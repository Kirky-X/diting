# Security Issues and Design Pattern Solutions

> 安全修复策略：注入攻击与认证授权问题。详细修复（数据保护/加密/其他安全）详见 [security-fixes-catalog.md](security-fixes-catalog.md)。

## Injection Attacks

### SQL Injection

**Problematic Code**:
```java
// DANGEROUS! Direct SQL concatenation
String query = "SELECT * FROM users WHERE id = " + userId;
Statement stmt = connection.createStatement();
ResultSet rs = stmt.executeQuery(query);
```

**Solution: Parameterized Queries + Decorator Pattern**
```java
// Use parameterized queries
String query = "SELECT * FROM users WHERE id = ?";
PreparedStatement pstmt = connection.prepareStatement(query);
pstmt.setString(1, userId);

// Or use Decorator pattern to add SQL injection detection
public class SqlInjectionDetector extends SecurityDecorator {
    private static final Pattern SQL_PATTERN = Pattern.compile(
        "(?i)(union|select|insert|update|delete|drop|create|alter|exec|execute)"
    );

    @Override
    public String execute(String sql) {
        if (SQL_PATTERN.matcher(sql).find()) {
            throw new SecurityException("Potential SQL injection detected");
        }
        return wrapped.execute(sql);
    }
}
```

**Checklist**:
- [ ] All database queries use parameterized queries
- [ ] Use ORM framework query builders
- [ ] Implement strict input validation
- [ ] Database uses least privilege account

### XSS Attack

**Problematic Code**:
```java
// DANGEROUS! Direct output of user input
String userInput = request.getParameter("comment");
response.getWriter().write("<div>" + userInput + "</div>");
```

**Solution: Output Encoding + Decorator Pattern**
```java
// HTML encoding
public class XssProtectionDecorator extends SecurityDecorator {
    private static final Map<Character, String> HTML_ENTITIES = Map.of(
        '<', "&lt;", '>', "&gt;",
        '"', "&quot;", '&', "&amp;",
        '\'', "&#x27;", '/', "&#x2F;"
    );

    @Override
    public String process(String input) {
        String encoded = input.chars()
            .mapToObj(c -> HTML_ENTITIES.getOrDefault(
                (char) c, String.valueOf((char) c)))
            .collect(Collectors.joining());
        return wrapped.process(encoded);
    }
}

// Or use existing library
import org.owasp.encoder.Encode;

public String sanitizeHtml(String input) {
    return Encode.forHtml(input);
}
```

### Command Injection

**Problematic Code**:
```java
// DANGEROUS! Direct execution of user input as command
String filename = request.getParameter("file");
Runtime.getRuntime().exec("cat " + filename);
```

**Solution: Whitelist Validation + Strategy Pattern**
```java
public class SafeCommandExecutor {
    private final CommandStrategy strategy;

    public SafeCommandExecutor(CommandStrategy strategy) {
        this.strategy = strategy;
    }

    public CommandResult execute(CommandRequest request) {
        // Validate filename against whitelist
        if (!isAllowedFilename(request.getFilename())) {
            throw new SecurityException("Filename not allowed");
        }
        // Execute using strategy
        return strategy.execute(buildCommand(request));
    }

    private boolean isAllowedFilename(String filename) {
        return filename != null &&
               filename.matches("^[a-zA-Z0-9_-]+\\.[a-zA-Z0-9]+$");
    }
}
```

## Authentication and Authorization Issues

### Weak Password Policy

**Solution: Strategy Pattern + Validation Decorator**
```java
public class PasswordPolicyValidator extends SecurityDecorator {
    private static final Pattern PASSWORD_PATTERN = Pattern.compile(
        "^(?=.*[a-z])(?=.*[A-Z])(?=.*\\d)(?=.*[@$!%*?&])[A-Za-z\\d@$!%*?&]{8,}$"
    );

    @Override
    public boolean validate(String password) {
        if (!PASSWORD_PATTERN.matcher(password).matches()) {
            throw new SecurityException(
                "Password must contain: 8+ chars, uppercase, lowercase, number, special char"
            );
        }
        return wrapped.validate(password);
    }
}
```

### Session Management Issues

**Solution: Secure Session Management Strategy**
```java
public class SecureSessionStrategy implements SessionStrategy {
    @Override
    public Session createSession(User user) {
        String sessionId = generateSecureRandom(32);

        Session session = new Session();
        session.setId(sessionId);
        session.setUserId(user.getId());
        session.setCreationTime(Instant.now());
        session.setLastAccessTime(Instant.now());
        session.setIpAddress(getClientIp());
        session.setUserAgent(getClientUserAgent());

        // Set security attributes
        Cookie cookie = new Cookie("SESSION_ID", sessionId);
        cookie.setHttpOnly(true);
        cookie.setSecure(true);
        cookie.setSameSite("Strict");
        cookie.setMaxAge((int) Duration.ofHours(24).getSeconds());

        return session;
    }

    @Override
    public boolean validateSession(String sessionId, Request request) {
        Session session = sessionStore.get(sessionId);
        if (session == null) return false;

        // Validate IP and User-Agent
        if (!session.getIpAddress().equals(request.getClientIp())) {
            logSecurityEvent("SESSION_HIJACK", session.getUserId());
            return false;
        }

        // Check session expiration
        if (session.isExpired(Duration.ofHours(24))) {
            sessionStore.remove(sessionId);
            return false;
        }

        return true;
    }
}
```

### Privilege Escalation

**Solution: Proxy Pattern + Least Privilege Check**
```java
public class AuthorizationProxy implements SecureResource {
    private final RealSecureResource realResource;
    private final PermissionService permissionService;
    private final AuditLogger auditLogger;

    @Override
    public Data access(String userId, String resourceId, String action) {
        // Check permission
        Permission required = Permission.from(action);
        if (!permissionService.hasPermission(userId, resourceId, required)) {
            auditLogger.logSecurityEvent("PRIVILEGE_VIOLATION",
                userId + " attempted " + action + " on " + resourceId);
            throw new AccessDeniedException();
        }

        // Log access
        auditLogger.logAccess(userId, resourceId, action);

        // Execute operation
        return realResource.access(userId, resourceId, action);
    }
}
```

## Security Checklist Quick Reference

| Vulnerability Type | Detection Method | Fix Pattern | Validation Method |
|----------|----------|----------|----------|
| SQL Injection | Code review, SAST | Parameterized queries | Penetration testing |
| XSS | DAST, Code review | Output encoding | Automated scanning |
| CSRF | Test verification | CSRF Token | Security testing |
| Authentication Flaw | Code review, Testing | Strong auth strategy | Penetration testing |
| Sensitive Data Leak | DAST, Manual review | Encryption, Sanitization | Data flow analysis |
| Access Control Flaw | Code review, Testing | Proxy pattern check | Permission testing |
| Encryption Flaw | Static analysis | Strategy pattern replacement | Algorithm audit |
