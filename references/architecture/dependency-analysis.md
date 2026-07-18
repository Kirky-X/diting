# Dependency Analysis Guide

## Dependency Types

### Direct Dependencies

Declared in project configuration: `package.json` (`{"express": "^4.18.0"}`), `requirements.txt` (`flask==2.0.0`), `Cargo.toml`, etc.

### Transitive Dependencies

Dependencies introduced by direct dependencies:

```mermaid
flowchart TD
    Project["Project"]
    Project --> Express["express (direct)"]
    Project --> Lodash["lodash (direct)"]
    Express --> BP["body-parser (transitive)"]
    Express --> CP["cookie-parser (transitive)"]
    Express --> DBG["debug (transitive)"]
```

### Dev Dependencies

Dependencies only needed during development:

```json
{
  "devDependencies": {
    "jest": "^29.0.0",
    "eslint": "^8.0.0"
  }
}
```

## Dependency Metrics

### Coupling Analysis

| Metric | Formula | Target |
|--------|---------|--------|
| Afferent Coupling (Ca) | Incoming dependencies | The lower the better |
| Efferent Coupling (Ce) | Outgoing dependencies | The lower the better |
| Instability (I) | Ce / (Ca + Ce) | 0.0 - 1.0 |
| Abstractness (A) | Abstract classes / Total | Balanced with I |

### Dependency Distance

```
Direct dependency: distance = 1
Transitive (1 level): distance = 2
Transitive (2 levels): distance = 3
```

**Risk**: Greater distance = lower visibility = higher risk

## Dependency Problems

### 1. Circular Dependencies

**Detection**
```mermaid
flowchart LR
    A["Module A"] --> B["Module B"]
    B --> C["Module C"]
    C --> A
```

**Problems**
- Unclear ownership
- Initialization issues
- Testing difficulties
- Deployment complexity

**Solutions**
- **Dependency Injection**: Pass instances as parameters instead of importing
- **Extract Shared Dependencies**: Move common logic to a third module
- **Invert Dependencies**: Define interfaces in lower-level modules

```python
# Before: A imports B, B imports A (circular)
# After: A receives B via DI — no import cycle
class A:
    def use_b(self, b_instance):  # Inject, not import
        return b_instance
```

### 2. Dependency Hell

**Symptoms**
- Version requirement conflicts
- Diamond dependency problem
- Version locking

**Diamond Problem Example**
```mermaid
flowchart TD
    Project["Project"]
    Project --> LibA["Lib A (needs X v1.0)"]
    Project --> LibB["Lib B (needs X v2.0)"]
    LibA --> X["X (incompatible versions)"]
    LibB --> X
```

**Solutions**
- Use dependency resolution tools
- Lock files (package-lock.json, Pipfile.lock)
- Carefully manage version ranges

### 3. Dependency Bloat

**Detection**
```
[ ] Unused dependencies in the project
[ ] Production includes dev dependencies
[ ] Feature duplication across dependencies
[ ] Dependencies are too large
```

**Analysis Commands**
```bash
# npm
npm ls --depth=0
npm prune

# pip
pip list --outdated
pip-autoremove

# cargo
cargo tree
cargo tree --duplicates
```

### 4. Outdated Dependencies

**Security Risks**
- Known vulnerabilities in older versions
- Missing security patches
- Deprecated dependencies

**Analysis**
```bash
# npm audit
npm audit
npm audit fix

# pip security check
safety check
pip-audit

# cargo audit
cargo audit
```

## Dependency Health Metrics

### Version Health

| Status | Description | Action |
|--------|-------------|--------|
| Current | Latest version | None |
| Outdated | Behind latest | Plan update |
| Deprecated | No longer maintained | Migrate |
| Vulnerable | Security issues | Update immediately |

### Dependency Freshness

```
Freshness score = (number of up-to-date dependencies) / (total dependencies) * 100

Target: > 80%
```

### License Compliance

**License Categories**
| Category | Risk Level | Examples |
|----------|------------|----------|
| Permissive | Low | MIT, Apache 2.0, BSD |
| Weak Copyleft | Medium | LGPL, MPL |
| Strong Copyleft | High | GPL, AGPL |
| Proprietary | Variable | Custom licenses |

**Compliance Check**
```
[ ] All licenses identified
[ ] License compatibility verified
[ ] Attribution requirements met
[ ] No prohibited licenses
```

## Dependency Visualization

### Dependency Graph

```mermaid
flowchart TD
    App["Application"]
    App --> Express["Express"]
    App --> Lodash["Lodash"]
    App --> Axios["Axios"]
    Express --> Body["Body Parser"]
    Express --> Cookie["Cookie Parser"]
    Axios --> Follow["Follow Redir"]
    Axios --> IsStream["Is-Stream"]
```

### Dependency Matrix

| From \ To | App | Auth | DB | API | Utils |
|-----------|-----|------|----|-----|-------|
| App       | -   | 1    | 1  | 1   | 1     |
| Auth      | 0   | -    | 1  | 0   | 1     |
| DB        | 0   | 0    | -  | 0   | 1     |
| API       | 0   | 1    | 1  | -   | 1     |
| Utils     | 0   | 0    | 0  | 0   | -     |

## Dependency Management Best Practices

### 1. Version Pinning

- **Exact** (`4.18.2`): Pin critical dependencies to known-good versions
- **Patch** (`~4.17.21`): Only allow patch updates
- **Minor** (`^1.4.0`): Allow minor updates within the same major version
- **Lock files** (`package-lock.json`, `Pipfile.lock`, `Cargo.lock`): Commit to VCS, update intentionally

### 2. Dependency Grouping

Group by purpose: `dependencies/{web,database,auth,utils}` (core) vs `dev-dependencies/{testing,linting,building}` (dev only). Scope dependency change impact to one concern.

### 3. Regular Maintenance

**Schedule**
| Task | Frequency |
|------|-----------|
| Security audit | Weekly |
| Update check | Monthly |
| Major version review | Quarterly |
| Dependency cleanup | Quarterly |

### 4. Dependency Decision

**Before Adding a Dependency**
```
[ ] Is it actively maintained?
[ ] Is the documentation good?
[ ] Is the package size acceptable?
[ ] Are there security issues?
[ ] Is the license compatible?
[ ] Can it be simply implemented internally?
```

## Dependency Analysis Tools

| Ecosystem | Tree / Dedup | Security | License | Outdated |
|-----------|-------------------|----------|---------|----------|
| JS/TS | `npx depcheck`, `npx bundle-analyzer` | `npm audit` | `npx license-checker` | `npm outdated` |
| Python | `pipdeptree` | `safety check`, `pip-audit` | `pip-licenses` | `pip list --outdated` |
| Rust | `cargo tree`, `cargo tree --duplicates` | `cargo audit` | (cargo metadata) | `cargo outdated` |

## Dependency Review Checklist

### Security
- [ ] No known vulnerabilities
- [ ] Security audit passed
- [ ] Dependencies from trusted sources
- [ ] No unnecessary dependencies

### Maintenance
- [ ] Dependencies actively maintained
- [ ] Compatible with project versions
- [ ] Clear update path
- [ ] Deprecated dependencies have migration plan

### Performance
- [ ] Package size acceptable
- [ ] No duplicate dependencies
- [ ] Supports tree-shaking
- [ ] Can be lazy-loaded

### Legal
- [ ] All licenses identified
- [ ] License compatibility verified
- [ ] Attribution requirements met
- [ ] No prohibited licenses

### Architecture
- [ ] No circular dependencies
- [ ] Clear dependency direction
- [ ] Appropriate abstraction level
- [ ] Testability not compromised
