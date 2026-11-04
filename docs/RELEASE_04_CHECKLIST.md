# 0.4 Beta acceptance checklist

Publication: **hold**. Public 0.3 assets remain unchanged.
[Plan](PLAN_04.md) · [Presentation guide](PRESENTATIONS.md)

**Owner decision, November 4:** keep 0.4 in development until automatic factual
checking becomes more reliable. The owner declined publication as an AI-draft
beta relying on manual review. Passing builds and the source-review interface
do not waive the unresolved semantic-quality gate.

## Implemented and checked locally

The last [packaged follow-up](VERIFICATION_04_GROUNDING_2026-11-03.md) is source
`629312ebf4f385445cd9026ea0278f42fe50957c`. The complete local suite passed
685 tests in 48.91 seconds with one existing deprecation warning; the final
focused transport suite passed 126 tests. Configured Ruff checks passed for
178 Python files. The earlier
[604-test candidate](VERIFICATION_04_CLOSURE_2026-11-03.md) remains historical
evidence and does not identify the current packages.

November 4 final preparation adds slide-local source review and updates the
Next.js/Electron patches. The earlier package hashes remain valid only for
`629312e`; the changed candidate needs a fresh native matrix and installed
upgrade before tagging. [Local final checks](VERIFICATION_04_FINAL_PREPARATION_2026-11-04.md)
passed; publication remains on hold.

- [x] Python-owned typed deck, bounded output and canonical source references.
- [x] Source-anchored fact ledger shared by titles, bullets and speaker notes;
      structured, fallible evidence audit with no automatic repair.
- [x] Saved outline review releases the worker before a separate explicit job.
- [x] Pinned source context and outline revision; idempotency and restart without replay.
- [x] Revision conflicts, preserved original, portable drafts and stale-save rejection.
- [x] Slide title/bullet/notes editing, reorder/delete and light/dark templates.
- [x] English/Russian interface strings and TypeScript validation.
- [x] Real PPTX/PDF export tests, embedded PDF/SVG Cyrillic fonts and editable PPTX text.
- [x] English/Russian sample PDFs rendered and visually inspected.
- [x] All original Python tests pass alongside new presentation tests.
- [x] Interrupted outline recovery, deleted-slide claim cleanup and atomic
      terminal-job/operation-release regressions.
- [x] Separate eight-MiB SSE wire budget; ordinary JSON stays at one MiB,
      with answer/event bounds, deadlines and completion checks preserved.

Measured results and limitations: [current verification](VERIFICATION_04_GROUNDING_2026-11-03.md)
and [grounding evaluation](GROUNDING_04_FOLLOWUP_2026-11-03.md).

## Release gates

- [x] Final deterministic-assembly checks: exact approved text, slide IDs and
      citations, preserved edited review states, no provider/embedding calls, and
      offline **Create slides / Оформить слайды** followed by export.
