# 0.4 grounding and packaging follow-up — November 3, 2026

Publication remains on hold. This follow-up changes the source and dependency
tree after the [previous candidate](VERIFICATION_04_CLOSURE_2026-11-03.md);
previous package hashes do not identify these changes.

## Scope

- Python parses a source-anchored ledger once. Titles, bullets and speaker notes
  reuse its texts. A separate structured, fallible audit checks each claim;
  malformed, unsupported and uncertain results stop generation without repair.
- Full cited passages are sent once, preserving each claim's citation scope.
  Exact anchors establish provenance, not entailment. `validated=false` and
  explicit user review remain unchanged.
- Saved outlines recover by identity and document integrity after interrupted
  job bookkeeping. Deleting slides clears obsolete claims and anchors while
  preserving revision history.
- Two affected packaging consumers now use minimatch 11.0.4 through exact,
  parent-scoped overrides. Legacy APIs remain unchanged. Native CI runs nine
  packaging contracts before building each platform.

Implementation and the frozen regression/holdout design are documented in
[grounding follow-up](GROUNDING_04_FOLLOWUP_2026-11-03.md). The
[dependency assessment](DEPENDENCY_REVIEW_04_2026-11-03.md) distinguishes fixed
implementations from the 15 remaining moderate audit findings.

## Checks so far

TypeScript, 484-key localization parity, nine packaging contracts, fourteen
native-target/upgrade unit tests, Ruff, formatting and release metadata passed.
The first complete Python run exposed a terminal-state/operation-release race:
**677 passed, 1 failed**, in 43.76 seconds. This failure is retained; the completed
result was visible before its notebook operation reservation was released.
A deterministic barrier test reproduced the race for both completed and failed
jobs. Terminal-state persistence and guard release now occur under the same
lock; cancellation still waits for the active provider to drain. Both regressions
pass. The subsequent full suite passed **680 tests** in **44.01 seconds**, with
one existing Starlette/httpx deprecation warning. Ruff and formatting passed for
178 Python files. No mocked response is presented as a factual-quality result.

Live evaluation has not produced a scored semantic result yet. A RAM preflight
and two isolated runtime startup attempts stopped before model questions. A
third attempt with 44 GPU layers successfully loaded and made one audit request,
but its 1,354 input and 2,742 generated tokens exhausted the 4,096-token context.
The provider correctly rejected the truncated stream. The same frozen cases
are being evaluated with an isolated 8,192-token alias and unchanged resource
guards. The logs and cleanup are recorded in the grounding follow-up. Neither
mocked responses nor package builds substitute for real-provider evaluation.

The changed candidate still requires a fresh six-target native build and
installed Windows upgrade verification. No merge, tag or public release is part
of this follow-up.
