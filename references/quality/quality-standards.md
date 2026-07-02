# Code Quality Standards

## 1. Naming Conventions

### Variable Naming

| Type | Style | Example |
|------|------|------|
| Local variables | lowercase_with_underscore | `user_name`, `total_count` |
| Constants | UPPER_SNAKE_CASE | `MAX_RETRIES`, `DEFAULT_TIMEOUT` |
| Instance variables | lowercase_snake or camelCase | `user_id` / `userId` |
| Class variables | lowercase_snake | `_cache`, `instances` |

### Function/Method Naming

- Start with verb: `get_user()`, `create_order()`, `validate_input()`
- Use `is_`, `has_`, `can_` prefixes for booleans: `is_valid()`, `has_permission()`
- Avoid meaningless names: `do_stuff()`, `process_data()`

### Class Naming

- PascalCase: `UserService`, `OrderProcessor`, `PaymentGateway`
- Avoid overusing suffixes: `Manager`, `Handler`, `Utils` (use only when necessary)

### File Naming

| Language | Style | Example |
|------|------|------|
| Python | lowercase_snake | `user_service.py` |
| JavaScript | camelCase or kebab-case | `userService.js` / `user-service.js` |
| Java | PascalCase | `UserService.java` |
| Go | lowercase_snake | `user_service.go` |

## 2. Code Formatting

### Indentation

- **Python**: 4 spaces
- **JavaScript/TypeScript**: 2 spaces
- **Java/Go/Rust**: 4 spaces or 2 spaces (consistent within project)
- **Tab characters are prohibited**

### Line Length

- **Maximum 120 characters**
- Ideally no more than 80 characters

### Spacing

- Spaces around operators: `a + b` not `a+b`
- Space after comma: `func(a, b)` not `func(a,b)`
- No space inside parentheses: `func(a)` not `func( a )`

### Blank Lines

- Between classes: 2 blank lines
- Between methods: 1 blank line
- Between logical sections: 1 blank line

## 3. Comment Standards

### Required Comments

- **Complex algorithms**: Explain the algorithm approach
- **Business rules**: Describe the business context
- **Hack solutions**: Explain why it's done this way
- **Incomplete work**: Use TODO markers

### Comment Styles

```python
# Single line comment (Python)
def calculate_tax(amount):
    # Tax rate is dynamically calculated based on income level
    if amount > 100000:
        return amount * 0.2
    return amount * 0.1
```

```java
// Single line comment (Java)
public class TaxCalculator {
    /**
     * Calculate tax amount
     * @param amount The amount
     * @return Tax amount
     */
    public double calculate(double amount) {
        // Amount over 100K applies 20% tax rate
        if (amount > 100000) {
            return amount * 0.2;
        }
        return amount * 0.1;
    }
}
```

### Prohibited Comments

- Explaining obvious code: `i++ // increment i`
- Outdated comments
- Commented out code (use version control)
- Excessive comments instead of good code

## 4. Function Standards

### Parameter Count

- **Maximum 4 parameters**
- More than 4 should be wrapped in object or use options object

### Return Values

- **Single exit point**: Reduce multiple returns
- **Explicit return type**: Avoid mixed return types
- **Error handling**: Use exceptions or return Result type

### Function Length

| Complexity | Line Range | Description |
|--------|----------|------|
| Simple | 1-10 | Atomic operations |
| Medium | 10-30 | Single responsibility |
| Complex | 30-50 | Needs review |
| Too long | >50 | Needs refactoring |

## 5. Error Handling

### Exception Principles

- **Use specific exceptions**: Avoid catching `Exception`
- **Don't swallow exceptions**: At minimum log them
- **Clean up resources**: Use try-finally or with statement
- **Expose exception interface**: Convert internal exceptions

### Error Examples

```python
# Wrong example
try:
    data = json.loads(body)
except:
    pass  # Silent failure

# Correct example
try:
    data = json.loads(body)
except json.JSONDecodeError as e:
    logger.error(f"JSON parsing failed: {e}")
    raise ValidationError("Invalid JSON format")
```

## 6. Testing Requirements

### Test Coverage

| Component | Minimum Coverage | Recommended Coverage |
|------|------------|------------|
| Core business logic | 80% | 90% |
| New features | 70% | 85% |
| Bug fixes | 100% | 100% |

### Testing Principles

- **Test behavior not implementation**
- **Use descriptive test names**
- **Keep tests fast**
- **Isolate external dependencies**
- **Use Given-When-Then pattern**

### Test Example

```python
def test_user_registration_with_valid_input():
    # Given
    user_data = {"email": "test@example.com", "password": "secure123"}

    # When
    result = UserService.register(user_data)

    # Then
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

### Type Standards

| Type | Description | Example |
|------|------|------|
| feat | New feature | feat(user): add user registration |
| fix | Bug fix | fix(auth): fix login vulnerability |
| docs | Documentation update | docs: update README |
| style | Code formatting | style: format code |
| refactor | Refactoring | refactor(payment): refactor payment logic |
| test | Testing | test: add unit tests |
| chore | Build/tools | chore: update dependencies |

### Commit Example

```
feat(auth): implement two-factor authentication

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
- [ ] Necessary documentation updates
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
4. **Maintainability**: Is future modification convenient?
5. **Testing**: Is there adequate testing?