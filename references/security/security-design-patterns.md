# Security Design Patterns

> Security-specific pattern catalog (architecture / design / implementation three layers).
> For "GoF patterns with security wrappers" (Secure Singleton, Secure
> Factory templates, etc.), see [pattern-classification.md](pattern-classification.md)
> — that is a different dimension. This file is an independent security pattern
> system (Single Access Point, Check Point, Pathname Canonicalization, RAII...).

## Three-Layer Overview

| Layer               | Concerns                                     | Patterns                                                                                                                      |
| ------------------ | ------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------- |
| **Architecture**   | Trust boundaries, system topology           | Single Access Point, Check Point, Distrustful Decomposition, Separation of Privilege, Defer to Kernel                         |
| **Design**         | Component interaction, responsibility splitting | Secure Factory, Secure Policy Factory, Secure Chain of Responsibility, Secure State Machine, Secure Visitor, Protection Proxy |
| **Implementation** | Point defense, code details           | Input Validation, Secure Logging, Clear Sensitive Information, Pathname Canonicalization, Secure Directory, RAII              |

Rule of thumb: failures at a higher layer cannot be compensated by lower layers —
an architectural gap cannot be fixed by adding input validation.

---

## Architecture-Layer Patterns

### Single Access Point

- **Intent**: All external access flows through one monitorable entry point.
- **When to use**: The system has multiple entry paths (HTTP + CLI + queue + cron)
  and needs to enforce consistent authentication/audit/rate-limiting.
- **Audit signals**: Auth checks duplicated across multiple controllers; an entry path
  bypasses logging; `@login_required` scattered on every handler instead of
  gateway/filters.
- **Counter-signal**: "We added a new internal endpoint and forgot to protect it."

### Check Point

- **Intent**: Insert security checks at well-defined interaction points rather than
  scattering them throughout business logic.
- **When to use**: Cross-cutting concerns (authentication, rate limiting, input validation,
  auditing) must run in a known order before the handler.
- **Audit signals**: Security logic mixed into business methods; "trusted" internal calls skip
  checks; order-dependent checks (auth before rate limiting?)
  have no enforced ordering.

### Distrustful Decomposition

- **Intent**: Split the system into mutually distrustful components;
  compromising one component does not cascade.
- **When to use**: Processing untrusted input alongside privileged operations; parsers,
  network listeners, plugin hosts.
- **Audit signals**: "Low-trust" components hold the same credentials as
  core; parser failures bubble up to privileged operations; no privilege boundary
  between frontend and backend in the same process.

### Separation of Privilege

- **Intent**: Security-critical operations require two or more components/roles
  to agree; no single point of control.
- **When to use**: Sensitive operations — fund transfers, key release, privilege
  grants, production deployments.
- **Audit signals**: A single service/account can independently complete an entire sensitive operation;
  "admin" role bundles all powerful permissions into a single grant.
- **Note**: Pair with Least Privilege — Separation splits permissions, Least
  Privilege minimizes each share.

### Defer to Kernel

- **Intent**: For check-time/use-time (TOCTOU) and access control
  decisions, delegate to the OS kernel rather than simulating in application code.
- **When to use**: File access by user identity, setuid-style privilege,
  reopening files after verification.
- **Audit signals**: Application code does `access(path, R_OK)` then `open(path)` —
  classic TOCTOU; hand-rolled permission checks the kernel already enforces.

---

## Design-Layer Patterns

### Secure Factory

- **Intent**: Create security-related objects in a controlled manner so that
  half-configured or inconsistent instances cannot exist.
- **When to use**: Constructing encryption contexts, authentication policy chains, policy
  objects — misconfiguration itself is a vulnerability.
- **Audit signals**: Security configuration assembled field-by-field in caller code
  (`ctx.setAlgorithm(...); ctx.setKey(...)` — what if one is missed?).

### Secure Policy Factory

- **Intent**: Select security policies from a closed, audited set based on context (environment, tenant, role)
  — never assembled ad hoc.
- **When to use**: Different policies for production/staging/testing, or per-tenant
  isolation rules.
- **Audit signals**: Policies constructed from loose flags/strings rather than
  a fixed enumeration; development policy accidentally available in production.

### Secure Chain of Responsibility

- **Intent**: Order security checks into a chain where each stage can reject;
  the chain is the only path to the handler.
- **When to use**: Multi-stage request validation (authentication → authorization → input check →
  rate limiting → audit → handler).
- **Audit signals**: Any check can be bypassed by calling the handler directly;
  ordering not enforced (rate limiting before authentication leaks user existence).

### Secure State Machine

- **Intent**: Model security-related lifecycles (sessions, accounts, orders) as
  explicit states with guarded transitions; disallowed transitions throw exceptions.
- **When to use**: Login attempts with locking, session lifecycles, payment
  states, account verification.
- **Audit signals**: States held as loose booleans (`isLocked`, `isActive`,
  `isVerified`) that can be combined into illegal configurations; no default-deny
  transition rule.

### Secure Visitor

- **Intent**: Apply security operations across heterogeneous object trees
  without polluting every element's interface.
- **When to use**: ACL traversal, configuration tree auditing, mixed
  record-type masking.
- **Audit signals**: Each domain class has its own `checkPermission` /
  `redact` method — security logic smeared across domain code.

### Protection Proxy

- **Intent**: The proxy object enforces access control before delegating to
  the real subject.
- **When to use**: Deferred authentication on sensitive resources, per-call authorization,
  audit-wrapped access.
- **Audit signals**: Client calls sensitive object directly; authentication only done at
  construction but object lifetime exceeds credentials.

---

## Implementation-Layer Patterns

### Input Validation

