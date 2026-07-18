# Security OWASP & Audit Examples

> OWASP defense and audit cases: defense in depth, audit systems, alert logging, audit analysis. See the main index [examples.md](examples.md).

## 1. Defense in Depth System

```java
public class DefenseInDepthManager {
    private final List<SecurityLayer> layers = new ArrayList<>();

    public DefenseInDepthManager() {
        layers.add(new InputValidationLayer());
        layers.add(new AuthLayer());
        layers.add(new EncryptionLayer());
        layers.add(new AuditLayer());
        layers.add(new IntrusionDetectionLayer());
    }

    public boolean validateRequest(SecurityRequest request) {
        for (SecurityLayer layer : layers) {
            if (!layer.check(request)) {
                return false;
            }
        }
        return true;
    }
}

interface SecurityLayer {
    boolean check(SecurityRequest request);
}

class InputValidationLayer implements SecurityLayer {
    @Override
    public boolean check(SecurityRequest request) {
        return request.getData() != null &&
               request.getData().length() < 1000 &&
               !request.getData().contains("<script>");
    }
}

class AuthLayer implements SecurityLayer {
    @Override
    public boolean check(SecurityRequest request) {
        return !"attacker".equals(request.getUser());
    }
}

class EncryptionLayer implements SecurityLayer {
    @Override
    public boolean check(SecurityRequest request) {
        return request.getData() != null;
    }
}

class AuditLayer implements SecurityLayer {
    @Override
    public boolean check(SecurityRequest request) {
        System.out.println("审计: " + request.getUser() + " - " + request.getAction());
        return true;
    }
}

class IntrusionDetectionLayer implements SecurityLayer {
    private final Map<String, Integer> requestCount = new ConcurrentHashMap<>();

    @Override
    public boolean check(SecurityRequest request) {
        String user = request.getUser();
        int count = requestCount.merge(user, 1, Integer::sum);
        if (count > 100) {
            System.err.println("IDS: " + user + " 请求过多");
            return false;
        }
        return true;
    }
}
```

## 2. Security Audit System

```java
public interface AuditLogger {
    void logSecurityEvent(SecurityEvent event);
    void logAccess(String user, String resource, String action);
    void logError(String user, String error, String details);
    List<AuditRecord> getAuditTrail(String user, Instant from, Instant to);
}

public class AuditRecord {
    private final String id;
    private final String user;
    private final String action;
    private final String resource;
    private final Instant timestamp;
    private final boolean success;
    private final String details;

    public AuditRecord(String user, String action, String resource,
                      boolean success, String details) {
        this.id = UUID.randomUUID().toString();
        this.user = user;
        this.action = action;
        this.resource = resource;
        this.timestamp = Instant.now();
        this.success = success;
        this.details = details;
    }
}

public class DatabaseAuditLogger implements AuditLogger {
    private final DataSource dataSource;

    @Override
    public void logSecurityEvent(SecurityEvent event) {
        String sql = "INSERT INTO security_events (event_type, user, source, details, timestamp) " +
                    "VALUES (?, ?, ?, ?, ?)";
        try (Connection conn = dataSource.getConnection();
             PreparedStatement stmt = conn.prepareStatement(sql)) {
            stmt.setString(1, event.getType().name());
            stmt.setString(2, event.getUser());
            stmt.setString(3, event.getSource());
            stmt.setString(4, event.getDetails());
            stmt.setTimestamp(5, Timestamp.from(event.getTimestamp()));
            stmt.executeUpdate();
        } catch (SQLException e) {
            System.err.println("记录安全事件失败: " + e.getMessage());
        }
    }

    @Override
    public void logAccess(String user, String resource, String action) {
        String sql = "INSERT INTO access_logs (user, resource, action, timestamp) VALUES (?, ?, ?, ?)";
        try (Connection conn = dataSource.getConnection();
             PreparedStatement stmt = conn.prepareStatement(sql)) {
            stmt.setString(1, user);
            stmt.setString(2, resource);
            stmt.setString(3, action);
            stmt.setTimestamp(4, Timestamp.from(Instant.now()));
            stmt.executeUpdate();
        } catch (SQLException e) {
            System.err.println("记录访问失败: " + e.getMessage());
        }
    }

    @Override
    public List<AuditRecord> getAuditTrail(String user, Instant from, Instant to) {
        List<AuditRecord> records = new ArrayList<>();
        String sql = "SELECT * FROM audit_logs WHERE user = ? AND timestamp BETWEEN ? AND ?";
        try (Connection conn = dataSource.getConnection();
             PreparedStatement stmt = conn.prepareStatement(sql)) {
            stmt.setString(1, user);
            stmt.setTimestamp(2, Timestamp.from(from));
            stmt.setTimestamp(3, Timestamp.from(to));
            ResultSet rs = stmt.executeQuery();
            while (rs.next()) {
                records.add(new AuditRecord(
                    rs.getString("user"),
                    rs.getString("action"),
                    rs.getString("resource"),
                    rs.getBoolean("success"),
                    rs.getString("details")
                ));
            }
        } catch (SQLException e) {
            System.err.println("获取审计轨迹失败: " + e.getMessage());
        }
        return records;
    }
}
```

