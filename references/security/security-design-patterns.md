# Security Design Patterns

> Security-specific pattern catalog (architecture / design / implementation tiers).
> For "GoF patterns applied with a security wrapper" (Secure Singleton, Secure
> Factory templates, etc.) see [pattern-classification.md](pattern-classification.md)
> — that is a different axis. This file is the independent security-pattern
> system (Single Access Point, Check Point, Pathname Canonicalization, RAII…).

## Three Tiers at a Glance

| Tier               | Concern                                     | Patterns                                                                                                                      |
| ------------------ | ------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------- |
| **Architecture**   | Trust boundaries, system topology           | Single Access Point, Check Point, Distrustful Decomposition, Separation of Privilege, Defer to Kernel                         |
| **Design**         | Component interaction, responsibility split | Secure Factory, Secure Policy Factory, Secure Chain of Responsibility, Secure State Machine, Secure Visitor, Protection Proxy |
| **Implementation** | Single-point defense, code detail           | Input Validation, Secure Logging, Clear Sensitive Information, Pathname Canonicalization, Secure Directory, RAII              |

Rule of thumb: a higher tier failing cannot be compensated by lower tiers —
architecture gaps are not fixable by adding input validation.

---

## Architecture-Tier Patterns

### Single Access Point（单一访问点）

- **Intent**: All external access flows through one monitorable entry.
- **Use when**: A system has multiple entry paths (HTTP + CLI + queue + cron)
  and must enforce consistent auth/audit/rate-limit.
- **Review signal**: auth checks duplicated across controllers; some entry path
  bypasses logging; `@login_required` sprinkled per-handler instead of at a
  gateway/filter.
- **Anti-signal**: "we added a new internal endpoint and forgot to protect it."

### Check Point（检查点）

- **Intent**: Insert security checks at well-defined interaction points, not
  scattered through business logic.
- **Use when**: Cross-cutting concerns (auth, rate-limit, input validation,
  audit) must run in a known order before the handler.
- **Review signal**: security logic mixed into business methods; checks skipped
  on "trusted" internal calls; order-dependent checks (auth before rate-limit?)
  with no enforced ordering.

### Distrustful Decomposition（不信任分解）

- **Intent**: Split a system into components that do not trust each other;
  compromise of one component does not cascade.
- **Use when**: Handling untrusted input alongside privileged operations; a
  parser, a network listener, a plugin host.
- **Review signal**: a "low-trust" component holds the same credentials as the
  core; parser failures bubble up as privileged actions; no privilege boundary
  between front-end and back-end of the same process.

### Separation of Privilege（特权分离）

- **Intent**: A security-critical action requires two or more components/roles
  to agree; no single point of control.
- **Use when**: Sensitive operations — fund transfer, key release, privilege
  grant, prod deploy.
- **Review signal**: one service/account can do the whole sensitive operation
  alone; "admin" role bundles every powerful permission into one grant.
- **Note**: pairs with Least Privilege — Separation splits authority, Least
  Privilege minimizes each share.

### Defer to Kernel（推迟到内核）

- **Intent**: For time-of-check/time-of-use (TOCTOU) and access-control
  decisions, delegate to the OS kernel rather than emulating in app code.
- **Use when**: File access by user identity, setuid-style privilege,
  re-opening a file after validation.
- **Review signal**: app code checks `access(path, R_OK)` then `open(path)` —
  classic TOCTOU; hand-rolled permission checks the kernel already enforces.

---

## Design-Tier Patterns

### Secure Factory（安全工厂）

- **Intent**: Create security-relevant objects in a controlled way, so
  half-configured or inconsistent instances cannot exist.
- **Use when**: Constructing crypto contexts, auth strategy chains, policy
  objects whose mis-configuration is itself a vulnerability.
- **Review signal**: security config assembled field-by-field in caller code
  (`ctx.setAlgorithm(...); ctx.setKey(...)` — what if one is skipped?).

