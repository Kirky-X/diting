# 并发正确性指南

并发正确性 —— 竞态条件检测与并发模式

## 概述

并发问题是代码审查中最难发现的问题之一。本文档提供识别常见竞态条件和正确并发处理方法的模式。

---

## 1. 常见竞态条件模式

### 检查-然后-执行

```python
# 竞态条件
if not file.exists():
    file.write(data)  # 可能已被另一个进程创建

# 原子操作
try:
    with open(path, 'xb') as f:  # 排他性创建
        f.write(data)
except FileExistsError:
    handle_conflict()
```

### 读取-修改-写入

```python
# 竞态条件
counter = Counter.objects.get(id=1)
counter.value += 1  # 两个请求可能读到相同的值
counter.save()

# 原子更新
Counter.objects.filter(id=1).update(value=F('value') + 1)

# 乐观锁
counter = Counter.objects.get(id=1)
counter.value += 1
counter.save(update_fields=['value'])  # 需要版本字段检查
```

### 双重检查锁定

```java
// 错误实现（可见性问题）
if (instance == null) {
    synchronized (lock) {
        if (instance == null) {
            instance = new Singleton();
        }
    }
}

// 正确实现（volatile）
private volatile Singleton instance;
```

---

## 2. 并发原语选择

### 锁类型

| 类型 | 适用场景 | 注意事项 |
|------|----------|----------|
| Mutex | 单个资源的互斥访问 | 避免死锁 |
| RLock | 可重入锁 | 同一线程可多次获取 |
| Semaphore | 限制并发数 | 注意释放顺序 |
| ReadWriteLock | 读多写少 | 避免写者饥饿 |
| SpinLock | 短时间等待 | CPU 消耗高 |

### 原子操作

```python
import threading

# 使用原子操作代替锁
counter = threading.AtomicLong(0)
counter.incrementAndGet()

# 无锁计数
from itertools import count
seq = count()
next(seq)  # 原子递增
```

### 线程安全集合

```python
from queue import Queue
from concurrent.futures import ThreadPoolExecutor

# 线程安全队列
queue = Queue()
queue.put(item)
item = queue.get()

# 列表不是线程安全的
items = []
items.append(item)  # 多线程下可能丢失数据
```

---

## 3. 数据库并发

### 事务隔离级别

| 隔离级别 | 脏读 | 不可重复读 | 幻读 |
|----------|------|-----------|------|
| Read Uncommitted | 是 | 是 | 是 |
| Read Committed | 否 | 是 | 是 |
| Repeatable Read | 否 | 否 | 是 |
| Serializable | 否 | 否 | 否 |

### 悲观锁

```python
# SELECT FOR UPDATE
with transaction.atomic():
    account = Account.objects.select_for_update().get(user=user)
    account.balance -= amount
    account.save()
```

### 乐观锁

```python
# 版本号检查
account = Account.objects.get(user=user)
account.balance -= amount
account.version += 1

rows = Account.objects.filter(
    id=account.id,
    version=account.version - 1  # 检查版本
).update(
    balance=account.balance,
    version=account.version
)

if rows == 0:
    raise ConcurrentModificationError("数据已被修改")
```

---

## 4. 分布式并发

### 分布式锁

```python
import redis
from redis.lock import Lock

client = redis.Redis()

# 带超时的分布式锁
lock = client.lock('resource_name', timeout=30)
if lock.acquire(blocking=True, timeout=10):
    try:
        # 临界区操作
        pass
    finally:
        lock.release()
```

### 幂等性设计

```python
def process_order(order_id: str):
    # 使用唯一键保证幂等性
    with redis.lock(f'order:{order_id}'):
        order = Order.objects.get(id=order_id)
        if order.status == 'processed':
            return  # 已处理，直接返回

        # 处理订单
        order.status = 'processed'
        order.save()
```

---

## 5. 死锁预防

### 死锁的四个必要条件

1. 互斥
2. 持有并等待
3. 不可抢占
4. 循环等待

### 预防策略

```python
# 按固定顺序获取锁
def transfer(from_account, to_account, amount):
    accounts = sorted([from_account, to_account], key=lambda a: a.id)
    with lock(accounts[0]), lock(accounts[1]):
        # 转账操作
        pass

# 使用超时
lock.acquire(timeout=5)

# 避免嵌套锁
# 重构代码以减少锁嵌套层级
```

---

## 6. 并发检测清单

### 静态检查

```
共享变量是否同步？
检查-然后-执行模式是否原子？
读取-修改-写入操作是否加锁？
锁获取顺序是否一致？
是否存在锁泄漏（获取但未释放）？
异常处理中是否释放锁？
```

### 运行时检查

```
并发测试覆盖？
压力测试验证？
使用线程检测工具（ThreadSanitizer）？
死锁检测工具（JConsole、pprof）？
```

---

## 7. 常见陷阱

### 延迟初始化

```python
# 非线程安全
class Singleton:
    _instance = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()  # 多个线程可能创建多个实例
        return cls._instance

# 线程安全
import threading

class Singleton:
    _instance = None
    _lock = threading.Lock()

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls()
        return cls._instance
```

### 发布-逃逸

```java
// this 逃逸
public class Example {
    public Example() {
        new Thread(() -> use(this)).start();  // 构造完成前 this 已发布
    }
}

// 安全发布
public class Example {
    public static Example create() {
        Example e = new Example();
        // 构造完成后发布
        register(e);
        return e;
    }
}
```

---

## 参考

- [edge-cases.md](edge-cases.md) —— 边界情况处理
- [../commands/correctness.md](../commands/correctness.md) —— 正确性审查命令
