# Design Pattern Review Guide

## Creational Patterns

### Factory Pattern

**When to Use**

- Creating objects with complex initialization
- Need to delegate object creation to subclasses
- Want to decouple object creation from usage

**Review Checklist**

- [ ] Factory returns interface type, not concrete
- [ ] Creation logic encapsulated
- [ ] Easy to add new product types
- [ ] No direct object instantiation in client code

**Code Smell Detection**

`if type == 'A': obj = ClassA() elif type == 'B': obj = ClassB()` → Use Factory pattern

### Builder Pattern

**When to Use**

- Object has many optional parameters
- Construction process has multiple steps
- Want immutable objects with many attributes

**Review Checklist**

- [ ] Builder returns fully constructed object
- [ ] Fluent interface supported
- [ ] Validation in build() method
- [ ] Immutable result object

### Singleton Pattern

**When to Use**

- Exactly one instance needed
- Global access point required
- Resource sharing (connection pools, caches)

**Review Checklist**

- [ ] Thread-safe implementation
- [ ] Private constructor
- [ ] Lazy or eager initialization appropriate
- [ ] Consider if DI container preferred

**Warning Signs**

```
[ ] Used for convenience, not necessity
[ ] Holds mutable state
[ ] Makes testing difficult
[ ] Hidden dependencies
```

## Structural Patterns

### Adapter Pattern

**When to Use**

- Integrate incompatible interfaces
- Wrap third-party libraries
- Legacy system integration

**Review Checklist**

- [ ] Adapts interface, not implementation
- [ ] Client code unchanged
- [ ] Single responsibility maintained
- [ ] No excessive wrapping

### Decorator Pattern

**When to Use**

- Add responsibilities dynamically
- Avoid class explosion from combinations
- Extend functionality without inheritance

**Review Checklist**

- [ ] Decorator implements same interface
- [ ] Wraps and delegates to component
- [ ] Can stack multiple decorators
- [ ] Order of decorators matters and is documented

**Security Decorator Chain**

```
InputValidator -> Encryption -> Compression -> Audit -> BaseProcessor
```

### Facade Pattern

**When to Use**

- Simplify complex subsystems
- Provide unified interface
- Reduce coupling to subsystems

**Review Checklist**

- [ ] Provides simplified interface
- [ ] Does not add new functionality
- [ ] Subsystem remains accessible if needed
- [ ] Reduces client complexity

### Proxy Pattern

**When to Use**

- Control access to object
- Add security layer
- Lazy loading
- Remote object access

**Review Checklist**

- [ ] Proxy and real object share interface
- [ ] Access control implemented
- [ ] Transparent to client
- [ ] Performance benefit measurable

## Behavioral Patterns

### Strategy Pattern

**When to Use**

- Multiple algorithms for same task
- Need to switch algorithms at runtime
- Avoid complex conditional logic

**Review Checklist**

- [ ] Strategy interface well-defined
- [ ] Context delegates to strategy
- [ ] Strategies are interchangeable
- [ ] Easy to add new strategies

**Code Smell Detection**

`if algorithm == 'A': process_a(data) elif algorithm == 'B': process_b(data)` → Use Strategy pattern

### Observer Pattern

**When to Use**

- One-to-many dependency
- Objects need to know about state changes
- Event-driven architecture

**Review Checklist**

- [ ] Subject knows only about observer interface
- [ ] Observers can be added/removed dynamically
- [ ] Notification order not critical
- [ ] Memory leaks prevented (unsubscribe)

### Chain of Responsibility

**When to Use**

- Multiple handlers for request
- Handler determined at runtime
- Decouple sender from receivers

**Review Checklist**

- [ ] Each handler knows only about successor
- [ ] Chain can be configured dynamically
- [ ] Request can be handled or passed
- [ ] No handler is also valid outcome

**Security Chain Example**

```
Request -> Authentication -> Authorization -> Validation -> RateLimit -> Handler
```

### Command Pattern

**When to Use**

- Parameterize objects with operations
- Queue operations for later execution
- Support undo operations

**Review Checklist**

- [ ] Command encapsulates all needed info
- [ ] Invoker knows only command interface
- [ ] Receiver is encapsulated in command
- [ ] Supports undo if required

### Template Method Pattern

**When to Use**

- Common algorithm structure with variations
- Control subclass extension points
- Code reuse across subclasses

**Review Checklist**

- [ ] Template method is final
- [ ] Hook methods are protected
- [ ] Subclasses override only specific steps
- [ ] Invariant parts in base class

## Anti-Patterns to Detect

