# 性能分析工具参考

## Chrome DevTools

| 面板 | 用途 |
|------|------|
| **Performance** | 页面加载性能分析 |
| **Memory** | 内存使用分析 |
| **Network** | 网络请求分析 |
| **Lighthouse** | 自动化性能审计 |

## Python 性能分析

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

## 性能报告模板

```markdown
# 性能测试报告

## 测试概述
- 测试日期: 2024-01-15
- 测试环境: staging
- 测试工具: k6 + Grafana

## 测试场景
| 场景 | 并发用户 | 持续时间 | 目标 RPS |
|------|---------|---------|----------|
| 浏览商品 | 500 | 10min | 1000 |
| 结账流程 | 200 | 10min | 200 |

## 测试结果
| 指标 | P50 | P95 | P99 | 最大 |
|------|-----|-----|-----|------|
| 首页加载 | 120ms | 350ms | 800ms | 2.5s |
| 商品列表 | 200ms | 500ms | 1.2s | 3s |

## 发现的问题
| 问题 | 严重度 | 建议修复 |
|------|----------|----------|
| 首页 LCP 超过 2.5s | 高 | 优化首屏资源 |
| 慢数据库查询 | 中 | 添加索引 |
```
