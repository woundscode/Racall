# Editable presentations — 0.4 development

The presentation workflow is implemented locally for 0.4 Beta. See the
[acceptance checklist](RELEASE_04_CHECKLIST.md); this is not a published release.

## Create and review

Choose Presentation in Studio, select sources and saved notes, then generate an
outline. Generation uses the configured text connection. Once the outline is
ready, the generation worker is free for other work; the outline stays saved
while you review it or close the app.

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
initial outline go through the evidence critic, whose known limitations still
apply. Creating slides carries forward the outline's existing review state; it
does not certify the facts again. Manually edited content stays marked as edited
and is not given a new model-validated status. Review facts and citations before
sharing a deck.

The [first live 0.4 Ollama check](MODEL_EVALUATION_04_2026-11-03.md) found a
speaker-note inference that the critic incorrectly accepted in the earlier
two-generation workflow. Python assembly now preserves the approved content
without a second model rewrite. Initial outline generation can still make factual
errors, and approval does not verify them. Review speaker notes as well as visible
bullets; they are included in PPTX and PDF exports.

The [follow-up check](MODEL_EVALUATION_04_FOLLOWUP_2026-11-03.md) completed both
language requests without a RAM stop. English passed independent review, while
the Russian outline incorrectly changed "results have not been received" into
"results are absent". That model-quality gate remains failed. A separate,
explicitly corrected copy passed offline assembly, export and restart checks.
Generated evidence markers such as `[E1, E2]` are now formatted using the saved
source numbers before outline review; user edits and original quotations are
not rewritten.

The preview shows the saved revision. Save current edits before export. Decks
remain in Reports independently of the originating chat.

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
file contracts. Real-model quality and six-platform packaging are separate
acceptance gates.
