# Decay Risks Reference

Six modes of software degradation. Apply the Iron Law to every finding.

---

## Risk 1: Cognitive Overload (R1)

**Diagnostic Question:** How much mental effort does this take for a human to understand?

Cognitive load beyond working memory capacity leads to mistakes, avoidance, and resistance to the refactoring that could fix it.

### Symptoms

- Functions over 20 lines with multiple abstraction levels mixed
- Nesting depth exceeding 3 levels
- Parameter lists with more than 4 parameters
- Magic numbers or unexplained constants
- Variable names that require reading the implementation to understand (e.g. `d`, `tmp2`, `flag`)
- Boolean expressions combining 3 or more conditions
- Train wreck chains: `a.getB().getC().doD()`
- Code names that don't match what the business calls the same concept
- Flag arguments: a boolean parameter that makes the function do two fundamentally different things depending on its value — indicating the function has two responsibilities
- Primitive obsession: domain concepts represented with primitive types (`String email`, `int orderId`, `double money`) instead of purpose-built value types — forcing callers to know which string is an email and which is a name
- Shallow module: a component whose interface or documentation is more complex than the functionality it provides

### Sources

| Symptom | Book | Principle / Smell |
|---------|------|-------------------|
| Long Method | Fowler — Refactoring | Long Method |
| Long Parameter List | Fowler — Refactoring | Long Parameter List |
| Message Chains | Fowler — Refactoring | Message Chains |
| Flag Arguments | Fowler — Refactoring | Flag Arguments |
| Primitive Obsession | Fowler — Refactoring | Primitive Obsession |
| Function length and nesting | McConnell — Code Complete | Ch. 7: High-Quality Routines |
| Variable naming | McConnell — Code Complete | Ch. 11: The Power of Variable Names |
| Magic numbers | McConnell — Code Complete | Ch. 12: Fundamental Data Types |
| Domain name mismatch | Evans — Domain-Driven Design | Ubiquitous Language |
| Shallow Module | Ousterhout — A Philosophy of Software Design | Ch. 4: Modules Should Be Deep |

### Severity Guide

- 🔴 Critical: Function > 50 lines, nesting > 5, or virtually no meaningful names
- 🟡 Warning: Function 20–50 lines, nesting 4–5, some unclear names
- 🟢 Suggestion: Minor naming issues, 1–2 magic numbers, isolated train wreck chain

### What Not to Flag

- Linear code with clear names and guard clauses is not automatically high cognitive load
- Internal implementation details hidden behind deep, simple module boundaries are not a shallow module issue
- Domain-specific terminology should not be flagged if it matches how experts actually talk

---

## Risk 2: Change Propagation (R2)

**Diagnostic Question:** How many unrelated things break when one thing is changed?

Every change wave that hits unrelated modules slows velocity and multiplies regression risk.

### Symptoms

- Modifying one feature requires touching more than 3 files in unrelated modules
- A class that changes for multiple different business reasons (e.g. `UserService` changes because of billing logic and notification logic and profile logic)
- A method that uses data from another class more than from its own class
- Two classes that directly know each other's internal state
- Changing one module requires recompiling or retesting many unrelated modules
- **Hyrum's Law**: With enough callers, every observable behavior — including implementation details, error message text, incidental call ordering, and undocumented side effects — becomes an implicit contract that callers depend on, even when the declared API never promised it
- **Orthogonality violation**: Changing one dimension of a feature forces edits in an unrelated dimension — adding a new payment type shouldn't require touching logging, caching, or notification code, but does in a non-orthogonal design
- Information leakage: A design decision (e.g., file format, protocol details, or data shape) is encoded in multiple modules, so modifying it requires coordinated edits in multiple places even though only one module "owns" the concept

### Sources

| Symptom | Book | Principle / Smell |
|---------|------|-------------------|
| Shotgun Surgery | Fowler — Refactoring | Shotgun Surgery |
| Divergent Change | Fowler — Refactoring | Divergent Change |
| Feature Envy | Fowler — Refactoring | Feature Envy |
| Inappropriate Intimacy | Fowler — Refactoring | Inappropriate Intimacy |
| Orthogonality violation | Hunt & Thomas — The Pragmatic Programmer | Ch. 2: Orthogonality |
| DIP violation | Martin — Clean Architecture | Dependency Inversion Principle |
| High change propagation radius | Brooks — The Mythical Man-Month | Ch. 2: Brooks's Law (communication overhead) |
| Hyrum's Law | Winters et al. — Software Engineering at Google | Ch. 1: Hyrum's Law |
| Information Leakage | Ousterhout — A Philosophy of Software Design | Ch. 5: Information Hiding and Leakage |

### Severity Guide

