# 后端性能优化参考

> **范围**：后端优化的具体代码模式 —— 数据库索引、缓存、连接池、异步处理。  
> 指标、阈值和瓶颈识别工作流见 [performance-engineer-guide.md](performance-engineer-guide.md)。

## 数据库优化

```sql
CREATE INDEX idx_orders_user_date 
ON orders(user_id, created_at DESC);

EXPLAIN ANALYZE
SELECT * FROM orders 
WHERE user_id = 123 
ORDER BY created_at DESC 
LIMIT 20;
```

## 缓存策略

```python
import redis
from functools import lru_cache

r = redis.Redis(host='localhost', port=6379, db=0)

def get_user(user_id: int) -> dict:
    cache_key = f"user:{user_id}"
    cached = r.get(cache_key)
    if cached:
        return json.loads(cached)
    
    user = db.get_user(user_id)
    r.setex(cache_key, 3600, json.dumps(user))
    return user

pipe = r.pipeline()
for user_id in user_ids:
    pipe.get(f"user:{user_id}")
results = pipe.execute()
```

## 连接池配置

```python
from sqlalchemy import create_engine

engine = create_engine(
    "postgresql://user:pass@host/db",
    pool_size=20,
    max_overflow=30,
    pool_pre_ping=True,
    pool_recycle=3600,
)
```

## 异步处理

```python
from celery import Celery

app = Celery('tasks', broker='redis://localhost')

@app.task(bind=True, max_retries=3)
def process_order(self, order_id):
    try:
        order = Order.objects.get(id=order_id)
        send_notification(order)
    except Exception as e:
        self.retry(exc=e, countdown=60)
```

## 数据库查询分析

```sql
SET GLOBAL slow_query_log = 'ON';
SET GLOBAL long_query_time = 1;

CREATE EXTENSION pg_stat_statements;
SELECT * FROM pg_stat_statements 
ORDER BY mean_time DESC LIMIT 10;
```
