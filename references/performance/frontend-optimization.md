# Frontend Performance Optimization Reference

## Core Web Vitals Optimization

| Metric | Optimization Strategy |
|------|----------|
| **LCP** | Preload critical resources, CDN, caching, SSR |
| **FID** | Reduce main thread work, code splitting, lazy loading |
| **CLS** | Fixed image dimensions, font loading strategy, avoid dynamic content |

## Resource Optimization

```javascript
const LazyComponent = lazy(() => import('./LazyComponent'));
const HeavyChart = React.lazy(() => import('./HeavyChart'));

<img 
  srcset="image-400.webp 400w, image-800.webp 800w"
  sizes="(max-width: 600px) 400px, 800px"
  loading="lazy"
  decoding="async"
/>

<link rel="preload" href="/fonts/inter-var.woff2" as="font" crossorigin>
```

## Rendering Optimization

```javascript
const MemoizedComponent = React.memo(Component, (prev, next) => {
  return prev.id === next.id;
});

const expensiveValue = useMemo(() => {
  return computeExpensiveValue(a, b);
}, [a, b]);

const handleClick = useCallback(() => {
  doSomething(id);
}, [id]);
```

## CSS Optimization

```css
.list-container {
  contain: content;
}

.animated {
  will-change: transform;
  transform: translateZ(0);
}

@font-face {
  font-display: swap;
}
```

## Performance Budget Configuration

```yaml
performance_budget:
  web_vitals:
    LCP: "< 2.5s"
    FID: "< 100ms"
    CLS: "< 0.1"
    
  resource:
    bundle_size: "< 200KB gzipped"
    js_size: "< 100KB"
    css_size: "< 30KB"
```