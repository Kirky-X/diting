# Security Command

Security review mode — OWASP Top 10 (2021) + CWE + modern attack vector detection

## Usage

```bash
review security [target-path]
```

## What to Check

### 1. OWASP Top 10 (2021)

| #   | Category                      | What to look for                                                           |
| --- | ----------------------------- | -------------------------------------------------------------------------- |
| A01 | Broken Access Control         | Missing auth checks, IDOR, path traversal, CORS misconfig                  |
| A02 | Cryptographic Failures        | Weak algos (MD5/SHA1/DES), hardcoded keys, HTTP not HTTPS, unencrypted PII |
| A03 | Injection                     | SQL, NoSQL, LDAP, OS command, SSTI, XPath injection                        |
| A04 | Insecure Design               | Missing threat modeling, security design patterns not applied              |
| A05 | Security Misconfiguration     | Debug mode on, default creds, verbose errors, unnecessary features enabled |
| A06 | Vulnerable Components         | Outdated deps with known CVEs, abandoned libraries                         |
| A07 | Auth & Session Failures       | Weak passwords, no MFA, session fixation, insecure JWT                     |
| A08 | Software & Data Integrity     | Unsigned packages, CI/CD without integrity checks, deserialization         |
| A09 | Logging & Monitoring Failures | No security event logging, logs contain PII/secrets                        |
| A10 | SSRF                          | User-controlled URLs fetched server-side, no URL allowlist                 |

---

### 2. Authentication & Authorization

```
□ No hardcoded credentials (passwords, API keys, tokens in code)
□ Passwords hashed with bcrypt / Argon2 / scrypt (NOT MD5/SHA1/plain SHA256)
□ Session IDs are cryptographically random, regenerated after login
□ Cookies: HttpOnly + Secure + SameSite=Strict/Lax
□ JWT: short expiry, verified signature, not just decoded payload trusted
□ Minimum privilege principle enforced
□ Authorization checked on every protected route (not just at login)
□ IDOR prevention: user can only access their own resources
□ Account lockout / rate limiting on login endpoints
```

### 3. Input Validation & Output Encoding

```
□ All user input validated (type, length, format, range)
□ Whitelist validation preferred over blacklist
□ SQL: parameterized queries / prepared statements / ORM — no string concat
□ NoSQL: typed queries, no $where with user data
□ XSS: output HTML-encoded, textContent not innerHTML, CSP header set
□ CSRF: tokens on state-changing forms, SameSite cookie attribute
□ File uploads: MIME type + extension validation, random filename, non-executable directory
□ Path traversal: Path.resolve() / os.path.realpath() to canonicalize, check prefix
□ Command injection: no shell=True with user input, use arrays
□ SSTI: no user input rendered in template engines (Jinja2, Handlebars, etc.)
```

### 4. Cryptography

```
□ Symmetric: AES-256-GCM or ChaCha20-Poly1305 (NOT AES-ECB, 3DES, RC4)
□ Asymmetric: RSA-2048+ with OAEP, or EC P-256+ (NOT RSA-512/1024)
□ Hashing: SHA-256+ for integrity; bcrypt/Argon2 for passwords (NOT MD5/SHA1)
□ Random: CSPRNG used (NOT Math.random(), random.random())
□ Keys: not hardcoded, loaded from env/KMS, rotated
□ TLS: 1.2+ enforced, certificate validated
□ Secrets: not in source code, logs, URLs, or error messages
```

### 5. Error Handling & Logging

```
□ No stack traces exposed to client
□ Generic error messages to users; detailed to logs only
□ Security events logged: login success/failure, permission denied, config changes
□ Logs do NOT contain: passwords, tokens, full card numbers, SSN
□ Exceptions not silently swallowed
```

### 6. Dependency Security

```
□ No packages with known critical/high CVEs (check npm audit / safety / cargo audit)
□ No abandoned packages (last commit > 2 years, no maintainer)
□ Dependency pinning or lock files committed
□ Supply chain: packages from official registries, not arbitrary URLs
```

### 7. Modern & Language-Specific Concerns

**Python**

- `pickle.loads()` with untrusted data → Deserialization RCE
- `eval()` / `exec()` with user input → Code injection
- `subprocess(shell=True, ...)` → Command injection
- `yaml.load()` → Use `yaml.safe_load()`
- `marshal.load()` with untrusted data → Deserialization RCE
- `shlex.quote()` for safe shell argument escaping

**JavaScript / TypeScript**

- `innerHTML` / `dangerouslySetInnerHTML` with user data → XSS
- `eval()` / `new Function()` with user data → Code injection
- `prototype` pollution in object merge utilities (`Object.assign`, spread with user input)
- Regex with catastrophic backtracking (ReDoS)
- `JSON.parse()` on untrusted input → Handle exceptions, validate structure

**Java**

- `ObjectInputStream` on untrusted data → Deserialization RCE
- SpEL / OGNL expression injection
- XXE: disable DOCTYPE in XML parsers
- JNDI lookup with user input → Log4Shell-style RCE
- `ScriptEngine.eval()` with user input → Code injection
- `XMLDecoder` on untrusted data → Deserialization RCE

**Go**

- `os/exec` with user-controlled args → Command injection
- `text/template` vs `html/template` (latter escapes, former doesn't)
- Integer overflow in calculations used for buffer sizes
- `filepath.Join` with user input → Path traversal (use `filepath.Clean`)

**Rust**

- `unsafe` blocks without clear safety invariants
- Unvalidated `FromStr` implementations
- Transmute operations with mismatched sizes

**PHP**

- `unserialize()` with user input → Object injection
- `include` / `require` with user input → LFI/RFI
- `preg_replace` with /e modifier → Code execution (deprecated but check legacy code)

### 8. Modern Attack Vectors

**SSRF (Server-Side Request Forgery)**

```
□ URL inputs validated against allowlist
□ Internal IP ranges blocked (10.x, 172.16-31.x, 192.168.x, 169.254.x, 127.x)
□ Cloud metadata endpoints blocked (169.254.169.254)
□ DNS rebinding mitigations in place
□ Redirect following limited or disabled
```

**Open Redirect**

```
□ Redirect URLs from allowlist only
□ Relative redirects preferred over absolute
□ `open redirect` via Referer header not possible
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

// ✅ Safe - check for __proto__, constructor, prototype
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

1. **Defense in Depth** — Multiple independent layers; single failure ≠ compromise
2. **Least Privilege** — Grant only what's needed, nothing more
3. **Default Deny** — Block by default, explicitly allow
4. **Fail Secure** — On error, deny access, don't silently allow
5. **Never Trust Input** — Validate ALL external input regardless of source
6. **Shift Left** — Security in design, not bolted on after

---

## References

- [security-expert-guide.md](../security/security-expert-guide.md) — Full expert guide
- [security-fixes.md](../security/security-fixes.md) — Fix patterns for common vulns
- [security-design-patterns.md](../security/security-design-patterns.md) — Security pattern catalog (architecture/design/implementation tiers: Single Access Point, Check Point, RAII…) + STRIDE→pattern map
- [pattern-classification.md](../security/pattern-classification.md) — GoF patterns with security wrappers (Secure Singleton template, Decorator chain)
- [examples.md](../security/examples.md) — Full working code examples (Proxy pattern, JWT, parameterized queries)
- [quality/security-checklist.md](../quality/security-checklist.md) — Detailed checklist

## Related Commands

- [performance.md](performance.md)
- [quality.md](quality.md)
- [architecture.md](architecture.md)
- [simplification.md](simplification.md)
