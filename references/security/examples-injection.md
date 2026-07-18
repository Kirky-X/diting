# Security Injection Defense Examples

> Injection-type security cases: Proxy Pattern, Decorator Pattern, Chain of Responsibility Pattern. See the main index [examples.md](examples.md).

## 1. Complete Proxy Pattern Implementation

```java
// Abstract subject
public interface SensitiveResource {
    String readData(String user);
    void writeData(String user, String data);
    void deleteData(String user);
}

// Real subject
public class RealSensitiveResource implements SensitiveResource {
    private final Map<String, String> dataStore = new HashMap<>();

    @Override
    public String readData(String user) {
        return dataStore.getOrDefault(user, "No data");
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

// Audit logger
class AuditLogger {
    private static final Logger logger = Logger.getLogger(AuditLogger.class.getName());

    public void logAccess(String operation, String user) {
        String logEntry = String.format("Access: %s by %s at %s",
            operation, user, new Date());
        logger.info(logEntry);
    }

    public void logSecurityEvent(String eventType, String user) {
        String logEntry = String.format("Security: %s by %s at %s",
            eventType, user, new Date());
        logger.warning(logEntry);
    }
}

// Security proxy
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
            throw new SecurityException("Access denied: " + user);
        }
        auditLogger.logAccess("READ", user);
        return realResource.readData(user);
    }

    @Override
    public void writeData(String user, String data) {
        // Input validation
        if (data == null || data.length() > 1000) {
            auditLogger.logSecurityEvent("INVALID_INPUT", user);
            throw new IllegalArgumentException("Invalid data");
        }

        // Security check
        if (!securityContext.authorize("write", user)) {
            auditLogger.logSecurityEvent("UNAUTHORIZED_WRITE", user);
            throw new SecurityException("Access denied: " + user);
        }

        auditLogger.logAccess("WRITE", user);
        realResource.writeData(user, securityContext.encrypt(data));
    }

    @Override
    public void deleteData(String user) {
        if (!securityContext.authorize("delete", user)) {
            auditLogger.logSecurityEvent("UNAUTHORIZED_DELETE", user);
            throw new SecurityException("Access denied: " + user);
        }
        auditLogger.logAccess("DELETE", user);
        realResource.deleteData(user);
    }
}
```

## 2. Complete Decorator Pattern Implementation

```java
// Abstract component
public interface DataProcessor {
    String process(String input);
}

// Base component
public class BasicDataProcessor implements DataProcessor {
    @Override
    public String process(String input) {
        return "Processed: " + input;
    }
}

// Security decorator base class
public abstract class SecurityDecorator implements DataProcessor {
    protected DataProcessor wrappedProcessor;

    public SecurityDecorator(DataProcessor processor) {
        this.wrappedProcessor = processor;
    }
}

// Input validation decorator
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
            throw new IllegalArgumentException("Input cannot be empty");
        }
        if (input.length() > MAX_LENGTH) {
            throw new IllegalArgumentException("Input too long");
        }
        if (DANGEROUS_CHARS.matcher(input).find()) {
            throw new SecurityException("Input contains dangerous characters");
        }
        return wrappedProcessor.process(input);
    }
}

// Encryption decorator
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

// Audit decorator
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
// Security request
public class SecurityRequest {
    private String user;
    private String operation;
    private String resource;
    private Map<String, Object> data;

    // getters and setters
}

// Security handler abstract class
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

// Authentication handler
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

// Authorization handler
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

// Usage example
SecurityHandler chain = new AuthenticationHandler(authService)
    .setNext(new AuthorizationHandler(permissionService))
    .setNext(new ValidationHandler(validator))
    .setNext(new EncryptionHandler(encryptionService));

if (chain.check(request)) {
    // Execute operation
}
```
