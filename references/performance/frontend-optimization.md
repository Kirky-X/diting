# 前端性能优化参考

## Core Web Vitals 优化

| 指标 | 优化策略 |
|------|----------|
| **LCP** | 预加载关键资源、CDN、缓存、SSR |
| **FID** | 减少主线程工作、代码分割、懒加载 |
| **CLS** | 固定图片尺寸、字体加载策略、避免动态内容 |

## 资源优化

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

## 渲染优化

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

## CSS 优化

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

## 性能预算配置

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
