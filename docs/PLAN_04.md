# 0.4 Beta: editable presentations from sources

Status: implementation authorized and started 2026-11-03. The core workflow is implemented locally; release acceptance remains in [the 0.4 checklist](RELEASE_04_CHECKLIST.md). Publication is on hold.

[Reference review](REFERENCE_PROJECTS.md#refresh-2026-11-03) · [Roadmap](ROADMAP.md) · [Code map](CODE_MAP.md) · [Published 0.3 baseline](releases/0.3.0-beta.1.md)

## User outcome

**Select sources and saved notes → generate and review a presentation outline → Create slides without a model → edit and reorder them → reopen the saved deck → export PPTX or PDF.**

Initial outline generation uses an existing text connection, including Ollama. Python then assembles the approved saved outline without a second model call. Do not require an image model, an Office installation, a new account, a speech engine or a larger GPU. Assembly and exporting an already saved deck must work with the provider offline.

## Release boundary

- One new Studio format: Presentation. Start with short decks, defaulting to about 6–10 slides; establish enforced count and text limits during the first layout prototype.
- A reviewable outline using the selected source versions and saved-note revisions, followed by deterministic Python slide assembly. Both English and Russian output must work.
- A deliberately small slide vocabulary: title, section and title-with-bullets layouts, with speaker notes and source references. Start with two restrained templates; app light/dark theme remains a separate preference.
- Manual editing of titles, bullet text and speaker notes, plus slide reordering and deletion. Save revisions without overwriting the generated baseline or losing an unsaved draft.
- A deck viewer/editor in the existing material library. Keep decks after chat deletion and restore them after app restart.
- Editable PPTX text and shapes, plus readable PDF export. Preserve source references in the export and provide a readable reference list/companion if full provenance cannot fit on a slide.
- Clear partial-context and review-state indicators. Human-edited claims must not retain a misleading model-validation state.

Do not expand this slice to generated images, full infographic/chart generation, a freeform PowerPoint replacement, imports of arbitrary presentations, AI regeneration of individual slides, audio/video, quizzes, new providers, sync or mobile. Those are separate follow-ups. Fix relevant defects found during this workflow without another project-wide refactor.

## Implementation direction

Python owns the deck schema, outline generation, deterministic assembly, citation checks, revision rules, storage and exporters. React/TypeScript presents the editor and calls the API; do not duplicate generation or file-export logic in the frontend.

Introduce a versioned typed presentation document containing stable slide IDs, editable content, speaker notes, source-version/note-revision references, revision identity and template selection. Render preview/PPTX/PDF from that authoritative document. Do not reconstruct the document from Markdown or treat an exported PPTX as the only saved result.

The model returns bounded data validated at the provider boundary. It must not produce a Python program, shell command or executable HTML for Racall to run. Shared layout data should keep preview and exports consistent. Detect content overflow instead of silently clipping or shrinking text until it is unreadable.

Keep substantive feature code under a focused Python `features/presentations/` folder, split by schemas, outline generation, assembly, editing/storage and rendering/export where useful. Reuse:

- `features/context`: explicit selection, evidence budgets and pinned input versions.
- `features/jobs`: idempotent submissions, one generation worker, actual stages, cancellation and explicit retry.
- `features/artifacts`: saved results independent of chat lifetime, legacy opening and the export boundary.
- Existing evidence-reference, language and provider policies.

Outline review is a persisted boundary, not a running job waiting for a person. The outline-generation job completes and saves a revisioned draft with its frozen evidence context. **Create slides / Оформить слайды** starts a separate Python assembly job pinned to the approved saved revision and that context. It preserves the exact accepted text, speaker notes, slide IDs, order, citations and review states, with no second writer or critic. Approval records which content was accepted; it is not factual verification. Manually edited content cannot regain model validation through assembly. Reopening or editing an outline after restart must not call a model. A changed outline or changed source cannot silently replace the approved input; preserve the pinned evidence or require an explicit new attempt.

Current Studio returns Markdown and an answer object. Add an explicit typed material payload with a compatible legacy-reading path rather than inserting many deck-specific branches into the text generator. Keep the original generated deck, user revisions and source snapshots distinguishable.

Implementation uses Python `python-pptx`, ReportLab and fontTools. Bundled DejaVu Sans regular/bold includes its original license and source hashes. Python produces measured layout data for SVG preview, PDF and editable PPTX. PDF/SVG embed the font; PPTX names it and may use font substitution on another computer. Native packaging and external PowerPoint/LibreOffice rendering remain distinct acceptance checks. No office suite is bundled.

## Delivery order

1. **Prove the output format offline.** A fixed EN/RU deck → real editable PPTX and PDF → inspected rendered pages. Establish layout/text limits, citation placement, font handling and packaged dependencies before model orchestration.
2. **Persist and edit that document.** Versioned schema, atomic/revision-aware saves, reopen, reorder/delete, undo or draft recovery where needed. Verify old materials still open.
3. **Connect selected evidence, outline generation and assembly.** Save the generated outline, let the user review/edit it, then explicitly submit a separate Python assembly job pinned to the approved revision and evidence. Release the worker between these jobs. Apply model evidence checks to initial outline titles, bullets and speaker notes; assembly preserves that content and its review state without a second model pass. Never silently substitute changed sources.
4. **Complete the desktop workflow.** Library, viewer/editor, export actions and EN/RU feedback in existing themes. Keep expensive work off the UI request path.
5. **Verify upgrade, package and model behavior.** Deterministic failures, real-model output review, installed 0.3 → 0.4 data preservation and native packages. Record measured limits before preparing release notes or publication.

Each stage should produce a usable, reviewable result before the next is started. No publication is implied by this plan.

## Acceptance criteria

### Evidence and edits

- Excluded sources never enter the model input. An explicit empty selection does not fall back to all sources.
- Each generated factual point can be traced to retained evidence, including after source replacement. Titles and speaker notes receive the same policy as bullets.
- The interface discloses trimmed evidence; a long selected document is not represented as fully read.
- Manual changes preserve the original, advance the edit revision and invalidate the changed content's previous validation state. Stale saves cannot overwrite newer edits.
- Editing, reordering and deletion survive restart. Chat deletion does not delete the deck. Library entries and citations from 0.2/0.3 remain readable.
- Restart while awaiting outline approval retains the draft without replay. Another job can use the worker while the user reviews. Assembly uses exactly the approved saved outline revision, including slide IDs and citations; duplicate confirmation cannot create two assembly jobs.
- Creating slides requires no provider, credentials or embedding call. Provider-setting changes cannot rewrite the accepted content. Assembly retains edited review states and cannot declare manually changed content model-validated.
- Include the recorded 0.3 absence-versus-event and approval-versus-finalization failures in semantic review. A critic acceptance is not a factual guarantee.

### Exports and layout

- PPTX contains individually editable text/shapes. Opening it must not require a model or network request; creating it must not require installed PowerPoint.
- PDF is readable and follows the preview's content/order. Links and citations remain useful outside Racall.
- Inspect real rendered output: English, Cyrillic, long titles, dense bullets, long URLs, notes and minimal decks. Define overflow behavior; no clipped text or missing glyphs.
- Preview and export use the saved revision the user selected. Repeated export is safe; a failed write cannot replace a good saved deck.
- Verify packaging and exports on Windows/macOS/Linux x64 and ARM64. Distinguish native automation, renderer inspection and actual hands-on PowerPoint/LibreOffice checks; do not claim the latter without doing them.

### Jobs and resources

- A duplicate request ID starts at most one job. Queue submission failure leaves a clear terminal failure, not an indefinitely pending material.
- Cancellation prevents late publication. App restart retains interruption and completed outputs without automatically repeating provider calls.
- Retry is explicit and traceable. Retrying a changed input cannot silently reuse a stale outline or alter the original deck.
- Test output validation failures, low-context models, provider disconnects and file-write failures. Keep local inference serial with bounded calls/time/resources; no new model downloads by default.
- Assemble an approved saved outline and export the deck with the provider offline. Deterministic fixtures prove workflow contracts; real-model review separately records initial outline quality and observed limitations. Preventing a second rewrite does not fix first-generation factual errors.

## Publication boundary

Local application metadata is 0.4 Beta, with publication on hold; the public release remains 0.3. The dedicated checklist and draft release notes distinguish implementation from platform/model acceptance. An implementation request does not authorize a GitHub release, remote push or replacement of existing public assets.
