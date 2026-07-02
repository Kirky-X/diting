# Performance Command

Performance review mode — latency, throughput, resource efficiency analysis

## Usage

```bash
review performance [target-path]
```

## Performance Targets

### Web API (Backend)

| Metric | Target | Alert |
|---|---|---|
| P50 Response Time | < 100ms | > 200ms |
| P95 Response Time | < 500ms | > 1s |
| P99 Response Time | < 1s | > 3s |
| Error Rate | < 0.1% | > 1% |
| CPU Utilization | < 70% | > 85% |
| Memory Utilization | < 75% | > 90% |

> ⚠️ Note: P99 is always ≥ P95 ≥ P50. A P99 target cannot be lower than P95.

### Web Vitals (Frontend)

| Metric | Good | Needs Work | Poor |
|---|---|---|---|
| LCP | ≤ 2.5s | 2.5–4s | > 4s |
| FID / INP | ≤ 100ms | 100–300ms | > 300ms |
| CLS | ≤ 0.1 | 0.1–0.25 | > 0.25 |
| TTFB | ≤ 800ms | 800ms–1.8s | > 1.8s |

### Resource Budgets (Frontend)

| Resource | Target |
|---|---|
| JS Bundle (gzipped) | < 200KB |
| Initial JS | < 100KB |
| CSS | < 30KB |
| Images (total per page) | < 1MB |

---

## What to Check

### Algorithm & Data Structures

```
□ No O(n²) or worse in hot paths (nested loops over large collections)
□ Appropriate data structure: Map/Set for lookup (O(1)) vs Array (O(n))
□ No repeated work: memoize or cache expensive computations
□ Pagination applied to unbounded collections
□ Sorting deferred until necessary
```

**Red flags to scan for:**
- Nested `for` loops both iterating the same collection
- `.filter().map()` chains that could be combined
- `.find()` inside a loop instead of a pre-built Map
- Recursive functions without memoization on overlapping subproblems

### Database

```
□ N+1 query problem: no DB call inside a loop
□ Indexes exist for all columns in WHERE, JOIN ON, ORDER BY clauses
□ SELECT * avoided — only fetch needed columns
□ EXPLAIN ANALYZE reviewed for slow queries (> 100ms)
□ Connection pool configured (not opening new connection per request)
□ Transactions scoped appropriately (not holding locks longer than needed)
□ Pagination with LIMIT/OFFSET or cursor-based for large tables
□ Read replicas used for read-heavy queries
```

### Caching

```
□ Frequently-read, rarely-changed data cached (user profiles, config, product catalog)
□ Cache TTL appropriate for data freshness requirements
□ Cache invalidation strategy defined (evict on write vs. TTL-only)
□ Cache penetration prevented (missing keys don't repeatedly hit DB)
□ Cache stampede / thundering herd handled (locks or probabilistic early expiry)
□ Distributed cache for multi-instance deployments
```

### Async & Concurrency

```
□ Blocking I/O in async context (don't call sync DB in async handler)
□ CPU-bound work offloaded from event loop / main thread
□ Fire-and-forget tasks queued (Celery, BullMQ, etc.) not awaited inline
□ Parallelizable work parallelized (Promise.all, asyncio.gather, goroutines)
□ Thread/connection pool sized correctly for workload
```

### Memory

```
□ No accumulation of large objects in memory (streaming large files instead of loading)
□ Event listeners detached when components unmount
□ Circular references not preventing GC
□ Large temporary arrays not held beyond their scope
```

### Frontend

```
□ Code splitting applied (lazy load routes and heavy components)
□ Images: WebP/AVIF format, responsive srcset, loading="lazy"
□ Fonts: font-display: swap, preloaded critical fonts
□ Third-party scripts deferred or async
□ React: useMemo/useCallback for expensive computations / stable references
□ Virtual scrolling for lists > 100 items
□ Debounce/throttle on scroll, resize, input event handlers
```

### Asset Optimization

```
□ Images use modern formats (WebP, AVIF) where supported
□ Images properly sized (not loading 4K for thumbnails)
□ Image dimensions specified to prevent CLS (width/height attributes)
□ Lazy loading for below-fold images (loading="lazy")
□ Responsive images with srcset for different screen sizes
□ Video uses poster image for initial frame
□ Fonts preloaded for critical content
□ SVG optimized (SVGO) and compressed
```

### Code Splitting & Lazy Loading

```
□ Route-level code splitting implemented
□ Heavy components lazy loaded (React.lazy, dynamic import)
□ Third-party libraries loaded dynamically when needed
□ Preload critical chunks for navigation
□ Prefetch likely-next-page resources
□ CSS code splitting enabled
□ Tree-shaking working (no unused exports)
```

### CDN & Caching

```
□ Static assets served from CDN
□ Cache-Control headers set appropriately
□ Immutable assets have long max-age
□ Versioned/cache-busted asset URLs
□ Service Worker for offline caching (where appropriate)
□ API responses use appropriate cache headers
□ ETags configured for conditional requests
```

### Bundle Optimization

```
□ Bundle size analyzed and documented
□ No duplicate dependencies
□ Large dependencies have lighter alternatives considered
□ Polyfills not duplicated
□ Source maps generated for production debugging
□ Compression enabled (gzip, brotli)
```

---

## Common Performance Anti-Patterns

| Anti-Pattern | Detection | Fix |
|---|---|---|
| N+1 Queries | DB call in loop | Eager load / batch fetch |
| Missing Index | Slow query without index on filter col | Add composite index |
| Synchronous HTTP in loop | `requests.get()` in for-loop | `asyncio.gather()` or thread pool |
| Unbounded query | `SELECT * FROM table` no LIMIT | Add pagination |
| Re-render on every keystroke | onChange triggers full list re-render | Debounce + useMemo |
| Large bundle | Single JS file > 1MB | Code splitting + lazy loading |
| Memory leak | Event listener not removed | Cleanup in useEffect return / destructor |

---

## References

- [performance-engineer-guide.md](../performance/performance-engineer-guide.md) — Full guide
- [backend-optimization.md](../performance/backend-optimization.md) — Backend patterns
- [frontend-optimization.md](../performance/frontend-optimization.md) — Frontend patterns
- [profiling-tools.md](../performance/profiling-tools.md) — Profiling tools
- [load-testing.md](../performance/load-testing.md) — Load testing scripts
- [monitoring.md](../performance/monitoring.md) — Metrics & alerting

## Related Commands

- [security.md](security.md)
- [quality.md](quality.md)
- [architecture.md](architecture.md)
- [simplification.md](simplification.md)
