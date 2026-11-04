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

The completed frozen audit made five calls and scored 34 claims: **3 false
acceptances, 0 false rejections, 2/5 passing cases**. All 23 valid claims were
accepted; eight of eleven invalid controls were rejected. The Russian
receipt-versus-absence failure still satisfies the structural protocol and
reaches application acceptance. Exact quotations do not prove entailment.
The [complete record](GROUNDING_04_FOLLOWUP_2026-11-03.md) preserves the scores,
raw parsed responses, independent review and earlier startup/context failures.

The separate ledger-generation check passed English source review, offline
assembly, PDF/PPTX export and restart. All four English PDF pages were visually
reviewed. The Russian writer stopped before producing an outline. A subsequent
single-request diagnostic reproduced the failure and captured its actual cause:
the one-MiB HTTP-body limit counted repeated SSE metadata and stopped the stream
after 4,123 recorded events, before any answer text. The recording contains
1,048,339 wire bytes but only 21,197 bytes of reasoning text. The next chunk
exceeded the wire limit. This is a transport failure, separate from semantic
quality. The new transport regression and follow-up results are recorded below.

## November 4 transport correction

SSE now has a separate eight-MiB wire budget for both OpenAI-compatible and
Anthropic streams. Ordinary JSON retains one MiB; decoded content, lines/events,
deadlines, cancellation and required completion markers are unchanged. Two
realistic streams over one MiB failed before the correction and pass afterward.
The final focused suite passes 126 tests, including exact eight-MiB acceptance,
one-byte-over rejection and retained JSON bounds. The complete suite passed
684 tests before the final extra boundary case was added; that case is included
in the focused result. All 66 statements in the changed event decoder/chunk
module are covered. The configured Ruff scope passes for 178 Python files.

The post-correction live evaluation and new native candidate are pending. No
model prompt, frozen gold label or recorded failure changed for this fix.

Native run 41673421566 tested source `4fd974d`: five targets succeeded, while
macOS ARM64 never acquired a hosted runner. Its infrastructure cancellation is
not a passing sixth target or a code-test failure. That source is superseded by
the transport correction; it is not used for a new installed-upgrade claim.
The changed candidate still requires a fresh six-target native build and
installed Windows upgrade verification. No merge, tag or public release is part
of this follow-up.
