# Presentation grounding follow-up — 2026-11-03

Status: protocol changes implemented locally; live evaluation blocked by runtime readiness.
No new live quality pass is claimed. A fresh native candidate matrix is pending;
publication remains on hold.

## One fact ledger for visible text and speaker notes

The Python outline writer now returns a bounded fact ledger and slide references,
rather than separate prose for each field. Each fact has a unique `F` ID, text of
at most 220 characters, and one or more exact quotations tied to supplied evidence
IDs. The writer is instructed to make each fact atomic; that instruction alone
does not prove that its meaning is atomic or supported.

Slides select a title, bullet points and note lines by fact ID. Python assembles
those fields from the same saved fact texts. A bullet reused in speaker notes
therefore does not get a second model paraphrase. Any additional note fact must
enter the ledger with its own evidence anchors. Titles retain their 160-character
limit; the protocol allows 1–60 facts, 1–12 slides and at most five bullet and five
note IDs per slide.

The parser rejects extra fields, duplicate fact IDs, unknown references, duplicate
IDs within a slide field, undeclared evidence, invalid/duplicate anchors within a
fact, unused facts and oversized values. It does
not silently truncate or repair them. Exact substring checks establish quotation
provenance only: copying a source phrase does not establish that a generated
claim follows from its context.

Implementation: [claims.py](../apps/api/on_knowledge/features/presentations/claims.py)
and [generator.py](../apps/api/on_knowledge/features/presentations/generator.py).

## One structured, fallible evidence audit

The server assigns separate `C` IDs to facts and makes one audit request after
successful writer-output validation. The auditor must return exactly one result
per claim: `supported`, `unsupported` or `uncertain`, a nonempty explanation, and
exact supporting quotations for every `supported` verdict. Support must belong
to that claim's declared evidence. Missing, duplicate or unknown verdict IDs,
invalid quotations and malformed responses are protocol errors. Any unsupported
or uncertain claim rejects the draft without rewriting it.

The request supplies each cited evidence passage once in a shared evidence list.
Claims reference its ID; partial highlighted anchors remain available, while an
anchor equal to the entire passage is not duplicated inside the claim. The
auditor sees the full supplied passage, not just a selected highlight. This does
not mean that every imported document is sent in full: the scope remains the
evidence passages selected for this generation.

Instructions explicitly cover subject, event, scope, time, negation, uncertainty,
conditions, quantities, units and causal claims. They are a fallible model check,
not a semantic proof. The writer/audit workflow contains no automatic repair,
retry or rewrite loop. Protocol errors, semantic rejection and transport failures
remain distinguishable. See [review.py](../apps/api/on_knowledge/features/presentations/review.py).

Manual review remains required. New presentation answers still have
`validated=false`; model acceptance and user approval do not certify facts.
Editing clears the relevant review state. Deterministic slide assembly and
exports preserve the approved text and existing review state without another
writer or audit call.

## Frozen, bounded evaluation

[evaluate_grounding04.py](../scripts/evaluate_grounding04.py) evaluates the actual
audit function against five cases and 34 claims. It makes at most one audit call
per case, five calls total, with a 20-minute global limit. It does not generate a
fresh outline or retry failed cases to obtain a better score.

| Case | Claims | Gold supported | Gold not supported |
| --- | ---: | ---: | ---: |
| Historical meeting approval versus global change | 8 | 7 | 1 |
| Historical results not received versus absent | 8 | 7 | 1 |
| Holdout: archive, publishing and power | 6 | 3 | 3 |
| Holdout: firmware, forecast and permission | 6 | 3 | 3 |
| Holdout: cross-language depot, oven and prototype | 6 | 3 | 3 |
| Total | 34 | 23 | 11 |

The two historical cases retain their original claim texts and evidence. Three
independently prepared holdout cases include positive and negative controls,
EN→RU/RU→EN translations and equivalent units. Their gold labels and rationale
were frozen before inference and are not sent to the model. The holdout file's
SHA-256 is
`ec464432ecbc68dd5ead4221d049fcbe6807778c1b4434d08604bcd92f2f95ce`:
[grounding-holdout.json](../evals/release04/grounding-holdout.json).

Scoring records both false acceptances and false rejections. Rejecting a whole
batch cannot hide an accepted false claim; rejecting everything cannot pass the
positive controls. A missing/malformed review is a failure, not a successful
semantic rejection. Protocol fixtures test these boundaries but do not measure
real-model quality.

## Live and release status

An initial preflight stopped before inference because approximately 7.0 GB of
available system RAM was below the chosen 8.0 GB start threshold. That attempt
made zero model calls and supplied no quality result. After the owner freed
memory, two owned runtime readiness attempts were recorded:

- The first runtime's loading/warmup request failed with HTTP 500 and a CUDA
  initialization error at `cudaFuncGetAttributes`, before any evaluation call.
- One process-local `CUDA_MODULE_LOADING=EAGER` comparison failed its 30-second
  server-readiness check during GPU discovery. It created no model alias and
  made no inference or evaluation calls. This is a different observed failure,
  not proof of a shared root cause.

Both attempts' cleanup reports confirm that their owned servers stopped, the
owner's model tags were unchanged, and the owner's loaded-model list was empty.
Those two attempts made zero evaluation calls. A subsequent controlled 44-layer
GPU alias loaded successfully with the same model and a 4,096-token context.
Its one audit request exhausted that context (1,354 input + 2,742 generated
tokens); the production provider rejected the incomplete stream. No case was
scored. Cleanup again stopped the owned server and removed only its alias.
The same frozen five cases are now being checked with 8,192 context tokens in
an isolated alias. This is a context-capacity comparison, not a change to the
claims, gold labels or audit prompt. Runtime guards and user-service isolation
remain in force. No factual-quality pass has been established yet.

Local evidence for the current attempt is retained under ignored
`test-results/grounding04-20261103T1920/` and
`test-results/grounding04-20261103T1915-eager/`, plus
`test-results/grounding04-20261103T1925-gpu44/` and the pending
`test-results/grounding04-20261103T1928-gpu44-8k/`. The start threshold is separate from the existing continuous
available-RAM stop guard during inference. No completed quality run or new
factual-quality pass is claimed.

The earlier [live failure](MODEL_EVALUATION_04_2026-11-03.md) and
[follow-up failure](MODEL_EVALUATION_04_FOLLOWUP_2026-11-03.md) remain historical
failures. Their recordings are preserved under [regressions](../evals/release04/regressions/).
Neither the ledger nor the new audit protocol retroactively changes those
results. Packaging, exports and upgrade preservation are separate checks; the
changed source and dependency set still require a fresh native candidate matrix.
