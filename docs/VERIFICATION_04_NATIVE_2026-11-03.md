# 0.4 Beta native candidate verification — 2026-11-03

Publication remains **hold**. The owner authorized committing the candidate,
pushing `codex/0.4-presentations`, running six native builds and checking an
installed 0.3 → 0.4 upgrade. This authorization excludes merging `main`, creating
a release tag and publishing a release. Public 0.3 downloads remain unchanged.

## Candidate and changes made during preflight

- `9675f5eff310a9105784f728d3979c9ef2947933`: prepared presentation candidate,
  native export checks and installed-upgrade harness.
- `f20d2fec7aaca23afae1cfe51cbfdc87bb79e591`: regenerated four installer catalog
  labels that still displayed 0.3 Beta. The catalog consistency check passes.
- `d38bbf99c817e55d4037c94394ccab4f3dacf64f`: pinned Electron 44.9.1 for the
  official CA security fix, with no other resolved dependency changes. See the
  [dependency review](DEPENDENCY_REVIEW_04_2026-11-03.md) for remaining findings.
- `c3abd0d3b4330cd82ed935025a93d113b108d544`: retained python-pptx's physical
  source directories in the frozen backend and added explicit HTTP export
  assertions to the desktop smoke test.

The renamed repository is `woundscode/Racall`, immutable GitHub repository ID
1385819102. Upgrade provenance checks use that ID, so a rename is accepted while
a different repository is rejected. Current public links were refreshed, and
the upstream font license is preserved byte-for-byte with an LF attribute.

The [first native run](https://github.com/woundscode/Racall/actions/runs/41649836412)
found the stale generated installer labels after the earlier validation steps.
Five targets reached that failure. Windows ARM64 saved its verified native
OpenSSL cache before the remaining obsolete run was cancelled. No package from
that run is accepted as the candidate.

The [second run](https://github.com/woundscode/Racall/actions/runs/41651914467)
passed the catalog gate but exposed a PPTX export failure on macOS ARM64 and both
Linux targets. python-pptx reads notes XML through `oxml/../templates`; data-only
collection left `oxml` inside PYZ without a physical directory. Windows resolves
the path despite that missing intermediate directory, masking the failure.
`--collect-all pptx` retains the required directory instead of changing library
code or extending timeouts. The same packaged export checks are the native
regression. The enhanced HTTP/download assertions passed against the existing
isolated Windows build (`presentations-desktop-1793715998631`); this alone does
not verify the POSIX fix. The obsolete run's remaining jobs were cancelled.

## Native build matrix

Source: `c3abd0d3b4330cd82ed935025a93d113b108d544`.
[Corrected native run](https://github.com/woundscode/Racall/actions/runs/41654163237).

| Target | Build and packaged checks |
| --- | --- |
| Windows x64 | Passed — [job 125980382457](https://github.com/woundscode/Racall/actions/runs/41654163237/job/125980382457), artifact 13239791812 |
| Windows ARM64 | Passed — [job 125980382651](https://github.com/woundscode/Racall/actions/runs/41654163237/job/125980382651), artifact 13240996163 |
| macOS Intel x64 | Passed — [job 125980383074](https://github.com/woundscode/Racall/actions/runs/41654163237/job/125980383074), artifact 13239942248 |
| macOS Apple Silicon ARM64 | Passed — [job 125980382631](https://github.com/woundscode/Racall/actions/runs/41654163237/job/125980382631), artifact 13239566682 |
| Linux x64 | Passed — [job 125980382587](https://github.com/woundscode/Racall/actions/runs/41654163237/job/125980382587), artifact 13240096554 |
| Linux ARM64 | Passed — [job 125980382376](https://github.com/woundscode/Racall/actions/runs/41654163237/job/125980382376), artifact 13240176469 |

The complete workflow finished **successfully**; its publish job was **skipped**.
Each target passed **585 Python tests**, contract tests, static checks, native
packaging, packaged application scenarios including PPTX/PDF exports, installer
checks, and candidate manifest/checksum generation. The POSIX presentation
failure is resolved in the native applications. These are synthetic-provider
behavior checks, not real-model factual evaluations.

[Candidate manifests](releases/0.4.0-beta.1-candidate.json) record all six artifacts
and the ten installer/archive package sizes and SHA-256 values. These are
temporary workflow artifacts, not public release assets. The Windows x64
artifact was also downloaded locally and its manifest, exact bytes and checksum
file independently matched the values printed by the successful job; no local
installation was performed.

## Installed upgrade

The [upgrade run](https://github.com/woundscode/Racall/actions/runs/41657996348)
**passed** on a disposable GitHub-hosted Windows x64 machine. It used the
successful native run above and artifact **13239791812**:

- File: `Racall-0.4.0-beta.1-win-x64.exe`.
- Size: **159,186,611 bytes**.
- SHA-256: `66a98d78f8e3c2dc70c0eb5e52a9bd6d27e118858c7e7e4ae508b174d394f214`.

The [upgrade gate](UPGRADE_04_GATE.md) independently verified provenance and
these file values before installation. Both the candidate and harness used
`c3abd0d3b4330cd82ed935025a93d113b108d544`. The baseline was the published 0.3
installer with its previously pinned size and SHA-256.

The scenario preserved **21 baseline files** byte-for-byte, including notes,
versioned originals, chat and Research records, a completed Studio job/material,
and notebook trash. It verified historical citations, unchanged Markdown export,
EN/RU, light/dark, new Studio generation and a full restart without replaying
inference. Uninstall removed the application while preserving the fixture's
knowledge. It made **9 synthetic provider calls** and recorded **zero errors**;
no real model was involved.

[Upgrade evidence](https://github.com/woundscode/Racall/actions/runs/41657996348/artifacts/13241540134)
contains the exact input provenance, snapshots, result JSON, screenshots and
logs. Its archive is 248,381 bytes, SHA-256
`3a9f5243983cc34ace060392f0f65e6be21eb956287b1fb240f49ac70d74dff1`.
The downloaded historical-citation and restarted-app screenshots were visually
inspected. No installer was executed on the owner's workstation.

## Repository state

Only `codex/0.4-presentations` was pushed. `main` remained at
`68d81b15c365dd8f6daa20166e0aafc391a3b340`; the public release remained 0.3 Beta.
Documentation added after the checks does not change the tested package source
SHA recorded above. No merge, release tag or publication was performed.

## Limits retained

- The [live-model follow-up](MODEL_EVALUATION_04_FOLLOWUP_2026-11-03.md) passed
  independent English review but failed Russian factual review. Deterministic
  assembly and a corrected manual copy do not erase that initial-outline failure.
- Actual PowerPoint/LibreOffice rendering remains unverified. PDF/SVG embed the
  supplied fonts; PPTX recipients may experience font substitution.
- The [dependency review](DEPENDENCY_REVIEW_04_2026-11-03.md) is scoped triage,
  not a clean security audit.
- Native hosted runners do not represent all user hardware, Linux distributions
  or local models. The installed-upgrade scenario covers Windows x64 only.

The [release checklist](RELEASE_04_CHECKLIST.md) retains these separate gates.
