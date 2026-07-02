# 安全审查清单

## 1. 认证与授权

### 认证安全

- [ ] 密码存储使用强哈希算法（bcrypt、Argon2）
- [ ] 避免硬编码凭据
- [ ] 实施密码强度验证
- [ ] 支持多因素认证
- [ ] 会话管理使用安全 Cookie（HttpOnly、Secure、SameSite）
- [ ] 实施合理的会话超时

### 授权检查

- [ ] 实施最小权限原则
- [ ] 验证用户对资源的访问权限
- [ ] 防止水平越权
- [ ] 防止垂直越权
- [ ] API 端点有适当的授权检查

## 2. 输入验证

### 参数验证

- [ ] 验证所有用户输入
- [ ] 检查输入长度限制
- [ ] 验证输入类型
- [ ] 优先使用白名单验证而非黑名单
- [ ] 防止整数溢出
- [ ] 验证文件上传类型和大小

### SQL 注入防护

- [ ] 使用参数化查询
- [ ] 避免动态 SQL 拼接
- [ ] 使用 ORM 或查询构建器
- [ ] 存储过程使用参数

### NoSQL 注入防护

- [ ] 验证查询参数类型
- [ ] 避免使用 $where 操作符
- [ ] 使用 MongoDB 参数化查询

## 3. 输出编码

### XSS 防护

- [ ] HTML 上下文使用 HTML 编码
- [ ] JavaScript 上下文使用 JavaScript 编码
- [ ] URL 参数使用 URL 编码
- [ ] CSS 上下文使用 CSS 编码
- [ ] 使用内容安全策略（CSP）

### 敏感数据保护

- [ ] 不记录敏感数据
- [ ] 错误消息不暴露敏感数据
- [ ] API 响应不包含敏感字段
- [ ] 静态金融数据加密
- [ ] PII 数据脱敏

## 4. 加密处理

### 算法选择

- [ ] 使用强加密算法（AES-256、RSA-2048+）
- [ ] 避免已知不安全算法（MD5、SHA1、DES）
- [ ] 使用安全随机数生成器
- [ ] 正确实现加密模式（CBC、GCM）

### 密钥管理

- [ ] 不硬编码密钥
- [ ] 通过安全渠道获取密钥
- [ ] 实施密钥轮换策略
- [ ] 开发与生产密钥分离
- [ ] 使用密钥管理服务（KMS、Vault）

### 传输安全

- [ ] 使用 HTTPS（TLS 1.2+）
- [ ] 证书正确配置
- [ ] 防止降级攻击
- [ ] 配置 HSTS 头

## 5. 错误处理

### 错误消息

- [ ] 不暴露堆栈跟踪
- [ ] 记录详细错误信息
- [ ] 向用户提供通用错误消息
- [ ] 区分不同错误类型

### 异常处理

- [ ] 捕获具体异常
- [ ] 失败时清理资源
- [ ] 不吞掉关键异常
- [ ] 实施重试机制（指数退避）

## 6. 文件安全

### 文件上传

- [ ] 验证文件类型（MIME 和扩展名）
- [ ] 限制文件大小
- [ ] 重命名上传文件
- [ ] 存储在非可执行目录
- [ ] 扫描恶意软件

### 文件访问

- [ ] 防止路径遍历
- [ ] 验证文件路径在允许范围内
- [ ] 限制文件权限
- [ ] 不执行用户上传的文件

## 7. 业务逻辑

### 业务安全

- [ ] 防止金额溢出
- [ ] 订单状态机正确实现
- [ ] 防止重复提交
- [ ] 实施幂等性
- [ ] 验证码保护

### 竞态条件

- [ ] 使用事务
- [ ] 实施乐观/悲观锁
- [ ] 防止 TOCTOU 漏洞
- [ ] 原子化余额操作

## 8. API 安全

### REST API

- [ ] 使用适当的 HTTP 方法
- [ ] 实施限流
- [ ] CORS 正确配置
- [ ] API 版本管理
- [ ] 请求签名验证

### 认证方式

- [ ] JWT 安全配置（短过期时间）
- [ ] OAuth 2.0 正确实现
- [ ] API Key 轮换
- [ ] Refresh token 安全存储

## 9. 基础设施

### 配置安全

- [ ] 生产配置安全
- [ ] 禁用调试模式
- [ ] 安全的默认配置
- [ ] 配置加密存储

### 依赖安全

- [ ] 定期更新依赖
- [ ] 使用依赖扫描工具
- [ ] 已知漏洞已修复
- [ ] 最小化依赖数量

## 10. 日志与监控

### 日志

- [ ] 记录认证尝试
- [ ] 记录敏感操作
- [ ] 记录错误和异常
- [ ] 安全的日志存储
- [ ] 实施日志脱敏

### 监控与告警

- [ ] 异常检测
- [ ] 登录失败告警
- [ ] 性能异常告警
- [ ] 安全事件告警

---

## 代码示例：常见问题对比

### SQL 注入

```python
# 危险 - 字符串拼接
query = "SELECT * FROM users WHERE name = '" + username + "'"
cursor.execute(query)

# 安全 - 参数化查询
cursor.execute("SELECT * FROM users WHERE name = %s", (username,))
```

### 硬编码凭据

```python
# 危险
API_KEY = "sk-prod-abc123xyz"

# 安全
import os
API_KEY = os.environ["API_KEY"]   # 或从 KMS/Vault 读取
```

### 密码哈希

```python
# 危险
import hashlib
stored = hashlib.md5(password.encode()).hexdigest()

# 安全
import bcrypt
stored = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
```

### XSS 防护

```javascript
// 危险
element.innerHTML = userInput;

// 安全
element.textContent = userInput;
// 或使用 DOMPurify
element.innerHTML = DOMPurify.sanitize(userInput);
```

### IDOR 防护

```python
# 危险 - 无所有权验证
def get_order(order_id):
    return Order.objects.get(id=order_id)

# 安全 - 验证当前用户拥有该资源
def get_order(order_id, current_user):
    order = Order.objects.get(id=order_id)
    if order.user_id != current_user.id:
        raise PermissionDenied("访问被拒绝")
    return order
```

### Cookie 安全配置

```python
# 危险
response.set_cookie("session", token)

# 安全
response.set_cookie(
    "session", token,
    httponly=True,       # XSS 防护
    secure=True,         # 仅 HTTPS
    samesite="Strict",   # CSRF 防护
    max_age=3600,
)
```
