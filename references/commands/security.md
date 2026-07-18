# Security Review Command

Security Review Mode — OWASP Top 10 (2021) + CWE + modern attack vector detection

## Usage

```bash
review security [target-path]
```

## Checklist

### 1. OWASP Top 10 (2021)

| #   | Category                        | Checkpoints                                                                |
| --- | ------------------------------- | -------------------------------------------------------------------------- |
| A01 | Broken Access Control           | Missing auth checks, IDOR, path traversal, CORS misconfiguration           |
| A02 | Cryptographic Failures          | Weak algorithms (MD5/SHA1/DES), hardcoded keys, HTTP instead of HTTPS, unencrypted PII |
| A03 | Injection                       | SQL, NoSQL, LDAP, OS command, SSTI, XPath injection                       |
| A04 | Insecure Design                 | Missing threat modeling, security design patterns not applied              |
| A05 | Security Misconfiguration       | Debug mode enabled, default credentials, verbose errors, unnecessary features enabled |
| A06 | Vulnerable Components           | Outdated dependencies with known CVEs, deprecated libraries               |
| A07 | Auth & Session Failures         | Weak passwords, no MFA, session fixation, insecure JWT                    |
| A08 | Software & Data Integrity       | Unsigned packages, CI/CD without integrity checks, deserialization        |
| A09 | Logging & Monitoring Failures   | No security event logging, logs containing PII/keys                       |
| A10 | SSRF                            | User-controlled URLs fetched server-side, no URL allowlist                |

---

### 2. Authentication and Authorization

```
□ No hardcoded credentials (passwords, API keys, tokens written in code)
□ Passwords hashed with bcrypt / Argon2 / scrypt (not MD5/SHA1/plain SHA256)
□ Session IDs cryptographically random, regenerated after login
□ Cookie: HttpOnly + Secure + SameSite=Strict/Lax
□ JWT: short expiration, signature verified, don't trust decoded payload alone
□ Least privilege principle enforced
□ Every protected route checks authorization (not just at login)
□ IDOR protection: users can only access their own resources
□ Login endpoints have account lockout/rate limiting
```

### 3. Input Validation and Output Encoding

```
□ All user input validated (type, length, format, range)
□ Allowlist validation preferred over denylist
□ SQL: parameterized queries / prepared statements / ORM — no string concatenation
□ NoSQL: typed queries, $where not using user data
□ XSS: output HTML-encoded, use textContent instead of innerHTML, set CSP headers
□ CSRF: tokens on state-changing forms, SameSite cookie attribute
□ File upload: MIME type + extension validation, random filename, non-executable directory
□ Path traversal: Path.resolve() / os.path.realpath() normalization then prefix check
□ Command injection: no shell=True with user input, use arrays
□ SSTI: user input not rendered in template engines (Jinja2, Handlebars, etc.)
```

### 4. Cryptography

```
□ Symmetric: AES-256-GCM or ChaCha20-Poly1305 (not AES-ECB, 3DES, RC4)
□ Asymmetric: RSA-2048+ with OAEP, or EC P-256+ (not RSA-512/1024)
□ Hashing: SHA-256+ for integrity; bcrypt/Argon2 for passwords (not MD5/SHA1)
□ Randomness: use CSPRNG (not Math.random(), random.random())
□ Keys: not hardcoded, loaded from env/KMS, rotated
□ TLS: enforce 1.2+, certificate validation
□ Secrets: not in source code, logs, URLs, error messages
```

### 5. Error Handling and Logging

```
□ Stack traces not exposed to clients
□ Generic error messages for users; details only in logs
□ Security events logged: login success/failure, permission denied, config changes
□ Logs do not contain: passwords, tokens, full card numbers, SSNs
□ Exceptions not silently swallowed
```

### 6. Dependency Security

```
□ No packages with known critical/high CVEs (check npm audit / safety / cargo audit)
□ No deprecated packages (last commit > 2 years, no maintainers)
□ Dependencies locked or lock files committed
□ Supply chain: packages from official repositories, not arbitrary URLs
```

### 7. Modern and Language-Specific Concerns

**Python**

