# Profiling Tools Reference

## Chrome DevTools

| Panel | Purpose |
|------|------|
| **Performance** | Page load performance analysis |
| **Memory** | Memory usage analysis |
| **Network** | Network request analysis |
| **Lighthouse** | Automated performance audit |

## Python Profiling

```python
import cProfile
import pstats

profiler = cProfile.Profile()
profiler.enable()
process_data()
profiler.disable()

stats = pstats.Stats(profiler)
stats.sort_stats('cumulative')
stats.print_stats(20)
```

```python
@profile
def process_data():
    ...

@profile
def memory_intensive():
    ...
```

## Performance Report Template

```markdown
# Performance Test Report

## Test Overview
- Test Date: 2024-01-15
- Test Environment: staging
- Test Tools: k6 + Grafana

## Test Scenarios
| Scenario | Concurrent Users | Duration | Target RPS |
|------|---------|---------|----------|
| Browse Products | 500 | 10min | 1000 |
| Checkout Flow | 200 | 10min | 200 |

## Test Results
| Metric | P50 | P95 | P99 | Max |
|------|-----|-----|-----|------|
| Homepage Load | 120ms | 350ms | 800ms | 2.5s |
| Product List | 200ms | 500ms | 1.2s | 3s |

## Issues Found
| Issue | Severity | Suggested Fix |
|------|----------|----------|
| Homepage LCP over 2.5s | High | Optimize above-the-fold resources |
| Slow database queries | Medium | Add indexes |
```