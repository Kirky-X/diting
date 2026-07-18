# Accessibility Review Command

Accessibility Review Mode — WCAG 2.1 compliance, keyboard navigation, screen reader support

## Usage

```bash
review accessibility [target-path]
```

## Checklist

### 1. WCAG 2.1 Four Principles (POUR)

| Principle | Checklist | Level |
|-----------|-----------|-------|
| **Perceivable** | Image alt text, color contrast 4.5:1, captions/transcripts | A/AA |
| **Operable** | Keyboard navigation, visible focus, no time limits | A/AA |
| **Understandable** | Consistent navigation, clear error messages, lang attribute | A/AA |
| **Robust** | Correct ARIA, semantic HTML, validation passes | A/AA |

---

### 2. Keyboard Navigation

```
All interactive elements accessible via Tab
Tab order follows visual/logical order
Focus styles visible (no outline: none without alternative)
Skip navigation link (Skip to main content)
No keyboard traps (all components can be Tabbed out of)
Shortcuts don't conflict with assistive technology
```

### 3. Screen Reader

```
Images have alt attributes (decorative images use alt="")
Form labels are associated (for/id or aria-labelledby)
ARIA roles and attributes are correct
Heading hierarchy is correct (h1 → h2 → h3, no skipping)
Data tables have <th> and scope
Dynamic content has live region notifications (aria-live)
```

### 4. Color and Contrast

```
Text contrast ≥ 4.5:1 (normal text < 18px)
Text contrast ≥ 3:1 (large text ≥ 18px or 14px bold)
Information not conveyed by color alone (icons, text, patterns)
Link contrast with surrounding text ≥ 3:1
Focus states have visible indicators (not just color changes)
```

### 5. Form Accessibility

```
Each input has an associated label
Error messages associated with fields (aria-describedby)
Required fields clearly marked (required, aria-required, or *)
autocomplete attribute is correct (autocomplete)
Validation errors perceivable by screen readers
```

### 6. Media Alternatives

```
Audio has transcripts
Video has captions
Video has audio descriptions (if needed)
Auto-playing audio/video has pause controls
```

---

## Severity Mapping

| Issue Type | Severity Level |
|------------|---------------|
| Not operable via keyboard | Critical |
| Insufficient contrast | High |
| Missing alt text | High |
| Form without label | High |
| Heading level skipped | Medium |
| Missing skip link | Medium |
| Incorrect ARIA usage | Medium |
| Missing captions/transcripts | Medium |

---

## Common Patterns

### Focus Management (Modal)

```tsx
// Move focus in on open
useEffect(() => {
  if (isOpen) {
    firstFocusableRef.current?.focus();
  }
}, [isOpen]);

// Restore focus on close
const handleClose = () => {
  triggerElementRef.current?.focus();
  onClose();
};
```

### Accessible Form

```html
<div class="form-group">
  <label for="email">Email <span aria-hidden="true">*</span></label>
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

### Skip Link

```html
<a href="#main-content" class="skip-link">
  Skip to main content
</a>
...
<main id="main-content">
```

---

## References

- [templates/feedback-examples.md](../templates/feedback-examples.md)
- [WCAG 2.1 Quick Reference](https://www.w3.org/WAI/WCAG21/quickref/)
- [MDN Accessibility Guide](https://developer.mozilla.org/en-US/docs/Web/Accessibility)

## Related Commands

- [quality.md](quality.md)
- [testing.md](testing.md)
