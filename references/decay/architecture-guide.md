# Architecture Audit Guide — Mode 2

**Purpose:** Analyze a system's module and dependency structure, identifying architectural decay risks. Every finding must follow the Iron Law:
Symptom → Source → Consequence → Remedy.

**Monorepo note:** Treat each deployable service or library as a top-level module. Draw dependency edges between services, not between their internal packages. Apply Conway's Law checks at service ownership level. Within a single service, apply standard module-level analysis.

---

## Analysis Flow

Complete the following six steps in order.

### Step 0: Gather Codebase Context

Before drawing anything, confirm what you can see.

**If the user provided a full directory tree or pasted relevant file contents:** skip the active reading below and jump to Step 1.

**Otherwise, actively read the project using these tools:**

1. **Top-level structure** — identify module boundaries by globbing the top two levels:
   ```
   Glob: **/*(depth 2, directories only)
   ```
2. **Entry points** — read package manifests or main config files (e.g. `package.json`, `go.mod`, `pom.xml`, `Cargo.toml`, `pyproject.toml`) to confirm language, framework, and declared dependencies.
3. **Dependency edges** — discover inter-module calls by grepping import statements. Run once per language; cap at the first 200 matches to avoid token overflow:
   ```
   Grep: "^\s*(import|from|require\(|use )" across *.ts|*.py|*.go|*.rs|*.java
   ```
4. **Large modules** — for any top-level directory with > 10 files, read files matching `index.*`, `main.*`, or `__init__.*` to understand declared responsibilities.

**Stop when you can answer these three questions:**
- What are the top-level modules (names and count)?
- Which modules import from which other modules?
- Which module has the highest fan-in or fan-out?

If the project has > 100 top-level files or > 4 levels of nesting, note which areas are sampled rather than inferred, and annotate this in the report scope line.

### Step 1: Draw the Module Dependency Graph (Mermaid)

Before evaluating any risks, map dependencies as a Mermaid diagram. Use this format:

````mermaid
graph TD
  subgraph UI
    WebApp
    MobileApp
  end

  subgraph Domain
    AuthService
    OrderService
    PaymentService
  end

  subgraph Infrastructure
    Database
    MessageQueue
  end

  WebApp --> AuthService
  WebApp --> OrderService
  MobileApp --> AuthService
  MobileApp --> OrderService
  OrderService --> PaymentService
  OrderService --> Database
  OrderService --> MessageQueue
  PaymentService --> Database
  AuthService -.->|circular| OrderService

  classDef critical fill:#ff6b6b,stroke:#c92a2a,color:#fff
  classDef warning fill:#ffd43b,stroke:#e67700
  classDef clean fill:#51cf66,stroke:#2b8a3e,color:#fff

  class PaymentService critical
  class OrderService warning
  class Database,MessageQueue,AuthService,WebApp,MobileApp clean
````

Draw the graph structure first — nodes, subgraphs, and edges — without any `classDef` or `class` lines. You cannot assign colors until you complete the risk scan in Steps 2–4.

**After completing Step 4**, come back to this graph and add `classDef` and `class` lines based on findings. The example above shows the final colored output.

Rules:
1. **Nodes** — use top-level directories or services as nodes, not individual files
2. **Grouping** — one `subgraph` per architecture layer or top-level directory (e.g. UI, Domain, Infrastructure)
3. **Edges** — solid arrows (`-->`) from dependent module to dependency; circular dependencies use labeled dashed arrows (`-.->|circular|`). If no circular dependencies exist, use only solid arrows
4. **Node count cap** — max ~50 nodes in the graph; merge low-risk leaf modules into their parents if needed
5. **Fan-out** — for any node with fan-out > 5, use a descriptive label: `HighFanOutModule["ModuleName (fan-out: 7)"]`
6. **Colors** — apply `classDef` colors after completing Steps 2–4: `critical` (red `#ff6b6b`) for nodes with Critical findings, `warning` (yellow `#ffd43b`) for nodes with Warning findings, `clean` (green `#51cf66`) for nodes with no findings or only Suggestions. If there are no findings at all, classify all nodes as `clean`
7. **Orientation** — default to `graph TD` (top-down); use `graph LR` only when the architecture is clearly a left-to-right pipeline

