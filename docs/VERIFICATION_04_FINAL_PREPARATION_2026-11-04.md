# 0.4 final preparation — November 4, 2026

Publication remains on hold. This follow-up changes the presentation review
interface and dependency patches; it does not change the Python model policy,
generation, assembly or exporters. Earlier `629312e` packages do not contain
these changes and cannot stand in for a new candidate build.

## Slide-local source review

Each slide now has a collapsible source list containing its full retained
passages, locations and a button opening the existing source viewer. Unrelated
deck citations are excluded. Unsaved, recovered and saved edits show that the
references belong to the original AI outline and need rechecking. No new model
call, factual-certification flag or restored stale claim ledger is introduced.

The expanded desktop test failed against the old interface at the expected
missing-source-block assertion. After the change it passed all 18 scenarios,
using real Python saves/drafts/exports with synthetic saved content and no model
calls. Two job submissions use controlled responses. Coverage includes source
filtering, full qualification text, opening the saved note, unsaved/recovered/
saved edit notices, restart, reorder/delete, PDF/PPTX download, preview,
navigation and English/Light plus Russian/Dark at the minimum window size.

Evidence is retained in
`test-results/presentations-desktop-1793806508928/`. Both new source-panel
screenshots were visually inspected: quotations, source locations and the
Russian edited-content notice are readable and fit their containers. A separate
code review found no actionable issue.

## Dependencies and local checks

The exact dependency updates are Next.js 16.4.4 → **16.4.5** and Electron
44.10.1 → **44.10.2**, with version-bound Next companions only. The
[dependency review](DEPENDENCY_REVIEW_04_2026-11-03.md) records official security
advisories, runtime checksums and the unchanged 15 moderate npm findings, with
zero high/critical findings. The audit is not described as clean.

Passed locally:

- Production web build, TypeScript check and 486-key EN/RU parity.
- Full presentation desktop workflow on Electron 44.10.2.
- Nine packaging glob contracts and the complete installed dependency tree.
- Ruff lint and formatting for 178 Python files; full interface/script Prettier.
- Release version consistency and modified-document local link resolution.
- `git diff --check`.

The restricted environment initially blocked Electron launch and stalled a
Next build. The owned stalled build was stopped; a network/process-enabled build
completed normally. The successful desktop evidence comes from that completed
build, not the failed restricted attempts.

## Model result and remaining release work

The earlier post-reboot EN/RU workflow passed with the existing 16-GB host and
local model. A new isolated-claim experiment nevertheless repeated the first
known semantic false acceptance and stopped after one request; independent
review confirmed unchanged input policy/context, no gold leakage, safe runtime
headroom and complete cleanup. See the
[recorded diagnostic](GROUNDING_04_FOLLOWUP_2026-11-03.md#november-4-isolated-claim-hypothesis-rejected).
No per-claim audit implementation was adopted and the frozen 34-claim score
remains unchanged. The source-review UI improves manual checking, not the
automatic semantic score.

A fresh six-target candidate and its exact installed Windows 0.3 → 0.4 upgrade
must complete before tagging. On November 4, the owner explicitly chose to keep
0.4 in development until automatic factual checking becomes more reliable. The
offered AI-draft beta with manual review was declined. This retains the semantic
quality requirement; passing interface or packaging checks cannot waive it.

The fresh [native workflow 41859887109](https://github.com/woundscode/Racall/actions/runs/41859887109)
was dispatched from `codex/0.4-presentations`, exact source
`1c4408dd4b8d68dfed28921c1382623c74154d77`. The branch push did not change `main`
or create a release tag. The Windows x64 artifact is `13341090588`; its EXE is
159,038,980 bytes, SHA-256
`4dc333eb0097f627b035e8a46699bf5ab4851199105ea34d60ff4e831cf1aef3`.
These identities prepare the upgrade inputs; they do not mean the six-target
workflow or installed-upgrade gate has passed. The upgrade is not dispatched
until GitHub confirms the complete native run succeeded.

The first native attempt completed unsuccessfully because neither macOS job
acquired a hosted runner. Both had runner ID 0 and no executed steps; GitHub's
annotation was "The job was not acquired by Runner of type hosted even after
multiple attempts." This is an infrastructure failure, not a passed macOS build
or a demonstrated application defect. Windows and Linux x64/ARM64 completed
successfully, including their 685 Python tests and packaging checks.

One retry of the failed jobs started at 16:23:14 UTC on the same source and run.
It also finished with a failed run: both macOS jobs were cancelled without a
runner or any executed steps, with the same acquisition annotation. The four
successful Windows/Linux results were carried forward; their full logs each
confirm 685 Python tests, 14 native/upgrade contracts, nine glob contracts and
eight packaged test groups. Four artifacts containing six packages were saved.

The six-platform gate remains **not passed**. No final six-platform candidate
manifest was created, no installed-upgrade workflow was dispatched and no more
automatic retries are scheduled. No tests, target requirements or upgrade
preconditions were relaxed. Raw attempt history, annotations, artifact identities
and the final `audit.final.json` are retained in
`test-results/native04-final-41859887109/`.

The owner also declined downloading the separately proposed NLI fact-checker
and its CPU dependencies. That [experiment](FACT_CHECK_04_EXPERIMENT.md) is
shelved before inference and is not an application requirement. The unresolved
semantic-quality work must be considered separately from both that optional
experiment and the macOS hosted-runner issue.

Proposed public README and documentation wording is prepared separately in the
ignored `test-results/release04-publication-draft/` directory, with original and
draft file hashes. Public download links still point to the published 0.3. The
preview is not a claim that 0.4 is already available.
