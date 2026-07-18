# Codebase Onboarding Guide

**Purpose:** Generate a newcomer-friendly tour of the codebase. This is not a diagnostic report — no Health Score, no Iron Law findings. Focus on explanation and orientation.

---

## Flow

### Step 1: Draw the Domain Map

- Read the top-level structure (same as architecture-guide Step 0)
- Output: a plain-language overview of what each top-level module does (one sentence each)
- Group by layer: "things the user interacts with", "business logic", "infrastructure"

### Step 2: Draw the Dependency Map

Draw the same Mermaid dependency graph as Architecture Audit Step 1, but color nodes by **recommended reading order**,
using a different palette than the severity palette (red/yellow/green)
to avoid conflating "red = danger" with "red = read last":

- 🔵 Blue (`#339af0`): Start here — entry points, core domain
- 🟣 Purple (`#9775fa`): Read next — supporting modules
- ⚪ Gray (`#ced4da`): Read last — infrastructure, generated code, utilities

Add numbered labels: `CoreModule["1. CoreModule"]`

```
classDef start fill:#339af0,color:#fff
classDef next fill:#9775fa,color:#fff
classDef last fill:#ced4da
```

### Step 3: Highlight Key Conventions

Identify and document the patterns the codebase follows:
- Naming conventions (file naming, class naming, variable naming)
- Directory organization pattern (feature-based? layer-based? hybrid?)
- Error handling pattern (exceptions? result types? error codes?)
- Test conventions (co-located? separate directory? naming pattern?)
- Dependency injection pattern (if any)

### Step 4: Flag Danger Zones

For each module known for complexity or coupling issues, add a brief warning:
- "OrderService: high complexity, only modify with full test suite running"
- "legacy/: no tests, use Characterization Tests before modifying"

Do not use Iron Law format — use plain warnings. This is orientation, not diagnosis.

### Step 5: Build a Domain Glossary

Extract 10–15 key domain terms from the code (class names, method names, constants) and map them to plain-language definitions. This applies Evans's Ubiquitous Language as documentation.

### Step 6: Suggest First Tasks

Based on the dependency graph, suggest 2–3 low-risk areas where a new developer can make their first contribution:
modules with good test coverage, clear boundaries, and low coupling.

---

## Output Template

```
# Codebase Tour: [Project Name]

## Overview
[2-3 sentence summary of what the project does and its tech stack]

## Module Map
[Mermaid graph with reading-order colors]

## Module Guide
[One paragraph per top-level module: what it does, what it depends on, key files to read]

## Conventions
[Bullet list of patterns this codebase follows]

## Danger Zones
[Bullet list of areas to be careful with, or "None identified" if the codebase is clean]

## Domain Glossary
| Term | Meaning |
|------|---------|

## Suggested First Tasks
[2-3 concrete suggestions for a new developer's first PR]
```
