# 性能审查命令

性能审查模式 —— 延迟、吞吐、资源效率分析

## 用法

```bash
review performance [target-path]
```

## 性能目标

### Web API（后端）

| 指标 | 目标 | 告警 |
|---|---|---|
| P50 响应时间 | < 100ms | > 200ms |
| P95 响应时间 | < 500ms | > 1s |
| P99 响应时间 | < 1s | > 3s |
| 错误率 | < 0.1% | > 1% |
| CPU 利用率 | < 70% | > 85% |
| 内存利用率 | < 75% | > 90% |

> ⚠️ 注意：P99 总是 ≥ P95 ≥ P50。P99 目标不能低于 P95。

### Web Vitals（前端）

| 指标 | 良好 | 需改进 | 较差 |
|---|---|---|---|
| LCP | ≤ 2.5s | 2.5–4s | > 4s |
| FID / INP | ≤ 100ms | 100–300ms | > 300ms |
| CLS | ≤ 0.1 | 0.1–0.25 | > 0.25 |
| TTFB | ≤ 800ms | 800ms–1.8s | > 1.8s |

### 资源预算（前端）

| 资源 | 目标 |
|---|---|
| JS 包（gzip 后） | < 200KB |
| 初始 JS | < 100KB |
| CSS | < 30KB |
| 图片（每页总计） | < 1MB |

---

## 检查内容

### 算法和数据结构

```
□ 热点路径无 O(n²) 或更差（大集合上的嵌套循环）
□ 合适的数据结构：Map/Set 查找（O(1)）vs Array（O(n)）
□ 无重复工作：memoize 或缓存昂贵计算
□ 无界集合分页
□ 排序延迟到必要时
```

**需扫描的危险信号：**
- 嵌套 `for` 循环都迭代同一集合
- `.filter().map()` 链可以合并
- 循环内 `.find()` 而非预构建 Map
- 重叠子问题无 memoization 的递归

### 数据库

```
□ N+1 查询问题：循环内无 DB 调用
□ WHERE、JOIN ON、ORDER BY 子句的所有列有索引
□ 避免 SELECT * —— 只取需要的列
□ 慢查询（> 100ms）已 EXPLAIN ANALYZE
□ 配置连接池（非每请求新建连接）
□ 事务范围合适（不长于需要地持有锁）
□ 大表用 LIMIT/OFFSET 或游标分页
□ 读多查询用读副本
```

### 缓存

```
□ 读多写少的数据缓存（用户画像、配置、商品目录）
□ 缓存 TTL 适合数据新鲜度要求
□ 缓存失效策略明确（写时驱逐 vs 仅 TTL）
□ 缓存穿透防护（缺失 key 不反复打 DB）
□ 缓存雪崩/惊群处理（锁或概率提前过期）
□ 多实例部署用分布式缓存
```

### 异步和并发

```
□ 异步上下文中无阻塞 I/O（不在 async handler 中调同步 DB）
□ CPU 密集工作从事件循环/主线程卸载
□ 即发即忘任务入队（Celery、BullMQ 等）不内联等待
□ 可并行工作并行化（Promise.all、asyncio.gather、goroutine）
□ 线程/连接池大小适合负载
```

### 内存

```
□ 无大对象内存堆积（大文件流式处理而非加载）
□ 组件卸载时事件监听器解绑
□ 循环引用不阻止 GC
□ 大临时数组不超出其作用域持有
```

### 前端

```
□ 代码分割（懒加载路由和重组件）
□ 图片：WebP/AVIF 格式、响应式 srcset、loading="lazy"
□ 字体：font-display: swap、预加载关键字体
□ 第三方脚本 deferred 或 async
□ React：useMemo/useCallback 用于昂贵计算/稳定引用
□ 列表 > 100 项虚拟滚动
□ scroll、resize、input 事件处理 debounce/throttle
```

### 资源优化

```
□ 图片用现代格式（WebP、AVIF）
□ 图片尺寸合适（不加载 4K 缩略图）
□ 图片尺寸指定以防 CLS（width/height 属性）
□ 折叠下方图片懒加载（loading="lazy"）
□ 响应式图片用 srcset 适配不同屏幕
□ 视频用 poster 图作为初始帧
□ 关键内容字体预加载
□ SVG 优化（SVGO）并压缩
```

### 代码分割和懒加载

```
□ 路由级代码分割实现
□ 重组件懒加载（React.lazy、dynamic import）
□ 第三方库需要时动态加载
□ 预加载导航的关键 chunk
□ 预取可能下一页的资源
□ CSS 代码分割启用
□ Tree-shaking 工作（无未使用导出）
```

### CDN 和缓存

```
□ 静态资源从 CDN 提供
□ Cache-Control 头设置合适
□ 不可变资源有长 max-age
□ 资源 URL 版本化/缓存破坏
□ Service Worker 离线缓存（如适用）
□ API 响应用合适缓存头
□ ETag 配置条件请求
```

### 包优化

```
□ 包大小已分析并记录
□ 无重复依赖
□ 大依赖有更轻替代方案考虑
□ Polyfill 不重复
□ 生产调试生成 source map
□ 启用压缩（gzip、brotli）
```

---

## 常见性能反模式

| 反模式 | 检测 | 修复 |
|---|---|---|
| N+1 查询 | 循环内 DB 调用 | 预加载/批量获取 |
| 缺失索引 | 过滤列无索引的慢查询 | 加复合索引 |
| 循环内同步 HTTP | for 循环中 `requests.get()` | `asyncio.gather()` 或线程池 |
| 无界查询 | `SELECT * FROM table` 无 LIMIT | 加分页 |
| 每次按键重渲染 | onChange 触发全列表重渲染 | Debounce + useMemo |
| 大包 | 单 JS 文件 > 1MB | 代码分割 + 懒加载 |
| 内存泄漏 | 事件监听器未移除 | useEffect return 中清理/析构 |

---

## 参考

- [performance-engineer-guide.md](../performance/performance-engineer-guide.md) — 完整指南
- [backend-optimization.md](../performance/backend-optimization.md) — 后端模式
- [frontend-optimization.md](../performance/frontend-optimization.md) — 前端模式
- [profiling-tools.md](../performance/profiling-tools.md) — 性能分析工具
- [load-testing.md](../performance/load-testing.md) — 压测脚本
- [monitoring.md](../performance/monitoring.md) — 指标和告警

## 相关命令

- [security.md](security.md)
- [quality.md](quality.md)
- [architecture.md](architecture.md)
- [simplification.md](simplification.md)