- 🔴 Critical: A single change touches > 5 files, or a structural DIP violation exists (domain depending on infrastructure)
- 🟡 Warning: A single change touches 3–5 files, moderate inter-module coupling
- 🟢 Suggestion: Mild coupling, easy to isolate

### What Not to Flag

- An assembly root wiring concrete dependencies is not a DIP violation by itself
- A stable public API with intentionally supported behavior is not automatically Hyrum's Law debt
- Similar edits within a single Bounded Context may be coordinated normal changes, not shotgun surgery

---

## Risk 3: Knowledge Duplication (R3)

**Diagnostic Question:** Is the same decision expressed in multiple places?

Multiple copies quietly diverge. DRY is about decisions, not lines of code.

### Symptoms

- Identical logic copy-pasted across multiple files or functions
- The same concept named differently in different parts of the codebase
  (e.g. `user`, `account`, `member`, `customer` all referring to the same domain entity)
- Parallel class hierarchies that must be changed in sync
  (e.g., adding a new payment type requires adding a class in 3 different hierarchies)
- Configuration values repeated as literals in multiple places
- Two modules independently implementing the same algorithm

### Sources

| Symptom | Book | Principle / Smell |
|---------|------|-------------------|
| Code duplication | Fowler — Refactoring | Duplicate Code |
| Parallel Inheritance | Fowler — Refactoring | Parallel Inheritance Hierarchies |
| DRY violation | Hunt & Thomas — The Pragmatic Programmer | DRY: Don't Repeat Yourself |
| Inconsistent naming | Evans — Domain-Driven Design | Ubiquitous Language |
| Alternative Classes | Fowler — Refactoring | Alternative Classes with Different Interfaces |

### Severity Guide

- 🔴 Critical: Core business logic duplicated across modules, or the same domain concept named 3+ different ways
- 🟡 Warning: Utility code duplication, inconsistent naming within a subsystem
- 🟢 Suggestion: Minor literal duplication, a single naming inconsistency

### What Not to Flag

- Duplication across independent Bounded Contexts is not automatically knowledge duplication
- Temporary duplication during active extraction or migration is not necessarily debt
- Shared protocol constants repeated at explicit boundaries may be acceptable when local ownership is clearer

---

## Risk 4: Accidental Complexity (R4)

**Diagnostic Question:** Is the code more complex than the problem it solves?

Accidental complexity accumulates one addition at a time until developers wrestle with scaffolding more than solving problems.

### Symptoms

- Abstractions built "for future use" with no current consumers
  (e.g., a plugin system built for a use case with only one known implementation)
- Classes that barely justify their existence (wrapping a single method call)
- Classes that only delegate to another class without adding behavior (pure middle men)
- A system's second attempt that is significantly more complex than the first,
  adding generality for requirements that don't yet exist
- Switch statements that represent a lack of polymorphism
- Configuration options that were never changed from their defaults
- Framework code that is larger than the application it drives
- Code growing under sustained tactical shortcuts: each workaround seems minor,
  but the accumulated shortcuts mean every new feature requires fighting existing structures

### Sources

| Symptom | Book | Principle / Smell |
|---------|------|-------------------|
| Speculative Generality | Fowler — Refactoring | Speculative Generality |
| Lazy Class | Fowler — Refactoring | Lazy Class |
| Middle Man | Fowler — Refactoring | Middle Man |
| Switch Statements | Fowler — Refactoring | Switch Statements |
| Second System Effect | Brooks — The Mythical Man-Month | Ch. 5: The Second-System Effect |
| YAGNI violations | McConnell — Code Complete | Ch. 5: Design in Construction |
| Over-engineering | Hunt & Thomas — The Pragmatic Programmer | Topic 4: Good-Enough Software |
| Tactical programming debt | Ousterhout — A Philosophy of Software Design | Ch. 3: Strategic vs. Tactical Programming |

### Severity Guide

- 🔴 Critical: An entire subsystem built around speculative requirements, or framework overhead dominating domain logic
- 🟡 Warning: Several unnecessary abstractions or wrapper classes, unused configuration systems
- 🟢 Suggestion: One or two lazy classes or middle man patterns in non-critical paths

### What Not to Flag

- Switch statements over external protocols, wire formats, or closed enumerations are not automatically a lack of polymorphism
- Thin wrappers that absorb vendor volatility or hide instability may be justified
- A larger second version is not a second-system effect unless the generality added exceeds current needs

---

## Risk 5: Dependency Disorder (R5)

**Diagnostic Question:** Do dependencies flow in a consistent, predictable direction?

When business logic depends on infrastructure, infrastructure changes cascade into domain changes. Cycles prevent isolation.

### Symptoms

