# Accessibility Command

Accessibility review mode — WCAG 2.1 compliance, keyboard navigation, screen reader support

## Usage

```bash
review accessibility [target-path]
```

## What to Check

### 1. WCAG 2.1 Four Principles (POUR)

| Principle | Checklist | Level |
|------|--------|------|
| **Perceivable** | Image alt text, color contrast 4.5:1, captions/transcripts | A/AA |
| **Operable** | Keyboard navigation, visible focus, no time limits | A/AA |
| **Understandable** | Consistent navigation, clear error messages, lang attribute | A/AA |
| **Robust** | Correct ARIA, semantic HTML, validation passes | A/AA |

---

### 2. Keyboard Navigation

```
All interactive elements accessible via Tab
Tab order follows visual/logical order
Focus styles visible (outline: none prohibited without alternative)
Skip navigation links (Skip to main content)
No keyboard traps (can Tab away from all components)
Shortcuts don't conflict with assistive technology
```

### 3. Screen Readers

```
Images have alt attributes (decorative uses alt="")
Form labels associated (for/id or aria-labelledby)
ARIA roles and properties correct
Heading hierarchy correct (h1 → h2 → h3, no skipping)
Data tables have <th> and scope
Dynamic content has live region notifications (aria-live)
```

### 4. Color and Contrast

```
Text contrast ≥ 4.5:1 (normal text < 18px)
Text contrast ≥ 3:1 (large text ≥ 18px or 14px bold)
Information not conveyed by color alone (icons, text, patterns)
Link contrast with surrounding text ≥ 3:1
Focus state has visible indication (not just color change)
```

### 5. Form Accessibility

```
Each input has associated label
Error messages associated with fields (aria-describedby)
Required fields clearly marked (required, aria-required, or *)
Autocomplete attributes correct (autocomplete)
Validation errors perceivable by screen readers
```

### 6. Media Alternatives

```
Audio has text transcripts
Video has captions
Video has audio descriptions (if needed)
Autoplay audio/video has pause controls
```

---

## Severity Mapping

| Issue Type | Severity Level |
|----------|----------|
| Cannot operate via keyboard | Critical |
| Insufficient contrast | High |
| Missing alt text | High |
| Form without label | High |
| Heading skip level | Medium |
| Missing skip link | Medium |
| Incorrect ARIA usage | Medium |
| Missing captions/transcripts | Medium |

---

## Common Patterns

### Focus Management (Modal)

```tsx
// Move focus in when opened
useEffect(() => {
  if (isOpen) {
    firstFocusableRef.current?.focus();
  }
}, [isOpen]);

// Restore focus when closed
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