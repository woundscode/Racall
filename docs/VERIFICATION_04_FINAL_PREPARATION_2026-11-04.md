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
must complete before tagging. The release scope also needs an explicit decision
about shipping AI drafts with this documented model-quality limitation. Do not
silently convert that decision into a passing factual-reliability claim.
