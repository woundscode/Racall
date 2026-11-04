# Editable presentations — 0.4 Beta preparation

The presentation workflow is implemented for 0.4 Beta. The owner accepts its
known AI limitation; publication still awaits final technical checks in the
[acceptance checklist](RELEASE_04_CHECKLIST.md). This is not a published release.

**Treat generated slides as drafts.** The evidence critic can accept unsupported
claims. Review titles, bullets and speaker notes against their saved sources
before sharing. More memory or a stronger model is not a factual guarantee.

## Create and review

Choose Presentation in Studio, select sources and saved notes, then generate an
outline. Generation uses the configured text connection. Once the outline is
ready, the generation worker is free for other work; the outline stays saved
while you review it or close the app.

Open **Sources for this slide** (**Источники этого слайда**) beneath a slide to
read its full saved passages and their locations. Select a source title to open
the retained source or note revision. These references belong to the original
AI outline: after editing, check that they still support your wording. The
notice appears for unsaved changes as well as saved or recovered edits; source
quotations are not shortened to a model-selected highlight.

Edit slide titles, bullet points and speaker notes, reorder/delete slides, and
choose Light or Dark as the presentation template. This template is independent
of the application theme. Save changes before selecting **Create slides**
(**Оформить слайды** in Russian). Python assembles the saved outline into a deck,
preserving its exact titles, bullets, speaker notes, slide IDs, order, citations
and review states. This is a separate job pinned to the approved revision and
original source context. It does not ask a model to rewrite the content or run a
second critic, and works with the model disconnected. Changed source versions
require a new outline rather than silently replacing the evidence.

The first version supports 1–12 slides, titles up to 160 characters, up to five
220-character bullets per slide and 1,200-character speaker notes. Text may still
exceed the visual layout: the preview/export reports overflow so you can shorten
it. It never silently drops text. Adding new slides and AI revision of a single
slide are later features.

## Save and recover

Edits are written to a separate local draft after a short pause, including a
temporarily blank field. Save creates a new document revision; conflicting saves
cannot replace newer data. Reopening restores an unfinished draft. Discard asks
for confirmation. Prior saved revisions remain in the notebook's
`materials/presentation-revisions/` directory and are readable through the API.

Generated and manually edited slide content remain distinguishable. Editing
content clears its previous validation state; changing template or order does not
change factual content. The document name is user-controlled metadata, not a
verified factual claim. Titles, bullets and speaker notes generated for the
initial outline go through a fallible AI evidence critic. It can reject a draft,
but acceptance is not factual certification: newly generated presentation answers
always have `validated=false`. Creating slides does not promote that status.
Manually edited content stays marked as edited. Review facts and citations before
sharing a deck, including the speaker notes.

One source-anchored fact ledger supplies titles, bullets and speaker notes. The
structured evidence audit rejects malformed support or negative verdicts without
automatic repair, but remains a model judgment. In the preserved
[34-claim evaluation](GROUNDING_04_FOLLOWUP_2026-11-03.md), all 23 valid claims
were accepted and three of eleven invalid controls were also accepted. The
[model-review record](MODEL_REVIEW_04_DISPOSITION_2026-11-03.md) retains those
failures and the owner's decision to accept this limitation for the beta.

Python assembly prevents a second model rewrite; it does not verify the initial
outline. Review speaker notes as well as visible bullets, because both appear in
exports. Generated evidence markers such as `[E1, E2]` use the saved source
numbers; user edits and original quotations are not rewritten. The workflow
uses your configured model and does not require an additional verifier download.

The preview shows the saved revision. Save current edits before export. Decks
remain in Reports independently of the originating chat.

Outline generation keeps complete blocks from saved sources and notes. If no
whole block fits the context limit, choose shorter material or prepare a shorter
note that retains the relevant conditions; the app does not send a cut-off
prefix instead. Missing saved source text requires reimport. Other blocks may
still be omitted, so the partial-context warning does not imply that the entire
document was reviewed. These input checks do not verify a model's paraphrase.

## Export

PPTX contains editable text and shapes. PDF and SVG preview use the same Python
layout and embed a DejaVu Sans subset, including Cyrillic glyphs. PPTX specifies
DejaVu Sans without embedding it; PowerPoint or another editor may substitute a
font. Check typography in the recipient's application, or use PDF for fixed
appearance. Speaker notes and exact evidence quotations are retained in the
export, including printable appendix pages.

Export uses saved data only and works with the model disconnected. No Office
installation or image model is required to create the files. Unsupported glyphs,
missing citation records or overflow produce explicit errors.

## Code ownership

Python `features/presentations` owns schemas, outline provider-output validation,
outline generation, deterministic assembly, revisions/drafts, layout, fonts and exporters. Shared jobs preserve
idempotency, cancellation, explicit retry and no automatic model replay after a
restart. The React editor presents these API operations and the server-rendered
preview; it does not build presentations or execute model-generated code.

Checks: `npm run test:presentations` for isolated desktop editing, restart and
exports; `tests/test_presentation_*.py` for schema, storage, generation, API and
file contracts. Native packaging has separate release gates; the unresolved
real-model factual-quality criterion remains a documented beta limitation.
