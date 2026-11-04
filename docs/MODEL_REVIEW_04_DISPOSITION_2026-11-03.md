# 0.4 model-review disposition — November 3, 2026

**Publication remains on hold. The automatic factual-quality criterion remains
unmet; this record does not close it or record owner acceptance.** Completed
evaluation and workflow checks are distinguished from model-quality results below.

## Workflow decision and references

Following the owner's direction to use the reference applications' approach,
Racall retains **source-based AI outline → user review/edit → deterministic
Python assembly/export**. A proposed exact-excerpts mode was not adopted. Review
means the user can inspect and correct titles, bullets and speaker notes against
retained sources; clicking Create slides is not factual certification.

The [reference review](REFERENCE_PROJECTS.md#refresh-2026-11-03) and inspected
source support this workflow, not a solved factual-verification mechanism:

- [Open Notebook transformations](https://github.com/lfnovo/open-notebook/blob/a0f6f3081ae06328f0a451b3a3ef2959ca25721d/open_notebook/graphs/transformation.py)
  check nonempty input/output and generation completion before saving model text.
- [Open-NotebookLM's outline agent](https://github.com/Anionex/Open-NotebookLM/blob/36ecc9336eb5fb9b9e91e48a057ef9fb010ea50a/workflow_engine/agentroles/kb_outline_agent.py)
  produces structured outlines for subsequent revision. Its inherited
  [default validator](https://github.com/Anionex/Open-NotebookLM/blob/36ecc9336eb5fb9b9e91e48a057ef9fb010ea50a/workflow_engine/agentroles/cores/base_agent.py#L1075-L1122)
  checks JSON parsing/nonempty output, not factual entailment.
- [SurfSense's office pipeline](https://github.com/MODSetter/SurfSense/blob/f41e037fd704a0e4418e74117734d13cffdd1a2f/surfsense_local/backend/worker/studio/office/pipeline.py)
  executes a model-written builder script; its repair loop addresses script
  failures. Racall retains fixed Python exporters instead of executing model code.

These are observations of the inspected paths at pinned revisions, not an audit
of every upstream feature or evidence that their generated claims are correct.

## Evidence and unresolved results

| Item                             | Disposition                                                                                                                                                                                                                                                                                                                                                |
| -------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Bounded EN/RU live evaluation    | Completed in the [follow-up run](MODEL_EVALUATION_04_FOLLOWUP_2026-11-03.md): four sequential production calls, independent factual review, resource monitoring and cleanup. English passed that review; Russian failed.                                                                                                                                   |
| Earlier English semantic failure | [Recorded failure](MODEL_EVALUATION_04_2026-11-03.md) remains unchanged: non-approval at one meeting became absence of changes. Removing the second writer eliminates that rewrite step, not the recorded failure or the general inference risk.                                                                                                           |
| Russian initial-outline failure  | Still unresolved: “results have not yet been received” became “results are absent.” The critic accepted the stronger claim.                                                                                                                                                                                                                                |
| Review/edit/assembly/export      | Demonstrated separately: the explicitly corrected Russian copy retained revision history, exact approved text/citations, offline export and restart. This passes the correction workflow, not Russian automatic generation.                                                                                                                                |
| False certification              | Fixed in `3cae3c4`: new presentation answers always retain `validated=false`, even after critic acceptance. Approval, editing and export cannot promote them to true. Historical files are not silently rewritten.                                                                                                                                         |
| Regression and full-suite checks | Recorded-response tests cover false certification and preservation through assembly; API/storage tests cover edits, exports and legacy flags. The subsequent local suite passed **604 tests** in **43.25 seconds**, as recorded in the [closure verification](VERIFICATION_04_CLOSURE_2026-11-03.md). This is offline evidence, not a new live model pass. |

The certification fix changes no writer/critic prompt and adds no retries. The
critic remains a fallible rejection filter; schema checks, known citation IDs and
versioned source provenance do not prove semantic truth. The original EN/RU
fixtures and failed live artifacts remain intact. No retry-until-pass run or
post-fix live quality pass is claimed.

## Release interpretation

0.4 may be proposed as an **AI-draft beta with explicit known limitations**:
generated facts, negation, uncertainty and speaker notes require review before
sharing. One local model and bounded synthetic EN/RU cases do not establish
performance across models, languages, hardware or real documents. Manual review
can also miss errors; it is an available correction step, not a guarantee.

Completing the bounded evaluation is not the same as satisfying its factual
quality criterion. Any decision to release with this limitation must be explicit
and separate from that still-open criterion. This document supplies neither that
decision nor owner publication approval. Other release checks retain their own
evidence and status; publication remains on hold.

## Owner decision — November 4

After reviewing the successful EN/RU application workflow and the repeated
single-claim audit failure, the owner chose: **keep 0.4 in development until
automatic factual checking becomes more reliable**. The offered release with
AI drafts and manual source review was declined. The earlier proposal above is
historical, not an accepted release scope. No tag, public release or quality-gate
waiver follows from the completed workflow or packaging tests.

The slide-local source interface remains a useful editing feature, but it does
not satisfy this retained automatic-quality requirement. Further work must test
a different verification mechanism against the preserved failures and fresh
controls; repeating prompts or relabelling the failing benchmark is not a fix.
