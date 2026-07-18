---
books:
  - The Mythical Man-Month
  - Code Complete
  - Refactoring
  - Clean Architecture
  - The Pragmatic Programmer
  - Domain-Driven Design
  - A Philosophy of Software Design
  - Software Engineering at Google
  - xUnit Test Patterns
  - The Art of Unit Testing
  - Working Effectively with Legacy Code
  - How Google Tests Software
---

# Source Coverage Matrix

Use this file after selecting a mode and before writing findings.
It exists to prevent shallow "book-title-drop" reviews.

## Review Discipline

- Only cite a book when the observed symptoms actually match that book's principles.
- Threshold crossings are signals, not conclusions. Check context, intent, and blast radius.
- Look for legitimate trade-offs before flagging a smell as debt.
- Prefer concrete architectural or domain consequences over abstract style complaints.
- If two books pull in different directions, state the trade-off rather than pretending there's no tension.

---

## Frederick Brooks — *The Mythical Man-Month*

**Contemporary Manifestations**
- Change propagation as communication overhead
- Second-system effect
- Conceptual integrity

**Do Not Miss**
- Whether the design shows a single coherent idea or competing local optimizations
- Whether cross-team coordination costs are becoming part of feature costs

**Do Not Over-Flag**
- Large systems are not automatically second systems
- Multi-module designs are acceptable when they preserve conceptual integrity

---

## Steve McConnell — *Code Complete*

**Contemporary Manifestations**
- Routine length, nesting, naming, and magic numbers
- Build-phase YAGNI checks
- Defensive programming and error handling discipline (guard clauses, input validation,
  explicit error paths, assertions on invariants)

**Do Not Miss**
- Whether low-level readability choices compound into operational risk
- Whether missing error handling makes failure modes invisible to maintainers

**Do Not Over-Flag**
- Small, explicit guard clauses are not cognitive overload
- Long routines may be acceptable when they are linear, well-named, and single-purpose

---

## Martin Fowler — *Refactoring*

**Contemporary Manifestations**
- Long Method, Long Parameter List, Message Chains
- Shotgun Surgery, Divergent Change, Feature Envy, Inappropriate Intimacy
- Duplicate Code, Speculative Generality, Lazy Class, Middle Man, Data Class
- Flag Arguments: a boolean parameter that splits a function into two behaviors
- Primitive Obsession: domain concepts represented with primitives instead of value types

**Do Not Miss**
- Whether code smells are local or systemic
- Whether the refactoring target has a natural home in the model

**Do Not Over-Flag**
- Temporary duplication during active extraction is not always debt
- Data-focused structures are acceptable when intentionally serving as DTOs or boundary records

---

## Robert C. Martin — *Clean Architecture*

**Contemporary Manifestations**
- DIP, ADP, SDP, SAP, and layering direction
- ISP: fat interfaces that force callers to depend on methods they don't use
- LSP: subclasses that break the parent type's behavioral contract
- SRP and OCP: classes with multiple reasons to change; modules closed for modification but open for extension
  (via abstractions)

**Do Not Miss**
- Policy vs. detail boundaries
- Whether dependency arrows preserve replaceability and testability

**Do Not Over-Flag**
- Assembly roots can legitimately depend on concrete infrastructure by design
- Thin adapter layers can import both ways when explicitly serving as boundary glue

---

## Andrew Hunt & David Thomas — *The Pragmatic Programmer*

**Contemporary Manifestations**
- Orthogonality
- DRY
- Law of Demeter

**Do Not Miss**
- Whether knowledge duplication is truly duplicated decision-making
- Whether coupling is accidental or deliberate local simplification

**Do Not Over-Flag**
- Similar code in different Bounded Contexts is not automatically a DRY violation
- Direct object access within a cohesive aggregate is not always a Law of Demeter issue

---

## Eric Evans — *Domain-Driven Design*

