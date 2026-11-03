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
  the user-controlled document name remains metadata.
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
