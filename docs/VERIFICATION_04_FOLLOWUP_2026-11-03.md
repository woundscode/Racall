# 0.4 assembly and local package verification — November 3, 2026

This follow-up covers uncommitted development on `codex/0.4-presentations`,
based on `68d81b15c365dd8f6daa20166e0aafc391a3b340`. No commit, push, remote
workflow or release was performed. Public 0.3 assets remain unchanged.

## Changes and reasons

- Removed the second presentation writer/critic: Python assembles the exact
  accepted outline revision, so it cannot rewrite the reviewed facts or notes.
- Added an approval snapshot and digest for recovery, while retaining source
  context fences, cancellation and retry. This is provenance, not a truth claim.
- Kept edited content unvalidated; assembly works with an empty model setting
  and without credential lookup or embedding requests.
- Formatted generated inline evidence groups using canonical citation numbers
  before the outline is saved. Unknown/undeclared references are rejected;
  ordinary bracketed prose, user edits and quoted source text are preserved.
- Updated EN/RU labels and documentation to describe offline slide assembly.
- Added continuous RAM monitoring to the opt-in evaluation harness and prepared
  the separately documented [installed upgrade gate](UPGRADE_04_GATE.md).

## Completed local checks

- Final Python suite: **585 passed**, one existing Starlette/httpx deprecation
  warning, **42.77 seconds**. The final run includes the new assembly, citation,
  resource-monitor and observer-guard tests.
- Ruff check and format check passed: **163 Python files**. Prettier and
  `git diff --check` passed.
- Production frontend build and its TypeScript check passed.
- **484** EN/RU localization keys passed parity and preference checks.
- Release metadata remains `0.4.0-beta.1`, Python `0.4.0b1`, `publication: hold`,
  `github_latest: false`.
- **14** native-target and upgrade-harness Node unit tests passed. These validate
  contracts and guards; they do not install an update or build other platforms.
- PyInstaller backend and Windows x64 unpacked Electron packaging completed.
- Both packaged executables were verified as native x64. Frozen-backend PDF
  import, full-text search, page citations, original download and authentication
  checks passed.
- The rebuilt Windows app passed presentations, existing Studio and persistence
  scenarios in isolated profiles with GPU acceleration disabled. Presentation
  saves, draft recovery, real binary exports and EN/RU layouts passed; job-submit
  responses in that UI scenario remain synthetic. Real offline assembly is
  covered by the Python API tests and the separately recorded manual-Russian run.

Package evidence:

- `test-results/presentations-desktop-1793713386665/result.json`
- `test-results/studio-desktop-1793713456681/result.json`
- `test-results/persistence-1793713526259/result.json`

The EN/light and RU/dark editor screenshots were visually inspected. This is an
unpacked, unsigned development build, not an installed release candidate. The
owner's installed application and data were not replaced.

The [live follow-up report](MODEL_EVALUATION_04_FOLLOWUP_2026-11-03.md) records
the actual model results separately: English passed independent factual review;
Russian failed a receipt-versus-absence inference. The model-quality gate remains
incomplete. A manually corrected copy passed offline assembly, export and restart.
Neither recorded-response tests nor manual corrections erase that failure.

## Rendering

Poppler-rendered English live, English citation-replay and corrected Russian
PDFs were visually inspected, including notes and source appendices (four pages
each). No text clipping, overlaps or missing Cyrillic glyphs were found.
PPTX content, notes and editable objects were checked programmatically; actual
PowerPoint/LibreOffice rendering remains unverified.

## Focused maintainability checks

Crapper, Dryer and Mutator were run against assembly, citation formatting and
the two evaluation-monitor modules. Coverage from six existing test files passed
**64 tests** and measured **90% combined line/branch coverage** across those four
modules. All **23 functions scored below CRAP 10**, with a maximum of **9.0**.
Dryer found no duplicates at the 0.8 threshold. Mutator discovered 62 mutation
sites; only discovery was run, so this is not a mutation-testing pass.

The earlier four-test-file coverage selection omitted job/recovery tests and
reported two CRAP scores above 10. Adding the already-existing job and API tests
resolved that measurement gap without code changes or new tests. Both raw
reports and unchanged source hashes are retained under the run's `metrics/`
directory. An initial pytest temporary-directory permission error was resolved
by using a fresh directory inside this isolated test run.

## Evidence and remaining gates

Raw local evidence is retained under `test-results/live04-20261103T162435/`,
including final Python/build logs, live trace, resource samples, independent
reviews, cleanup and the separately marked `manual-ru/` workflow. The citation
regression exports and provenance are in `test-results/inline-citations04/`.
The earlier [verification record](VERIFICATION_04_2026-11-03.md) is unchanged.

Fresh native macOS/Linux/ARM64 builds, the installed 0.3-to-0.4 upgrade, external
PPTX rendering, model-quality acceptance and publication approval remain open.
The upgrade harness requires a fresh GitHub-hosted Windows runner and genuine
successful-build identifiers. It was not bypassed on the owner's computer.
