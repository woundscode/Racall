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
one-byte-over rejection and retained JSON bounds. The complete suite on the
committed source passes **685 tests in 48.91 seconds**, with one existing
Starlette/httpx deprecation warning. The preceding 684-test run also passed,
before the final extra boundary case. All 66 statements in the changed event
decoder/chunk module are covered. The configured Ruff scope passes for 178
Python files. The changed chunk function has CRAP 3; the unchanged decoder's
pre-existing CRAP 17 is recorded rather than presented as a new refactor.

The post-correction live attempt stopped during empty-prompt model loading,
before the evaluator or any content request. Ollama returned HTTP 500 with
`CUDA error: shared object initialization failed` at `cudaFuncGetAttributes`,
then exited its runner with `0xc0000409`. Starting available RAM was
9,022,394,368 bytes and free VRAM was 9,327 MiB; the continuous minimum available
RAM was 6,911,864,832 bytes. The memory stop guard did not trigger. The cause of
this external CUDA initialization failure is not established by these numbers.
No further inference retry was made.

Cleanup verified the temporary alias was removed, the owned server stopped,
original API model tags and all manifest hashes were unchanged, and the normal
Ollama port remained stopped. Evidence is in
`test-results/live04-20261104-streamfix/`; its initial short socket preflight
also remains recorded. This is an incomplete live check, not a semantic or
transport pass. No model prompt, frozen gold label or recorded failure changed
for this fix.

Native run 41673421566 tested source `4fd974d`: five targets succeeded, while
macOS ARM64 never acquired a hosted runner. Its infrastructure cancellation is
not a passing sixth target or a code-test failure. That source is superseded by
the transport correction; it is not used for a new installed-upgrade claim.
## Current native candidate

