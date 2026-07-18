# Security Injection Defense Examples

> Injection-type security cases: Proxy Pattern, Decorator Pattern, Chain of Responsibility Pattern. See the main index [examples.md](examples.md).

## 1. Complete Proxy Pattern Implementation

```java
// 抽象主题
public interface SensitiveResource {
    String readData(String user);
    void writeData(String user, String data);
    void deleteData(String user);
}

// 真实主题
public class RealSensitiveResource implements SensitiveResource {
    private final Map<String, String> dataStore = new HashMap<>();

    @Override
    public String readData(String user) {
        return dataStore.getOrDefault(user, "无数据");
    }

    @Override
    public void writeData(String user, String data) {
        dataStore.put(user, data);
    }

    @Override
    public void deleteData(String user) {
        dataStore.remove(user);
    }
}

// 审计日志器
class AuditLogger {
    private static final Logger logger = Logger.getLogger(AuditLogger.class.getName());

    public void logAccess(String operation, String user) {
        String logEntry = String.format("访问: %s 由 %s 于 %s",
            operation, user, new Date());
        logger.info(logEntry);
    }

    public void logSecurityEvent(String eventType, String user) {
        String logEntry = String.format("安全: %s 由 %s 于 %s",
            eventType, user, new Date());
        logger.warning(logEntry);
    }
}

// 安全代理
public class SecurityProxy implements SensitiveResource {
    private final SensitiveResource realResource;
    private final SecurityContext securityContext;
    private final AuditLogger auditLogger;

    public SecurityProxy(SensitiveResource realResource,
                        SecurityContext securityContext) {
        this.realResource = realResource;
        this.securityContext = securityContext;
        this.auditLogger = new AuditLogger();
    }

    @Override
    public String readData(String user) {
        if (!securityContext.authorize("read", user)) {
            auditLogger.logSecurityEvent("UNAUTHORIZED_READ", user);
            throw new SecurityException("访问被拒绝: " + user);
        }
        auditLogger.logAccess("READ", user);
        return realResource.readData(user);
    }

    @Override
    public void writeData(String user, String data) {
        // 输入验证
        if (data == null || data.length() > 1000) {
            auditLogger.logSecurityEvent("INVALID_INPUT", user);
            throw new IllegalArgumentException("无效数据");
        }

        // 安全检查
        if (!securityContext.authorize("write", user)) {
            auditLogger.logSecurityEvent("UNAUTHORIZED_WRITE", user);
            throw new SecurityException("访问被拒绝: " + user);
        }

        auditLogger.logAccess("WRITE", user);
        realResource.writeData(user, securityContext.encrypt(data));
    }

    @Override
    public void deleteData(String user) {
        if (!securityContext.authorize("delete", user)) {
            auditLogger.logSecurityEvent("UNAUTHORIZED_DELETE", user);
            throw new SecurityException("访问被拒绝: " + user);
        }
        auditLogger.logAccess("DELETE", user);
        realResource.deleteData(user);
    }
}
```

## 2. Complete Decorator Pattern Implementation

```java
// 抽象组件
public interface DataProcessor {
    String process(String input);
}

// 基础组件
public class BasicDataProcessor implements DataProcessor {
    @Override
    public String process(String input) {
        return "已处理: " + input;
    }
}

// 安全装饰器基类
public abstract class SecurityDecorator implements DataProcessor {
    protected DataProcessor wrappedProcessor;

    public SecurityDecorator(DataProcessor processor) {
        this.wrappedProcessor = processor;
    }
}

// 输入验证装饰器
public class InputValidationDecorator extends SecurityDecorator {
    private static final int MAX_LENGTH = 1000;
    private static final Pattern DANGEROUS_CHARS =
        Pattern.compile("[<>\"'&;");

    public InputValidationDecorator(DataProcessor processor) {
        super(processor);
    }

    @Override
    public String process(String input) {
        if (input == null || input.trim().isEmpty()) {
            throw new IllegalArgumentException("输入不能为空");
        }
        if (input.length() > MAX_LENGTH) {
            throw new IllegalArgumentException("输入过长");
        }
        if (DANGEROUS_CHARS.matcher(input).find()) {
            throw new SecurityException("输入包含危险字符");
        }
        return wrappedProcessor.process(input);
    }
}

// 加密装饰器
public class EncryptionDecorator extends SecurityDecorator {
    private final EncryptionService encryptionService;

    public EncryptionDecorator(DataProcessor processor) {
        super(processor);
        this.encryptionService = new AESEncryptionService();
    }

    @Override
    public String process(String input) {
        String encrypted = encryptionService.encrypt(input);
        String result = wrappedProcessor.process(encrypted);
        return encryptionService.decrypt(result);
    }
}

// 审计装饰器
public class AuditDecorator extends SecurityDecorator {
    private final AuditLogger logger;

    public AuditDecorator(DataProcessor processor) {
        super(processor);
        this.logger = new AuditLogger();
    }

    @Override
    public String process(String input) {
        long start = System.currentTimeMillis();
        try {
            String result = wrappedProcessor.process(input);
            logger.logAccess("PROCESS", "user");
            return result;
        } catch (Exception e) {
            logger.logSecurityEvent("PROCESS_ERROR", "user");
            throw e;
        }
    }
}
```

## 3. Chain of Responsibility Pattern Implementation

```java
// 安全请求
public class SecurityRequest {
    private String user;
    private String operation;
    private String resource;
    private Map<String, Object> data;

    // getters 和 setters
}

// 安全处理器抽象类
public abstract class SecurityHandler {
    private SecurityHandler next;

    public SecurityHandler setNext(SecurityHandler handler) {
        this.next = handler;
        return handler;
    }

    public abstract boolean check(SecurityRequest request);

    protected boolean checkNext(SecurityRequest request) {
        return next == null || next.check(request);
    }
}

// 认证处理器
public class AuthenticationHandler extends SecurityHandler {
    private final AuthService authService;

    @Override
    public boolean check(SecurityRequest request) {
        boolean authenticated = authService.isAuthenticated(request.getUser());
        if (!authenticated) {
            logSecurityEvent("AUTH_FAILURE", request.getUser());
        }
        return authenticated && checkNext(request);
    }
}

// 授权处理器
public class AuthorizationHandler extends SecurityHandler {
    private final PermissionService permissionService;

    @Override
    public boolean check(SecurityRequest request) {
        boolean authorized = permissionService.hasPermission(
            request.getUser(), request.getOperation(), request.getResource());
        if (!authorized) {
            logSecurityEvent("AUTHZ_FAILURE", request.getUser());
        }
        return authorized && checkNext(request);
    }
}

// 使用示例
SecurityHandler chain = new AuthenticationHandler(authService)
    .setNext(new AuthorizationHandler(permissionService))
    .setNext(new ValidationHandler(validator))
    .setNext(new EncryptionHandler(encryptionService));

if (chain.check(request)) {
    // 执行操作
}
```