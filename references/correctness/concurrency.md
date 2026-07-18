# Concurrency Correctness Guide

Concurrency Correctness — Race condition detection and concurrency patterns

## Overview

Concurrency issues are among the hardest problems to spot in code review. This document provides patterns for identifying common race conditions and correct concurrency handling methods.

---

## 1. Common Race Condition Patterns

### Check-Then-Act

```python
# Race condition
if not file.exists():
    file.write(data)  # May have been created by another process

# Atomic operation
try:
    with open(path, 'xb') as f:  # Exclusive creation
        f.write(data)
except FileExistsError:
    handle_conflict()
```

### Read-Modify-Write

```python
# Race condition
counter = Counter.objects.get(id=1)
counter.value += 1  # Two requests may read the same value
counter.save()

# Atomic update
Counter.objects.filter(id=1).update(value=F('value') + 1)

# Optimistic lock
counter = Counter.objects.get(id=1)
counter.value += 1
counter.save(update_fields=['value'])  # Requires version field check
```

### Double-Checked Locking

```java
// Incorrect implementation (visibility issue)
if (instance == null) {
    synchronized (lock) {
        if (instance == null) {
            instance = new Singleton();
        }
    }
}

// Correct implementation (volatile)
private volatile Singleton instance;
```

---

## 2. Concurrency Primitive Selection

### Lock Types

| Type | Use Case | Notes |
|------|----------|-------|
| Mutex | Mutual exclusion for a single resource | Avoid deadlocks |
| RLock | Reentrant lock | Same thread can acquire multiple times |
| Semaphore | Limit concurrency count | Be careful with release ordering |
| ReadWriteLock | Read-heavy, write-light workloads | Avoid writer starvation |
| SpinLock | Short wait times | High CPU consumption |

### Atomic Operations

```python
import threading

# Use atomic operations instead of locks
counter = threading.AtomicLong(0)
counter.incrementAndGet()

# Lock-free counting
from itertools import count
seq = count()
next(seq)  # Atomic increment
```

### Thread-Safe Collections

```python
from queue import Queue
from concurrent.futures import ThreadPoolExecutor

# Thread-safe queue
queue = Queue()
queue.put(item)
item = queue.get()

# Lists are NOT thread-safe
items = []
items.append(item)  # May lose data under multithreading
```

---

## 3. Database Concurrency

### Transaction Isolation Levels

| Isolation Level | Dirty Read | Non-Repeatable Read | Phantom Read |
|-----------------|------------|---------------------|--------------|
| Read Uncommitted | Yes | Yes | Yes |
| Read Committed | No | Yes | Yes |
| Repeatable Read | No | No | Yes |
| Serializable | No | No | No |

### Pessimistic Locking

```python
# SELECT FOR UPDATE
with transaction.atomic():
    account = Account.objects.select_for_update().get(user=user)
    account.balance -= amount
    account.save()
```

### Optimistic Locking

```python
# Version check
account = Account.objects.get(user=user)
account.balance -= amount
account.version += 1

rows = Account.objects.filter(
    id=account.id,
    version=account.version - 1  # Check version
).update(
    balance=account.balance,
    version=account.version
)

if rows == 0:
    raise ConcurrentModificationError("Data has been modified")
```

---

## 4. Distributed Concurrency

### Distributed Lock

```python
import redis
from redis.lock import Lock

client = redis.Redis()

# Distributed lock with timeout
lock = client.lock('resource_name', timeout=30)
if lock.acquire(blocking=True, timeout=10):
    try:
        # Critical section operations
        pass
    finally:
        lock.release()
```

### Idempotency Design

```python
def process_order(order_id: str):
    # Use unique key to ensure idempotency
    with redis.lock(f'order:{order_id}'):
        order = Order.objects.get(id=order_id)
        if order.status == 'processed':
            return  # Already processed, return immediately

        # Process the order
        order.status = 'processed'
        order.save()
```

---

## 5. Deadlock Prevention

### Four Necessary Conditions for Deadlock

1. Mutual exclusion
2. Hold and wait
3. No preemption
4. Circular wait

### Prevention Strategies

```python
# Acquire locks in a fixed order
def transfer(from_account, to_account, amount):
    accounts = sorted([from_account, to_account], key=lambda a: a.id)
    with lock(accounts[0]), lock(accounts[1]):
        # Transfer operation
        pass

# Use timeouts
lock.acquire(timeout=5)

# Avoid nested locks
# Refactor code to reduce lock nesting levels
```

---

## 6. Concurrency Detection Checklist

### Static Checks

```
Are shared variables synchronized?
Is the check-then-act pattern atomic?
Are read-modify-write operations locked?
Is lock acquisition order consistent?
Are there lock leaks (acquired but not released)?
Are locks released in exception handlers?
```

### Runtime Checks

```
Concurrency test coverage?
Stress testing verification?
Thread detection tools used (ThreadSanitizer)?
Deadlock detection tools (JConsole, pprof)?
```

---

## 7. Common Pitfalls

### Lazy Initialization

```python
# Not thread-safe
class Singleton:
    _instance = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()  # Multiple threads may create multiple instances
        return cls._instance

# Thread-safe
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

### Safe Publication

```java
// this escape
public class Example {
    public Example() {
        new Thread(() -> use(this)).start();  // this published before construction completes
    }
}

// Safe publication
public class Example {
    public static Example create() {
        Example e = new Example();
        // Published after construction completes
        register(e);
        return e;
    }
}
```

---

## References

- [edge-cases.md](edge-cases.md) — Edge case handling
- [../commands/correctness.md](../commands/correctness.md) — Correctness review commands
