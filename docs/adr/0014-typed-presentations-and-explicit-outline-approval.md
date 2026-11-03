# Typed presentations and explicit outline approval

Status: implemented for local 0.4 development, 2026-11-03; publication on hold.

## Context

Studio 0.3 stores Markdown materials. Editable presentations need stable slide
identity, source references, revisions and several consistent renderers. A person
may review an outline much later than its generation finishes.

## Decision

- A versioned Python/Pydantic presentation document is authoritative inside the
  existing material record. Markdown is a readable derivative, not the deck schema.
- Outline generation completes normally. Python slide assembly is a separate
  explicit job, pinned to the approved saved outline revision and original source
  context. It preserves accepted text, speaker notes, slide IDs, order, citations
  and review states without a second writer or critic. The worker never waits for
  a person's approval. Existing cancellation and no-replay behavior apply to both
  stages; assembly requires no provider connection or credentials.
- Provider output is bounded slide data. It cannot become a script or executable
  HTML. Initial outline titles, bullets and notes pass the existing evidence critic;
  the user-controlled document name remains metadata. The critic is a rejection
  filter, not factual certification. New presentation answers have `validated=false`.
- Python saves edits under the store lock with expected revisions. Prior material
  snapshots are retained before atomically replacing the current revision. A failed
  current write leaves the prior revision authoritative. Drafts have separate files
  and may contain temporarily incomplete text, while explicit Save validates a
  usable document.
- Content edits mark affected slides edited and clear material validation. Moving
  slides and changing templates do not change factual content or source references.
- Approval records the accepted outline revision and its content digest. It is an
  integrity marker, not a factual verdict. Assembly carries prior review state
  forward and cannot assign a new model-validated status to manually edited text.
- One Python layout supplies SVG, PDF and PPTX. Bundled redistributable fonts make
  PDF/SVG self-contained; PPTX uses editable text and shapes with a named font.

## Consequences

The existing jobs/material library is reused without a new queue or database.
React handles editor state, navigation guards and API requests only. Assembly and
exports need no model or Office installation. Source changes invalidate later work rather than
silently updating an approved outline. Exact PPTX typography remains dependent on
the recipient's fonts/editor and needs separate native rendering acceptance.

Verification must cover rejected/stale edits, restart drafts, canonical evidence,
the two jobs, exact assembly preservation without provider calls, offline exports,
EN/RU glyphs and bounded layout. See the [acceptance checklist](../RELEASE_04_CHECKLIST.md)
for measured status. Provider fixtures do not establish factual quality on real
models; initial outline errors and known critic limitations remain.

## Reference-workflow follow-up, 2026-11-03

The owner asked to follow the reference applications when choosing between exact
excerpts and AI paraphrasing. Keep one generative workflow: selected evidence →
AI outline → human review/edit → deterministic assembly/export. Do not introduce
an additional exact-excerpts mode or silently change the language/translation
behavior. [Reference evidence](../PRESENTATION_REFERENCE_REVIEW_04.md) distinguishes
actual inspected code from product documentation.

Recorded EN/RU writer/critic pairs reproduce false positive verification. Tests
now require these outputs to remain uncertified; they do not establish that the
unsupported paraphrases themselves have been corrected. Historical live factual
failures remain failed, independently of the certification fix or export checks.

## Fact-ledger and audit follow-up, 2026-11-03

Initial generation now produces a source-anchored fact ledger. Slide titles,
bullets and speaker notes refer to those exact fact texts, so notes do not receive
an independent paraphrase. One structured audit checks every server-labelled
claim against its full cited evidence passages, supplied once per evidence ID.
Malformed responses and negative/uncertain verdicts fail without automatic repair
or rewriting. These checks remain fallible and do not change `validated=false`,
manual review or deterministic assembly. The bounded regression/holdout
evaluation and current pending live status are documented in the
[grounding follow-up](../GROUNDING_04_FOLLOWUP_2026-11-03.md).