- `pickle.loads()` on untrusted data → deserialization RCE
- `eval()` / `exec()` on user input → code injection
- `subprocess(shell=True, ...)` → command injection
- `yaml.load()` → use `yaml.safe_load()`
- `marshal.load()` on untrusted data → deserialization RCE
- `shlex.quote()` for safe shell argument escaping

**JavaScript / TypeScript**

- `innerHTML` / `dangerouslySetInnerHTML` with user data → XSS
- `eval()` / `new Function()` with user data → code injection
- Prototype pollution via object merge utilities (`Object.assign`, spread with user input)
- ReDoS (catastrophic backtracking in regex)
- `JSON.parse()` on untrusted input → catch exception, validate structure

**Java**

- `ObjectInputStream` on untrusted data → deserialization RCE
- SpEL / OGNL expression injection
- XXE: disable DOCTYPE in XML parsers
- JNDI lookup with user input → Log4Shell-style RCE
- `ScriptEngine.eval()` with user input → code injection
- `XMLDecoder` on untrusted data → deserialization RCE

**Go**

- `os/exec` with user-controlled parameters → command injection
- `text/template` vs `html/template` (the latter escapes, the former does not)
- Integer overflow in buffer size calculations
- `filepath.Join` with user input → path traversal (use `filepath.Clean`)

**Rust**

- `unsafe` blocks without clear safety invariants
- Unvalidated `FromStr` implementations
- Size-mismatched transmute operations

**PHP**

- `unserialize()` with user input → object injection
- `include` / `require` with user input → LFI/RFI
- `preg_replace` with /e modifier → code execution (deprecated but check legacy code)

### 8. Modern Attack Vectors

**SSRF (Server-Side Request Forgery)**

```
□ URL input validated against allowlist
□ Internal IP ranges blocked (10.x, 172.16-31.x, 192.168.x, 169.254.x, 127.x)
□ Cloud metadata endpoints blocked (169.254.169.254)
□ DNS rebinding protection in place
□ Redirect following limited or disabled
```

**Open Redirect**

```
□ Redirect URLs only from allowlist
□ Relative redirects preferred over absolute
□ Referer header `open redirect` not exploitable
□ OAuth state parameter validated
```

**Prototype Pollution (JavaScript)**

```javascript
// ❌ Vulnerable
function merge(target, source) {
  for (let key in source) {
    target[key] = source[key];
  }
}

// ✅ Safe - check __proto__, constructor, prototype
function safeMerge(target, source) {
  const dangerous = ["__proto__", "constructor", "prototype"];
  for (let key in source) {
    if (!dangerous.includes(key)) {
      target[key] = source[key];
    }
  }
}
```

**ReDoS (Regular Expression DoS)**

```javascript
// ❌ Vulnerable - catastrophic backtracking
 /^(a+)+$/.test('aaaaaaaaaaaaaaaaaaaaa!')

// ✅ Safe - avoid nested quantifiers
/^a+$/.test('aaa')
```

---

## Security Design Principles

1. **Defense in Depth** — multiple independent layers; single point of failure ≠ total compromise
2. **Least Privilege** — grant only required permissions, nothing more
3. **Default Deny** — block by default, explicitly allow
4. **Fail Secure** — deny access on error, don't silently allow
5. **Never Trust Input** — validate all external input regardless of source
6. **Shift Left** — security at design time, not bolted on after

---

## References

- [security-expert-guide.md](../security/security-expert-guide.md) — full expert guide
- [security-fixes.md](../security/security-fixes.md) — common vulnerability fix patterns
- [security-design-patterns.md](../security/security-design-patterns.md) — security pattern catalog (architecture/design/implementation layers: Single Access Point, Check Point, RAII…) + STRIDE→pattern mapping
- [pattern-classification.md](../security/pattern-classification.md) — GoF patterns with security wrappers (Secure Singleton template, Decorator chain)
- [examples.md](../security/examples.md) — complete runnable code examples (Proxy pattern, JWT, parameterized queries)
- [quality/security-checklist.md](../quality/security-checklist.md) — detailed checklist

## Related Commands

- [performance.md](performance.md)
- [quality.md](quality.md)
- [architecture.md](architecture.md)
- [simplification.md](simplification.md)
