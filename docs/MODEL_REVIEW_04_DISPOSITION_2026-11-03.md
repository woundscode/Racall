# 0.4 model-review disposition — November 3, 2026

**Latest disposition, November 4: the owner accepts 0.4 Beta with the known AI
semantic limitation, subject to fresh technical release checks.** The automatic
factual-quality criterion remains unmet. This acceptance supersedes the earlier
refusal recorded below; it does not turn failed model results into passes.
The [final native packages and installed upgrade](VERIFICATION_04_CANDIDATE_2026-11-04.md)
passed. Publication remains on hold until the owner chooses its timing.

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

0.4 is accepted in scope as an **AI-draft beta with explicit known limitations**:
generated facts, negation, uncertainty and speaker notes require review before
sharing. One local model and bounded synthetic EN/RU cases do not establish
performance across models, languages, hardware or real documents. Manual review
can also miss errors; it is an available correction step, not a guarantee.

Completing the bounded evaluation is not the same as satisfying its factual
quality criterion. The latest owner decision accepts the limitation separately
from that still-open criterion. Other release checks retain their own evidence
and status; the [release checklist](RELEASE_04_CHECKLIST.md) records the completed
technical acceptance separately from the remaining publication decision.

## Earlier owner decision — November 4 (superseded)

After reviewing the successful EN/RU application workflow and the repeated
single-claim audit failure, the owner chose: **keep 0.4 in development until
automatic factual checking becomes more reliable**. The offered release with
AI drafts and manual source review was declined. At that time, the proposed
AI-draft scope was not accepted. No tag, public release or quality-gate waiver
followed from the completed workflow or packaging tests.

At that stage, the slide-local source interface did not satisfy the retained
automatic-quality requirement. Repeating prompts or relabelling the failing
benchmark was not accepted as a fix. This remains the history of that decision;
the subsequent decision below changes the permitted beta scope.

## Latest owner decision — November 4

The owner subsequently authorized preparing **0.4 Beta with the known AI
semantic limitation** and rerunning the technical gates. This supersedes the
earlier refusal to ship an AI-draft beta. It does not require another model or an
independent verifier: the proposed NLI experiment remains shelved, and the owner
has not authorized new downloads.

This work prepares a release candidate. The current action does not publish,
tag or merge it; publication timing remains a separate owner decision.

The [frozen audit](GROUNDING_04_FOLLOWUP_2026-11-03.md) remains unchanged: 34 claims,
23 valid and 11 invalid, three false acceptances, no false rejections, and two of
five cases passing. A later isolated single-claim request repeated its first
known failure with complete evidence. The
[context-preservation fixes](VERIFICATION_04_CONTEXT_2026-11-04.md) address real
application truncation defects; they do not establish a fix for these semantic
mistakes or a new live-model quality pass.

Additional memory helped model loading on the tested host. It does not correct
the demonstrated full-context reasoning failures. A stronger model may improve
quality, but neither hardware nor a model change guarantees factual correctness.
Generated content remains unvalidated, and the interface and release notes must
retain clear source-review guidance. Historical failed artifacts and labels stay
intact while factual reliability remains an open improvement area.
