# Test Decay Risks Reference

Six modes of test suite degradation. Apply the Iron Law to every finding.

---

## Risk T1: Test Obscurity

**Diagnostic Question:** How much effort does it take to understand what this test verifies?

Unclear test intent breeds distrust, missed failures, and duplication — one step away from an abandoned suite.

### Symptoms

- Assertion Roulette: multiple assertions with no message strings — when one fails,
  you can't tell which behavior broke without reading every assertion
- Mystery Guest: tests depend on external state (files, database rows, shared fixtures)
  that is invisible from within the test body
- Test names that don't express the scenario and expected outcome
  (e.g., `test1`, `shouldWork`, `testLogin`, `testUserService`)
- General Fixture: an overly large setUp or beforeEach shared by irrelevant tests, making
  each test's preconditions invisible
- Test bodies that require reading production code to understand what they're verifying

### Sources

| Symptom | Book | Principle / Smell |
|---------|------|-------------------|
| Assertion Roulette | Meszaros — xUnit Test Patterns | Assertion Roulette (p.224) |
| Mystery Guest | Meszaros — xUnit Test Patterns | Mystery Guest (p.411) |
| General Fixture | Meszaros — xUnit Test Patterns | General Fixture (p.316) |
| Test naming | Osherove — The Art of Unit Testing | method_scenario_expected naming convention |

### Severity Guide

- 🔴 Critical: No test names in the file describe the behavior under test; all assertions lack messages
- 🟡 Warning: Multiple Mystery Guests; several vague test names
- 🟢 Suggestion: Minor naming issues; isolated General Fixture

### What Not to Flag

- Multiple assertions describing a coherent behavior that fail with a clear story are acceptable
- Shared setup is acceptable when nearly every test uses most of the initialized values
- Concise test names are acceptable when the scenario and expected outcome are still obvious

---

## Risk T2: Test Brittleness

**Diagnostic Question:** Do tests break when refactoring without changing behavior?

Brittle tests punish refactoring — eventually developers stop refactoring, and the codebase stagnates to protect the suite.

### Symptoms

- Tests assert private method results, internal state, or implementation details
  rather than observable behavior
- Eager Test: a single test method verifies multiple unrelated behaviors; any single change
  causes it to fail regardless of which behavior it touches
- Over-specification: assertions enforce mock call order or exact parameter values
  unrelated to the behavior under test
- Renaming or extracting a method causes 5 or more tests to fail, even with no behavior change
- Erratic Test: a test produces different results across runs without any production code changes
  — caused by race conditions, time-dependent logic, random data, or
  shared mutable state between tests

### Sources

| Symptom | Book | Principle / Smell |
|---------|------|-------------------|
| Eager Test | Meszaros — xUnit Test Patterns | Eager Test (p.228) |
| Erratic Test | Meszaros — xUnit Test Patterns | Erratic Test |
| Implementation coupling | Osherove — The Art of Unit Testing | Test isolation principle |
| Orthogonality violation | Hunt & Thomas — The Pragmatic Programmer | Ch. 2: Orthogonality |

### Severity Guide

- 🔴 Critical: Refactoring with no behavior change causes test failures; > 5 tests coupled to a single implementation detail
- 🟡 Warning: Eager Tests prevalent in the suite; moderate implementation-detail assertions
- 🟢 Suggestion: Isolated over-specification in non-critical tests

### What Not to Flag

- Verifying externally observable events or emitted commands is not implementation coupling
- A test with several assertions is acceptable when all assertions support one behavioral claim
- Fakes or in-memory adapters are not brittleness if the tests still assert behavior vs. wiring

---

## Risk T3: Test Duplication

**Diagnostic Question:** Is the same test scenario expressed in multiple places?

Duplicated tests must be changed in multiple places and create false confidence by not testing unique behavior.

### Symptoms

- Test Code Duplication: identical setup or assertion logic copy-pasted across multiple tests
  without extraction into a shared helper
- Lazy Test: multiple tests verify the same behavior with no difference in inputs,
  state, or expected output
- The same boundary condition tested identically at the unit, integration, and E2E levels
  — three copies with no level-appropriate differences
- Test helper functions or fixtures duplicated across test files rather than shared

### Sources

| Symptom | Book | Principle / Smell |
|---------|------|-------------------|
| Test Code Duplication | Meszaros — xUnit Test Patterns | Test Code Duplication (p.213) |
| Lazy Test | Meszaros — xUnit Test Patterns | Lazy Test (p.232) |
| DRY violation in tests | Hunt & Thomas — The Pragmatic Programmer | DRY: Don't Repeat Yourself |

### Severity Guide

- 🔴 Critical: Core business scenarios fully duplicated across all three test levels with no differences
- 🟡 Warning: Common scenario setups repeated in 5 or more tests without extraction
- 🟢 Suggestion: Minor helper duplication; isolated Lazy Test

### What Not to Flag

- The same scenario can appear at both unit and integration levels when each level verifies different risks
- Small local setup duplication may be clearer than a maze of over-abstracted fixtures
- Similar assertions for different domain rules are not Lazy Tests when the business intent differs

---

## Risk T4: Mock Abuse

**Diagnostic Question:** Is the test more complex than the behavior it tests?

