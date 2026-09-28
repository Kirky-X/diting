# Architecture Review Command

Architecture Review Mode — system design, pattern application, coupling, microservices compliance

## Usage

```bash
review architecture [target-path]
```

## Checklist

### Module Structure and Boundaries

```
□ Clear separation of responsibilities (presentation / business logic / data / infrastructure)
□ Module boundaries match domain boundaries (DDD alignment)
□ No circular dependencies between modules
□ Public API surface is intentional and minimal
□ Internal implementation details do not leak to callers
□ Dependency direction: high-level → low-level (no reversal)
```

### Coupling and Cohesion

| Metric                           | Target          | Description                                  |
| -------------------------------- | --------------- | -------------------------------------------- |
| Afferent Coupling (Ca)           | Lower is better | How many modules depend on this module       |
| Efferent Coupling (Ce)           | Lower is better | How many modules this module depends on      |
| Instability (I = Ce / (Ca + Ce)) | 0.0–1.0         | 0 = stable, 1 = unstable                    |
| Cohesion                         | High            | Group related things, separate unrelated things |

**Red Flags:**

- God Object: a class/module referenced everywhere
- Shotgun Surgery: a single change requires touching 10+ files
- Parallel class hierarchies always growing in sync

**Boundary Contracts**: beyond structural metrics, audit every component handoff (parser → policy, service boundary, inter-process) — compare what upstream actually guarantees (normalization form, units, truncation, type coercion, encoding, tenant scope) with the stronger form downstream assumes, and compare same-kind controls for equivalence, not presence. See [correctness.md](correctness.md) — Cross-Component Handoffs.

### Design Pattern Application

| Scenario                    | Recommended Pattern                 |
| --------------------------- | ----------------------------------- |
| Complex or conditional object creation | Factory / Builder            |
| Need a single shared instance  | Singleton (prefer DI container)    |
| Add behavior without modifying a class | Decorator                    |
| Control access / add security layer | Proxy                         |
| Decouple event sender from handler | Observer / Event Bus          |
| Multiple interchangeable algorithms | Strategy                     |
| Multi-step validation/processing chain | Chain of Responsibility    |
| Simplify complex subsystem    | Facade                             |
| Distributed transactions      | Saga                               |

**Priority Signal**: a missing pattern is itself a finding — more than 3 types of `if/elif` chains, ≥ 3× duplicated algorithms, or a class with > 6 unrelated responsibilities each defaults to **High** severity. See [design-pattern-review.md](../architecture/design-pattern-review.md) for full thresholds and code-smell→pattern reverse lookup.

### Anti-patterns to Detect

```
□ God Object — a class responsible for everything
□ Anemic Domain Model — domain objects are just getter/setter collections
□ Distributed Monolith — microservices but tightly coupled via synchronous calls
□ Hardcoded Dependencies — `new ServiceImpl()` instead of interface injection
□ Spaghetti Dependencies — no clear layering, any module calls any module
□ Premature Microservices — microservice overhead without benefits
```

### Microservices (if applicable)

```
□ Each service owns one business capability
□ One database per service (no shared databases between services)
□ Communication: prefer asynchronous (events) over synchronous for non-critical paths
□ Circuit breakers configured for all inter-service calls
□ Services independently deployable without coordinated releases
□ Health endpoints exposed (/health or /readyz)
□ Observability: structured logging, distributed tracing, metrics
□ API Gateway handles cross-cutting concerns: authentication, rate limiting, routing
```

### Dependency Management

```
□ No circular imports/circular dependencies
□ External dependencies abstracted as interfaces (easily replaceable)
□ Third-party libraries not directly used in codebase (adapter/wrapper)
□ Dependency versions locked; lock files committed
□ No deprecated or vulnerable dependencies
```

### Scalability and Reliability

```
□ Stateless services (session state in shared storage, not in memory)
□ Idempotent operations (safe to retry)
□ Graceful degradation (partial failure ≠ total failure)
□ Retry with exponential backoff for transient failures
□ Timeouts configured for all external calls
□ Resource pooling (DB connections, HTTP clients)
```

---

## Architecture Decision Quick Guide

### When to Use Which Pattern

```
Simple applications (1-3 developers):
  → Layered architecture (presentation / business / data layer)

Growing codebase (multiple teams, clear domain boundaries):
  → Modular monolith + DDD aggregates

High scale, independent scaling needs, large organizations:
  → Microservices (only when the team can support the operational overhead)

Complex business logic, multiple state transitions:
  → Domain-Driven Design (aggregates, value objects, domain events)

Large read/write ratio difference:
  → CQRS + read models
```

---

## References

- [architect-guide.md](../architecture/architect-guide.md) — full architect reference
- [system-architecture.md](../architecture/system-architecture.md) — architecture quality attributes
- [design-pattern-review.md](../architecture/design-pattern-review.md) — GoF pattern review
- [microservices-compliance.md](../architecture/microservices-compliance.md) — microservices checklist
- [dependency-analysis.md](../architecture/dependency-analysis.md) — dependency analysis guide

## Related Commands

- [security.md](security.md)
- [performance.md](performance.md)
- [quality.md](quality.md)
- [simplification.md](simplification.md)