- **Intent**: Validate at every trust boundary; reject first, then sanitize, never
  sanitize only.
- **When to use**: Any data crossing a trust boundary (HTTP, files, queues, IPC).
- **Audit signals**: Validation only on the "happy" path; `try/except: pass`
  wrapping parsing; no whitelist where one is available.
- **Boundary rule**: Validate once at the boundary, trust internally — do not
  re-validate the same value five times up the call stack.

### Secure Logging

- **Intent**: Record security-relevant events for audit/forensics — without
  leaking keys or being forgeable.
- **When to use**: Authentication events, permission changes, access denials, configuration
  changes, suspicious traffic signals.
- **Audit signals**: Logs contain keys/PII (`password=...`, full tokens, PANs);
  logs writable by the same subject they audit; audit logs lack
  tamper-protection; successes unrecorded enabling repudiation.

### Clear Sensitive Information

- **Intent**: Zero/overwrite keys as soon as they are no longer needed —
  in memory, in buffers, in logs, in error messages.
- **When to use**: Encryption keys, passwords, tokens, decrypted plaintext, session
  keys.
- **Audit signals**: Keys stored in long-lived fields/strings and never
  cleared; exception messages contain keys; debug dumps
  include request bodies with credentials.

### Pathname Canonicalization

- **Intent**: Resolve paths to their canonical absolute form before any
  whitelist/prefix check, defeating `..`, symlinks, and case
  tricks.
- **When to use**: Any code opening files from user-influenced input.
- **Audit signals**: `if path.startswith(base_dir)` without first `realpath`/
  `canonicalize`; user input string-concatenated into filesystem paths.

### Secure Directory

- **Intent**: Place sensitive files in restricted directories owned by the correct principal
  so unauthorized users cannot read
  or race them.
- **When to use**: Temporary files, sockets, disk keys, upload destinations.
- **Audit signals**: Temp files in world-readable `/tmp`; `mktemp` races;
  `chmod 777` to "fix" permission errors.

### RAII / Try-with-Resources

- **Intent**: Bind resource lifetimes to scope so cleanup (close, zero, release)
  is never forgotten, even on exceptions.
- **When to use**: File handles, sockets, encryption contexts, locks, DB
  transactions.
- **Audit signals**: Manual `close()` without `finally`/context managers;
  locks released only on normal path; resources held across throwable
  awaitables.

---

## Security Principles → Pattern Mapping

| Principle                | Patterns That Implement It                                                     |
| ------------------------ | ---------------------------------------------------------------------------- |
| Least Privilege          | Separation of Privilege, Check Point, Protection Proxy, Secure State Machine |
| Separation of Duties     | Distrustful Decomposition, Separation of Privilege                           |
| Defense in Depth         | Single Access Point → Check Point → Input Validation (layered)               |
| Secure by Default        | Secure State Machine (default-deny state), Clear Sensitive Information       |
| Fail Secure              | Secure Chain of Responsibility (any stage can reject), Secure State Machine  |
| Economy of Mechanism     | Single Access Point, Secure Factory (fewer ways to misbuild)                |
| Weakest Link             | Secure Logging (makes the weak link observable)                               |

## Threats (STRIDE) → Pattern Selection

| Threat                     | Primary Pattern                                                         |
| -------------------------- | ------------------------------------------------------------------------ |
| **S**poofing               | Single Access Point + Auth Check Point + Protection Proxy                |
| **T**ampering              | Input Validation + Pathname Canonicalization + Secure State Machine      |
| **R**epudiation            | Secure Logging (write-side audit, tamper-proof)                          |
| **I**nformation Disclosure | Clear Sensitive Information + Separation of Privilege + Secure Directory |
| **D**enial of Service      | Check Point (rate limiting) + Distrustful Decomposition (isolation)      |
| **E**levation of Privilege | Separation of Privilege + Least Privilege + Secure State Machine         |

## "Should Have Used This Pattern" Audit Signals (Default Severity)

| Code Smell in Audit                                | Missing Pattern                   | Severity |
| --------------------------------------------------- | --------------------------------- | -------- |
| Multiple unguarded entry points, inconsistent auth  | Single Access Point / Check Point | High     |
| Security config assembled field-by-field, skippable | Secure Factory                    | Medium   |
| Loose booleans forming illegal security states      | Secure State Machine              | High     |
| `path.startswith(prefix)` without canonicalization  | Pathname Canonicalization         | High     |
| Keys in long-lived strings, never cleared           | Clear Sensitive Information       | High     |
| Temp files in shared `/tmp`                         | Secure Directory                  | Medium   |
| Audit logs writable by audited subject              | Secure Logging                    | High     |
| `access()` then `open()` on user path               | Defer to Kernel                   | High     |
| One role/account can complete critical ops alone    | Separation of Privilege           | High     |

## Adoption Workflow (Audit-Oriented)

1. **Identify threats** — do STRIDE on each trust boundary/entry point.
2. **Match patterns** — select from the tables above; prioritize architecture-layer
   over implementation-layer.
3. **Integrate** — patterns at boundaries, not smeared over business logic.
4. **Verify** — confirm checks cannot be bypassed via alternative paths.
5. **Monitor** — Secure Logging covers what the patterns enforce.

## References

- [pattern-classification.md](pattern-classification.md) — GoF patterns with security wrappers
  (Secure Singleton template, Secure Decorator chains, etc.)
- [security-expert-guide.md](security-expert-guide.md) — Threat modeling
  process and complete audit workflow
- [security-fixes.md](security-fixes.md) — Concrete fix recipes per vulnerability category
- [../quality/security-checklist.md](../quality/security-checklist.md) —
  Pre-commit security checklist