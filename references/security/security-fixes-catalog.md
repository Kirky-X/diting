# 安全修复目录

> 安全修复详细目录：数据保护、加密、其他安全问题。修复策略详见 [security-fixes.md](security-fixes.md)。

## 数据保护问题

### 敏感数据泄露

**解决方案：加密装饰器**
```java
public class SensitiveDataProtector extends SecurityDecorator {
    private final EncryptionService encryptionService;

    @Override
    public Data process(Data input) {
        // 检测并加密敏感字段
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

### 日志记录敏感信息

**解决方案：日志清理装饰器**
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
                sanitized.put(field.getKey(), "***已脱敏***");
            } else {
                sanitized.put(field.getKey(), field.getValue());
            }
        }
        return wrapped.log(new LogEntry(entry.getLevel(), sanitized));
    }
}
```

## 加密相关问题

### 弱加密算法

**解决方案：策略模式 + 算法白名单**
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
            throw new SecurityException("算法未获批准: " + algorithm);
        }
        return strategy;
    }

    public static Set<String> approvedAlgorithms() {
        return Collections.unmodifiableSet(APPROVED.keySet());
    }
}
```

### 密钥管理问题

**解决方案：密钥管理服务**
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
        // 使用旧密钥重新加密所有数据
        // 更新密钥版本
        hsm.storeKey(keyId, newKey, KeyVersion.NEXT);
    }
}
```

## 其他安全问题

### 路径遍历

**解决方案：路径规范化验证**
```java
public class PathTraversalProtection extends SecurityDecorator {
    private final String baseDirectory;

    @Override
    public InputStream read(String userPath) {
        Path requestedPath = Paths.get(userPath).normalize();
        Path basePath = Paths.get(baseDirectory).toAbsolutePath();

        // 确保路径在 baseDirectory 范围内
        if (!requestedPath.startsWith(basePath)) {
            throw new SecurityException("路径遍历尝试: " + userPath);
        }

        // 检查符号链接
        if (Files.isSymbolicLink(requestedPath)) {
            Path realPath = Files.readSymbolicLink(requestedPath);
            if (!realPath.startsWith(basePath)) {
                throw new SecurityException("符号链接遍历尝试");
            }
        }

        return wrapped.read(userPath);
    }
}
```

### 限流绕过

**解决方案：分布式限流 + 观察者模式**
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

### 不安全的反序列化

**解决方案：白名单验证 + 策略模式**
```java
public class SafeDeserializationStrategy implements DeserializationStrategy {
    private static final Set<Class<?>> ALLOWED_CLASSES = Set.of(
        UserData.class, OrderInfo.class, ConfigData.class
    );

    @Override
    public <T> T deserialize(byte[] data, Class<T> expectedType) {
        if (!ALLOWED_CLASSES.contains(expectedType)) {
            throw new SecurityException(
                "不允许反序列化: " + expectedType.getName()
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
