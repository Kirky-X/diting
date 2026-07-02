# 可访问性审查命令

可访问性审查模式 —— WCAG 2.1 合规、键盘导航、屏幕阅读器支持

## 用法

```bash
review accessibility [target-path]
```

## 检查内容

### 1. WCAG 2.1 四大原则（POUR）

| 原则 | 检查清单 | 级别 |
|------|--------|------|
| **可感知（Perceivable）** | 图片 alt 文本、颜色对比度 4.5:1、字幕/文字版 | A/AA |
| **可操作（Operable）** | 键盘导航、可见焦点、无时间限制 | A/AA |
| **可理解（Understandable）** | 一致导航、清晰错误信息、lang 属性 | A/AA |
| **健壮（Robust）** | ARIA 正确、语义化 HTML、校验通过 | A/AA |

---

### 2. 键盘导航

```
所有交互元素可通过 Tab 访问
Tab 顺序遵循视觉/逻辑顺序
焦点样式可见（禁止 outline: none 而无替代方案）
跳过导航链接（Skip to main content）
无键盘陷阱（所有组件都能 Tab 离开）
快捷键不与辅助技术冲突
```

### 3. 屏幕阅读器

```
图片有 alt 属性（装饰性图片用 alt=""）
表单标签已关联（for/id 或 aria-labelledby）
ARIA 角色和属性正确
标题层级正确（h1 → h2 → h3，不跳级）
数据表有 <th> 和 scope
动态内容有 live region 通知（aria-live）
```

### 4. 颜色和对比度

```
文本对比度 ≥ 4.5:1（正常文本 < 18px）
文本对比度 ≥ 3:1（大文本 ≥ 18px 或 14px 加粗）
信息不仅通过颜色传达（图标、文字、图案）
链接与周围文本对比度 ≥ 3:1
焦点状态有可见指示（不仅是颜色变化）
```

### 5. 表单可访问性

```
每个输入有关联的标签
错误信息与字段关联（aria-describedby）
必填字段明确标记（required、aria-required 或 *）
autocomplete 属性正确（autocomplete）
校验错误可被屏幕阅读器感知
```

### 6. 媒体替代

```
音频有文字版
视频有字幕
视频有音频描述（如需要）
自动播放音视频有暂停控件
```

---

## 严重度映射

| 问题类型 | 严重度级别 |
|----------|----------|
| 无法通过键盘操作 | Critical |
| 对比度不足 | High |
| 缺少 alt 文本 | High |
| 表单无标签 | High |
| 标题跳级 | Medium |
| 缺少跳过链接 | Medium |
| ARIA 使用不当 | Medium |
| 缺少字幕/文字版 | Medium |

---

## 常见模式

### 焦点管理（模态框）

```tsx
// 打开时移入焦点
useEffect(() => {
  if (isOpen) {
    firstFocusableRef.current?.focus();
  }
}, [isOpen]);

// 关闭时恢复焦点
const handleClose = () => {
  triggerElementRef.current?.focus();
  onClose();
};
```

### 可访问表单

```html
<div class="form-group">
  <label for="email">邮箱 <span aria-hidden="true">*</span></label>
  <input
    id="email"
    type="email"
    required
    aria-required="true"
    aria-describedby="email-error"
  />
  <span id="email-error" role="alert"></span>
</div>
```

### 跳过链接

```html
<a href="#main-content" class="skip-link">
  跳到主要内容
</a>
...
<main id="main-content">
```

---

## 参考

- [templates/feedback-examples.md](../templates/feedback-examples.md)
- [WCAG 2.1 快速参考](https://www.w3.org/WAI/WCAG21/quickref/)
- [MDN 可访问性指南](https://developer.mozilla.org/en-US/docs/Web/Accessibility)

## 相关命令

- [quality.md](quality.md)
- [testing.md](testing.md)
