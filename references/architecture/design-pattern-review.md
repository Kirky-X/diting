# Design Pattern Review Guide

## Creational Patterns

### Factory Pattern

**When to Use**

- Creating objects with complex initialization
- Need to delegate object creation to subclasses
- Want to decouple object creation from usage

**Review Checklist**

- [ ] Factory returns interface type, not concrete type
- [ ] Creation logic is encapsulated
- [ ] Easy to add new product types
- [ ] Client code has no direct object instantiation

**Code Smell Detection**

`if type == 'A': obj = ClassA() elif type == 'B': obj = ClassB()` → Use Factory pattern

### Builder Pattern

**When to Use**

- Object has many optional parameters
- Construction process has multiple steps
- Want immutable objects with many attributes

**Review Checklist**

- [ ] Builder returns fully constructed object
- [ ] Supports fluent interface
- [ ] Validation in build() method
- [ ] Result object is immutable

### Singleton Pattern

**When to Use**

- Need exactly one instance
- Need a global access point
- Resource sharing (connection pool, cache)

**Review Checklist**

- [ ] Thread-safe implementation
- [ ] Private constructor
- [ ] Lazy or eager initialization is appropriate
- [ ] Consider whether DI container is preferred

**Warning Signs**

```
[ ] Used for convenience, not necessity
[ ] Holds mutable state
[ ] Makes testing difficult
[ ] Hides dependencies
```

## Structural Patterns

### Adapter Pattern

**When to Use**

- Integrating incompatible interfaces
- Wrapping third-party libraries
- Legacy system integration

**Review Checklist**

- [ ] Adapts interface, not implementation
- [ ] Client code unchanged
- [ ] Maintains single responsibility
- [ ] No over-wrapping

### Decorator Pattern

**When to Use**

- Dynamically adding responsibilities
- Avoiding class explosion from composition explosion
- Extending functionality without inheritance

**Review Checklist**

- [ ] Decorators implement the same interface
- [ ] Wraps and delegates to the component
- [ ] Multiple decorators can be stacked
- [ ] Decorator ordering is important and documented

**Secure Decorator Chain**

```
InputValidator -> Encryption -> Compression -> Audit -> BaseProcessor
```

### Facade Pattern

**When to Use**

- Simplifying complex subsystems
- Providing a unified interface
- Reducing coupling with subsystems

**Review Checklist**

- [ ] Provides simplified interface
- [ ] Does not add new functionality
- [ ] Subsystem is still accessible when needed
- [ ] Reduces client complexity

### Proxy Pattern

**When to Use**

- Controlling object access
- Adding security layer
- Lazy loading
- Remote object access

**Review Checklist**

- [ ] Proxy shares interface with real object
- [ ] Implements access control
- [ ] Transparent to client
- [ ] Performance benefit is measurable

## Behavioral Patterns

### Strategy Pattern

**When to Use**

- Same task with multiple algorithms
- Need to switch algorithms at runtime
- Avoiding complex conditional logic

**Review Checklist**

- [ ] Strategy interface is well-defined
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

- [ ] Subject only knows Observer interface
- [ ] Observers can be dynamically added/removed
- [ ] Notification order is not critical
- [ ] Prevents memory leaks (unsubscribe)

### Chain of Responsibility Pattern

**When to Use**

- A request has multiple handlers
- Handlers are determined at runtime
- Decoupling sender and receiver

**Review Checklist**

- [ ] Each handler only knows the successor
- [ ] Chain can be dynamically configured
- [ ] Request can be handled or passed
- [ ] No handler is also a valid outcome

**Security Chain Example**

```
Request -> Authentication -> Authorization -> Validation -> RateLimit -> Handler
```

### Command Pattern

**When to Use**

- Parameterizing objects with operations
- Queuing operations for later execution
- Supporting undo operations

**Review Checklist**

- [ ] Command encapsulates all required information
- [ ] Invoker only knows command interface
- [ ] Receiver is encapsulated in command
- [ ] Supports undo when needed

### Template Method Pattern

**When to Use**

- Generic algorithm structure with variants
- Controlling subclass extension points
- Code reuse across subclasses

**Review Checklist**

- [ ] Template method is final
- [ ] Hook methods are protected
- [ ] Subclasses only override specific steps
- [ ] Invariant parts are in base class

## Anti-Patterns to Detect

