# F9 — Compact Errors into Context Window (detect, strong)

**Principle**: Push tool-failure errors (via `format_error`) into the context window
as events so the LLM self-heals. Use a `consecutive_errors` counter to cap retries
(~3 per tool), then break/escalate to a human.

## Detect (grep the target)

Good signal (highly specific, low false-positive):
- `consecutive_errors` / `consecutive_errors = 0` / `consecutive_errors += 1`
- `consecutive_errors < 3` (capped retry)
- `format_error(` / `format_error(e)`
- error event appended: `"type": 'error'` / `"type": "error"` into thread/events
- `except Exception as e:` that appends error to thread (not swallow, not bare raise)

Bad signal:
- bare `except Exception: pass` / `except: pass` (swallow)
- errors raised to terminate with no retry/self-heal
- retry loop with no cap (spin-out risk)

## Anti-pattern
Swallowing errors silently, or letting them terminate the agent — instead of
folding `format_error(e)` into the context so the LLM can recover.

## Ref
`../content/factor-09-compact-errors.md` §"9. Compact Errors into Context Window"

## Finding level
HIGH on bare `except: pass` swallow, or retry with no cap.
MID if errors raised but not folded into context for self-heal.
`consecutive_errors` + `format_error` present = clean (no finding).
