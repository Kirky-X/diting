# Performance Engineer Guide

> Comprehensive performance engineering reference covering testing, optimization, and monitoring methodologies.
>
> See [performance-deep-dive.md](performance-deep-dive.md) for in-depth analysis (frontend/backend optimization, monitoring configuration).

## Role Definition

Performance engineering specialist with 8+ years of experience:
- Performance testing and benchmarking
- System optimization (frontend, backend, database)
- Monitoring and observability
- Capacity planning

## Core Competencies

### Performance Testing

| Test Type | Purpose | Tools |
|-----------|---------|-------|
| **Load Testing** | Verify system behavior under expected load | k6, Locust, JMeter, Gatling |
| **Stress Testing** | Find the breaking point | k6, JMeter |
| **Soak Testing** | Verify long-term stability | Custom scripts |
| **Spike Testing** | Test sudden load surges | k6, Gatling |
| **Scalability Testing** | Measure scaling capability | Custom frameworks |
| **Benchmarking** | Compare performance metrics | hyperfine, JMH |

### Performance Optimization

| Area | Focus |
|------|-------|
| **Frontend** | Core Web Vitals, bundle size, rendering |
| **Backend** | Algorithms, caching, database |
| **Network** | Compression, CDN, protocols |
| **Memory** | Allocation patterns, GC tuning |
| **CPU** | Hot paths, parallelization |
| **I/O** | Async operations, batch processing |

### Monitoring & Observability

| Category | Tools |
|----------|-------|
| **APM** | Datadog, New Relic, AppDynamics |
| **Metrics** | Prometheus, Grafana |
| **Tracing** | Jaeger, Zipkin |
| **Logging** | ELK Stack, Splunk |
| **RUM** | Real User Monitoring |

## Workflow

### 1. Assessment Phase

1. Define performance requirements
2. Establish baseline metrics
3. Identify critical paths
4. Map dependencies
5. Set performance budgets

**Key Questions**:
- What are the performance requirements?
- What are the current baselines?
- What are the critical user journeys?
- What dependencies exist?

### 2. Testing Phase

1. Design test scenarios
2. Create test data
3. Execute load tests
4. Monitor system behavior
5. Collect metrics

### 3. Analysis Phase

1. Analyze bottlenecks
2. Profile code paths
3. Review database queries
4. Check infrastructure limitations
5. Identify optimization opportunities

### 4. Optimization Phase

1. Implement optimizations
2. Verify improvements
3. Re-test to confirm
4. Document changes
5. Set up monitoring

## Performance Budgets

### Web Vitals Targets

| Metric | Good | Needs Improvement | Poor |
|--------|------|-------------------|------|
| **LCP** (Largest Contentful Paint) | ≤ 2.5s | 2.5s - 4.0s | > 4.0s |
| **FID** (First Input Delay) | ≤ 100ms | 100ms - 300ms | > 300ms |
| **CLS** (Cumulative Layout Shift) | ≤ 0.1 | 0.1 - 0.25 | > 0.25 |
| **TTFB** (Time to First Byte) | ≤ 800ms | 800ms - 1800ms | > 1800ms |

### Resource Budgets

| Resource | Target |
|----------|--------|
| Bundle size | < 200KB gzipped |
| JavaScript | < 100KB |
| CSS | < 30KB |
| Images | < 500KB total |
| Fonts | < 50KB |

### System Metrics

| Metric | Target | Notes |
|--------|--------|-------|
| P50 response time | < 100ms | Median — typical user experience |
| P95 response time | < 500ms | 95th percentile — must be ≥ P50 |
| P99 response time | < 1s | 99th percentile — must be ≥ P95 |
| Error rate | < 0.1% | 5xx + timeouts |
| CPU utilization | < 70% | Sustained average |
| Memory utilization | < 80% | Leave headroom for GC spikes |

## Load Testing

> Complete test scripts (k6, Locust, JMeter) are maintained in [load-testing.md](load-testing.md) to avoid duplication.

**Quick Reference — Thresholds to set in load tests:**

```
p(95) < 500ms   ← Maps to P95 target
p(99) < 1000ms  ← Maps to P99 target
error rate < 1%
```

**Load Stage Pattern:**
```mermaid
flowchart LR
    R["Ramp Up (2m)"] --> P["Steady at target RPS (5m)"]
    P --> Peak["Peak x2 (5m)"]
    Peak --> RD["Ramp Down (2m)"]
```

Full k6, Locust, and JMeter scripts are in [load-testing.md](load-testing.md).

## Profiling Tools

### Frontend Profiling

```bash
# Chrome DevTools
# Performance tab → Record → Analyze

# Lighthouse CLI
lighthouse https://example.com --view

# WebPageTest
webpagetest test https://example.com
```

### Backend Profiling

```bash
# Python
py-spy top --pid 12345

# Java
async-profiler -d 60 -f flamegraph.html 12345

# Go
go tool pprof http://localhost:6060/debug/pprof/profile

# Rust
perf record -g ./target/release/myapp
perf report
```

## Collaboration

### With Backend Developers
- Analyze code performance
- Optimize database queries
- Implement caching strategies
- Review architectural decisions

### With Frontend Developers
- Optimize bundle size
- Improve rendering performance
- Implement lazy loading
- Optimize Core Web Vitals

### With DevOps
- Set up monitoring
- Configure auto-scaling
- Optimize infrastructure
- Manage resources

### With QA Engineers
- Define performance tests
- Create test plans
- Support testing
- Verify optimizations

## Key Metrics Summary

### User-Facing Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| LCP | < 2.5s | Largest contentful paint time |
| FID | < 100ms | First interaction delay |
| CLS | < 0.1 | Layout shift score |
| TTFB | < 800ms | Server response time |

### System Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Response time P50 | < 100ms | Median — typical request |
| Response time P95 | < 500ms | 95th percentile (must be ≥ P50) |
| Response time P99 | < 1s | 99th percentile (must be ≥ P95) |
| Throughput | Variable | Requests per second at target latency |
| Error rate | < 0.1% | Failed requests |

### Business Metrics

| Metric | Description |
|--------|-------------|
| Conversion rate | Impact on business goals |
| User satisfaction | NPS and feedback |
| Cost per request | Infrastructure efficiency |
| Time to market | Development speed |
