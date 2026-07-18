# Code Quality Standards

## 1. Naming Conventions

### Variable Naming

| Type | Style | Example |
|------|-------|---------|
| Local variables | lowercase with underscores | `user_name`, `total_count` |
| Constants | UPPER_SNAKE_CASE | `MAX_RETRIES`, `DEFAULT_TIMEOUT` |
| Instance variables | lowercase_underscore or camelCase | `user_id` / `userId` |
| Class variables | lowercase_underscore | `_cache`, `instances` |

### Function/Method Naming

- Start with verbs: `get_user()`, `create_order()`, `validate_input()`
- Use `is_`, `has_`, `can_` prefixes for booleans: `is_valid()`, `has_permission()`
- Avoid meaningless names: `do_stuff()`, `process_data()`

### Class Naming

- PascalCase: `UserService`, `OrderProcessor`, `PaymentGateway`
- Avoid overusing suffixes: `Manager`, `Handler`, `Utils` (only when necessary)

### File Naming

| Language | Style | Example |
|----------|-------|---------|
| Python | lowercase_underscore | `user_service.py` |
| JavaScript | camelCase or kebab-case | `userService.js` / `user-service.js` |
| Java | PascalCase | `UserService.java` |
| Go | lowercase_underscore | `user_service.go` |

## 2. Code Formatting

### Indentation

- **Python**: 4 spaces
- **JavaScript/TypeScript**: 2 spaces
- **Java/Go/Rust**: 4 spaces or 2 spaces (consistent within the project)
- **Tab characters are prohibited**

### Line Length

- **Maximum 120 characters**
- Ideally no more than 80 characters

### Spacing

- Spaces around operators: `a + b` not `a+b`
- Spaces after commas: `func(a, b)` not `func(a,b)`
- No spaces inside parentheses: `func(a)` not `func( a )`

### Blank Lines

- Between classes: 2 blank lines
- Between methods: 1 blank line
- Between logical sections: 1 blank line

## 3. Comment Standards

### Required Comments

- **Complex algorithms**: Explain the algorithmic approach
- **Business rules**: Describe business context
- **Workarounds**: Explain why this approach is used
- **Incomplete work**: Mark with TODO

### Comment Style

```python
# Single-line comment (Python)
def calculate_tax(amount):
    # Tax rate is dynamically calculated based on income level
    if amount > 100000:
        return amount * 0.2
    return amount * 0.1
```

```java
// Single-line comment (Java)
public class TaxCalculator {
    /**
     * Calculate tax amount
     * @param amount The amount
     * @return The tax amount
     */
    public double calculate(double amount) {
        // Amounts over 100,000 are subject to 20% tax rate
        if (amount > 100000) {
            return amount * 0.2;
        }
        return amount * 0.1;
    }
}
```

### Prohibited Comments

- Explaining obvious code: `i++ // increment i`
- Stale comments
- Commented-out code (use version control)
- Using comments as a substitute for good code

## 4. Function Standards

### Parameter Count

- **Maximum 4 parameters**
- More than 4 should be wrapped in an object or use an options object

### Return Values

- **Single exit point**: Reduce multiple returns
- **Explicit return types**: Avoid mixed return types
- **Error handling**: Use exceptions or return Result type

### Function Length

| Complexity | Lines | Description |
|------------|-------|-------------|
| Simple | 1-10 | Atomic operations |
| Medium | 10-30 | Single responsibility |
| Complex | 30-50 | Needs review |
| Too long | >50 | Needs refactoring |

## 5. Error Handling

### Exception Principles

- **Use specific exceptions**: Avoid catching `Exception`
- **Don't swallow exceptions**: At minimum, log them
- **Clean up resources**: Use try-finally or with statements
- **Expose exception interface**: Convert internal exceptions

### Error Examples

```python
# Bad example
try:
    data = json.loads(body)
except:
    pass  # Silent failure

# Good example
try:
    data = json.loads(body)
except json.JSONDecodeError as e:
    logger.error(f"JSON parse failed: {e}")
    raise ValidationError("Invalid JSON format")
```

## 6. Testing Requirements

### Test Coverage

| Component | Minimum Coverage | Recommended Coverage |
|-----------|-----------------|---------------------|
| Core business logic | 80% | 90% |
| New features | 70% | 85% |
| Bug fixes | 100% | 100% |

### Testing Principles

- **Test behavior, not implementation**
- **Use descriptive test names**
- **Keep tests fast**
- **Isolate external dependencies**
- **Use Given-When-Then pattern**

### Test Example

```python
def test_user_registration_with_valid_input():
    # Given (preconditions)
    user_data = {"email": "test@example.com", "password": "secure123"}

    # When (execute action)
    result = UserService.register(user_data)

    # Then (verify result)
    assert result.status == "success"
    assert result.user.email == "test@example.com"
    assert mock_email.called
```

## 7. Git Commit Standards

### Commit Message Format

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

### Type Definitions

| Type | Description | Example |
|------|-------------|---------|
| feat | New feature | feat(user): Add user registration |
| fix | Bug fix | fix(auth): Fix login vulnerability |
| docs | Documentation update | docs: Update README |
| style | Code formatting | style: Format code |
| refactor | Refactoring | refactor(payment): Refactor payment logic |
| test | Tests | test: Add unit tests |
| chore | Build/tooling | chore: Update dependencies |

### Commit Example

```
feat(auth): Implement two-factor authentication

- Add TOTP verification
- Generate recovery codes
- Update user settings page

Closes #123
```

## 8. Code Review Standards

### Must Pass

- [ ] All tests pass
- [ ] No critical security issues
- [ ] Code style follows conventions
- [ ] Required documentation updates
- [ ] Does not break existing functionality

### Should Include

- [ ] Meaningful tests
- [ ] No significant performance regression
- [ ] Edge cases considered
- [ ] Complete error handling

### Review Focus

1. **Correctness**: Does the code correctly solve the problem?
2. **Security**: Are there security risks?
3. **Readability**: Is the code easy to understand?
4. **Maintainability**: Is future modification easy?
5. **Testing**: Is there adequate test coverage?
