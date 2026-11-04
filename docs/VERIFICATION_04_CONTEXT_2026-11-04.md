# 0.4 context-preservation fixes — November 4, 2026

Publication remains on hold. The owner requested improvements using the current
Python/Ollama stack and declined all new model/dependency downloads. These fixes
need no installation, new model, migration or search reindex. Healthy saved
sources need no reimport. Existing saved materials and their citation identities
are not rewritten.

## Defect and changed behavior

The shared evidence budget previously shortened the last quotation to the
remaining character allowance. A statement could survive while its condition
or uncertainty was cut off. It now keeps or omits a whole supplied passage;
later complete passages may still fit. Omitted evidence retains the existing
partial-context indicator. The budget itself is not increased.

Notes previously split every 1,600 characters. They now pack complete canonical
Markdown paragraphs/fenced blocks, retaining exact original body offsets,
line locations, CRLF and intervening blank lines. The target size is soft for
an individual block; oversized blocks are still subject to the hard evidence
budget. Fence parsing preserves tilde/backtick markers, up to three leading
spaces, matching marker lengths and valid closers. This is not a claim of full
CommonMark parsing.

Presentation outline generation now reads complete elements from the source's
saved normalized document. Existing word-split search chunks are no longer
used as its supposedly complete source blocks. Source version, original element
index and exact text offsets determine citations. Source selection and version
checks remain enforced. Chat/search indexing is not migrated or replaced.

Oversized blocks are filtered before representative selection, so an early
large block cannot hide every later fitting candidate. The omission is still
reported. If no complete selected block fits, the job stops before a provider
call with an actionable EN/RU `context_too_large` error. A missing/corrupt saved
document yields `context_unavailable`; the code does not silently fall back to
potentially incomplete search chunks.

The source viewer now interprets stored Python offsets as Unicode code points,
fixing exact citation highlighting when emoji occur before or within a quote.
The underlying saved offsets/text remain unchanged.

## Checks and evidence

- Budget/note tests first reproduced seven failures; after the fix, all eight
  focused integrity cases passed, including English/Russian qualifications.
- Five job-level tests first reproduced partial source input, wrong overflow
  reporting and missing-document fallback. The corrected cases pass before
  provider invocation where required. A further regression covers later fitting
  source/note blocks hidden by oversized representative candidates.
- Sixteen fence scenarios failed before the parser correction; the resulting
  22 fence tests pass, including exact CRLF slices and unclosed blocks.
- Actual React component rendering failed to highlight a Python-offset emoji
  citation before the viewer fix; three exact-range cases and nine mismatch
  guards passed afterward. The persistence smoke uses a real imported document
  and Python-generated mid-paragraph offsets.
- Full local Python suite: **722 passed**, one existing Starlette/httpx
  deprecation warning, **49.12 seconds**. Ruff lint and format passed for
  **183 Python files**. Reports: `test-results/context04-20261104/`.
- TypeScript, 488-key EN/RU parity, changed web/script Prettier and production
  Next.js build passed using installed dependencies only.

The restricted broad API test attempt was interrupted after its pure parser
tests; it is not a pass. The full result above comes from the completed
process-enabled run.

Presentation desktop regression completed successfully with 18 checks,
zero model calls and two synthetic job submissions. Saved edits, drafts,
restart, complete slide-local sources, EN/RU themes and PPTX/PDF exports passed.
Evidence: `test-results/presentations-desktop-1793811602051/result.json`.

Persistence desktop regression completed all 15 scenarios, including real
source import, Unicode quotation offsets, complete service restart, note conflict
recovery, notebook isolation and Russian controls. Its two provider requests use
the local synthetic HTTP server, not Ollama or a cloud model. No replay occurs
after restart. Evidence: `test-results/persistence-1793811760591/result.json`.
Independent code review found no remaining actionable issue in the changed
context, fence or citation-viewer paths. All 244 local links in changed documents
resolved and `git diff --check` passed.

## Remaining limits

These checks establish input preservation and application behavior. Complete
selected blocks are not complete-document coverage: adjacent blocks, pages or
other selected material may still be omitted by the context budget. The UI's
partial-context warning remains necessary.

The frozen 34-claim semantic audit and all recorded failed model responses are
unchanged. Its three false acceptances occurred on complete short passages;
these context repairs do not establish that those mistakes are fixed. The
writer/auditor policy, claim labels and acceptance threshold were not changed,
and no real-model quality pass is claimed. No numeric substring filter was
added: valid unit conversions, rounding and derived quantities cannot be judged
by simple number membership.

Fresh packages/upgrade acceptance are still required for changed production
code. The earlier native run's macOS hosted-runner acquisition failures remain
separate [recorded infrastructure issues](VERIFICATION_04_FINAL_PREPARATION_2026-11-04.md).
No new build dispatch, tag or release follows from this local verification.
