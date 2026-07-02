# 批量审查

批量审查多个文件。

## 用法

```bash
review batch ./src ./tests
review batch --pattern "**/*.ts"
```

## 审查方法

1. 逐文件审查
2. 交叉引用检查
3. 依赖分析

## 输出

- 按文件列出问题
- 按严重度分组
- 总体评估
