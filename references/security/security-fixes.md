# 安全问题与设计模式解决方案

> 安全修复策略：注入攻击与认证授权问题。详细修复（数据保护/加密/其他安全）详见 [security-fixes-catalog.md](security-fixes-catalog.md)。

## 注入攻击

### SQL 注入

**问题代码**：
```java
// 危险！直接 SQL 拼接
String query = "SELECT * FROM users WHERE id = " + userId;
Statement stmt = connection.createStatement();
ResultSet rs = stmt.executeQuery(query);
```

**解决方案：参数化查询 + 装饰器模式**
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

**清单**：
- [ ] 所有数据库查询使用参数化查询
- [ ] 使用 ORM 框架查询构建器
- [ ] 实施严格输入验证
- [ ] 数据库使用最小权限账户

### XSS 攻击

**问题代码**：
```java
// 危险！直接输出用户输入
String userInput = request.getParameter("comment");
response.getWriter().write("<div>" + userInput + "</div>");
```

**解决方案：输出编码 + 装饰器模式**
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

### 命令注入

**问题代码**：
```java
// 危险！直接执行用户输入作为命令
String filename = request.getParameter("file");
Runtime.getRuntime().exec("cat " + filename);
```

**解决方案：白名单验证 + 策略模式**
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

## 认证与授权问题

### 弱密码策略

**解决方案：策略模式 + 验证装饰器**
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

### 会话管理问题

**解决方案：安全会话管理策略**
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

### 权限提升

**解决方案：代理模式 + 最小权限检查**
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

## 安全清单快速参考

| 漏洞类型 | 检测方法 | 修复模式 | 验证方法 |
|----------|----------|----------|----------|
| SQL 注入 | 代码审查、SAST | 参数化查询 | 渗透测试 |
| XSS | DAST、代码审查 | 输出编码 | 自动化扫描 |
| CSRF | 测试验证 | CSRF Token | 安全测试 |
| 认证缺陷 | 代码审查、测试 | 强认证策略 | 渗透测试 |
| 敏感数据泄露 | DAST、人工审查 | 加密、脱敏 | 数据流分析 |
| 访问控制缺陷 | 代码审查、测试 | 代理模式检查 | 权限测试 |
| 加密缺陷 | 静态分析 | 策略模式替换 | 算法审计 |
