# 0.4 development verification — November 3, 2026

Local branch: `codex/0.4-presentations`, based on
`68d81b15c365dd8f6daa20166e0aafc391a3b340`. These checks cover uncommitted working
tree changes. Publication remains on hold; no remote branch, tag, release or
public 0.3 asset was changed.

[Presentation guide](PRESENTATIONS.md) · [Acceptance checklist](RELEASE_04_CHECKLIST.md)

Later the same day, the owner authorized a live Ollama check. That separate
[evaluation report](MODEL_EVALUATION_04_2026-11-03.md) records a completed English
workflow, a critic false positive and a resource stop before Russian. The
automated results below retain their original scope.

## Completed checks

- Full Python suite: **534 passed**, one existing Starlette TestClient/httpx
  deprecation warning, 37.93 seconds. Command:
  `.venv/Scripts/python.exe scripts/test.py -q -o faulthandler_timeout=45`.
- Ruff check and format check passed; 153 Python files formatted.
- Production static frontend build and TypeScript validation passed.
- Localization: **483** matching EN/RU keys, placeholders and preference checks.
- Release metadata agrees: `0.4.0-beta.1`, Python `0.4.0b1`, display `0.4 Beta`,
  publication `hold` and `github_latest: false`.
- Prettier and `git diff --check` passed.
- PyInstaller backend and `electron-builder --win --x64 --dir --publish never`
  completed. Both packaged executables were verified as x64.
- The frozen backend contains DejaVu fonts, PPTX templates, ReportLab resources,
  fontTools tables and licenses for the new runtime dependencies.
- All three relevant desktop scenarios passed against
  `release/win-unpacked/Racall.exe`: presentations, existing Studio, persistence.
  They use isolated data/profile directories and disable GPU acceleration.

The Windows package is an unpacked development application, not an installed or
signed release candidate. The installed user application/data were not replaced.

## Presentation coverage

Python tests exercise selected-note context through outline generation, manual
revision and explicitly approved slide generation; canonical citations and pinned
source versions; critic rejection of unsupported slide content; malformed output;
job idempotency/cancellation/restart; revision conflicts; atomic-write failure;
preserved prior versions and separate recovery drafts; authenticated API access
and development-origin PATCH; offline exports and saved-revision fences.

The packaged desktop scenario checks real Python saves, draft recovery after
restart, invalidation of edited content's previous verification, reordering and
deletion, discarding a draft, actual PDF/PPTX downloads, saved SVG preview,
immediate tab/result navigation, recovery of an existing generation job without
duplicate submission, a new explicit job after an outline revision, EN/light,
RU/dark and the minimum 1,000×680 window without horizontal overflow.

Generation submission responses in that desktop scenario are synthetic. Python
generation integration tests also use deterministic provider responses. These
are workflow checks, not a live-model quality evaluation.

Existing Studio passed selected-context chat, citation snapshots, three original
material formats, editable copies, Markdown download, cancellation/retry,
persistent results and restart without inference replay. The persistence scenario
passed the existing chat/note recovery and conflict cases after the navigation
guard changes.

## Rendering and maintainability

English/light and Russian/dark sample PDFs were rendered with `pdftoppm` and
visually inspected, including notes and reference appendices. Each sample has
four pages. Export tests inspect editable PPTX objects/text/notes through
`python-pptx`; no external PowerPoint/LibreOffice rendering was performed.

Focused coverage for the three export/layout/font modules is **98%**. Their
maximum CRAP score is approximately **9.01**; Dryer found no duplicates at the
0.8 threshold within the presentation Python feature. The Windows Mutator CLI
could not create its symlink overlays. Two corresponding mutations were instead
tested in isolated copied packages: the unchanged baseline passed all nine export
tests, and both mutations were caught. This is a focused mutation check, not a
complete mutation campaign.

## Reproducible local evidence

Ignored artifacts under `test-results/`:

- `presentations04/python-tests.log`, `backend-build.log`, `desktop-build.log` and
  `packaged-presentations.log`, `packaged-studio.log`, `packaged-persistence.log`.
- `presentations04/sample-en-light.*`, `sample-ru-dark.*`, rendered page PNGs,
  `export-results.json`, coverage/metrics and `mutations/results.json`.
- `presentations-desktop-1793708234476/result.json`: development desktop check.
- `presentations-desktop-1793708479854/result.json`: packaged presentation check,
  with real downloaded `edited.pdf` and `edited.pptx`.
- `studio-desktop-1793708547788/result.json`: packaged Studio check.
- `persistence-1793708614263/result.json`: packaged persistence check.
- `presentation-capture-1793708752784/`: final packaged editor/preview PNGs and
  `result.json`, visually checked against the requested scroll positions. The
  ignored `test-results/capture-presentation-window.cjs` repeats this capture
  using a separate copy of the synthetic profile.

Initial Windows sandbox runs stalled inside the event-loop socket-pair setup;
the same checks completed outside that restriction. The first packaged desktop
attempts stopped during CDP screenshot capture of a hidden window after the
preceding functional assertions passed. The tests now use an owned Electron
window capture helper; the functional checks subsequently passed. A final
capture-only check verified the helper's warm-up and paint wait, preventing
stale frames after scrolling a hidden window. These changes
affect test infrastructure, not application permissions or data handling.

## Not established

At this initial automated check, no live Ollama/cloud inference, model download
or factual-quality evaluation was performed. The subsequent live result is
linked above. The known 0.3 critic limitations remain; synthetic acceptance does
not resolve them. No Docker/WSL load was used.

Fresh macOS/Linux/ARM64 native packages, the full six-platform matrix, an
installed 0.3-to-0.4 upgrade, external PPTX rendering and publication acceptance
remain unchecked. PPTX names DejaVu Sans without embedding it, so another
computer may substitute a font. PDF/SVG embed their font data.
