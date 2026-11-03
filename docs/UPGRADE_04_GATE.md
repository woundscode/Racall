# Installed 0.3 to 0.4 upgrade gate

This document describes the prepared gate, **not a completed installed upgrade**.
Local contract tests never execute an installer. An actual run requires the
candidate source and harness to be available on GitHub and a successful native
build. No candidate run ID, artifact ID or source SHA is invented in the gate.

Repository identity is pinned to GitHub repository ID **1385819102**, currently
`woundscode/Racall`, in `apps/shared/repository.json`. Provenance checks both the
build repository and its head repository IDs; the hosted-runner guard checks
`GITHUB_REPOSITORY_ID`. A rename keeps that identity, while a fork with the same
name cannot substitute its build. The descriptor's current name supplies the
published baseline download URL.

## Immutable baseline and explicit candidate

The baseline is the published `Racall-0.3.0-beta.1-win-x64.exe`, 153,279,432 bytes,
SHA-256 `b968cb0f91f0ddfba481853c2949e0978d7d603a9634b18be6d76fde91dc1eb9`.
Its source and publication are documented in
[the historical 0.3 release verification](VERIFICATION_03_RELEASE_2026-10-25.md).
That report remains evidence for 0.2 → 0.3; it does not prove 0.3 → 0.4.

The manual **Check installed 0.3 to candidate upgrade** workflow takes five
required inputs from the completed candidate build:

| Input                | Where to obtain it                                                                    |
| -------------------- | ------------------------------------------------------------------------------------- |
| `candidate_source`   | Full 40-character commit SHA from the successful `build.yml` run and its `BUILD.json` |
| `candidate_run`      | That run's numeric GitHub Actions ID                                                  |
| `candidate_artifact` | Numeric ID of its `Racall-win-x64` artifact                                           |
| `candidate_size`     | Windows x64 EXE's exact byte count in `BUILD.json`                                    |
| `candidate_sha256`   | Windows x64 EXE's SHA-256 in `BUILD.json`                                             |

Select a harness ref whose `apps/shared/release.json` has the candidate's version
and publication state. The current 0.4 candidate remains `publication: hold`.
Use a `push` or `workflow_dispatch` source build, not a pull request merge build.
GitHub reports PR head and merge SHAs differently; this gate deliberately uses an
explicit source commit throughout.

Before download, the workflow checks the repository, workflow path, completed
successful result, source SHA, artifact ID, artifact name, expiry and associated
run. Before any installation, the harness independently checks `BUILD.json`, the
EXE's byte count and SHA-256, and `SHA256SUMS.txt` against the explicit inputs. The
candidate manifest cannot change the permitted executable name or package list.
The baseline download is also checked against its pinned size and digest.

## Disposable-host boundary and coverage

Installation requires GitHub Actions on a **GitHub-hosted Windows x64 runner**,
the exact repository/workspace, a candidate directory beneath `RUNNER_TEMP`, and
no existing Racall default profile. Self-hosted runners and local workstations are
rejected. Do not bypass these guards to run the scenario on a user's computer.

The installed baseline creates real records through its API: notes, chat,
versioned sources, a saved Research report, a completed Studio job and material,
trash, language and theme settings. A synthetic provider supplies deterministic
answers; no Ollama model, GPU or cloud credentials are involved.

The candidate installs over the registered baseline directory. The gate checks
old authoritative file hashes, historical citations and original sources, legacy
report export, baseline Studio material/job/export, EN/RU, light/dark and new
Studio generation. Restart must not replay inference. Finally, uninstall must
remove the application while preserving fixture knowledge. Evidence includes
provenance, pinned inputs, both runtime versions, snapshots, screenshots and logs.

This does not cover real model quality or an installed upgrade on macOS/Linux.
New 0.4 presentation editing/export is covered separately by the native packaged
presentation smoke test.

## Native packaging checks

The existing build matrix still contains Windows x64/ARM64, macOS x64/ARM64 and
Linux x64/ARM64. Every target runs the Python tests and packaged smoke suite,
including presentations. The Python bundle collects python-pptx/ReportLab data,
fontTools tables, bundled DejaVu fonts and relevant distribution metadata. The
font paths use `os.pathsep`, preserving native PyInstaller argument syntax.

Local Windows verification cannot substitute for the five other native jobs.
Their result remains pending until an authorized source push/build. This gate
does not publish, create a tag or change release approval.

## Local verification log

- Inspected the old pinned 0.2 → 0.3 harness and historical published 0.3 hashes.
- Added failing contract tests before parameterizing candidate inputs.
- Replaced the obsolete candidate constants with required runtime inputs and
  provenance checks; kept the disposable-host and profile guards.
- Added baseline Studio job/material preservation to the installed scenario.
- Added the upgrade contracts to the native build workflow's existing Node test
  step. Ran all fourteen native-target/upgrade tests, JavaScript syntax checks,
  Prettier and `git diff --check`; they passed. The upgrade tests use synthetic
  bytes only and never launch Electron or an installer. The installed scenario
  and remote workflows have not been run here.
