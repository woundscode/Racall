# 0.4 candidate follow-up — 2026-11-03

Publication remains **hold**. This follows the historical
[native verification](VERIFICATION_04_NATIVE_2026-11-03.md) without replacing its
tested source or original evidence. No merge, tag or release publication is authorized.

Candidate source: `3c22f580ad09078917c86075adc70bf17628faa0` on
`codex/0.4-presentations`.

## Changes and local checks

- Kept the reference-style AI outline → review/edit → saved slide assembly workflow.
  The proposed extra excerpt mode was withdrawn after the owner's reference-based
  preference. [Reference review](PRESENTATION_REFERENCE_REVIEW_04.md).
- Removed automatic factual certification from new AI presentation answers.
  Recorded model false positives are replayed unchanged and must remain uncertified.
  Approval, edits and export cannot promote new drafts to validated facts; legacy
  saved files remain byte-stable on read. This does not correct the model's wording.
- Updated compatible runtime/build dependencies, including Electron 44.10.1 and
  Next 16.4.4. [Security assessment](DEPENDENCY_REVIEW_04_2026-11-03.md).
- Added an independent LibreOffice conversion/round-trip gate, isolated from the
  user's computer. Its failure tests reject lost text, notes and invalid geometry.

Local full suite: **604 Python tests passed in 43.25 seconds**. One existing
Starlette/httpx deprecation warning remains. Ruff lint/format, Prettier, TypeScript,
14 native-target/upgrade contract tests, 484-key EN/RU catalog checks, release
metadata, installer catalog and Next production/static build passed.

The first sandboxed TestClient run stalled in `asyncio`'s loopback socketpair,
before application startup. The sandboxed Next child process also stalled.
The owned build process was stopped and both checks passed outside the sandbox,
using test directories inside the repository. No application/profile migration,
local Office installation, WSL/Docker load or new model inference was used here.

## Independent office rendering

The [initial LibreOffice run](https://github.com/woundscode/Racall/actions/runs/41662366119)
passed on `4abe9c1063cd313c8dc22125501b3fea5a458b0a`. The
[candidate run](https://github.com/woundscode/Racall/actions/runs/41662832717)
also passed on the source above. Six cases cover EN/RU, both templates and supported
boundary text. Each checks native PDF, PPTX opened in LibreOffice, and a
PPTX → ODP → PPTX round trip: **22 pages in each path, 66 rendered pages**.

The root agent visually reviewed all 66 initial-run pages using six labeled
contact sheets. Text, Cyrillic glyphs, themes, source appendices and speaker notes
were readable, without clipping, overlap or missing glyphs. The boundary fixture's
intentionally incomplete final note is preserved equally in all three outputs.
This is agent visual review, not owner hands-on acceptance. The
[compatibility record](PRESENTATION_COMPATIBILITY_04.md) identifies versions,
artifact hashes and candidate-image comparison.

LibreOffice 24.2.7.2 and Poppler 24.02.0 were tested on Ubuntu 24.04. System DejaVu
Sans files have different hashes from Racall's bundled fonts; the tests passed
with those recorded fonts. Microsoft PowerPoint and other font substitutions
remain untested.

## Candidate packaging and installed upgrade

The [six-target build](https://github.com/woundscode/Racall/actions/runs/41662836801)
completed successfully for the source above; its publication job was skipped.
Each target passed **604 Python tests**, static/contract checks, native packaging,
all eight packaged desktop scenarios, frozen-backend/provider checks and the
platform-specific installer check.

| Platform | x64 | ARM64 | Produced packages |
| --- | --- | --- | --- |
| Windows | Passed | Passed | EXE for each architecture |
| macOS | Passed | Passed | DMG and ZIP for each architecture |
| Linux | Passed | Passed | AppImage and DEB for each architecture |

The root agent independently compared all six stdout manifests with their raw job
logs and GitHub artifact metadata, checking source, version, publication hold,
artifact association, sizes and SHA-256 entries for all ten packages. The
[candidate manifest](releases/0.4.0-beta.1-candidate-3c22f58.json) and
[combined checksums](releases/0.4.0-beta.1-candidate-3c22f58-SHA256SUMS.txt)
identify this build separately from the older candidate. Binaries were not all
downloaded locally; these checks bind hosted build evidence, not a claim of an
independent local hash of every package.

Windows x64 candidate: `Racall-0.4.0-beta.1-win-x64.exe`, **158,836,641 bytes**,
SHA-256 `c7b91236758cb03f7c868389a8147b36fa09af56c605717a290300e67a10f88d`,
artifact `13245556202`. The
[installed upgrade](https://github.com/woundscode/Racall/actions/runs/41666757073)
completed successfully with those exact inputs after the native run completed.
The published 0.3 installer was also verified against its pinned size/hash before
use. Evidence artifact: `13246517538` (`upgrade-win-x64`, 248,257 bytes).

The installed 0.3 → 0.4 check passed all eight scenarios with zero errors and nine
synthetic provider calls. The executable directory and application profile were
reused. Old chats, versioned sources, notes, Research, Studio materials/jobs and
trash remained readable; historical citations kept their original evidence.
EN/RU, themes, a new note-only Studio material and a full restart worked without
inference replay. Uninstall removed the app and retained knowledge.

Both the monitoring agent and root independently compared the before/after file
maps: **21/21 original files retained identical sizes and SHA-256**, with only the
expected new job and material added (23 retained files). The root agent also
visually inspected all four screenshots: baseline 0.3, upgraded historical
citation, upgraded Studio and restarted 0.4. The historical report's original raw
location metadata remains visible because its stored Markdown was preserved;
this is not a new rendering or migration claim. No local installation was run.

Evidence is retained in `test-results/native04-closure-41662836801/` and
`test-results/upgrade04-run41666757073/`. The hosted Windows x64 synthetic-provider
check is not real-model evaluation or a physical macOS/Linux upgrade test.

## Remaining quality limits

The live-model factual failures remain recorded failures. Removing the validation
flag fixes false certification; it does not make the unsupported paraphrase true.
See the [model-review disposition](MODEL_REVIEW_04_DISPOSITION_2026-11-03.md).
No new model run was needed to test an unchanged prompt/critic with exact recorded
responses, and no retry-until-pass claim is made.

The dependency audit retains 15 moderate findings associated with one minimatch
advisory in build tooling. Its reviewed usage does not enable the reported
optimization mode or accept notebook/user input as glob patterns. This is a
documented scoped assessment, not a patched or zero-finding audit. Reassess if
build inputs/options or upstream advisories change.

The prepared beta workflow requires user review of generated content. The original
automatic factual-quality criterion remains unmet; publication still needs an
explicit owner decision with those limits visible.