| Anti-Pattern | Detection Signal | Fix |
|--------------|-------------------|-----|
| God Object | > 20 methods, > 10 instance variables, used everywhere | Apply SRP (Single Responsibility) |
| Spaghetti Code | Deep nesting (> 4), long methods (> 50 lines), global state, no structure | Extract methods, apply patterns |
| Copy-Paste Programming | Similar code blocks in multiple places with only slight variations | Extract common code; inheritance/composition |
| Premature Optimization | Complex code for assumed performance, no profiling data | Profile first; only optimize proven bottlenecks |
| Magic Numbers/Strings | `if status == 3`, scattered `'admin'` literals | Use constants or enums |

## Pattern Selection Guide

| Problem                    | Primary Pattern         | Alternative             |
| -------------------------- | ----------------------- | ----------------------- |
| Complex object creation | Factory                 | Builder                 |
| Need single instance       | Singleton               | DI Container            |
| Dynamically add behavior   | Decorator               | Chain of Responsibility |
| Simplify interface         | Facade                  | Adapter                 |
| Switch algorithms          | Strategy                | State                   |
| Event handling             | Observer                | Mediator                |
| Multi-step validation      | Chain of Responsibility | Decorator               |
| Undo operations            | Command                 | Memento                 |
| Templates with variants    | Template Method         | Strategy                |

## Pattern Combination Examples

- **Web Request**: Facade (Controller) → Chain of Responsibility (Auth/Validation/Rate Limit) → Strategy (Business Logic) → Decorator (Logging/Caching/Tx)
- **Data Pipeline**: Builder (Config) → Chain of Responsibility (Transformation Steps) → Strategy (Processing) → Observer (Progress)

## Review Priority: "Should Have Used a Pattern"

Missing patterns are themselves review findings — but only when the code smell truly exists.
Default severity:

| Code Signal                                                              | Pattern to Use                  | Severity             |
| --------------------------------------------------------------------------- | ----------------------------------- | -------------------- |
| `if type == 'A' … elif type == 'B' …` branching by type                    | Factory / Strategy / Polymorphism   | High if > 3 branches |
| A class holds > 6 unrelated responsibilities                                | Facade + Extract Class              | High                 |
| Same algorithm with slight variations copied ≥ 3×                           | Template Method / Strategy          | Medium               |
| Long constructor with many optional parameters                              | Builder                             | Medium               |
| Manual singleton via module globals                                         | Singleton, or (preferred) DI container | Low              |
| Cross-cutting concerns (logging/caching/auth) wired ad-hoc at each call site | Decorator                           | Medium               |
| Subsystems tangled via direct dependencies                                  | Facade                              | Medium               |

**YAGNI Guard**: Do not flag missing patterns when simple non-pattern code is clearly sufficient. A 2-branch `if/else` does not need Strategy; a single-method interface does not need Factory. Findings require the smell to reach the above thresholds — the Simplification Engine (Engine C) catches the opposite failure (introducing patterns where they should not be introduced).

## Code Smells → Pattern Reverse Lookup

Reviews typically start from code smells, not from "which pattern to use." Reverse mapping:

| Code Smell (Fowler)       | Detection Signal                        | Pattern to Apply                       |
| -------------------- | -------------------------------------------- | -------------------------------------- |
| Long Method          | > 50 lines, or name contains "And"/"Or"      | Extract Method; branches use Strategy |
| Large Class          | > 300 lines, many unrelated fields           | Extract Class; Facade                  |
| Duplicate Code       | Same block ≥ 3 places                        | Extract Method; Template Method        |
| Switch Statements    | Type switch repeated across codebase         | Strategy / State / Factory             |
| Parallel Hierarchies | Adding a subclass forces changes elsewhere   | Composition over inheritance           |
| Feature Envy         | Method primarily uses another class's data   | Move Method                            |
| Data Class           | Only getter/setter, no behavior              | Move behavior in; Observer for changes |
| Mysterious Name      | Unclear name, magic numbers                  | Rename; Extract Constant               |

## Refactoring Priority (When Multiple Smells Coexist)

1. **Security / Blocking Defects First** (hardcoded credentials, null paths,
   missing auth) — not a pattern issue, but it gates everything else.
2. **Duplication & Long Methods (Medium)** — highest leverage, lowest risk.
3. **Coupling / Pattern Introduction (Medium)** — do while already changing the area; do not open working modules just to impose patterns.
4. **Naming / Clarity Polish (Low)** — defer unless readability is requested.

This ordering prevents pattern-driven refactoring that churns working code to hit abstract ideals — the opposite direction (removing patterns) is covered by Engine C's over-engineering review.
