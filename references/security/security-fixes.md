# Security Issues & Design Pattern Solutions

> Security fix strategies: injection attacks and authentication/authorization issues. See [security-fixes-catalog.md](security-fixes-catalog.md) for detailed fixes (data protection/encryption/other security).

## Injection Attacks

### SQL Injection

**Vulnerable Code**:
```java
// 危险！直接 SQL 拼接
String query = "SELECT * FROM users WHERE id = " + userId;
Statement stmt = connection.createStatement();
ResultSet rs = stmt.executeQuery(query);
```

**Solution: Parameterized Queries + Decorator Pattern**
```java
// 使用参数化查询
String query = "SELECT * FROM users WHERE id = ?";
PreparedStatement pstmt = connection.prepareStatement(query);
pstmt.setString(1, userId);

// 或用装饰器模式添加 SQL 注入检测
public class SqlInjectionDetector extends SecurityDecorator {
    private static final Pattern SQL_PATTERN = Pattern.compile(
        "(?i)(union|select|insert|update|delete|drop|create|alter|exec|execute)"
    );

    @Override
    public String execute(String sql) {
        if (SQL_PATTERN.matcher(sql).find()) {
            throw new SecurityException("检测到潜在 SQL 注入");
        }
        return wrapped.execute(sql);
    }
}
```

**Checklist**:
- [ ] All database queries use parameterized queries
- [ ] Use ORM framework query builders
- [ ] Implement strict input validation
- [ ] Database uses least-privilege accounts

### XSS Attack

**Vulnerable Code**:
```java
// 危险！直接输出用户输入
String userInput = request.getParameter("comment");
response.getWriter().write("<div>" + userInput + "</div>");
```

**Solution: Output Encoding + Decorator Pattern**
```java
// HTML 编码
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

// 或使用现有库
import org.owasp.encoder.Encode;

public String sanitizeHtml(String input) {
    return Encode.forHtml(input);
}
```

### Command Injection

**Vulnerable Code**:
```java
// 危险！直接执行用户输入作为命令
String filename = request.getParameter("file");
Runtime.getRuntime().exec("cat " + filename);
```

**Solution: Allowlist Validation + Strategy Pattern**
```java
public class SafeCommandExecutor {
    private final CommandStrategy strategy;

    public SafeCommandExecutor(CommandStrategy strategy) {
        this.strategy = strategy;
    }

    public CommandResult execute(CommandRequest request) {
        // 用白名单验证文件名
        if (!isAllowedFilename(request.getFilename())) {
            throw new SecurityException("文件名不允许");
        }
        // 用策略执行
        return strategy.execute(buildCommand(request));
    }

    private boolean isAllowedFilename(String filename) {
        return filename != null &&
               filename.matches("^[a-zA-Z0-9_-]+\\.[a-zA-Z0-9]+$");
    }
}
```

## Authentication & Authorization Issues

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
                "密码须包含：8+ 字符、大写、小写、数字、特殊字符"
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

        // 设置安全属性
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

        // 验证 IP 与 User-Agent
        if (!session.getIpAddress().equals(request.getClientIp())) {
            logSecurityEvent("SESSION_HIJACK", session.getUserId());
            return false;
        }

        // 检查会话过期
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
        // 检查权限
        Permission required = Permission.from(action);
        if (!permissionService.hasPermission(userId, resourceId, required)) {
            auditLogger.logSecurityEvent("PRIVILEGE_VIOLATION",
                userId + " attempted " + action + " on " + resourceId);
            throw new AccessDeniedException();
        }

        // 记录访问
        auditLogger.logAccess(userId, resourceId, action);

        // 执行操作
        return realResource.access(userId, resourceId, action);
    }
}
```

## Security Checklist Quick Reference

| Vulnerability Type | Detection Method | Fix Pattern | Verification Method |
|----------|----------|----------|----------|
| SQL Injection | Code review, SAST | Parameterized queries | Penetration testing |
| XSS | DAST, code review | Output encoding | Automated scanning |
| CSRF | Testing verification | CSRF tokens | Security testing |
| Auth Deficiencies | Code review, testing | Strong authentication policies | Penetration testing |
| Sensitive Data Leakage | DAST, manual review | Encryption, masking | Data flow analysis |
| Access Control Deficiencies | Code review, testing | Proxy pattern checks | Permission testing |
| Encryption Deficiencies | Static analysis | Strategy pattern replacement | Algorithm audit |