- [x] Previous-candidate automated desktop and installer acceptance across all six
      Windows/macOS/Linux x64 and ARM64 targets, including packaged resources
      and export smoke checks. [Native run 41836749757](https://github.com/woundscode/Racall/actions/runs/41836749757)
      passed on source `629312e`.
- [x] Previous-candidate installed Windows x64 0.3 → 0.4 upgrade preserves original
      notebooks/materials/revisions and knowledge after uninstall.
      [Upgrade run 41840303042](https://github.com/woundscode/Racall/actions/runs/41840303042)
      passed eight checks against the verified Windows x64 artifact from the
      successful native matrix; all 21 original fixture files remained
      byte-for-byte unchanged after uninstall.
- [x] Actual LibreOffice rendering and editable round trip checked; all 66 rendered
      pages from the earlier `3c22f58` candidate were visually reviewed. Rendering
      code is unchanged; font limits and untested PowerPoint are recorded in
      [compatibility evidence](PRESENTATION_COMPATIBILITY_04.md).
- [x] Frozen real-provider audit scored and independently reviewed: 34 claims,
      three false acceptances, no false rejections, two of five cases passing.
- [x] Post-transport-fix EN/RU end-to-end live evaluation on the current Windows
      host: four production calls, separate outline/deck reviews, manual save,
      offline assembly, PPTX/PDF export and restart. All eight rendered PDF pages
      passed visual review. The Russian stream exceeded the former wire cap
      and completed. [Runtime evidence](VERIFICATION_04_GROUNDING_2026-11-03.md)
      records the host-specific settings and preserved earlier failures.
- [ ] Original automatic factual-quality criterion: source-faithful initial
      outlines in both languages. Recorded writer and auditor counterexamples
      remain unresolved.
- [x] A bounded single-claim isolation experiment evaluated the first known
      false acceptance and stopped on its repeated semantic failure. No
      per-claim inference change was added; the frozen audit score is unchanged.
- [x] Final slide-local source review passes desktop checks, including complete
      passages, source opening, edited states, restart and EN/RU themes.
- [x] Final Next.js/Electron security patches pass the local web build and
      presentation desktop checks;
      dependency review records remaining findings separately.
- [ ] Fresh six-target candidate and exact installed Windows upgrade include the
      final source-review interface and dependency versions.
- [x] Two affected minimatch consumers fixed using exact parent-scoped overrides;
      15 remaining moderate build-tool findings assessed without suppression or a
      zero-finding claim ([dependency assessment](DEPENDENCY_REVIEW_04_2026-11-03.md)).
- [x] Candidate release-note draft updated with implemented features and known limits.
- [x] Previous-candidate ten-package [manifest](releases/0.4.0-beta.1-candidate-629312e.json)
      and [SHA-256 checksums](releases/0.4.0-beta.1-candidate-629312e-SHA256SUMS.txt).
- [x] Previous-candidate installed-upgrade evidence recorded, including exact package
      identity, original-file hashes and review of all four captured screenshots
      ([verification](VERIFICATION_04_GROUNDING_2026-11-03.md)).
- [x] Owner scope decision: retain development status until automatic factual
      checking improves; do not publish with manual review as the substitute.
- [ ] Later publication authorization after the retained quality requirement is met.

## Model-quality limits

The installed-upgrade test used nine synthetic provider calls and the same
installation/profile. Its 23 final knowledge files comprise 21 unchanged originals
and two expected additions. These preservation and interface checks do not
establish real-model quality.

Automated fixtures establish request, storage and file-format behavior, not model
factual reliability. In the [frozen audit](GROUNDING_04_FOLLOWUP_2026-11-03.md),
all 23 valid claims were accepted, but only eight of eleven invalid controls were
rejected. The Russian receipt-versus-absence false acceptance persists even with
structurally valid exact quotations. The separate pre-correction ledger run
passed English review, exports and restart; Russian stopped at the SSE wire limit.
The first post-correction run stopped earlier at external CUDA initialization.
Neither failed attempt supplies a semantic score. After increasing the Windows
page file and using ordinary non-mmap loading, a new cold-load EN/RU workflow
passed four production calls and separate reviews of both saved outlines/decks.
Those two examples establish the checked workflow, not a replacement score for
the frozen audit or a general factual-reliability claim.

The [reference workflow](PRESENTATION_REFERENCE_REVIEW_04.md) retains AI outlines
and manual correction. Python assembly preserves the approved text without a
second writer or critic. This removes a rewrite opportunity; it cannot establish
that an initial claim is true. Generated content stays `validated=false`, and
user approval is not factual certification. Historical failures and their
[disposition](MODEL_REVIEW_04_DISPOSITION_2026-11-03.md) remain recorded. No
WSL/Docker load or model download was used for this follow-up.

## Historical package evidence

Source `3c22f58` passed 604 tests on six native targets, ten-package verification
and an installed Windows upgrade preserving all 21 original fixture files
([record](VERIFICATION_04_CLOSURE_2026-11-03.md)). Source `4fd974d` subsequently
passed five native targets; macOS ARM64 never acquired a hosted runner. Its
LibreOffice check succeeded. Those results do not replace the current source's
native and installed-upgrade gates, and no historical package hash is reused as
the new candidate's identity.