| Anti-Pattern | Detection signals | Fix |
|--------------|-------------------|-----|
| God Object | > 20 methods, > 10 instance vars, used everywhere | Apply SRP (Single Responsibility) |
| Spaghetti Code | Deep nesting (> 4), long methods (> 50 lines), global state, no structure | Extract methods, apply patterns |
| Copy-Paste Programming | Similar blocks in multiple places, minor variations only | Extract common code; inheritance/composition |
| Premature Optimization | Complex code for hypothetical perf, no profiling data | Profile first; optimize only proven bottlenecks |
| Magic Numbers/Strings | `if status == 3`, scattered `'admin'` literals | Use constants or enums |

## Pattern Selection Guide

| Problem                    | Primary Pattern         | Alternative             |
| -------------------------- | ----------------------- | ----------------------- |
| Object creation complexity | Factory                 | Builder                 |
| Need single instance       | Singleton               | DI Container            |
| Add behavior dynamically   | Decorator               | Chain of Responsibility |
| Simplify interface         | Facade                  | Adapter                 |
| Switch algorithms          | Strategy                | State                   |
| Event handling             | Observer                | Mediator                |
| Multi-step validation      | Chain of Responsibility | Decorator               |
| Undo operations            | Command                 | Memento                 |
| Template with variations   | Template Method         | Strategy                |

## Pattern Combination Examples

- **Web Request**: Facade (Controller) → Chain of Responsibility (Auth/Validation/Rate Limit) → Strategy (Business Logic) → Decorator (Logging/Caching/Tx)
- **Data Pipeline**: Builder (Config) → Chain of Responsibility (Transform Steps) → Strategy (Processing) → Observer (Progress)

## Review Priority: "Should-Have-Used-a-Pattern"

A missing pattern is itself a review finding — but only when the smell is real.
Default severities:

| Signal in code                                                              | Pattern called for                  | Severity             |
| --------------------------------------------------------------------------- | ----------------------------------- | -------------------- |
| `if type == 'A' … elif type == 'B' …` over types                            | Factory / Strategy / polymorphism   | High if > 3 branches |
| One class holds > 6 unrelated responsibilities                              | Facade + Extract Class              | High                 |
| Same algorithm copied with minor variation ≥ 3×                             | Template Method / Strategy          | Medium               |
| Long constructor, many optional params                                      | Builder                             | Medium               |
| Hand-rolled single instance via module global                               | Singleton, or (prefer) DI container | Low                  |
| Cross-cutting concern (logging/caching/auth) wired ad hoc at each call site | Decorator                           | Medium               |
| Subsystem called through a tangle of direct deps                            | Facade                              | Medium               |

**YAGNI guard**: do NOT flag a missing pattern when simple non-pattern code is
clearly sufficient. A 2-branch `if/else` does not need Strategy; a one-method
interface does not need Factory. The finding requires the smell to cross the
thresholds above — the Simplicity engine (Engine C) catches the opposite
failure (pattern introduced where none was needed).

## Code-Smell → Pattern Reverse Lookup

Review usually starts from a smell, not from "which pattern." Reverse-map:

| Smell (Fowler)       | Identification signal                        | Pattern to apply                       |
| -------------------- | -------------------------------------------- | -------------------------------------- |
| Long Method          | > 50 lines, or name contains "And"/"Or"      | Extract Method; Strategy for branching |
| Large Class          | > 300 lines, many unrelated fields           | Extract Class; Facade                  |
| Duplicate Code       | same block ≥ 3 places                        | Extract Method; Template Method        |
| Switch Statements    | type-switch repeated across codebase         | Strategy / State / Factory             |
| Parallel Hierarchies | adding a subclass forces additions elsewhere | Composition over inheritance           |
| Feature Envy         | method mostly uses another class's data      | Move Method                            |
| Data Class           | only getters/setters, no behavior            | Move behavior in; Observer for changes |
| Mysterious Name      | unclear name, magic numbers                  | Rename; Extract Constant               |

## Refactoring Priority (when multiple smells surface)

1. **Security / blocking defects first** (hardcoded creds, null paths,
   missing auth) — not a pattern concern, but it gates everything below.
2. **Duplication and long methods (Medium)** — highest leverage, lowest risk.
3. **Coupling / pattern introduction (Medium)** — do it when already touching
   the area; do not open a working module just to impose a pattern.
4. **Naming / clarity polish (Low)** — defer unless readability is the ask.

This ordering prevents pattern-driven refactors that churn working code to hit
an abstract ideal — see Engine C's Over-engineering Review for the deletion
counterpart.
