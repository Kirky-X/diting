# Security Authentication & Configuration Examples

> Authentication + configuration security cases: Observer Pattern, Strategy Pattern, configuration management, configuration strategies. See the main index [examples.md](examples.md).

## 1. Complete Observer Pattern Implementation

```java
// Security event types
enum SecurityEventType {
    LOGIN_SUCCESS, LOGIN_FAILURE,
    UNAUTHORIZED_ACCESS, DATA_BREACH_ATTEMPT,
    CONFIG_CHANGE, PRIVILEGE_ESCALATION
}

// Security event
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

// Security event observer
public interface SecurityObserver {
    void update(SecurityEvent event);
}

// Event manager
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
                System.err.println("Observer execution failed: " + e.getMessage());
            }
        }
    }
}

// Brute force detection observer
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
                // Trigger account lockout
                SecurityEvent lockEvent = new SecurityEvent(
                    SecurityEventType.DATA_BREACH_ATTEMPT,
                    user, "BruteForceDetector",
                    "Multiple login failure attempts detected"
                );
                SecurityEventManager.getInstance().notifyObservers(lockEvent);
            }
        }
    }
}
```

## 2. Strategy Pattern Implementation

```java
// Encryption strategy interface
public interface EncryptionStrategy {
    String encrypt(String data);
    String decrypt(String encryptedData);
    String getAlgorithmName();
}

// AES encryption strategy
public class AESEncryptionStrategy implements EncryptionStrategy {
    private static final String ALGORITHM = "AES/GCM/NoPadding";
    private final SecretKey key;

    @Override
    public String encrypt(String data) {
        // Implement AES encryption
    }

    @Override
    public String decrypt(String encryptedData) {
        // Implement AES decryption
    }

    @Override
    public String getAlgorithmName() {
        return "AES-256-GCM";
    }
}

// RSA encryption strategy
public class RSAStrategy implements EncryptionStrategy {
    private static final String ALGORITHM = "RSA/ECB/OAEPWithSHA-256AndMGF1Padding";

    @Override
    public String encrypt(String data) {
        // Implement RSA encryption
    }

    @Override
    public String decrypt(String encryptedData) {
        // Implement RSA decryption
    }

    @Override
    public String getAlgorithmName() {
        return "RSA-2048";
    }
}

// Security context using strategy
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

## 3. Secure Configuration Management

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
            throw new SecurityException("Insufficient permissions");
        }
        logConfigChange(adminUser, key, value);
        config.put(key, value);
        saveEncryptedConfig();
    }

    private boolean verifyAdminAccess(String user) {
        return "admin".equals(user) || "security-admin".equals(user);
    }

    private void logConfigChange(String user, String key, Object value) {
        System.out.println("Config change: user=" + user +
                          ", key=" + key +
                          ", value=" + value +
                          ", time=" + new Date());
    }
}
```

## 4. Security Configuration Strategy

```java
// Config strategy factory
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
                throw new IllegalArgumentException("Unknown config type: " + configType);
        }
    }
}

// Config strategy interface
interface SecurityConfigStrategy {
    void apply(String value);
}

class EncryptionKeyUpdateStrategy implements SecurityConfigStrategy {
    @Override
    public void apply(String value) {
        System.out.println("Updating encryption key: " + value);
        // Implement key update logic
    }
}

class AccessPolicyUpdateStrategy implements SecurityConfigStrategy {
    @Override
    public void apply(String value) {
        System.out.println("Updating access policy: " + value);
        // Implement access policy update logic
    }
}

class PasswordPolicyUpdateStrategy implements SecurityConfigStrategy {
    @Override
    public void apply(String value) {
        System.out.println("Updating password policy: " + value);
        // Implement password policy update logic
    }
}
```