Mock abuse produces tests that pass regardless of correctness — as long as the mock is wired up,
production code can be completely broken.

### Symptoms

- Mock setup code longer than the test logic itself
- Primary assertion is `expect(mock).toHaveBeenCalledWith(...)` — the test verifies
  the mock was called, not that any real behavior occurred
- Test-only methods added to production classes for lifecycle management in tests
- A single unit test uses more than 3 mocks
- Incomplete Mock: mock object is missing fields downstream code will access,
  causing silent failures visible only in integration
- Hard-Coded Test Data: test data bears no resemblance to real data shapes or constraints

### Sources

| Symptom | Book | Principle / Smell |
|---------|------|-------------------|
| Mock count > 3 | Osherove — The Art of Unit Testing | Mock usage guidelines |
| Testing mock behavior | Meszaros — xUnit Test Patterns | Behavior Verification (p.544) |
| Test-only production methods | Feathers — Working Effectively with Legacy Code | Ch. 3: Sensing and Separation |
| Hard-Coded Test Data | Meszaros — xUnit Test Patterns | Hard-Coded Test Data (p.534) |
| Incomplete Mock | Osherove — The Art of Unit Testing | Mock completeness requirement |

### Severity Guide

- 🔴 Critical: Mock setup > 50% of test code; production classes have methods called only from tests
- 🟡 Warning: Mocks consistently > 3 per test; primary assertions are mock call verifications
- 🟢 Suggestion: Isolated Incomplete Mock; minor Hard-Coded Test Data

### What Not to Flag

- A small number of mocks around non-deterministic dependencies are acceptable when assertions still verify behavior
- Fakes and spies used to observe state transitions are not mock abuse by default
- A single interaction assertion may be appropriate when the interaction itself is the behavior under test

---

## Risk T5: Coverage Illusion

**Diagnostic Question:** Does the test suite actually prevent important failures?

Coverage measures execution, not verification. 90% line coverage can still miss every critical failure mode — the team stops looking because the numbers say "covered."

### Symptoms

- High line coverage but error-handling branches, boundary conditions, and exception paths
  have no corresponding tests
- Happy-path only: no sad paths, no null/empty/zero inputs, no concurrency edge cases
- Legacy code areas being actively modified with no tests present
  (Feathers: "Legacy code is code without tests")
- Coverage percentage used as a sign-off criterion; critical change paths remain untested
- Tests assert return values but don't assert important side effects like database writes,
  event publications, or state transitions

### Sources

| Symptom | Book | Principle / Smell |
|---------|------|-------------------|
| Legacy code = no tests | Feathers — Working Effectively with Legacy Code | Ch. 1: "Legacy code is code without tests" |
| Change coverage vs line coverage | Google — How Google Tests Software | Ch. 11: Testing at Google Scale |
| Happy-path only | Osherove — The Art of Unit Testing | Test completeness principle |

### Severity Guide

- 🔴 Critical: Legacy code areas actively modified with no tests; error-handling paths completely missing
- 🟡 Warning: Coverage > 80% but edge and exception paths systematically absent
- 🟢 Suggestion: Some non-critical paths missing sad-path tests

### What Not to Flag

- High line coverage is useful when paired with branch, boundary, and change-path coverage
- New modules may legitimately have limited coverage early on if they're still private and low-risk
- Side-effect assertions may exist in integration tests rather than unit tests, not implying a gap

---

## Risk T6: Architecture Mismatch

**Diagnostic Question:** Does the test suite structure reflect the system's actual risk profile?

Wrong suite shape is slow and costly — not because of bad tests, but because of the wrong type of tests at the wrong level.

### Symptoms

- Inverted test pyramid: E2E or integration test counts exceed unit test counts,
  causing a slow and brittle suite
- Legacy code with no seam points: no interfaces, dependency injection, or seams,
  making it impossible to isolate tests without modifying production code
- Modified legacy areas without Characterization Tests to capture current behavior
  before changes
- Full suite execution time exceeding 10 minutes (indicating an architectural problem,
  not a performance problem — too many slow tests)
- High-risk and low-risk paths tested at the same density;
  no risk-based prioritization in test distribution

### Sources

| Symptom | Book | Principle / Smell |
|---------|------|-------------------|
| Inverted pyramid | Google — How Google Tests Software | 70:20:10 unit:integration:E2E ratio |
| No seam points | Feathers — Working Effectively with Legacy Code | Ch. 4: Seam Model |
| Missing Characterization Tests | Feathers — Working Effectively with Legacy Code | Ch. 13: Characterization Tests |
| Suite execution time | Meszaros — xUnit Test Patterns | Slow Tests (p. 253) |

### Severity Guide

- 🔴 Critical: Modified legacy code has no seams and no Characterization Tests; pyramid fully inverted
- 🟡 Warning: Suite execution > 10 minutes; integration/E2E counts exceed unit tests
- 🟢 Suggestion: Local pyramid ratio deviations; a few legacy areas missing Characterization Tests

### What Not to Flag

- Deviating from 70:20:10 may be justified by platform constraints or product risk
- Heavy integration test suites can still be healthy if feedback is fast and layering is purposeful
- A small number of critical-path E2E tests are desirable, not a smell
