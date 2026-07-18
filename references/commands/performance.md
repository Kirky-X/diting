# Performance Review Command

Performance Review Mode — latency, throughput, resource efficiency analysis

## Usage

```bash
review performance [target-path]
```

## Performance Targets

### Web API (Backend)

| Metric | Target | Alert |
|---|---|---|
| P50 response time | < 100ms | > 200ms |
| P95 response time | < 500ms | > 1s |
| P99 response time | < 1s | > 3s |
| Error rate | < 0.1% | > 1% |
| CPU utilization | < 70% | > 85% |
| Memory utilization | < 75% | > 90% |

> ⚠️ Note: P99 is always ≥ P95 ≥ P50. P99 target cannot be lower than P95.

### Web Vitals (Frontend)

| Metric | Good | Needs Improvement | Poor |
|---|---|---|---|
| LCP | ≤ 2.5s | 2.5–4s | > 4s |
| FID / INP | ≤ 100ms | 100–300ms | > 300ms |
| CLS | ≤ 0.1 | 0.1–0.25 | > 0.25 |
| TTFB | ≤ 800ms | 800ms–1.8s | > 1.8s |

### Resource Budget (Frontend)

| Resource | Target |
|---|---|
| JS bundle (gzipped) | < 200KB |
| Initial JS | < 100KB |
| CSS | < 30KB |
| Images (per page total) | < 1MB |

---

## Checklist

### Algorithms and Data Structures

```
□ No O(n²) or worse on hot paths (nested loops on large collections)
□ Appropriate data structures: Map/Set lookup (O(1)) vs Array (O(n))
□ No duplicate work: memoize or cache expensive computations
□ Bounded collection pagination
□ Sorting deferred until needed
```

**Red Flags to Scan For:**
- Nested `for` loops both iterating the same collection
- `.filter().map()` chains that could be merged
- `.find()` inside a loop instead of pre-building a Map
- Recursion on overlapping subproblems without memoization

### Database

```
□ N+1 query issues: no DB calls inside loops
□ All columns in WHERE, JOIN ON, ORDER BY clauses have indexes
□ Avoid SELECT * — fetch only needed columns
□ Slow queries (> 100ms) analyzed with EXPLAIN ANALYZE
□ Connection pooling configured (not per-request connections)
□ Transaction scope appropriate (not holding locks longer than necessary)
□ Large tables use LIMIT/OFFSET or cursor-based pagination
□ Read-heavy queries use read replicas
```

### Caching

```
□ Read-heavy, write-light data cached (user profiles, configs, product catalogs)
□ Cache TTL appropriate for data freshness requirements
□ Cache invalidation strategy explicit (evict on write vs TTL only)
□ Cache stampede protection (missing keys don't repeatedly hit DB)
□ Cache avalanche/thundering herd handling (locks or probabilistic early expiration)
□ Distributed cache for multi-instance deployments
```

### Async and Concurrency

```
□ No blocking I/O in async contexts (no sync DB calls in async handlers)
□ CPU-intensive work offloaded from event loop/main thread
□ Fire-and-forget tasks enqueued (Celery, BullMQ, etc.), not inline-waited
□ Parallelizable work parallelized (Promise.all, asyncio.gather, goroutines)
□ Thread/connection pool sizes appropriate for load
```

### Memory

```
□ No large object memory accumulation (stream large files instead of loading)
□ Event listeners unbound on component unmount
□ Circular references don't prevent GC
□ Large temporary arrays not held beyond their scope
```

### Frontend

```
□ Code splitting implemented (lazy-load routes and heavy components)
□ Images: WebP/AVIF format, responsive srcset, loading="lazy"
□ Fonts: font-display: swap, preload critical fonts
□ Third-party scripts deferred or async
□ React: useMemo/useCallback for expensive computations/stable references
□ Lists > 100 items use virtual scrolling
□ scroll, resize, input event handlers debounced/throttled
```

### Resource Optimization

```
□ Images use modern formats (WebP, AVIF)
□ Image sizes appropriate (don't load 4K thumbnails)
□ Image dimensions specified to prevent CLS (width/height attributes)
□ Below-the-fold images lazy-loaded (loading="lazy")
□ Responsive images use srcset for different screens
□ Videos use poster images as initial frame
□ Critical content fonts preloaded
□ SVGs optimized (SVGO) and compressed
```

### Code Splitting and Lazy Loading

```
□ Route-level code splitting implemented
□ Heavy components lazy-loaded (React.lazy, dynamic import)
□ Third-party libraries dynamically loaded when needed
□ Critical chunks preloaded for navigation
□ Resources for likely next pages prefetched
□ CSS code splitting enabled
□ Tree-shaking working (no unused exports)
```

### CDN and Caching

```
□ Static assets served from CDN
□ Cache-Control headers set appropriately
□ Immutable assets have long max-age
□ Asset URL versioning/cache busting
□ Service Worker offline caching (if applicable)
□ API responses have appropriate cache headers
□ ETag configured for conditional requests
```

### Bundle Optimization

```
□ Bundle size analyzed and documented
□ No duplicate dependencies
□ Consider lighter alternatives for heavy dependencies
□ Polyfills not duplicated
□ Source maps generated for production debugging
□ Compression enabled (gzip, brotli)
```

---

## Common Performance Anti-patterns

| Anti-pattern | Detection | Fix |
|---|---|---|
| N+1 queries | DB calls inside loops | Preload/batch fetch |
| Missing indexes | Slow queries on unindexed filter columns | Add composite index |
| Synchronous HTTP in loops | `requests.get()` in for loops | `asyncio.gather()` or thread pool |
| Unbounded queries | `SELECT * FROM table` without LIMIT | Add pagination |
| Re-render on every keystroke | onChange triggers full list re-render | Debounce + useMemo |
| Large bundle | Single JS file > 1MB | Code splitting + lazy loading |
| Memory leak | Event listeners not removed | Cleanup/destructor in useEffect return |

---

## References

- [performance-engineer-guide.md](../performance/performance-engineer-guide.md) — full guide
- [backend-optimization.md](../performance/backend-optimization.md) — backend patterns
- [frontend-optimization.md](../performance/frontend-optimization.md) — frontend patterns
- [profiling-tools.md](../performance/profiling-tools.md) — performance analysis tools
- [load-testing.md](../performance/load-testing.md) — load testing scripts
- [monitoring.md](../performance/monitoring.md) — metrics and alerting

## Related Commands

- [security.md](security.md)
- [quality.md](quality.md)
- [architecture.md](architecture.md)
- [simplification.md](simplification.md)
