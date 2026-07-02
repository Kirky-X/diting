# Architecture Command

Architecture review mode — system design, pattern application, coupling, microservices compliance

## Usage

```bash
review architecture [target-path]
```

## What to Check

### Module Structure & Boundaries

```
□ Clear separation of concerns (presentation / business logic / data / infrastructure)
□ Module boundaries match domain boundaries (DDD alignment)
□ No circular dependencies between modules
□ Public API surface is intentional and minimal
□ Internal implementation details not leaked to callers
□ Dependency direction: high-level → low-level (not reversed)
```

### Coupling & Cohesion

| Metric                           | Target          | Description                                 |
| -------------------------------- | --------------- | ------------------------------------------- |
| Afferent Coupling (Ca)           | Lower is better | How many modules depend on this one         |
| Efferent Coupling (Ce)           | Lower is better | How many modules this one depends on        |
| Instability (I = Ce / (Ca + Ce)) | 0.0–1.0         | 0 = stable, 1 = unstable                    |
| Cohesion                         | High            | Related things grouped, unrelated separated |

**Red flags:**

- God object: one class / module referenced everywhere
- Shotgun surgery: one change requires touching 10+ files
- Parallel class hierarchies that always grow together

### Design Pattern Application

| Scenario                                  | Recommended Pattern             |
| ----------------------------------------- | ------------------------------- |
| Object creation is complex or conditional | Factory / Builder               |
| Need single shared instance               | Singleton (prefer DI container) |
| Add behavior without modifying class      | Decorator                       |
| Control access / add security layer       | Proxy                           |
| Decouple event emitter from handlers      | Observer / Event Bus            |
| Multiple interchangeable algorithms       | Strategy                        |
| Multi-step validation / processing chain  | Chain of Responsibility         |
| Simplify complex subsystem                | Facade                          |
| Distributed transactions                  | Saga                            |

**Priority signal**: a missing pattern is itself a finding — `if/elif` chains
over > 3 types, ≥ 3× duplicated algorithms, or a class with > 6 unrelated
responsibilities each default to **High** severity. Full thresholds and the
code-smell→pattern reverse lookup live in
[design-pattern-review.md](../architecture/design-pattern-review.md).

### Anti-Patterns to Detect

```
□ God Object — one class responsible for everything
□ Anemic Domain Model — domain objects are just bags of getters/setters
□ Distributed Monolith — microservices but tightly coupled via synchronous calls
□ Hardcoded Dependencies — `new ServiceImpl()` instead of injected interface
□ Spaghetti Dependencies — no clear layering, anything calls anything
□ Premature Microservices — microservice overhead with none of the benefits
```

### Microservices (if applicable)

```
□ Each service owns one business capability
□ Database per service (no shared DB between services)
□ Communication: async (events) preferred over sync for non-critical paths
□ Circuit breakers on all inter-service calls
□ Services independently deployable without coordinating releases
□ Health endpoint exposed (/health or /readyz)
□ Observability: structured logs, distributed tracing, metrics
□ API Gateway handles cross-cutting: auth, rate limiting, routing
```

### Dependency Management

```
□ No circular imports / circular dependencies
□ External dependencies abstracted behind interfaces (easy to swap)
□ Third-party library not used directly throughout codebase (adapter/wrapper)
□ Dependency versions pinned; lock files committed
□ No abandoned or vulnerable dependencies
```

### Scalability & Reliability

```
□ Stateless services (session state in shared storage, not memory)
□ Idempotent operations (safe to retry)
□ Graceful degradation (partial failure ≠ total outage)
□ Retry + exponential backoff for transient failures
□ Timeout configured on all external calls
□ Resource pooling (DB connections, HTTP clients)
```

---

## Architecture Decision Quick Guide

### When to use which pattern

```
Simple application (1–3 developers):
  → Layered architecture (Presentation / Business / Data)

Growing codebase (multiple teams, clear domain boundaries):
  → Modular monolith + DDD aggregates

High scale, independent scaling needs, large org:
  → Microservices (only if team can support the operational overhead)

Complex business logic with many state transitions:
  → Domain-Driven Design (Aggregates, Value Objects, Domain Events)

High read/write ratio difference:
  → CQRS + Read Models
```

---

## References

- [architect-guide.md](../architecture/architect-guide.md) — Full architect reference
- [system-architecture.md](../architecture/system-architecture.md) — Architecture quality attributes
- [design-pattern-review.md](../architecture/design-pattern-review.md) — GoF pattern review
- [microservices-compliance.md](../architecture/microservices-compliance.md) — Microservices checklist
- [dependency-analysis.md](../architecture/dependency-analysis.md) — Dependency analysis guide

## Related Commands

- [security.md](security.md)
- [performance.md](performance.md)
- [quality.md](quality.md)
- [simplification.md](simplification.md)