### Secure Policy Factory（安全策略工厂）

- **Intent**: Select a security policy based on context (env, tenant, role)
  from a closed, reviewed set — never assembled ad hoc.
- **Use when**: Different policies for prod/staging/test, or per-tenant
  isolation rules.
- **Review signal**: policy constructed from loose flags/strings instead of
  from a fixed enum; dev policy accidentally usable in prod.

### Secure Chain of Responsibility（安全责任链）

- **Intent**: Order security checks as a chain where each stage can reject;
  the chain is the only path to the handler.
- **Use when**: Multi-stage request validation (auth → authz → input check →
  rate-limit → audit → handler).
- **Review signal**: any check can be bypassed by calling the handler
  directly; order not enforced (rate-limit before auth leaks user existence).

### Secure State Machine（安全状态机）

- **Intent**: Model security-relevant lifecycles (session, account, order) as
  explicit states with guarded transitions; disallowed transitions throw.
- **Use when**: Login attempts with lockout, session lifecycle, payment
  states, account verification.
- **Review signal**: state held as loose booleans (`isLocked`, `isActive`,
  `isVerified`) that can be combined into illegal configurations; no default-
  deny transition rule.

### Secure Visitor（安全访问者）

- **Intent**: Apply a security operation across a heterogeneous object tree
  without polluting each element's interface with security logic.
- **Use when**: ACL traversal, audit over a config tree, redaction over mixed
  record types.
- **Review signal**: every domain class has its own `checkPermission` /
  `redact` method — security logic smeared across domain code.

### Protection Proxy（保护代理）

- **Intent**: A stand-in object enforces access control before delegating to
  the real subject.
- **Use when**: Lazy auth on sensitive resources, per-call authorization,
  audit-wrapped access.
- **Review signal**: clients call the sensitive object directly; auth done
  once at construction but the object outlives the credential.

---

## Implementation-Tier Patterns

### Input Validation（输入验证）

- **Intent**: Validate at every trust boundary; reject-then-sanitize, never
  sanitize-only.
- **Use when**: Any data crossing a trust boundary (HTTP, file, queue, IPC).
- **Review signal**: validation only on the "happy" path; `try/except: pass`
  around parsing; allowlist absent where allowlist is possible.
- **Boundary rule**: validate once at the boundary, trust internally — do not
  re-validate the same value five times through the call stack.

### Secure Logging（安全日志）

- **Intent**: Record security-relevant events for audit/forensics — without
  leaking secrets or being forgeable.
- **Use when**: Auth events, privilege changes, denied accesses, config
  changes, suspicious-traffic signals.
- **Review signal**: secrets/PII in logs (`password=...`, full tokens, PAN);
  logs writable by the same principal they audit; no tamper-evidence on
  audit logs; success not logged so repudiation is possible.

### Clear Sensitive Information（清除敏感信息）

- **Intent**: Zero/overwrite secrets the moment they are no longer needed —
  in memory, in buffers, in logs, in error messages.
- **Use when**: Crypto keys, passwords, tokens, decrypted plaintext, session
  secrets.
- **Review signal**: secrets held in long-lived fields/strings and never
  cleared; exceptions that include the secret in the message; debug dumps of
  request bodies containing credentials.

### Pathname Canonicalization（路径名规范化）

- **Intent**: Resolve a path to its canonical absolute form before any
  allowlist/prefix check, to defeat `..`, symlinks, and case-insensitivity
  tricks.
- **Use when**: Any code opens a file from user-influenced input.
- **Review signal**: `if path.startswith(base_dir)` without `realpath`/
  `canonicalize` first; user input joined into a filesystem path with string
  concatenation.

### Secure Directory（安全目录）

- **Intent**: Place sensitive files in a directory with restrictive
  permissions, owned by the right principal, so unrelated users cannot read
  or race them.