## 3. Alert & Log Observer

```java
// 日志观察者
public class LoggingObserver implements SecurityObserver {
    private static final Logger logger = Logger.getLogger(LoggingObserver.class.getName());

    @Override
    public void update(SecurityEvent event) {
        String logMessage = String.format("[%s] %s - 用户: %s, 来源: %s, 详情: %s",
            event.getTimestamp(),
            event.getType(),
            event.getUser(),
            event.getSource(),
            event.getDetails()
        );

        if (event.getType() == SecurityEventType.UNAUTHORIZED_ACCESS ||
            event.getType() == SecurityEventType.DATA_BREACH_ATTEMPT) {
            logger.severe(logMessage);
        } else {
            logger.info(logMessage);
        }
    }
}

// 告警观察者
public class AlertObserver implements SecurityObserver {
    private final EmailService emailService;
    private final Set<SecurityEventType> alertTypes;

    public AlertObserver(EmailService emailService) {
        this.emailService = emailService;
        this.alertTypes = EnumSet.of(
            SecurityEventType.UNAUTHORIZED_ACCESS,
            SecurityEventType.DATA_BREACH_ATTEMPT,
            SecurityEventType.PRIVILEGE_ESCALATION
        );
    }

    @Override
    public void update(SecurityEvent event) {
        if (alertTypes.contains(event.getType())) {
            String subject = "安全告警: " + event.getType();
            String body = String.format(
                "检测到安全事件:\n类型: %s\n用户: %s\n来源: %s\n时间: %s\n详情: %s",
                event.getType(), event.getUser(), event.getSource(),
                event.getTimestamp(), event.getDetails()
            );
            emailService.sendAlert("security@company.com", subject, body);
        }
    }
}
```

## 4. Audit Analyzer

```java
public class AuditAnalyzer {
    private final AuditLogger auditLogger;

    public AuditAnalyzer(AuditLogger auditLogger) {
        this.auditLogger = auditLogger;
    }

    // 检测可疑登录模式
    public void detectSuspiciousLogins(Instant from, Instant to) {
        List<AuditRecord> records = auditLogger.getAuditTrail("ALL", from, to);
        Map<String, Long> loginFailures = records.stream()
            .filter(r -> r.getAction().equals("LOGIN") && !r.isSuccess())
            .collect(Collectors.groupingBy(AuditRecord::getUser, Collectors.counting()));

        loginFailures.forEach((user, count) -> {
            if (count > 5) {
                System.err.println("可疑: 用户 " + user + " 有 " + count + " 次登录失败");
            }
        });
    }

    // 检测权限提升
    public void detectPrivilegeEscalation(Instant from, Instant to) {
        List<AuditRecord> records = auditLogger.getAuditTrail("ALL", from, to);
        records.stream()
            .filter(r -> r.getAction().equals("PRIVILEGE_CHANGE"))
            .forEach(r -> System.out.println("权限提升: " + r));
    }

    // 生成安全报告
    public String generateSecurityReport(Instant from, Instant to) {
        List<AuditRecord> records = auditLogger.getAuditTrail("ALL", from, to);
        long totalEvents = records.size();
        long failedEvents = records.stream().filter(r -> !r.isSuccess()).count();
        long uniqueUsers = records.stream().map(AuditRecord::getUser).distinct().count();

        return String.format(
            "安全报告:\n时间段: %s 至 %s\n事件总数: %d\n" +
            "失败事件: %d\n独立用户: %d\n失败率: %.2f%%",
            from, to, totalEvents, failedEvents, uniqueUsers,
            (double) failedEvents / totalEvents * 100
        );
    }
}
```