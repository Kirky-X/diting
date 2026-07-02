# 安全审查命令

安全审查模式 —— OWASP Top 10 (2021) + CWE + 现代攻击向量检测

## 用法

```bash
review security [target-path]
```

## 检查内容

### 1. OWASP Top 10 (2021)

| #   | 类别                          | 检查要点                                                                   |
| --- | ----------------------------- | -------------------------------------------------------------------------- |
| A01 | 访问控制失效（Broken Access Control） | 缺失认证检查、IDOR、路径遍历、CORS 配置错误                                |
| A02 | 加密失败（Cryptographic Failures） | 弱算法（MD5/SHA1/DES）、硬编码密钥、HTTP 非 HTTPS、PII 未加密              |
| A03 | 注入（Injection）              | SQL、NoSQL、LDAP、OS 命令、SSTI、XPath 注入                                |
| A04 | 不安全设计（Insecure Design）   | 缺失威胁建模、未应用安全设计模式                                           |
| A05 | 安全配置错误（Security Misconfiguration） | 调试模式开启、默认凭据、冗长错误、启用不必要功能                           |
| A06 | 易受攻击的组件（Vulnerable Components） | 已知 CVE 的过期依赖、废弃库                                                |
| A07 | 认证和会话失效（Auth & Session Failures） | 弱密码、无 MFA、会话固定、不安全的 JWT                                     |
| A08 | 软件和数据完整性失效（Software & Data Integrity） | 未签名包、无完整性检查的 CI/CD、反序列化                                   |
| A09 | 日志和监控失效（Logging & Monitoring Failures） | 无安全事件日志、日志含 PII/密钥                                           |
| A10 | SSRF                          | 用户控制的 URL 被服务端获取、无 URL 白名单                                 |

---

### 2. 认证和授权

```
□ 无硬编码凭据（密码、API key、token 写在代码里）
□ 密码用 bcrypt / Argon2 / scrypt 哈希（不要用 MD5/SHA1/纯 SHA256）
□ 会话 ID 加密随机，登录后重新生成
□ Cookie：HttpOnly + Secure + SameSite=Strict/Lax
□ JWT：短过期时间、验签、不只信任解码后的 payload
□ 最小权限原则落实
□ 每个受保护路由都检查授权（不仅在登录时）
□ IDOR 防护：用户只能访问自己的资源
□ 登录端点有账户锁定/限流
```

### 3. 输入验证和输出编码

```
□ 所有用户输入已验证（类型、长度、格式、范围）
□ 白名单验证优于黑名单
□ SQL：参数化查询 / 预编译语句 / ORM —— 不用字符串拼接
□ NoSQL：类型化查询，$where 不用用户数据
□ XSS：输出 HTML 编码，用 textContent 而非 innerHTML，设置 CSP 头
□ CSRF：状态变更表单加 token，SameSite cookie 属性
□ 文件上传：MIME 类型 + 扩展名校验、随机文件名、非可执行目录
□ 路径遍历：Path.resolve() / os.path.realpath() 规范化后检查前缀
□ 命令注入：不用 shell=True 加用户输入，用数组
□ SSTI：用户输入不在模板引擎中渲染（Jinja2、Handlebars 等）
```

### 4. 加密

```
□ 对称：AES-256-GCM 或 ChaCha20-Poly1305（不要用 AES-ECB、3DES、RC4）
□ 非对称：RSA-2048+ 配 OAEP，或 EC P-256+（不要用 RSA-512/1024）
□ 哈希：SHA-256+ 用于完整性；bcrypt/Argon2 用于密码（不要用 MD5/SHA1）
□ 随机：使用 CSPRNG（不要用 Math.random()、random.random()）
□ 密钥：不硬编码，从 env/KMS 加载，轮换
□ TLS：强制 1.2+，证书校验
□ 密钥：不在源码、日志、URL、错误信息中
```

### 5. 错误处理和日志

```
□ 堆栈跟踪不暴露给客户端
□ 给用户通用错误信息；详细信息只进日志
□ 安全事件记录：登录成功/失败、权限拒绝、配置变更
□ 日志中不含：密码、token、完整卡号、SSN
□ 异常不被静默吞掉
```

### 6. 依赖安全

```
□ 无已知 critical/high CVE 的包（检查 npm audit / safety / cargo audit）
□ 无废弃包（最后提交 > 2 年、无维护者）
□ 依赖锁定或 lock 文件已提交
□ 供应链：包来自官方仓库，非任意 URL
```

### 7. 现代和语言专属关注点

**Python**