### Step 2: Scan for Dependency Disorder

*Highest architectural impact risk — scan first.*

Look for:
- Circular dependencies (any `-.->|circular|` edge in the graph above)
- Upward-flowing arrows (high-level domain depending on low-level infrastructure)
- Stable, widely-depended-upon modules importing from frequently-changing modules
- Modules with fan-out > 5
- Absence of clear layering rules (no consistent answer to "what depends on what")

### Step 3: Scan for Domain Model Distortion

Look for:
- Do module names match business domain vocabulary?
- Is there a "services" layer that contains all business logic while domain objects are just plain data structures?
- Are there modules that cross Bounded Context boundaries (e.g., a user module containing billing logic)?
- Is there an Anti-Corruption Layer at the interface between external systems and the domain?

### Step 4: Scan for the Remaining Four Risks

Check each in turn:

**Knowledge Duplication:**
- Are there multiple modules independently implementing the same concept?
- Does the same domain concept appear under different names in different modules?

**Accidental Complexity:**
- Are there entire architecture layers that add no value?
- Are there modules whose responsibility cannot be stated in one sentence?

**Change Propagation:**
- Which modules are "blast radius hotspots"? (A change here requires changes in many other modules)
- Does the dependency graph reveal why certain features are slow to develop?

**Cognitive Overload:**
- Can each module's responsibility be stated in one sentence from its name alone?
- Would a new developer know which module to add a new feature to?

### Step 5: Testability Seam Assessment

A *seam* is a place in the architecture where behavior can be changed without editing source code — typically interfaces, configuration points, or dependency injection boundaries. Seam density is a proxy metric for testability and evolvability.

Scan for:
- **No seams at infrastructure boundaries**: Can you replace the real database, filesystem, or HTTP client with test doubles without editing the module under test? If not, the architecture forces integration tests where unit tests would suffice.
- **Collapsed seams**: Modules that once had independently-testable seams have had those seams removed (e.g., direct constructor instantiation replacing injection points, or global singletons replacing injected collaborators).
- **Legacy areas with no seams**: Modules with no obvious injection points or interface boundaries — any change must touch the entire call stack to swap behavior.

If all modules have clear seams at infrastructure boundaries → no finding.

If seams are missing or collapsed: flag as 🟡 Warning, Remedy points to the specific module and the injection point that needs to be restored or introduced.

Source: Feathers — Working Effectively with Legacy Code, Ch. 4: The Seam Model

### Step 6: Conway's Law Check

After completing the six-risk scan, evaluate the relationship between architecture and team structure:

- Does the module/service structure mirror the team structure?
  (Conway's Law: "Organizations which design systems are constrained to produce systems whose structures are copies of the communication structures of these organizations")
- If yes: Is this intentional design or accidental coupling?
- Mismatches that cause every feature to require cross-team coordination overhead are 🔴 Critical.
- Mismatches that exist theoretically but haven't caused pain yet are 🟡 Warning.
- If the team structure is unknown, record it as missing context and skip this check.

**Calibration examples:**
- 🔴 Critical: The Payments module is owned by Team A but contains authentication logic owned by Team B — every Payments change requires a sync meeting with Team B
- 🟡 Warning: Two different teams own `utils/` and `helpers/` directories that do the same thing — theoretically painful but not yet causing release coordination issues
- Not a finding: A single team owns a monorepo containing multiple logical modules — Conway's Law misalignment requires *different teams* to be meaningful

---

## Output

Before writing the report, run one lightweight coverage critic pass: dispatch a fresh
critic subagent that took no part in Steps 0–6 and ask exactly two questions:
- Which entry point, parallel path, lifecycle pattern, or risk category did no step cover?
- Which module was classified without any scanned dependency edge?

Accepted gaps are
scanned once with the Steps 2–6 checklists and the graph and colors updated; no
accepted gaps → output as planned. One pass only — no loop.

Use the standard report template in `common.md`. Mode: Architecture Audit.

Place the Mermaid dependency graph at the top under "Module Dependency Graph". Reference relevant node names in findings. Add `classDef` color assignments last, after all findings are identified.