**Contemporary Manifestations**
- Ubiquitous Language
- Bounded Contexts
- Anemic Domain Model
- Entity vs. Value Object: objects with identity and lifecycle vs. objects defined entirely by their attributes
  (Money, Email, Address should be immutable value types, not mutable entities)
- Aggregate roots: who owns invariants; cross-aggregate access only through the root

**Do Not Miss**
- Aggregate boundaries, invariant ownership, and Anti-Corruption Layers
- Whether names match the business language experts use

**Do Not Over-Flag**
- CRUD-heavy workflows may legitimately use transaction scripts
- Thin entities are acceptable when the domain itself is simple

---

## John Ousterhout — *A Philosophy of Software Design*

**Contemporary Manifestations**
- Deep modules vs. shallow modules
- Strategic vs. tactical programming
- Information leakage: design decisions encoded in multiple modules creating
  change coupling even without explicit imports between them

**Do Not Miss**
- Interface complexity relative to hidden complexity
- Whether repeated tactical patches are raising long-term cognitive load
- Whether "helpers" expose internal design decisions callers shouldn't know about

**Do Not Over-Flag**
- Internal implementation complexity is acceptable when the interface stays simple
- Small wrappers are acceptable when they meaningfully absorb volatility

---

## Titus Winters, Tom Manshreck, Hyrum Wright — *Software Engineering at Google*

**Contemporary Manifestations**
- Hyrum's Law
- Dependency management and upgrade blockage
- Code sustainability: whether code can be maintained, migrated, and upgraded over years
  without heroic effort
- Backward compatibility: whether API changes preserve existing callers or force
  cross-organization coordination to upgrade

**Do Not Miss**
- Factual APIs created by observable behavior
- Maintenance costs of exposing too much surface area
- Whether the dependency graph allows independent upgrades over time

**Do Not Over-Flag**
- Stable public APIs are not debt when intentionally supported
- Fan-out alone is not disorder when the dependency strategy is explicit and governed

---

## Gerard Meszaros — *xUnit Test Patterns*

**Contemporary Manifestations**
- Assertion Roulette, Mystery Guest, General Fixture
- Eager Test, Lazy Test, Test Code Duplication, Behavior Verification
- Erratic Test: tests that produce non-deterministic results due to shared state,
  time dependencies, or ordering assumptions between tests

**Do Not Miss**
- Whether test failures are diagnosable
- Whether suite shape amplifies maintenance cost

**Do Not Over-Flag**
- Multiple assertions are acceptable when they express one behavior and one failure story
- Shared fixtures are acceptable when every field is relevant to the scenario

---

## Roy Osherove — *The Art of Unit Testing*

**Contemporary Manifestations**
- Test naming discipline
- Test isolation
- Mock usage guidelines
- Edge-path test completeness

**Do Not Miss**
- Whether tests verify behavior vs. wiring
- Whether seams are used to simplify tests, or whether production code is being warped for testability

**Do Not Over-Flag**
- Mocks are acceptable when dependencies are non-deterministic and assertions still verify behavior
- Naming conventions are guidelines; clarity is the goal

---

## Michael Feathers — *Working Effectively with Legacy Code*

**Contemporary Manifestations**
- Legacy code as code without tests
- Sensing and separation
- Seams
- Characterization tests

**Do Not Miss**
- Whether the team can safely change risk areas today
- Whether the code provides any seams for isolating behavior under change

**Do Not Over-Flag**
- Untested code is not automatically legacy if it's stable and not under active change
- Characterization tests are most important before modifying unclear existing behavior

---

## Google Engineering — *How Google Tests Software*

**Contemporary Manifestations**
- Change coverage vs. line coverage
- Pyramid shape and suite composition economics

**Do Not Miss**
- Whether the suite reflects business risk, not just percentages
- Whether expensive tests dominate the feedback loop

**Do Not Over-Flag**
- Non-70:20:10 ratios can be healthy when justified by platform constraints or product risk
- High coverage is useful when paired with meaningful branch and change protection
