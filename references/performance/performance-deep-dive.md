# 性能深度分析

> 性能工程深度分析：前端优化、后端优化、监控配置。主流程详见 [performance-engineer-guide.md](performance-engineer-guide.md)。

## 1. 前端优化

### Core Web Vitals 优化

#### LCP 优化

```javascript
// 预加载关键资源
<link rel="preload" href="/fonts/inter.woff2" as="font" crossorigin>
<link rel="preload" href="/hero-image.webp" as="image">

// 使用响应式图片
<img 
  srcset="image-400.webp 400w, image-800.webp 800w"
  sizes="(max-width: 600px) 400px, 800px"
  loading="lazy"
  decoding="async"
/>

// 关键内容服务端渲染
// 静态资源 CDN 缓存
```

#### FID 优化

```javascript
// 代码分割
const LazyComponent = React.lazy(() => import('./LazyComponent'));

// 延迟非关键工作
requestIdleCallback(() => {
  // 非关键初始化
});

// 拆分长任务
function processLargeArray(array) {
  const CHUNK_SIZE = 100;
  let index = 0;
  
  function processChunk() {
    const end = Math.min(index + CHUNK_SIZE, array.length);
    while (index < end) {
      process(array[index++]);
    }
    if (index < array.length) {
      requestIdleCallback(processChunk);
    }
  }
  
  requestIdleCallback(processChunk);
}
```

#### CLS 优化

```css
/* 为图片预留空间 */
.image-container {
  aspect-ratio: 16 / 9;
  background: #f0f0f0;
}

/* 为广告预留空间 */
.ad-slot {
  min-height: 250px;
}

/* 字体加载 */
@font-face {
  font-family: 'Inter';
  font-display: swap;
}
```

### 包优化

```javascript
// webpack.config.js
module.exports = {
  optimization: {
    splitChunks: {
      chunks: 'all',
      cacheGroups: {
        vendor: {
          test: /[\\/]node_modules[\\/]/,
          name: 'vendors',
          chunks: 'all',
        },
      },
    },
  },
};

// Tree shaking
export { usedFunction };  // 仅导出使用的

// 动态导入
const module = await import('./heavy-module');
```

## 2. 后端优化

### 算法复杂度

| 复杂度 | n=1000 时的操作数 | 优化建议 |
|------------|----------------------|--------------|
| O(1) | 1 | 理想 |
| O(log n) | 10 | 优秀 |
| O(n) | 1,000 | 良好 |
| O(n log n) | 10,000 | 可接受 |
| O(n²) | 1,000,000 | 需要优化 |
| O(2^n) | 2^1000 | 避免 |

### 缓存策略

#### 多级缓存
```python
class CacheStrategy:
    L1_CACHE = {}  # 内存
    L2_CACHE = Redis()  # 分布式
    L3_CACHE = Database()  # 持久化
    
    async def get(self, key: str):
        if key in self.L1_CACHE:
            return self.L1_CACHE[key]
        value = await self.L2_CACHE.get(key)
        if value:
            self.L1_CACHE[key] = value
            return value
        value = await self.L3_CACHE.query(key)
        if value:
            await self.L2_CACHE.set(key, value, ttl=3600)
            self.L1_CACHE[key] = value
        return value
```

#### 缓存保护与预热
```python
class CachePenetrationProtection:
    async def get_or_default(self, key: str, fallback_value: str = ""):
        value = await self.cache.get(key)
        if value is None:
            return fallback_value
        return value
    
    async def might_exist(self, key: str) -> bool:
        return self.bloom_filter.might_contain(key)

# 缓存预热 - 系统启动时预加载热点数据
async def warm_up_cache():
    hot_keys = ["config:system", "config:features", "user:popular_tags"]
    for key in hot_keys:
        value = await database.query(key)
        await cache.set(key, value, ttl=3600)
```

#### 缓存更新策略
```python
class CacheUpdateStrategy:
    # 强一致性 - DB 更新后立即更新缓存
    async def write_through(self, key: str, value: Any):
        await self.db.update(key, value)
        await self.cache.set(key, value)
    
    # 最终一致性 - 允许轻微延迟
    async def write_back(self, key: str, value: Any):
        await self.cache.set(key, value)
        await self.queue.push(f"update:{key}:{value}")  # 异步 DB 同步
    
    # 定时刷新
    async def timed_refresh(self, key: str):
        while True:
            value = await self.db.query(key)
            await self.cache.set(key, value)
            await asyncio.sleep(300)  # 每 5 分钟刷新
```

### 数据库优化

```sql
-- 索引优化
CREATE INDEX idx_orders_user_date 
ON orders(user_id, created_at DESC);

-- 查询优化
EXPLAIN ANALYZE
SELECT * FROM orders 
WHERE user_id = 123 
ORDER BY created_at DESC 
LIMIT 20;

-- 分区
CREATE TABLE orders (
    id BIGSERIAL,
    created_at TIMESTAMP,
    -- ...
) PARTITION BY RANGE (created_at);

-- 连接池
-- 池大小 = (核心数 * 2) + 磁盘主轴数
```

### 异步处理

> 完整实现模式（Redis 管道、连接池、Celery 重试）在 [backend-optimization.md](backend-optimization.md) 中。

关键原则：将慢操作（邮件、通知、报表生成）移出请求路径到异步工作器。

```mermaid
flowchart TD
    Req["请求"] --> Queue["入队任务"]
    Queue --> Resp["返回 202 Accepted"]
    Queue --> Worker["工作器"]
    Worker --> Proc["处理"]
    Proc --> Notify["通过 webhook/push 通知"]
```

## 3. 监控配置

### Prometheus 指标

```yaml
# prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'app'
    static_configs:
      - targets: ['localhost:8080']
```

### Grafana 仪表板

```json
{
  "panels": [
    {
      "title": "请求速率",
      "targets": [{
        "expr": "rate(http_requests_total[5m])"
      }]
    },
    {
      "title": "P95 延迟",
      "targets": [{
        "expr": "histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))"
      }]
    },
    {
      "title": "错误率",
      "targets": [{
        "expr": "rate(http_requests_total{status=~\"5..\"}[5m])"
      }]
    }
  ]
}
```
