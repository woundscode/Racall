# 0.4 Beta candidate verification — November 4, 2026

Candidate source: `9acf6f4050f72fd6c627d2df816ac6b2163c9a2e`.
Publication remains **on hold**. The six native targets and the exact
installed Windows upgrade passed. Preparing and checking this candidate
does not publish, tag or merge it.

## Native packages

[Build run 41879150536](https://github.com/woundscode/Racall/actions/runs/41879150536)
passed all six declared targets at the source above. Each target passed 722
Python tests, 14 native-target/upgrade unit checks, nine packaging-glob checks,
eight packaged application scenario groups, and its native installer acceptance.

| Target        | Result | Candidate packages |
| ------------- | ------ | ------------------ |
| Windows x64   | Passed | EXE                |
| Windows ARM64 | Passed | EXE                |
| macOS x64     | Passed | DMG, ZIP           |
| macOS ARM64   | Passed | DMG, ZIP           |
| Linux x64     | Passed | AppImage, DEB      |
| Linux ARM64   | Passed | AppImage, DEB      |

The verified ten packages are identified by the
[candidate manifest](releases/0.4.0-beta.1-candidate-9acf6f4.json) and
[SHA-256 checksums](releases/0.4.0-beta.1-candidate-9acf6f4-SHA256SUMS.txt).
The manifest records the source, workflow, artifact identities, archive digests,
package sizes and package hashes. These are candidate artifacts, not published
release downloads. Old candidate hashes are not reused.

## Local checks and the preserved smoke failure

The [context-preservation verification](VERIFICATION_04_CONTEXT_2026-11-04.md)
records the Python, source-integrity, Unicode citation, web and persistence
checks. The final local presentation desktop run passed **20 checks**, with
**zero model calls** and two synthetic job submissions. The AI-draft notice was
visually reviewed in English/Light and Russian/Dark. Evidence:
`test-results/presentations-desktop-1793813738440/result.json`.

The earlier candidate `a3d43cb` failed its macOS ARM64 and x64 presentation smoke in
[run 41877368860](https://github.com/woundscode/Racall/actions/runs/41877368860)
after 722 Python tests had passed. A Russian notice check incorrectly expected
assembly to be enabled for an outline with an existing completed job. A local
deterministic reproduction retained the failure. The corrected smoke uses an
independent unused outline for that check, while preserving assertions for the
completed-job duplicate guard and opening its result. No production generation
guard was relaxed. Those failed jobs remain recorded; the earlier workflow was
subsequently cancelled by the replacement run, with Linux ARM64 successful and
the remaining jobs cancelled. Only the fresh six-target run above establishes
this candidate's native acceptance. Raw logs and the independent package audit
are retained in `test-results/native04-disclosure-41879150536/`.

## Installed Windows upgrade

[Upgrade run 41882758598](https://github.com/woundscode/Racall/actions/runs/41882758598)
passed all eight installed Windows x64 0.3 → 0.4 checks using candidate artifact
`13348963061` from run 41879150536. The verified installer identity is:

- File: `Racall-0.4.0-beta.1-win-x64.exe`
- Size: `159043970` bytes
- SHA-256: `19ca5ba73956afdf7ade562dae666a7893038e146e246eb23d21d0279494ba56`

The test harness and package both identify source `9acf6f4`. The installed
executable and profile paths stayed the same. All 21 original fixture files
retained their sizes and SHA-256 hashes after upgrade and uninstall; the final
23 files include two expected new job/material records. Nine synthetic provider
calls exercised the old and new workflows; restart did not replay generation.

All four captured screenshots passed visual review: the 0.3 baseline, the retained
historical citation in 0.4, Studio after upgrade and the original conversation
after restart. Evidence artifact `13350441168` is 248,110 bytes; its downloaded SHA-256 was
verified as `98b8989128756db714eca6187fdf708b44648be20458a03e024a26a23d3f7976`.
Raw evidence, independent checks and visual-review observations are retained in
`test-results/upgrade04-run41882758598/`. This confirms the tested Windows x64
upgrade with synthetic fixtures, not real-model factual quality or installed
upgrades on macOS/Linux.

## Limits retained

These are application and packaging results, not a new real-model evaluation.
The preserved [34-claim audit](GROUNDING_04_FOLLOWUP_2026-11-03.md) still has three
false acceptances, no false rejections, and two of five cases passing. The
isolated full-context semantic failure remains recorded. Context preservation,
the UI notice and this smoke-fixture repair do not establish a semantic fix.
Generated content remains unvalidated and needs source review.

No new model or local runtime dependency was downloaded for these checks.
Automated native acceptance does not establish every device, model or OS
configuration. Windows/macOS packages remain unsigned, macOS is not notarized,
and Microsoft PowerPoint itself remains untested. See the
[release checklist](RELEASE_04_CHECKLIST.md) for remaining publication gates.
