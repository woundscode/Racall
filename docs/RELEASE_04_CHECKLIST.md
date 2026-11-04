# 0.4 Beta acceptance checklist

Publication: **published; exact released-installer upgrade passed; final main-page
review pending**. The approved-source checks and fresh tag build passed. Existing
0.3 release assets remain unchanged. [Published verification](VERIFICATION_04_RELEASE_2026-11-04.md).
[Plan](PLAN_04.md) · [Presentation guide](PRESENTATIONS.md)

**Latest owner decision, November 4:** publish 0.4 Beta with the documented AI
semantic limitation and the established GitHub presentation.
This supersedes the earlier decision to keep development open until automatic
factual checking improves. It changes the accepted beta scope, not the failed
model-quality result. Both decisions remain in the
[model-review record](MODEL_REVIEW_04_DISPOSITION_2026-11-03.md).
The owner's publication request was completed on November 4 at 19:18:51 UTC.
The final tagged source has its own package identities and checks below; the
earlier held candidate's hashes are not relabelled as release hashes.

## Implemented and checked locally

The [context-preservation verification](VERIFICATION_04_CONTEXT_2026-11-04.md)
records **722 passing Python tests**, one existing deprecation warning, and
Ruff lint/format checks for **183 Python files**. TypeScript, EN/RU parity, web
build, presentation desktop checks and persistence checks also passed for that
change. Synthetic provider checks do not establish real-model factual quality.

The final AI-draft notice also passes TypeScript, 488-key EN/RU parity, Prettier
and the production web build. Its local presentation desktop run passes 20 checks
with zero model calls and two synthetic job submissions; the notice was visually
reviewed in English/Light and Russian/Dark. Evidence:
`test-results/presentations-desktop-1793813738440/result.json`.

