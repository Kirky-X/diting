# 安全认证与配置示例

> 认证+配置类安全案例：观察者模式、策略模式、配置管理、配置策略。详见主索引 [examples.md](examples.md)。

## 1. 完整观察者模式实现

```java
// 安全事件类型
enum SecurityEventType {
    LOGIN_SUCCESS, LOGIN_FAILURE,
    UNAUTHORIZED_ACCESS, DATA_BREACH_ATTEMPT,
    CONFIG_CHANGE, PRIVILEGE_ESCALATION
}

// 安全事件
public class SecurityEvent {
    private final SecurityEventType type;
    private final String user;
    private final String source;
    private final Instant timestamp;
    private final String details;

    public SecurityEvent(SecurityEventType type, String user,
                        String source, String details) {
        this.type = type;
        this.user = user;
        this.source = source;
        this.details = details;
        this.timestamp = Instant.now();
    }
}

// 安全事件观察者
public interface SecurityObserver {
    void update(SecurityEvent event);
}

// 事件管理器
public class SecurityEventManager {
    private static final SecurityEventManager INSTANCE =
        new SecurityEventManager();
    private final List<SecurityObserver> observers =
        new CopyOnWriteArrayList<>();

    private SecurityEventManager() {}

    public static SecurityEventManager getInstance() {
        return INSTANCE;
    }

    public void registerObserver(SecurityObserver observer) {
        observers.add(observer);
    }

    public void notifyObservers(SecurityEvent event) {
        for (SecurityObserver observer : observers) {
            try {
                observer.update(event);
            } catch (Exception e) {
                System.err.println("观察者执行失败: " + e.getMessage());
            }
        }
    }
}

// 暴力破解检测观察者
public class BruteForceDetector implements SecurityObserver {
    private final Map<String, List<Instant>> loginAttempts =
        new ConcurrentHashMap<>();
    private static final int MAX_ATTEMPTS = 5;
    private static final Duration TIME_WINDOW =
        Duration.ofMinutes(15);

    @Override
    public void update(SecurityEvent event) {
        if (event.getType() == SecurityEventType.LOGIN_FAILURE) {
            String user = event.getUser();
            List<Instant> attempts = loginAttempts
                .computeIfAbsent(user, k -> new CopyOnWriteArrayList<>());

            Instant windowStart = Instant.now().minus(TIME_WINDOW);
            attempts.removeIf(t -> t.isBefore(windowStart));
            attempts.add(Instant.now());

            if (attempts.size() >= MAX_ATTEMPTS) {
                // 触发账户锁定
                SecurityEvent lockEvent = new SecurityEvent(
                    SecurityEventType.DATA_BREACH_ATTEMPT,
                    user, "BruteForceDetector",
                    "检测到多次登录失败尝试"
                );
                SecurityEventManager.getInstance().notifyObservers(lockEvent);
            }
        }
    }
}
```

## 2. 策略模式实现

```java
// 加密策略接口
public interface EncryptionStrategy {
    String encrypt(String data);
    String decrypt(String encryptedData);
    String getAlgorithmName();
}

// AES 加密策略
public class AESEncryptionStrategy implements EncryptionStrategy {
    private static final String ALGORITHM = "AES/GCM/NoPadding";
    private final SecretKey key;

    @Override
    public String encrypt(String data) {
        // 实现 AES 加密
    }

    @Override
    public String decrypt(String encryptedData) {
        // 实现 AES 解密
    }

    @Override
    public String getAlgorithmName() {
        return "AES-256-GCM";
    }
}

// RSA 加密策略
public class RSAStrategy implements EncryptionStrategy {
    private static final String ALGORITHM = "RSA/ECB/OAEPWithSHA-256AndMGF1Padding";

    @Override
    public String encrypt(String data) {
        // 实现 RSA 加密
    }

    @Override
    public String decrypt(String encryptedData) {
        // 实现 RSA 解密
    }

    @Override
    public String getAlgorithmName() {
        return "RSA-2048";
    }
}

// 使用策略的安全上下文
public class EncryptionContext {
    private EncryptionStrategy strategy;

    public void setStrategy(EncryptionStrategy strategy) {
        this.strategy = strategy;
    }

    public String encrypt(String data) {
        return strategy.encrypt(data);
    }

    public String decrypt(String encryptedData) {
        return strategy.decrypt(encryptedData);
    }
}
```

## 3. 安全配置管理

```java
public class SecureConfigurationManager {
    private static final String CONFIG_FILE = "security-config.json";
    private final Map<String, Object> config;
    private final EncryptionService encryptionService;

    public SecureConfigurationManager() {
        this.encryptionService = new AESEncryptionService();
        this.config = loadSecureConfig();
    }

    private Map<String, Object> getDefaultConfig() {
        Map<String, Object> defaultConfig = new HashMap<>();
        defaultConfig.put("maxLoginAttempts", 5);
        defaultConfig.put("sessionTimeout", 1800);
        defaultConfig.put("passwordMinLength", 8);
        defaultConfig.put("enable2FA", true);
        defaultConfig.put("encryptionAlgorithm", "AES-256");
        return defaultConfig;
    }

    public String getValue(String key) {
        return String.valueOf(config.get(key));
    }

    public int getIntValue(String key) {
        Object value = config.get(key);
        return value instanceof Number ? ((Number) value).intValue() : 0;
    }

    public boolean getBoolValue(String key) {
        Object value = config.get(key);
        return value instanceof Boolean ? (Boolean) value : false;
    }

    public void updateConfig(String key, Object value, String adminUser) {
        if (!verifyAdminAccess(adminUser)) {
            throw new SecurityException("权限不足");
        }
        logConfigChange(adminUser, key, value);
        config.put(key, value);
        saveEncryptedConfig();
    }

    private boolean verifyAdminAccess(String user) {
        return "admin".equals(user) || "security-admin".equals(user);
    }

    private void logConfigChange(String user, String key, Object value) {
        System.out.println("配置变更: 用户=" + user +
                          ", 键=" + key +
                          ", 值=" + value +
                          ", 时间=" + new Date());
    }
}
```

## 4. 安全配置策略

```java
// 配置策略工厂
class SecurityConfigStrategyFactory {
    public static SecurityConfigStrategy getStrategy(String configType) {
        switch (configType) {
            case "encryption-key":
                return new EncryptionKeyUpdateStrategy();
            case "access-policy":
                return new AccessPolicyUpdateStrategy();
            case "password-policy":
                return new PasswordPolicyUpdateStrategy();
            default:
                throw new IllegalArgumentException("未知配置类型: " + configType);
        }
    }
}

// 配置策略接口
interface SecurityConfigStrategy {
    void apply(String value);
}

class EncryptionKeyUpdateStrategy implements SecurityConfigStrategy {
    @Override
    public void apply(String value) {
        System.out.println("更新加密密钥: " + value);
        // 实现密钥更新逻辑
    }
}

class AccessPolicyUpdateStrategy implements SecurityConfigStrategy {
    @Override
    public void apply(String value) {
        System.out.println("更新访问策略: " + value);
        // 实现访问策略更新逻辑
    }
}

class PasswordPolicyUpdateStrategy implements SecurityConfigStrategy {
    @Override
    public void apply(String value) {
        System.out.println("更新密码策略: " + value);
        // 实现密码策略更新逻辑
    }
}
```
