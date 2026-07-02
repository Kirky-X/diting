# 监控配置参考

## Prometheus 指标

```yaml
scrape_configs:
  - job_name: 'api-service'
    metrics_path: /metrics
    static_configs:
      - targets: ['api-service:8080']
      
  - job_name: 'node-exporter'
    static_configs:
      - targets: ['node-exporter:9100']
```

```python
from prometheus_client import Counter, Histogram

REQUEST_COUNT = Counter(
    'api_requests_total',
    'Total API requests',
    ['method', 'endpoint', 'status']
)

REQUEST_LATENCY = Histogram(
    'api_request_duration_seconds',
    'API request latency',
    ['method', 'endpoint'],
    buckets=[0.01, 0.05, 0.1, 0.5, 1, 5]
)
```

## Grafana 仪表板

```json
{
  "dashboard": {
    "title": "API Performance",
    "panels": [
      {
        "title": "Request Rate",
        "type": "graph",
        "targets": [{
          "expr": "sum(rate(api_requests_total[5m])) by (endpoint)",
          "legendFormat": "{{endpoint}}"
        }]
      },
      {
        "title": "P99 Latency",
        "type": "graph",
        "targets": [{
          "expr": "histogram_quantile(0.99, sum(rate(api_request_duration_seconds_bucket[5m])) by (le, endpoint))",
          "legendFormat": "{{endpoint}}"
        }]
      }
    ]
  }
}
```

## 告警规则

```yaml
groups:
  - name: performance_alerts
    rules:
      - alert: HighLatency
        expr: histogram_quantile(0.95, rate(api_request_duration_seconds_bucket[5m])) > 1
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "API latency too high"
          
      - alert: HighErrorRate
        expr: sum(rate(api_requests_total{status=~'5..'}[5m])) / sum(rate(api_requests_total[5m])) > 0.01
        for: 3m
        labels:
          severity: critical
        annotations:
          summary: "Error rate too high"
```
