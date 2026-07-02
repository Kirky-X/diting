# API 审查

REST/GraphQL API 设计审查。

## 检查清单

### REST API
- URL 结构遵循 REST 约定
- HTTP 方法使用正确（GET/POST/PUT/DELETE）
- 状态码返回正确
- 版本管理策略
- 分页和过滤参数
- 错误响应格式一致性

### GraphQL
- Query/Mutation/Subscription 分离
- N+1 查询问题
- 认证和授权
- 限流策略

### 通用
- API 文档完整性
- 请求/响应示例
- 认证机制（OAuth、JWT、API Key）
