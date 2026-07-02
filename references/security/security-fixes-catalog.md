# Security Fixes Catalog

> 安全修复详细目录：数据保护、加密、其他安全问题。修复策略详见 [security-fixes.md](security-fixes.md)。

## Data Protection Issues

### Sensitive Data Leakage

**Solution: Encryption Decorator**
```java
public class SensitiveDataProtector extends SecurityDecorator {
    private final EncryptionService encryptionService;

    @Override
    public Data process(Data input) {
        // Detect and encrypt sensitive fields
        if (containsSensitiveData(input)) {
            Data protected = input.clone();
            for (Field field : protected.getSensitiveFields()) {
                field.setValue(encryptionService.encrypt(field.getValue()));
            }
            return wrapped.process(protected);
        }
        return wrapped.process(input);
    }

    private boolean containsSensitiveData(Data data) {
        return data.getSensitiveFields().stream()
            .anyMatch(f -> f.isPii() || f.isFinancial());
    }
}
```

### Logging Sensitive Information

**Solution: Log Sanitization Decorator**
```java
public class LogSanitizerDecorator extends SecurityDecorator {
    private static final Set<String> SENSITIVE_FIELDS = Set.of(
        "password", "creditCard", "ssn", "token", "secret", "apiKey"
    );

    @Override
    public LogEntry log(LogEntry entry) {
        Map<String, Object> sanitized = new HashMap<>();
        for (Map.Entry<String, Object> field : entry.getData().entrySet()) {
            if (SENSITIVE_FIELDS.contains(field.getKey().toLowerCase())) {
                sanitized.put(field.getKey(), "***REDACTED***");
            } else {
                sanitized.put(field.getKey(), field.getValue());
            }
        }
        return wrapped.log(new LogEntry(entry.getLevel(), sanitized));
    }
}
```

## Encryption Related Issues

### Weak Encryption Algorithm

**Solution: Strategy Pattern + Algorithm Whitelist**
```java
public class ApprovedEncryptionStrategies {
    public static final Map<String, EncryptionStrategy> APPROVED = Map.of(
        "AES-256-GCM", new AESGCM256Strategy(),
        "ChaCha20-Poly1305", new ChaCha20Strategy(),
        "RSA-2048", new RSAStrategy()
    );

    public static EncryptionStrategy getStrategy(String algorithm) {
        EncryptionStrategy strategy = APPROVED.get(algorithm);
        if (strategy == null) {
            throw new SecurityException("Algorithm not approved: " + algorithm);
        }
        return strategy;
    }

    public static Set<String> approvedAlgorithms() {
        return Collections.unmodifiableSet(APPROVED.keySet());
    }
}
```

### Key Management Issues

**Solution: Key Management Service**
```java
public class KeyManagementService {
    private final KeyStore keyStore;
    private final HsmService hsm;

    public KeyInfo getKey(String keyId) {
        Key key = hsm.getKey(keyId);
        return new KeyInfo(key.getAlgorithm(), key.getSize());
    }

    public String encrypt(String keyId, String plaintext) {
        Key key = getKey(keyId);
        Cipher cipher = Cipher.getInstance(key.getAlgorithm());
        cipher.init(Cipher.ENCRYPT_MODE, key);
        byte[] ciphertext = cipher.doFinal(plaintext.getBytes());
        return Base64.getEncoder().encodeToString(ciphertext);
    }

    public void rotateKey(String keyId) {
        Key newKey = generateKey();
        // Re-encrypt all data using old key
        // Update key version
        hsm.storeKey(keyId, newKey, KeyVersion.NEXT);
    }
}
```

## Other Security Issues

### Path Traversal

**Solution: Path Normalization Validation**
```java
public class PathTraversalProtection extends SecurityDecorator {
    private final String baseDirectory;

    @Override
    public InputStream read(String userPath) {
        Path requestedPath = Paths.get(userPath).normalize();
        Path basePath = Paths.get(baseDirectory).toAbsolutePath();

        // Ensure path is within baseDirectory
        if (!requestedPath.startsWith(basePath)) {
            throw new SecurityException("Path traversal attempt: " + userPath);
        }

        // Check symbolic links
        if (Files.isSymbolicLink(requestedPath)) {
            Path realPath = Files.readSymbolicLink(requestedPath);
            if (!realPath.startsWith(basePath)) {
                throw new SecurityException("Symbolic link traversal attempt");
            }
        }

        return wrapped.read(userPath);
    }
}
```

### Rate Limiting Bypass

**Solution: Distributed Rate Limiting + Observer Pattern**
```java
public class RateLimitObserver implements SecurityObserver {
    private final RateLimiter rateLimiter;
    private final RedisTemplate<String, Integer> redis;

    @Override
    public void onSecurityEvent(SecurityEvent event) {
        if (event.getType() == SecurityEventType.LOGIN_ATTEMPT) {
            String userIp = event.getSource();
            if (!rateLimiter.tryAcquire(userIp)) {
                firewall.block(userIp, Duration.ofHours(1));
                logSecurityEvent("RATE_LIMIT_EXCEEDED", userIp);
            }
        }
    }
}
```

### Insecure Deserialization

**Solution: Whitelist Validation + Strategy Pattern**
```java
public class SafeDeserializationStrategy implements DeserializationStrategy {
    private static final Set<Class<?>> ALLOWED_CLASSES = Set.of(
        UserData.class, OrderInfo.class, ConfigData.class
    );

    @Override
    public <T> T deserialize(byte[] data, Class<T> expectedType) {
        if (!ALLOWED_CLASSES.contains(expectedType)) {
            throw new SecurityException(
                "Deserialization not allowed for: " + expectedType.getName()
            );
        }

        ObjectInputStream ois = new CustomObjectInputStream(
            new ByteArrayInputStream(data),
            ALLOWED_CLASSES
        );
        return expectedType.cast(ois.readObject());
    }
}
```