The first disclosure candidate, `a3d43cb`, exposed a smoke-fixture error on macOS
ARM64 after all 722 Python tests passed: the Russian no-extra-confirmation check
expected assembly to be enabled on an outline that already had a completed job.
A deterministic local reproduction preserved that failure. The corrected smoke
uses an independent unused outline while retaining the completed-job duplicate
guard and accessible result checks; no production generation guard was changed.
The [failed native run](https://github.com/woundscode/Racall/actions/runs/41877368860)
is retained as evidence, not counted as acceptance.

- [x] Python-owned outline generation, typed deck, bounded output and canonical citations.
- [x] One source-anchored fact ledger for titles, bullets and notes, with a
      fallible evidence audit and no automatic repair.
- [x] Saved outline review frees the worker; separate Python assembly preserves
      exact approved text, slide IDs, order, citations and review states without
      another provider or embedding call.
- [x] Pinned source context and outline revision, idempotency and restart without replay.
- [x] Revision conflicts, preserved originals, recovery drafts and stale-save rejection.
- [x] Slide editing, reorder/delete, Light/Dark templates and English/Russian controls.
- [x] Complete saved source passages beside slides, source opening and original-reference
      notices for unsaved, saved and recovered edits.
- [x] PPTX/PDF exports, SVG preview, editable PPTX text/notes and embedded PDF/SVG Cyrillic fonts.
- [x] Whole source/note blocks, valid Markdown fence boundaries and partial-context
      warnings; unavailable or wholly oversized context fails before inference.
- [x] Exact source quotation highlighting with Python Unicode offsets, including emoji.
- [x] Interrupted outline recovery, deleted-slide claim cleanup and atomic job release.
- [x] Separate eight-MiB SSE wire budget with ordinary JSON, answer/event bounds,
      cancellation, deadlines and completion checks preserved.
- [x] Electron 44.10.2 and Next.js 16.4.5 pass local build/desktop checks. Two
      affected minimatch consumers use exact scoped overrides; the
      [dependency assessment](DEPENDENCY_REVIEW_04_2026-11-03.md) retains 15
      moderate build-tool findings rather than claiming zero findings.

## Publication gates for the final candidate

- [x] Owner accepts the known semantic limitation for this beta, with honest
      source-review guidance and no factual-certification claim.
- [x] Owner explicitly authorizes 0.4 publication, its release tag, the main-branch
      update and the established Latest presentation.
- [x] Release-note draft, presentation guide and model-review disposition record
      that decision without changing historical failed scores.
- [x] Fresh Windows/macOS/Linux x64 and ARM64 matrix passes for source
      `9acf6f4050f72fd6c627d2df816ac6b2163c9a2e`, including packaged resources,
      desktop acceptance, exports and native installer checks.
      [Native run 41879150536](https://github.com/woundscode/Racall/actions/runs/41879150536).
- [x] All ten candidate packages verified with exact source identity,
      [manifest](releases/0.4.0-beta.1-candidate-9acf6f4.json) and
      [SHA-256 checksums](releases/0.4.0-beta.1-candidate-9acf6f4-SHA256SUMS.txt).
- [x] Installed Windows x64 0.3 → 0.4 acceptance uses the exact verified candidate
      package and preserves notebooks, materials, revisions and historical citations,
      including after uninstall. [Run 41882758598](https://github.com/woundscode/Racall/actions/runs/41882758598)
      passed eight checks with the exact Windows x64 artifact. All 21 original
      fixture files remained byte-identical after uninstall; four screenshots
      passed visual review.
- [x] Final approved-policy source `c6f828ea1a17fde50b0133125c2b12a9616165f7`
      passes all six native targets in [run 41885468361](https://github.com/woundscode/Racall/actions/runs/41885468361)
      and its exact installed Windows 0.3 → 0.4 upgrade in
      [run 41890361060](https://github.com/woundscode/Racall/actions/runs/41890361060)
      before tagging. The upgrade passed eight checks and preserved all 21 originals.
- [x] Fresh tagged source passes all six builds and publishes all ten packages
      plus checksums with the approved notes and Latest presentation in
      [run 41890925811](https://github.com/woundscode/Racall/actions/runs/41890925811).
- [x] Public asset names/sizes/digests, tag/source identity and preserved 0.3 assets
      verified. All eleven anonymous download URLs return HTTP 200.
      [Release manifest](releases/0.4.0-beta.1-release.json) ·
      [Exact public checksums](releases/0.4.0-beta.1-SHA256SUMS.txt).
- [x] Exact published Windows x64 EXE passes the separate installed upgrade in
      [run 41895993036](https://github.com/woundscode/Racall/actions/runs/41895993036):
      eight checks, all 21 original files unchanged after uninstall, two expected
      additions and nine synthetic provider calls. All four screenshots passed review.
- [x] Public release page shows the correct title and Latest marker; three
      brand/screenshot images loaded and passed visual review. Its 13 asset entries
      comprise eleven uploads and GitHub's two automatic source archives.
- [ ] Review the final main README's links, images and GitHub presentation.

The [earlier candidate verification](VERIFICATION_04_CANDIDATE_2026-11-04.md)
records six successful native targets, package identity and the exact successful
installed upgrade for the held `9acf6f4` candidate. Publication used the separately
verified approved source and fresh tagged packages recorded above.
The earlier
[native run 41859887109](https://github.com/woundscode/Racall/actions/runs/41859887109)
passed Windows and Linux x64/ARM64, but neither macOS job acquired a hosted runner.
It did not pass the six-target gate and is not substituted for the current
successful run; see the
[preparation record](VERIFICATION_04_FINAL_PREPARATION_2026-11-04.md).

## Open model-quality issue — accepted beta limitation

- [ ] Original automatic factual-quality criterion: source-faithful initial
      outlines and reliable rejection of unsupported claims in both languages.
      This remains unresolved; the latest owner decision allows the beta to ship
      with the limitation rather than marking this criterion passed.

The [frozen audit](GROUNDING_04_FOLLOWUP_2026-11-03.md) evaluated 34 claims:
all 23 valid claims were accepted, but three of eleven invalid controls were also
accepted. There were no false rejections and two of five cases passed. The
single-claim isolation experiment repeated its first semantic failure with the
full short passage. Neither splitting the audit nor the context-preservation
repair establishes a fix for those errors.

A separate [bounded EN/RU workflow](VERIFICATION_04_GROUNDING_2026-11-03.md)
completed four production calls, outline/deck reviews, manual save, offline
assembly, export and restart; eight rendered PDF pages passed visual review.
That establishes the tested workflow on one Windows/model configuration, not a
replacement score for the frozen audit. Increased Windows commit headroom helped
the model load, but memory alone does not correct full-context semantic mistakes.
A stronger model may improve quality; no model or hardware choice guarantees it.

Generated presentation content stays `validated=false`. User approval and Python
assembly do not certify an initial claim. Review titles, bullets and speaker
notes against their sources before sharing; manual review can also miss errors.
The optional independent-verifier experiment remains shelved after the owner
declined new downloads. It is not a required dependency or a proven fix.

## Historical package and compatibility evidence

- Source `629312e` passed 685 Python tests and the
  [six-target native run 41836749757](https://github.com/woundscode/Racall/actions/runs/41836749757).
  Its ten packages have a [manifest](releases/0.4.0-beta.1-candidate-629312e.json)
  and [SHA-256 checksums](releases/0.4.0-beta.1-candidate-629312e-SHA256SUMS.txt).
- Its [installed upgrade run 41840303042](https://github.com/woundscode/Racall/actions/runs/41840303042)
  passed eight checks and preserved all 21 original fixture files byte-for-byte
  after uninstall. Nine synthetic provider calls and two expected new files
  exercised preservation and interface behavior, not model factual reliability.
  [Recorded evidence](VERIFICATION_04_GROUNDING_2026-11-03.md) includes package
  identity, original hashes and four reviewed screenshots.
- Source `3c22f58` passed 604 tests, six native targets, package verification and
  an installed upgrade ([record](VERIFICATION_04_CLOSURE_2026-11-03.md)). The later
  `4fd974d` run passed five targets; macOS ARM64 did not acquire a hosted runner.
- [LibreOffice compatibility checks](PRESENTATION_COMPATIBILITY_04.md) covered six
  EN/RU cases and an editable round trip; all 66 rendered pages from `3c22f58`
  were visually reviewed. Microsoft PowerPoint itself remains untested, and
  PPTX font substitution remains possible.

These results remain valid historical evidence. No old package hash or successful
workflow is reused as the final candidate's identity or semantic-quality score.
