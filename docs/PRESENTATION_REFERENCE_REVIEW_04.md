# Presentation workflow reference check — 2026-11-03

The owner requested the reference applications' approach instead of choosing a
new excerpt-versus-paraphrase mode. This is a source/documentation review, not a
runtime quality test of those applications. No upstream code was imported.

| Reference | Inspected behavior | What this establishes |
| --- | --- | --- |
| [Open Notebook](https://github.com/lfnovo/open-notebook/blob/a0f6f3081ae06328f0a451b3a3ef2959ca25721d/open_notebook/graphs/transformation.py) | Model-generated text transformations; checks nonempty output and completion limits | Useful source-to-text workflow; this path is not a presentation editor or semantic proof |
| [SurfSense](https://github.com/MODSetter/SurfSense/blob/f41e037fd704a0e4418e74117734d13cffdd1a2f/surfsense_local/backend/worker/studio/office/pipeline.py) | Office generation runs model-written Python; [repair attempts](https://github.com/MODSetter/SurfSense/blob/f41e037fd704a0e4418e74117734d13cffdd1a2f/surfsense_local/backend/worker/studio/office/script_attempts.py) address script execution failures | A generation/export implementation, not evidence that factual accuracy is guaranteed |
| [Open-NotebookLM](https://github.com/Anionex/Open-NotebookLM/blob/36ecc9336eb5fb9b9e91e48a057ef9fb010ea50a/workflow_engine/workflow/wf_paper2ppt_parallel_consistent_style.py) | AI outline, revision and image-slide stages; this inspected workflow disables the PPTX output path | Staged review is useful; do not infer editable PPTX quality from an export helper's existence |
| [Google Slide Deck help](https://support.google.com/gemininotebook/answer/16757456?hl=en) | Source/language selection, AI generation, optional outline review, revisions and PDF/PPTX download | Public product behavior, not implementation evidence. The page warns about factual/visual inaccuracies; the outline-review feature currently requires Google AI Ultra |

The default-branch SHAs for SurfSense and Open Notebook were rechecked and match
the pinned November 3 review. The broader [reference record](REFERENCE_PROJECTS.md)
retains prior snapshots and implementation limitations.

## Racall decision

Keep the familiar generative outline and manual editor. Avoid an extra content-mode
selector. Python assembles the saved accepted content without another rewrite;
sources remain accessible for comparison, including their saved quotations.

The AI critic remains a useful rejection filter but cannot assign a factual
certification to a presentation. New outlines are explicitly uncertified, as are
their assembled decks. Legacy stored files are not rewritten just to change a
label. The editor consistently asks users to compare points and speaker notes
with sources, regardless of a historical answer's validation flag.

This fixes false certification, not model reasoning. The earlier live EN/RU
counterexamples remain recorded failures. Reference applications' similar
limitations do not turn those failures into passes or justify a reliability claim.