- `pickle.loads()` 处理不可信数据 → 反序列化 RCE
- `eval()` / `exec()` 处理用户输入 → 代码注入
- `subprocess(shell=True, ...)` → 命令注入
- `yaml.load()` → 用 `yaml.safe_load()`
- `marshal.load()` 处理不可信数据 → 反序列化 RCE
- `shlex.quote()` 用于安全 shell 参数转义

**JavaScript / TypeScript**

- `innerHTML` / `dangerouslySetInnerHTML` 处理用户数据 → XSS
- `eval()` / `new Function()` 处理用户数据 → 代码注入
- 对象合并工具的 prototype 污染（`Object.assign`、spread 加用户输入）
- 灾难性回溯的正则（ReDoS）
- `JSON.parse()` 处理不可信输入 → 捕获异常、校验结构

**Java**

- `ObjectInputStream` 处理不可信数据 → 反序列化 RCE
- SpEL / OGNL 表达式注入
- XXE：在 XML 解析器中禁用 DOCTYPE
- JNDI lookup 加用户输入 → Log4Shell 式 RCE
- `ScriptEngine.eval()` 加用户输入 → 代码注入
- `XMLDecoder` 处理不可信数据 → 反序列化 RCE

**Go**

- `os/exec` 加用户控制参数 → 命令注入
- `text/template` vs `html/template`（后者转义，前者不转义）
- 用于缓冲区大小的计算中的整数溢出
- `filepath.Join` 加用户输入 → 路径遍历（用 `filepath.Clean`）

**Rust**

- `unsafe` 块无清晰安全不变量
- 未校验的 `FromStr` 实现
- 不匹配大小的 transmute 操作

**PHP**

- `unserialize()` 加用户输入 → 对象注入
- `include` / `require` 加用户输入 → LFI/RFI
- `preg_replace` 加 /e 修饰符 → 代码执行（已废弃但检查遗留代码）

### 8. 现代攻击向量

**SSRF（服务端请求伪造）**

```
□ URL 输入对白名单校验
□ 内网 IP 段封禁（10.x、172.16-31.x、192.168.x、169.254.x、127.x）
□ 云元数据端点封禁（169.254.169.254）
□ DNS 重绑定防护到位
□ 重定向跟随受限或禁用
```

**开放重定向**

```
□ 重定向 URL 仅来自白名单
□ 相对重定向优于绝对重定向
□ Referer 头的 `open redirect` 不可利用
□ OAuth state 参数已校验
```

**Prototype 污染（JavaScript）**

```javascript
// ❌ 易受攻击
function merge(target, source) {
  for (let key in source) {
    target[key] = source[key];
  }
}

// ✅ 安全 - 检查 __proto__、constructor、prototype
function safeMerge(target, source) {
  const dangerous = ["__proto__", "constructor", "prototype"];
  for (let key in source) {
    if (!dangerous.includes(key)) {
      target[key] = source[key];
    }
  }
}
```

**ReDoS（正则表达式 DoS）**

```javascript
// ❌ 易受攻击 - 灾难性回溯
/^(a+)+$/.test('aaaaaaaaaaaaaaaaaaaaa!')

// ✅ 安全 - 避免嵌套量词
/^a+$/.test('aaa')
```

---

## 安全设计原则

1. **纵深防御** —— 多个独立层；单点失败 ≠ 全面沦陷
2. **最小权限** —— 只授予所需权限，不多给
3. **默认拒绝** —— 默认阻止，显式允许
4. **失败安全** —— 出错时拒绝访问，不静默允许
5. **永不信任输入** —— 无论来源，校验所有外部输入
6. **左移安全** —— 安全在设计阶段，而非事后附加

---

## 参考

- [security-expert-guide.md](../security/security-expert-guide.md) — 完整专家指南
- [security-fixes.md](../security/security-fixes.md) — 常见漏洞修复模式
- [security-design-patterns.md](../security/security-design-patterns.md) — 安全模式目录（架构/设计/实现三层：Single Access Point、Check Point、RAII…）+ STRIDE→pattern 映射
- [pattern-classification.md](../security/pattern-classification.md) — 带安全包装的 GoF 模式（Secure Singleton 模板、Decorator 链）
- [examples.md](../security/examples.md) — 完整可运行代码示例（Proxy 模式、JWT、参数化查询）
- [quality/security-checklist.md](../quality/security-checklist.md) — 详细检查清单

## 相关命令

- [performance.md](performance.md)
- [quality.md](quality.md)
- [architecture.md](architecture.md)
- [simplification.md](simplification.md)