- Circular dependencies between modules or packages
- High-level business logic importing directly from low-level infrastructure
  (e.g., a domain service importing a specific database driver)
- Stable, widely-used components depending on unstable, frequently-changing components
- Abstract components depending on concrete implementations
- Law of Demeter violation: `order.getCustomer().getAddress().getCity()`
- Module fan-out greater than 5 (imports from more than 5 other modules)
- A module implementing an interface but only using a subset of its methods, or having to provide stub implementations for methods it doesn't need (ISP violation: fat interfaces force callers to depend on methods they don't use)
- The system feels like "it wasn't designed by one mind" — different modules use incompatible architectural patterns with no clear rules about which applies where
- Direct version pinning on transitive packages (diamond dependency risk);
  upgrading one library requires coordination across multiple unrelated teams or repositories

### Sources

| Symptom | Book | Principle / Smell |
|---------|------|-------------------|
| Dependency cycles | Martin — Clean Architecture | Acyclic Dependencies Principle (ADP) |
| DIP violation | Martin — Clean Architecture | Dependency Inversion Principle (DIP) |
| Instability direction | Martin — Clean Architecture | Stable Dependencies Principle (SDP) |
| Abstraction mismatch | Martin — Clean Architecture | Stable Abstractions Principle (SAP) |
| ISP violation | Martin — Clean Architecture | Interface Segregation Principle (ISP) |
| Conceptual integrity | Brooks — The Mythical Man-Month | Ch. 4: Conceptual Integrity |
| Law of Demeter | Hunt & Thomas — The Pragmatic Programmer | Ch. 5: Decoupling and the Law of Demeter |
| SOLID violations | Martin — Clean Architecture | Single Responsibility, Open/Closed Principles |
| Diamond dependency / upgrade blockage | Winters et al. — Software Engineering at Google | Ch. 21: Dependency Management |

### Severity Guide

- 🔴 Critical: Dependency cycles exist, or the domain layer directly depends on the infrastructure layer
- 🟡 Warning: Several SDP or DIP violations but no cycles; conceptual inconsistency across modules
- 🟢 Suggestion: Mild Law of Demeter violations, slightly elevated fan-out in isolated modules

### What Not to Flag

- High fan-out in an orchestration layer or assembly root is not automatically disorder
- Adapter modules can depend on both domain and infrastructure when explicitly translating across boundaries
- A stable facade covering many leaf dependencies may be healthy if the dependency strategy is clear

---

## Risk 6: Domain Model Distortion (R6)

**Diagnostic Question:** Does the code faithfully represent the problem it is solving?

Code that doesn't match the business language forces mental translation. Over time it models patterns rather than the domain, and logic seeps into service layers.

### Symptoms

- Business logic scattered across service layers while domain objects have only getters and setters
  (anemic domain model)
- Code variables, class, or method names that don't match what business stakeholders call the concept
- Classes whose only purpose is holding data with no behavior (pure data bags)
- Subclasses that ignore or override most of the parent class behavior (Refused Bequest)
- Bounded Context boundaries crossed without any translation or Anti-Corruption Layer
- Methods that are more interested in another class's data than their own
  (domain logic in the wrong place)
- Subclasses that override most parent methods with incompatible behavior, or throw exceptions where the parent contract guarantees success
  (LSP violation: substitution breaks callers)
- Value objects treated as entities: concepts defined entirely by their attributes (e.g. Money,
  Email, Address) given mutable IDs and lifecycles rather than being replaced on change

### Sources

| Symptom | Book | Principle / Smell |
|---------|------|-------------------|
| Anemic Domain Model | Evans — Domain-Driven Design | Domain Model pattern |
| Ubiquitous Language drift | Evans — Domain-Driven Design | Ubiquitous Language |
| Bounded context violation | Evans — Domain-Driven Design | Bounded Context |
| Data Class | Fowler — Refactoring | Data Class |
| Refused Bequest | Fowler — Refactoring | Refused Bequest |
| Feature Envy | Fowler — Refactoring | Feature Envy |
| LSP violation | Martin — Clean Architecture | Liskov Substitution Principle (LSP) |

### Severity Guide

- 🔴 Critical: Domain logic is entirely in the service layer, domain objects are pure data bags with no behavior
- 🟡 Warning: Partial anemia, some naming inconsistency between code and domain language
- 🟢 Suggestion: Minor naming drift in non-core areas, isolated Feature Envy cases

### What Not to Flag

- CRUD-heavy workflows may legitimately use transaction scripts rather than rich domain objects
- DTOs, persistence records, and API payload models can legitimately be pure data
- Shared infrastructure vocabulary should not be mistaken for domain drift when the business model itself is simple