Fresh native [run 41836749757](https://github.com/woundscode/Racall/actions/runs/41836749757)
completed successfully on source `629312ebf4f385445cd9026ea0278f42fe50957c`.
Windows/macOS/Linux x64 and ARM64 each passed 685 Python tests, fourteen native
target/upgrade unit tests, nine packaging-glob contracts, eight packaged app
suites, frozen backend/provider checks and the platform's installer checks.
The publish job was skipped.

The [candidate manifest](releases/0.4.0-beta.1-candidate-629312e.json) and
[SHA-256 list](releases/0.4.0-beta.1-candidate-629312e-SHA256SUMS.txt) bind ten
packages from six artifacts to this exact source. Raw job logs and independent
audit are retained in `test-results/native04-transport-41836749757/`.

Installed Windows [upgrade run 41840303042](https://github.com/woundscode/Racall/actions/runs/41840303042)
passed all eight scenarios. It uses artifact `13328365048`, EXE size 158,845,729 bytes and SHA-256
`5d00085d4835478989fb77a96e4cf27e0d47369787dc7b8cf4f5ce9b0a461de7`.
Independent comparison found all 21 original fixture files unchanged in size
and SHA-256 after uninstall, with two expected new job/material files. The
installed executable and profile paths stayed the same. Nine synthetic provider
calls exercised the old/new workflows; restart did not replay generation.
All four upgrade screenshots were visually reviewed, including the old source
version and preserved conversation after restart.

Evidence artifact `13328955744` is 248,209 bytes, SHA-256
`bd34db666923ed863648b85d1179d54d9c9c860a015252597950c4f3b1bd93a1`.
Its downloaded archive hash was verified; raw logs, snapshots and independent
checks are in `test-results/upgrade04-run41840303042/`. This verifies installed
Windows x64 preservation with synthetic responses, not real-model quality or
installed upgrades on macOS/Linux.

## November 4: memory-constrained runtime investigation

Read-only Windows measurements found 17,079,209,984 bytes of physical RAM,
automatic page-file management enabled, and a currently allocated 1,024 MiB
page file on C:. The measured system commit limit was 18,152,951,808 bytes.
Physical availability and commit headroom are different constraints: before
the experiment they were approximately 8.3 GB and 6.0 GB respectively.

One isolated experiment changed only the existing model alias's `use_mmap`
option to `true`, keeping 44 GPU layers, 8,192 context, draft decoding and the
disabled RAM prompt cache. The installed Ollama 0.40.14 runner confirmed
`load_mode = mmap`. A new read-only Windows commit sampler supplemented the
existing physical-memory guard; no normal Ollama settings changed.

During loading, sampled commit headroom fell from 6,007,418,880 to
2,325,217,280 bytes. Physical RAM availability was still 4,977,790,976 bytes.
The 2.5 GB commit reserve stopped the owned runner before loading completed;
its exit 15 followed the sampled stop by about 0.95 seconds. The log contains
no CUDA 303 or `cudaFuncGetAttributes` error. No content inference ran.
This is a guarded, incomplete experiment, not a successful model check,
proof that mmap is ineffective, or a reproduction of the earlier CUDA error.
The provisional 6 GB starting commit budget was not sufficient to complete
this guarded experiment. Actual peak VRAM was not recorded.

Cleanup verified that the temporary alias was removed, original model tags
and manifest hashes were unchanged, and the owned server stopped. Raw evidence
is retained in `test-results/live04-20261104-mmap/`; the native Windows sampler
and page-file snapshot are in `test-results/runtime04-memory-20261104/`.

The stop occurred around 87.2% of the commit limit, before the approximately
90% automatic page-file growth threshold described by
[Microsoft](https://learn.microsoft.com/en-us/troubleshoot/windows-client/performance/introduction-to-the-page-file).
It does not establish that automatic growth is broken. The user explicitly
approved preallocating an 8 GiB page file with a 16 GiB maximum. After saving
the original WMI and registry values, an elevated, bounded script configured
C:\pagefile.sys with InitialSize=8192 and MaximumSize=16384 MiB and disabled
automatic size management. WMI readback confirmed those settings. A guarded
restore action for the original automatic configuration was also prepared.

After the user's manual restart at 17:41:11 Moscow time, WMI confirmed an
allocated 8,192 MiB page file, configured initial/maximum sizes of
8,192/16,384 MiB, and a live commit limit of 25,669,144,576 bytes. The original
values, apply result, post-restart measurements and restore script remain in
`test-results/runtime04-memory-20261104/`. This increases commit headroom,
not GPU memory; it does not establish the cause of the earlier CUDA failure.

A first post-restart harness attempt stopped before model loading because it
looked for the new alias in legacy `manifests`, whereas Ollama writes it to
`manifests-v2/ollama.com`. Its initial cleanup result was incomplete. The exact
owned alias manifest was subsequently verified and removed; both original
manifest hashes were preserved. Evidence is in
`test-results/live04-20261104-postreboot/cleanup-recovery.json`. The corrected
harness covers both manifest roots, captures ownership immediately after
creation, and preserves independent cleanup failures.

The corrected mmap run stopped at the physical-RAM guard: minimum sampled
availability was 2,098,769,920 bytes, while commit headroom remained
8,422,842,368 bytes and free VRAM at least 2,262 MiB. No CUDA 303 occurred.
The alias was removed and both manifest roots restored. A diagnostic parsing
error on Ollama's successful empty DELETE response was retained and corrected
before the next run. Evidence: `test-results/live04-20261104-postreboot-v2/`.

With only `use_mmap=false` changed, the native smoke test then passed on
Ollama 0.40.14: 44 GPU layers, context 8,192, inherited draft length 3 and RAM
prompt cache disabled. Model loading completed in 6.23 seconds; the one short
request returned `READY`, six generated tokens and `done_reason=stop`.
Minimum sampled available RAM was 6,983,331,840 bytes, commit headroom
4,722,757,632 bytes and free VRAM 1,712 MiB. No CUDA/OOM error or resource-stop
occurred. All cleanup steps passed, including the original API-tag comparison;
independent file hashing confirmed both original manifest roots matched the
baseline and the alias was absent. Evidence is in
`test-results/live04-20261104-postreboot-nommap/`.

The short test establishes a working run on this machine, not universal CUDA
stability. A separate cold load then completed the fixed EN/RU presentation
workflow with the same runtime settings. Its four production calls (writer
and auditor per language) finished normally, without retries or output repair.
Both outlines passed independent, exact-hash source review. The subsequent
manual save, offline assembly, PPTX/PDF export and service restart passed in
both languages. All eight rendered PDF pages were visually checked, including
Cyrillic, notes and sources; PPTX text and speaker notes were also inspected.

The Russian writer stream was 1,059,613 bytes, exceeding the former 1,048,576-byte
wire cap and completing under the corrected transport limit. This exercises
the transport fix with a real provider. Minimum sampled available RAM was
6,246,252,544 bytes, commit headroom 3,459,768,320 bytes and free VRAM 1,703 MiB.
There were no CUDA/OOM errors or resource stops in this run. Cleanup stopped
the owned evaluator/server, removed the alias, and restored both original
manifest inventories and API tags. Evidence, source hashes, four artifact
reviews, exports and continuous measurements are retained in
`test-results/live04-20261104-enru-postreboot/`.

These two reviewed examples do not replace the frozen semantic audit. Its
three false acceptances remain unresolved. The evaluator deliberately retains
`quality_verdict=manual_pending` alongside the separate artifact-review verdicts;
generated content remains `validated=false`. No production code or provider
prompt was changed for these runtime experiments. The host-specific GPU/context
parameters were temporary test-alias settings, not new defaults for all users.

## Remaining limits and publication

The frozen semantic audit still fails. The post-fix live EN/RU workflow now
passes the two separately reviewed scenarios on this host; the earlier blocked
attempts remain recorded. The 15 assessed moderate legacy build-tool findings
remain; the two affected newer consumers were fixed.
Previous LibreOffice rendering evidence applies to unchanged rendering code;
Microsoft PowerPoint was not tested. These limits remain in the checklist and
release-note draft instead of being replaced by successful package results.

Only the authorized development branch was pushed. A final read confirmed
`main` at `68d81b15c365dd8f6daa20166e0aafc391a3b340` and the latest public release
still `v0.3.0-beta.1`. No merge, tag or public release was performed.
