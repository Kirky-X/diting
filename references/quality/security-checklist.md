# Security Review Checklist

## 1. Authentication & Authorization

### Authentication Security

- [ ] Password storage uses strong hashing algorithms (bcrypt, Argon2)
- [ ] No hardcoded credentials
- [ ] Password strength validation implemented
- [ ] Multi-factor authentication supported
- [ ] Session management uses secure cookies (HttpOnly, Secure, SameSite)
- [ ] Reasonable session timeout implemented

### Authorization Checks

- [ ] Principle of least privilege implemented
- [ ] User access to resources verified
- [ ] Horizontal privilege escalation prevented
- [ ] Vertical privilege escalation prevented
- [ ] API endpoints have proper authorization checks

## 2. Input Validation

### Parameter Validation

- [ ] All user input is validated
- [ ] Input length limits checked
- [ ] Input types validated
- [ ] Whitelist validation preferred over blacklist
- [ ] Integer overflow prevented
- [ ] File upload type and size validated

### SQL Injection Prevention

- [ ] Parameterized queries used
- [ ] Dynamic SQL string concatenation avoided
- [ ] ORM or query builder used
- [ ] Stored procedures use parameters

### NoSQL Injection Prevention

- [ ] Query parameter types validated
- [ ] $where operator avoided
- [ ] MongoDB parameterized queries used

## 3. Output Encoding

### XSS Prevention

- [ ] HTML encoding used in HTML context
- [ ] JavaScript encoding used in JavaScript context
- [ ] URL encoding used for URL parameters
- [ ] CSS encoding used in CSS context
- [ ] Content Security Policy (CSP) used

### Sensitive Data Protection

- [ ] Sensitive data not logged
- [ ] Error messages don't expose sensitive data
- [ ] API responses don't contain sensitive fields
- [ ] Static financial data encrypted
- [ ] PII data masked

## 4. Cryptographic Handling

### Algorithm Selection

- [ ] Strong encryption algorithms used (AES-256, RSA-2048+)
- [ ] Known insecure algorithms avoided (MD5, SHA1, DES)
- [ ] Secure random number generator used
- [ ] Cryptographic modes properly implemented (CBC, GCM)

### Key Management

- [ ] Keys not hardcoded
- [ ] Keys obtained through secure channels
- [ ] Key rotation strategy implemented
- [ ] Development and production keys separated
- [ ] Key management service used (KMS, Vault)

### Transport Security

- [ ] HTTPS used (TLS 1.2+)
- [ ] Certificates properly configured
- [ ] Downgrade attacks prevented
- [ ] HSTS header configured

## 5. Error Handling

### Error Messages

- [ ] Stack traces not exposed
- [ ] Detailed error information logged
- [ ] Generic error messages provided to users
- [ ] Different error types distinguished

### Exception Handling

- [ ] Specific exceptions caught
- [ ] Resources cleaned up on failure
- [ ] Critical exceptions not swallowed
- [ ] Retry mechanism implemented (exponential backoff)

## 6. File Security

### File Upload

- [ ] File type validated (MIME and extension)
- [ ] File size limited
- [ ] Uploaded files renamed
- [ ] Files stored in non-executable directory
- [ ] Malware scanned

### File Access

- [ ] Path traversal prevented
- [ ] File paths verified to be within allowed scope
- [ ] File permissions restricted
- [ ] User-uploaded files not executed

## 7. Business Logic

### Business Security

- [ ] Amount overflow prevented
- [ ] Order state machine correctly implemented
- [ ] Duplicate submissions prevented
- [ ] Idempotency implemented
- [ ] CAPTCHA protection

### Race Conditions

- [ ] Transactions used
- [ ] Optimistic/pessimistic locking implemented
- [ ] TOCTOU vulnerabilities prevented
- [ ] Balance operations made atomic

## 8. API Security

### REST API

- [ ] Appropriate HTTP methods used
- [ ] Rate limiting implemented
- [ ] CORS properly configured
- [ ] API versioning managed
- [ ] Request signature verification

### Authentication Methods

- [ ] JWT properly configured (short expiry)
- [ ] OAuth 2.0 correctly implemented
- [ ] API Key rotation
- [ ] Refresh token securely stored

## 9. Infrastructure

### Configuration Security

- [ ] Production configuration secured
- [ ] Debug mode disabled
- [ ] Secure default configurations
- [ ] Configuration encrypted at rest

### Dependency Security

- [ ] Dependencies regularly updated
- [ ] Dependency scanning tools used
- [ ] Known vulnerabilities patched
- [ ] Dependency count minimized

## 10. Logging & Monitoring

### Logging

- [ ] Authentication attempts logged
- [ ] Sensitive operations logged
- [ ] Errors and exceptions logged
- [ ] Secure log storage
- [ ] Log data masking implemented

### Monitoring & Alerting

- [ ] Anomaly detection
- [ ] Failed login alerts
- [ ] Performance anomaly alerts
- [ ] Security event alerts

---

## Code Examples: Common Issues Comparison

### SQL Injection

```python
# Dangerous - string concatenation
query = "SELECT * FROM users WHERE name = '" + username + "'"
cursor.execute(query)

# Safe - parameterized query
cursor.execute("SELECT * FROM users WHERE name = %s", (username,))
```

### Hardcoded Credentials

```python
# Dangerous
API_KEY = "sk-prod-abc123xyz"

# Safe
import os
API_KEY = os.environ["API_KEY"]   # Or read from KMS/Vault
```

### Password Hashing

```python
# Dangerous
import hashlib
stored = hashlib.md5(password.encode()).hexdigest()

# Safe
import bcrypt
stored = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
```

### XSS Prevention

```javascript
// Dangerous
element.innerHTML = userInput;

// Safe
element.textContent = userInput;
// Or use DOMPurify
element.innerHTML = DOMPurify.sanitize(userInput);
```

### IDOR Prevention

```python
# Dangerous - no ownership verification
def get_order(order_id):
    return Order.objects.get(id=order_id)

# Safe - verify current user owns the resource
def get_order(order_id, current_user):
    order = Order.objects.get(id=order_id)
    if order.user_id != current_user.id:
        raise PermissionDenied("Access denied")
    return order
```

### Cookie Security Configuration

```python
# Dangerous
response.set_cookie("session", token)

# Safe
response.set_cookie(
    "session", token,
    httponly=True,       # XSS protection
    secure=True,         # HTTPS only
    samesite="Strict",   # CSRF protection
    max_age=3600,
)
```
