# Architecture Anti-Patterns & Deep Dive

> 架构深度技术：高可用、高并发、分布式、文档、安全架构。主流程详见 [architect-guide.md](architect-guide.md)。

## High-Availability Design

### Fault Tolerance Patterns

```
┌─────────────────────────────────────────────────────────┐
│                  Fault Tolerance                         │
├─────────────────────────────────────────────────────────┤
│ Circuit Breaker                                          │
│   └── Prevent cascade failures                           │
│                                                          │
│ Retry with Backoff                                       │
│   └── Handle transient failures                          │
│                                                          │
│ Bulkhead Isolation                                       │
│   └── Isolate failure domains                            │
│                                                          │
│ Timeout                                                  │
│   └── Prevent resource exhaustion                        │
│                                                          │
│ Fallback                                                 │
│   └── Graceful degradation                               │
└─────────────────────────────────────────────────────────┘
```

### Availability Targets

| Nines | Availability | Downtime/Year |
|-------|--------------|---------------|
| 99% | Two nines | 3.65 days |
| 99.9% | Three nines | 8.77 hours |
| 99.99% | Four nines | 52.6 minutes |
| 99.999% | Five nines | 5.26 minutes |

## High-Concurrency Architecture

### Caching Strategies

```
┌─────────────────────────────────────────────────────────┐
│                 Caching Layers                           │
├─────────────────────────────────────────────────────────┤
│ CDN Cache                                                │
│   └── Static assets, edge caching                        │
│                                                          │
│ Application Cache                                        │
│   └── In-memory (local), Redis (distributed)             │
│                                                          │
│ Database Cache                                           │
│   └── Query cache, buffer pool                           │
│                                                          │
│ Cache Patterns                                           │
│   ├── Cache-aside: Application manages cache             │
│   ├── Read-through: Cache reads from source              │
│   └── Write-through: Cache writes to source              │
└─────────────────────────────────────────────────────────┘
```

### Database Optimization

```
┌─────────────────────────────────────────────────────────┐
│              Database Scaling                            │
├─────────────────────────────────────────────────────────┤
│ Vertical Scaling                                         │
│   └── More CPU, RAM, SSD                                 │
│                                                          │
│ Read Replicas                                            │
│   └── Distribute read traffic                            │
│                                                          │
│ Sharding                                                 │
│   └── Horizontal partitioning                            │
│                                                          │
│ Partitioning                                             │
│   └── Range, Hash, List partitioning                     │
└─────────────────────────────────────────────────────────┘
```

### Async Processing

```mermaid
flowchart TD
    subgraph Sync["Synchronous Flow"]
        SUser["User"] --> SAPI["API"]
        SAPI --> SDB["Database"]
        SDB --> SResp["Response (blocking)"]
    end
    subgraph Async["Asynchronous Flow"]
        AUser["User"] --> AAPI["API"]
        AAPI --> AQueue["Queue"]
        AAPI --> AResp["Response (immediate)"]
        AQueue --> AWorker["Worker"]
        AWorker --> ADB["Database"]
    end
```

## Distributed System Design

### CAP Theorem

| Property | Description | Trade-off |
|----------|-------------|-----------|
| **Consistency** | All nodes see same data | Latency |
| **Availability** | Every request gets response | Stale data |
| **Partition Tolerance** | System works despite network failures | Must have |

**Choose**: CP (Consistency + Partition) or AP (Availability + Partition)

### Distributed Transactions

| Pattern | Use Case | Trade-off |
|---------|----------|-----------|
| **2PC** | Strong consistency | Blocking, single point of failure |
| **Saga** | Long-running transactions | Compensation logic complexity |
| **TCC** | High performance | Implementation complexity |

### Saga Pattern

```mermaid
sequenceDiagram
    participant OS as Order Service
    participant PS as Payment Service
    participant IS as Inventory Service
    OS->>PS: OrderCreated
    PS->>IS: PaymentProcessed
    IS->>OS: InventoryReserved
    OS->>OS: OrderConfirmed
    Note over OS,IS: Compensation (if failure)
    IS->>PS: InventoryReleased
    PS->>OS: PaymentRefunded
    OS->>OS: OrderCancelled
```

## Architecture Documentation

### C4 Model

```mermaid
flowchart TD
    L1["Level 1: Context<br/>System in its environment"]
    L2["Level 2: Container<br/>Applications and data stores"]
    L3["Level 3: Component<br/>Components within containers"]
    L4["Level 4: Code<br/>Implementation details"]
    L1 --> L2 --> L3 --> L4
```

### Architecture Decision Records (ADR)

```markdown
# ADR-001: Use Event-Driven Architecture

## Status
Accepted

## Context
System needs to handle high volume of async operations
with loose coupling between services.

## Decision
Implement event-driven architecture using message queues.

## Consequences
- Pros: Decoupling, scalability, resilience
- Cons: Complexity, eventual consistency, debugging challenges

## Alternatives Considered
1. Synchronous REST - Rejected due to tight coupling
2. gRPC streaming - Rejected due to complexity
```

## Security Architecture

### Authentication Architecture

```
┌─────────────────────────────────────────────────────────┐
│              Authentication Flow                         │
├─────────────────────────────────────────────────────────┤
│ Client → API Gateway → Auth Service                     │
│                          │                               │
│                          ├── Validate credentials        │
│                          ├── Generate JWT                │
│                          └── Return token                │
│                                                          │
│ Subsequent Requests:                                     │
│ Client → API Gateway → Validate JWT → Backend Service   │
└─────────────────────────────────────────────────────────┘
```

### Authorization Patterns

| Pattern | Use Case | Complexity |
|---------|----------|------------|
| **RBAC** | Role-based access | Low |
| **ABAC** | Attribute-based access | Medium |
| **PBAC** | Policy-based access | High |