- **Use when**: Temp files, sockets, secrets on disk, upload destinations.
- **Review signal**: temp files in a world-readable `/tmp`; `mktemp` race;
  `chmod 777` to "fix" a permission error.

### RAII / Try-with-Resources（资源获取即初始化）

- **Intent**: Tie resource lifetime to scope so cleanup (close, zero, release)
  cannot be forgotten, even on exception.
- **Use when**: File handles, sockets, crypto contexts, locks, DB
  transactions.
- **Review signal**: manual `close()` without `finally`/context-manager;
  locks released on the happy path only; resource held across an awaitable
  that can throw.

---

## Security Principle → Pattern Mapping

| Principle                | Patterns that realize it                                                     |
| ------------------------ | ---------------------------------------------------------------------------- |
| Least Privilege          | Separation of Privilege, Check Point, Protection Proxy, Secure State Machine |
| Separation of Duties     | Distrustful Decomposition, Separation of Privilege                           |
| Defense in Depth         | Single Access Point → Check Point → Input Validation (layered)               |
| Secure by Default        | Secure State Machine (default-deny state), Clear Sensitive Information       |
| Fail Secure              | Secure Chain of Responsibility (any stage can reject), Secure State Machine  |
| Economy of Mechanism     | Single Access Point, Secure Factory (fewer ways to mis-build)                |
| Protect the Weakest Link | Secure Logging (make the weak link observable)                               |

## Threat (STRIDE) → Pattern Selection

| Threat                     | Primary patterns                                                         |
| -------------------------- | ------------------------------------------------------------------------ |
| **S**poofing               | Single Access Point + auth Check Point + Protection Proxy                |
| **T**ampering              | Input Validation + Pathname Canonicalization + Secure State Machine      |
| **R**epudiation            | Secure Logging (write-side audit, tamper-evident)                        |
| **I**nformation Disclosure | Clear Sensitive Information + Separation of Privilege + Secure Directory |
| **D**enial of Service      | Check Point (rate-limit) + Distrustful Decomposition (isolate)           |
| **E**levation of Privilege | Separation of Privilege + Least Privilege + Secure State Machine         |

## "Should-Have-Used-This" Review Signals (default severity)

| Code smell in review                                | Pattern missing                   | Severity |
| --------------------------------------------------- | --------------------------------- | -------- |
| Multiple unguarded entry points, inconsistent auth  | Single Access Point / Check Point | High     |
| Security config assembled field-by-field, skippable | Secure Factory                    | Medium   |
| Loose booleans forming illegal security states      | Secure State Machine              | High     |
| `path.startswith(prefix)` without canonicalize      | Pathname Canonicalization         | High     |
| Secrets held in long-lived strings, never cleared   | Clear Sensitive Information       | High     |
| Temp files in shared `/tmp`                         | Secure Directory                  | Medium   |
| Audit log writable by the audited principal         | Secure Logging                    | High     |
| `access()` then `open()` on user path               | Defer to Kernel                   | High     |
| One role/account can complete a critical op alone   | Separation of Privilege           | High     |

## Adoption Workflow (review-facing)

1. **Identify threats** — STRIDE over each trust boundary / entry point.
2. **Match patterns** — pick from the tables above; prefer architecture-tier
   before implementation-tier.
3. **Integrate** — patterns at boundaries, not smeared through business logic.
4. **Verify** — confirm the check cannot be bypassed by an alternate path.
5. **Monitor** — Secure Logging covers what the patterns enforce.

## References

- [pattern-classification.md](pattern-classification.md) — GoF patterns with
  security wrappers (Secure Singleton template, Secure Decorator chain, etc.)
- [security-expert-guide.md](security-expert-guide.md) — threat modeling
  process and full review workflow
- [security-fixes.md](security-fixes.md) — concrete fix recipes per vuln class
- [../quality/security-checklist.md](../quality/security-checklist.md) —
  pre-commit security checklist
