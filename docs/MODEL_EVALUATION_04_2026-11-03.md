# 0.4 local-model evaluation — November 3, 2026

**Acceptance: incomplete; English deck factual review failed.** The owner
authorized local Ollama testing. This run used synthetic sources and an isolated
Racall vault. No personal documents, cloud credentials or public release assets
were used or changed.

## What completed

| Check | Outcome |
| --- | --- |
| English outline, two content slides | Generated and saved; independent assistant review passed all eight title/bullet/note records. |
| Manual outline save and restart | Revision 2 retained; original revision 1 readable. |
| English slides from approved revision 2 | Generated with the original selected source/note versions and stable slide IDs. |
| Factual review of the generated deck | **Failed:** unsupported speaker-note claim C8 passed the production critic. |
| Real PPTX/PDF export and service restart | Completed without additional model calls; saved material reopened unchanged. |
| PDF visual inspection | All four pages rendered and inspected: two content slides, notes and sources, without clipping. This is a layout pass, not a factual pass. |
| PPTX inspection | Editable text/notes read through `python-pptx`; the unsupported note is preserved in the export. No PowerPoint/LibreOffice rendering was performed. |
| Russian workflow | Not started: resource stop after the English workflow. |

There were **four completed, sequential production calls**, two writers and two
critics. Observed durations were 41.17, 49.59, 49.25 and 76.03 seconds. A separate
eight-token warm-up disabled thinking and is not an acceptance result. Production
requests retained the normal sampling/thinking behavior. No retry-until-pass
run or prompt change was performed.

## Confirmed semantic failure

The meeting record says:

> Changes to the schedule or budget were not approved at this meeting.

The generated speaker notes for slide 2 say:

> Overview of the status of data reporting and the lack of schedule or budget adjustments-at this stage.

The evidence establishes a lack of **approval at a particular meeting**, not an
absence of **changes throughout a project stage**. Both the predicate and its
scope changed. The critic accepted C1–C8, including this unsupported C8, and the
saved material had `validated=true`. The error propagated unchanged into PPTX
speaker notes, the PPTX notes appendix and the PDF notes appendix.

The exact writer/critic inputs and responses are retained in the
[regression fixture](../evals/release04/regressions/meeting-approval-versus-global-change.json).
It is a recorded **unfixed** semantic failure, not a passing mocked-model test.
The critic prompt hash was
`a9f8f74ee9ed3da4321bbbb39d8835a92cfc6c47dc0a6c2add4a6f3bf2aecaeb`,
the same policy already associated with the recorded
[0.3 false positives](MODEL_EVALUATION_03_2026-10-25.md).

The requested dates, planned sensor count/capacity and unknown-results coverage
were otherwise present. Source/note hashes, quotation offsets, canonical
citation IDs, approved outline revision and export contents were consistent.
The intentionally excluded conflicting note did not reach the model. Correct
provenance does not make the unsupported inference true.

## Runtime and stop

- Ollama **0.40.11**, installed `gemma4:12b`, 11.9B Q4_K_M; original digest
  `6114515d63c17436a7c0417d82820ac65ad643e2806c5a3c89cb62846436ed0b`.
- Windows, RTX 3080 with 10,240 MiB VRAM and approximately 16 GiB system RAM.
- A unique temporary alias reused the existing weights with `num_gpu=40` and
  `num_ctx=4096`. No weights were downloaded; the original tag was unchanged.
  These settings are an observed configuration for this machine, not a general
  hardware recommendation. Alias creation/unloading use the documented
  [Ollama create](https://docs.ollama.com/api/create) and
  [generate](https://docs.ollama.com/api/generate) endpoints.
- One completion at a time, maximum 12 calls / 20 minutes, explicit STOP file,
  model-digest checks and before/after-call RAM/VRAM checks. Embeddings and the
  credential store were disabled in the isolated vault.
- The minimum boundary-sampled available RAM was **1,632,354,304 bytes**;
  a subsequent Windows observation was about **1.55 GB**. Free VRAM stayed at
  or above **2,277 MiB** in those samples. These are snapshots, not peak monitoring.
- The run was stopped at the English deck review checkpoint before starting
  Russian. All four calls had completed; shutdown drained with no unfinished
  completion. No CUDA/provider error or machine restart was observed in this run.
  The measurements do not establish a memory-leak or hardware root cause.
- Only the owned temporary alias was unloaded and removed. All original model
  tags/digests matched before/after, Ollama remained running, and its loaded-model
  list was empty. Cleanup reported about 6.93 GB available RAM and 9,436 MiB free
  VRAM.

## Reproduction and evidence

The opt-in Python runner is [evaluate_presentations.py](../scripts/evaluate_presentations.py).
Without `--run`, it makes no model calls. A live run requires an explicitly named,
already prepared local alias and a new output directory:

```powershell
python scripts/evaluate_presentations.py --run --model YOUR_TEST_ALIAS --output test-results/YOUR_NEW_RUN
```

It pauses after each outline/deck at an independent-review checkpoint. A distinct
reviewer compares every factual clause with its cited evidence and writes
`review-en-outline.json`, `review-en-deck.json` and the corresponding `ru` files
atomically. Each review requires `verdict` (`pass` or `fail`) and `material_sha256`,
computed from `json.dumps(material, ensure_ascii=False, sort_keys=True).encode()`.
Only a pass matching the whole saved material permits continuation. A valid
critic response, schema check or export success must not substitute for this
review. Author, reasoning, coverage and limitations should be retained alongside
the verdict. The runner does not create/download/unload models or modify the
owner's app settings.

Ignored evidence: `test-results/live04-20261103T124354Z/`, including the initial
runtime snapshot, owned-alias parameters, warm-up, source manifest, raw provider
trace, isolated vault, both reviews, English deck/PPTX/PDF, extracted export text,
four rendered pages, STOP record, resource summary and cleanup verification.

The combined quality gate remains failed/not certified. Russian, other models,
other hardware, embeddings and external PPTX rendering remain unverified. No
application prompt/validator was changed in response to this result, and no
release was published.
