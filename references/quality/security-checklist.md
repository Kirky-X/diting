# Security Review Checklist

## 1. Authentication and Authorization

### Authentication Security

- [ ] Password storage uses strong hashing algorithms (bcrypt, Argon2)
- [ ] Avoid hardcoded credentials
- [ ] Implement password strength validation
- [ ] Support multi-factor authentication
- [ ] Session management uses secure cookies (HttpOnly, Secure, SameSite)
- [ ] Implement reasonable session timeout

### Authorization Checks

- [ ] Implement least privilege principle
- [ ] Verify user access permissions to resources
- [ ] Prevent horizontal privilege escalation
- [ ] Prevent vertical privilege escalation
- [ ] API endpoints have appropriate authorization checks

## 2. Input Validation

### Parameter Validation

- [ ] Validate all user input
- [ ] Check input length limits
- [ ] Validate input types
- [ ] Whitelist validation preferred over blacklist
- [ ] Prevent integer overflow
- [ ] Validate file upload types and sizes

### SQL Injection Protection

- [ ] Use parameterized queries
- [ ] Avoid dynamic SQL concatenation
- [ ] Use ORM or query builders
- [ ] Stored procedures use parameters

### NoSQL Injection Protection

- [ ] Validate query parameter types
- [ ] Avoid using $where operator
- [ ] Use MongoDB parameterized queries

## 3. Output Encoding

### XSS Protection

- [ ] Use HTML encoding in HTML context
- [ ] Use JavaScript encoding in JavaScript context
- [ ] Use URL encoding for URL parameters
- [ ] Use CSS encoding in CSS context
- [ ] Use Content Security Policy

### Sensitive Data Protection

- [ ] Don't log sensitive data
- [ ] Error messages don't expose sensitive data
- [ ] API responses don't contain sensitive fields
- [ ] Financial data encrypted at rest
- [ ] PII data masked

## 4. Encryption Processing

### Algorithm Selection

- [ ] Use strong encryption algorithms (AES-256, RSA-2048+)
- [ ] Avoid known insecure algorithms (MD5, SHA1, DES)
- [ ] Use secure random number generators
- [ ] Correctly implement encryption modes (CBC, GCM)

### Key Management

- [ ] Don't hardcode keys
- [ ] Obtain keys through secure channels
- [ ] Implement key rotation strategy
- [ ] Separate development and production keys
- [ ] Use key management services (KMS, Vault)

### Transmission Security

- [ ] Use HTTPS (TLS 1.2+)
- [ ] Certificates properly configured
- [ ] Prevent downgrade attacks
- [ ] HSTS header configured

## 5. Error Handling

### Error Messages

- [ ] Don't expose stack traces
- [ ] Log detailed error information
- [ ] Generic error messages to users
- [ ] Distinguish between different error types

### Exception Handling

- [ ] Catch specific exceptions
- [ ] Clean up resources on failure
- [ ] Don't swallow critical exceptions
- [ ] Implement retry mechanism (exponential backoff)

## 6. File Security

### File Upload

- [ ] Validate file types (MIME and extension)
- [ ] Limit file size
- [ ] Rename uploaded files
- [ ] Store in non-executable directories
- [ ] Scan for malware

### File Access

- [ ] Prevent path traversal
- [ ] Verify file paths within allowed range
- [ ] Restrict file permissions
- [ ] Don't execute user-uploaded files

## 7. Business Logic

### Business Security

- [ ] Prevent amount overflow
- [ ] Order state machine correctly implemented
- [ ] Prevent duplicate submission
- [ ] Implement idempotency
- [ ] Captcha protection

### Race Conditions

- [ ] Use transactions
- [ ] Implement optimistic/pessimistic locking
- [ ] Prevent TOCTOU vulnerabilities
- [ ] Atomic balance operations

## 8. API Security

### REST API

- [ ] Use appropriate HTTP methods
- [ ] Implement rate limiting
- [ ] CORS properly configured
- [ ] API versioning
- [ ] Request signature verification

### Authentication Methods

- [ ] JWT security configuration (short expiry)
- [ ] OAuth 2.0 correctly implemented
- [ ] API Key rotation
- [ ] Refresh tokens securely stored

## 9. Infrastructure

### Configuration Security

- [ ] Production configuration secure
- [ ] Disable debug mode
- [ ] Secure default configuration
- [ ] Encrypted configuration storage

### Dependency Security

- [ ] Regularly update dependencies
- [ ] Use dependency scanning tools
- [ ] Known vulnerabilities fixed
- [ ] Minimize dependency count

## 10. Logging and Monitoring

### Logging

- [ ] Log authentication attempts
- [ ] Log sensitive operations
- [ ] Log errors and exceptions
- [ ] Secure log storage
- [ ] Implement log masking

### Monitoring and Alerting

- [ ] Anomaly detection
- [ ] Login failure alerts
- [ ] Performance anomaly alerts
- [ ] Security event alerts

---

## Code Examples: Common Problem Comparisons

### SQL Injection

```python
# DANGEROUS - String concatenation
query = "SELECT * FROM users WHERE name = '" + username + "'"
cursor.execute(query)

# SAFE - Parameterized query
cursor.execute("SELECT * FROM users WHERE name = %s", (username,))
```

### Hardcoded Credentials

```python
# DANGEROUS
API_KEY = "sk-prod-abc123xyz"

# SAFE
import os
API_KEY = os.environ["API_KEY"]   # Or read from KMS/Vault
```

### Password Hashing

```python
# DANGEROUS
import hashlib
stored = hashlib.md5(password.encode()).hexdigest()

# SAFE
import bcrypt
stored = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
```

### XSS Protection

```javascript
// DANGEROUS
element.innerHTML = userInput;

// SAFE
element.textContent = userInput;
// Or use DOMPurify
element.innerHTML = DOMPurify.sanitize(userInput);
```

### IDOR Protection

```python
# DANGEROUS - No ownership verification
def get_order(order_id):
    return Order.objects.get(id=order_id)

# SAFE - Verify current user owns the resource
def get_order(order_id, current_user):
    order = Order.objects.get(id=order_id)
    if order.user_id != current_user.id:
        raise PermissionDenied("Access denied")
    return order
```

### Cookie Security Configuration

```python
# DANGEROUS
response.set_cookie("session", token)

# SAFE
response.set_cookie(
    "session", token,
    httponly=True,       # XSS protection
    secure=True,         # HTTPS only
    samesite="Strict",   # CSRF protection
    max_age=3600,
)
```