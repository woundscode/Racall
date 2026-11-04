# Published 0.4 Beta verification — November 4, 2026

**[Racall 0.4 Beta](https://github.com/woundscode/Racall/releases/tag/v0.4.0-beta.1)
was published at `2026-11-04T19:18:51Z` and is GitHub Latest.**
The exact released-installer upgrade and release-page review passed. Only the
final main-branch page review remains pending.

## Released source and public integrity

- Annotated tag: `v0.4.0-beta.1`.
- Exact application source: `c6f828ea1a17fde50b0133125c2b12a9616165f7`.
- Fresh six-target tag build and publication:
  [run 41890925811](https://github.com/woundscode/Racall/actions/runs/41890925811), passed.
- Release ID: `434345553`. GitHub Latest points to it; draft and prerelease flags
  are false under the approved Latest presentation. The product retains Beta status.

The fresh tag build passed all six native targets, each with 722 Python tests,
14 native-target/upgrade unit checks, nine packaging-glob checks, eight packaged
application groups and native installer acceptance. Its logs were reviewed
separately from the approved-source candidate's results.

The public set is exactly **ten distribution packages plus `SHA256SUMS.txt`**.
The [release manifest](releases/0.4.0-beta.1-release.json) records the exact
source, target/artifact identities, package sizes and SHA-256 digests.
All uploaded package names, sizes and digests match that fresh tagged build.
The public [checksum file](releases/0.4.0-beta.1-SHA256SUMS.txt) is byte-identical
to the combined CI file, with SHA-256
`717c8111fe03092238fb1b50b6bf5faa2cbece54a2f4473943dcc77816f902a5`.
All eleven anonymous download HEAD requests returned HTTP 200 and the expected
content lengths. `BUILD.json` manifests remain in Actions artifacts rather than
becoming extra public release assets.

The existing 0.3 release metadata and asset identities/content hashes are
unchanged. Download counts may change naturally. Verification evidence is in
`test-results/publication04-published-41890925811/verified-release.json`;
the tag build's manifest and raw evidence are in
`test-results/publication04-tag-41890925811/`.

## Approved-source checks before tagging

[Candidate build 41885468361](https://github.com/woundscode/Racall/actions/runs/41885468361)
passed all six Windows/macOS/Linux x64 and ARM64 targets. Each passed 722 Python
tests, 14 native-target/upgrade unit checks, nine packaging-glob checks, eight
packaged application groups and native installer acceptance.

Attempt 1's macOS ARM64 job never acquired a runner because hosted capacity was
unavailable. Only that target was rerun; it passed. The five successful artifact
hashes were preserved, as recorded in
`test-results/publication04-candidate-41885468361/retry-provenance.json`.
This capacity failure remains distinct from application-test failures.

[Approved-candidate upgrade 41890361060](https://github.com/woundscode/Racall/actions/runs/41890361060)
passed eight installed Windows x64 0.3 → 0.4 checks before tagging. All 21 original
fixture files remained unchanged after uninstall; the final 23 files include
two expected additions. The fixture used nine synthetic provider calls.
Four screenshots passed visual review. The evidence archive is 248,202 bytes,
SHA-256 `bd7cf306533fe234d57170ed469b0cbab5f7ea1e8e6e216c593f0194f44aab7a`.

These candidate checks do not substitute for testing the exact released EXE.
The earlier [held candidate](VERIFICATION_04_CANDIDATE_2026-11-04.md) remains
historical evidence; its hashes are not reused as final-release hashes.

## Exact published-installer upgrade

[Upgrade run 41895993036](https://github.com/woundscode/Racall/actions/runs/41895993036)
was created at `2026-11-04T19:20:30Z` and completed successfully at
`2026-11-04T19:22:11Z`. It used the exact publicly released Windows x64 EXE:
asset `710624865`, matching tag-run artifact `13353159852`.
`Racall-0.4.0-beta.1-win-x64.exe` is 159,044,014 bytes, SHA-256
`941c5057558864677c47fabe6d9cab959cc6cb2bdbfccb34cbb3e2c090893da5`.
The package and test harness identify source `c6f828e`.

All eight installed Windows 0.3 → 0.4 checks passed. All 21 original fixture
files retained their sizes and SHA-256 hashes after uninstall; the final 23
files include two expected additions. The fixture made nine synthetic provider
calls. Four screenshots passed visual review. The evidence archive is 248,128
bytes, SHA-256 `069fdb7fb7bfcebf7c7a38fa34b1213fe6a596b1334c47726f2cb163205f366d`.
Raw evidence and the separate visual record are retained in
`test-results/publication04-released-upgrade-41895993036/`, including
`root-visual-review.json`.

This establishes the checked published-installer upgrade with synthetic data,
not real-model quality or installed upgrades on other operating systems.
The earlier candidate upgrade used a separately built package and retains its
own independent result.

## Main-page review — pending

The public release page passed review: correct title, Latest marker and all
three brand/screenshot images loaded and were visually inspected. GitHub shows
13 asset entries: the eleven uploaded files plus its two automatic source archives.
Those automatic archives are not extra uploaded distribution packages.

Final main-branch README navigation and image rendering remain pending until
the main update. The hero and presentation images are actual Racall 0.4 UI
captures with sample content.

## Known limits

The owner authorized publication with the AI-draft limitation. The
[frozen 34-claim audit](GROUNDING_04_FOLLOWUP_2026-11-03.md) remains unchanged:
three false acceptances, no false rejections, and two of five cases passing.
Application and packaging checks do not certify model factual quality.
Context preservation and more memory do not resolve the demonstrated
full-context semantic errors. Generated titles, bullets and notes need source review.

Windows/macOS packages are unsigned; macOS is not notarized. Native checks do
not cover every device, OS version or AppImage FUSE setup. Microsoft PowerPoint
itself remains untested, and PPTX may substitute fonts. Installed-upgrade checks
cover Windows x64 with synthetic data, not every platform or live model.
