# Presentation grounding follow-up — 2026-11-03

Status: the bounded live audit evaluation completed and failed its quality gate.
Two of five cases passed; three unsupported claims received a supported verdict.
Fresh native candidate verification is separate; publication remains on hold.

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
The same frozen five cases then completed with 8,192 context tokens in an
isolated alias. Only the alias context changed after the 4,096-token truncation;
the claims, gold labels and audit prompt were unchanged. This was a separate
context-capacity comparison, not an automatic repair of a failed answer.

Local evidence for these attempts is retained under ignored
`test-results/grounding04-20261103T1920/` and
`test-results/grounding04-20261103T1915-eager/`, plus
`test-results/grounding04-20261103T1925-gpu44/` and
`test-results/grounding04-20261103T1928-gpu44-8k/`. The start threshold is separate
from the existing continuous available-RAM stop guard during inference. The
earlier runtime failures and truncated attempt remain recorded; they were not
converted into quality scores.

## Completed 8,192-token audit result

Ollama 0.40.14 ran the existing `gemma4:12b` model through an isolated alias with
44 GPU layers and an 8,192-token context. The bounded run made exactly five audit
calls, one per frozen case, with no production generation overrides, semantic
retries or repair calls. Raw provider messages contain only the audit instructions
and the question, server-labelled claims and cited evidence; gold labels and
rationale were not sent.

| Case | False supported verdicts | False rejections | Application protocol outcome | Case passed |
| --- | ---: | ---: | --- | --- |
| Meeting approval versus global change | 1 (`C8`) | 0 | Protocol error: missing support | No |
| Results not received versus absent | 1 (`C8`) | 0 | Accepted despite the unsupported claim | No |
| Archive, publishing and power | 0 | 0 | Semantic rejection of invalid controls | Yes |
| Firmware, forecast and permission | 1 (`C1`) | 0 | Batch rejected other invalid controls | No |
| Cross-language depot, oven and prototype | 0 | 0 | Semantic rejection of invalid controls | Yes |

All **23 gold-positive claims received a supported verdict**. Of 11 negative
controls, eight received unsupported/uncertain verdicts and three were falsely
supported. Thus the result is **3 false acceptances out of 34 claims, zero false
rejections and 2/5 passing cases**. These are per-claim model verdicts, not a claim
that every positively labelled draft was accepted by the application.

Independent review of all 34 claim/verdict/explanation rows confirmed:

- English historical `C8` turns the lack of approval at one meeting into a
  broader lack of schedule/budget adjustments. The model called it supported but
  supplied no quotation. `C1`, `C4` and `C5` also had empty support, so the
  application rejected this response as a protocol error. That rejection does
  not make the incorrect semantic verdict a quality pass.
- Russian historical `C8` changes results not yet received into results being
  absent and broadens the meeting-specific approval statement. The response
  satisfies the structural quotation contract, but its cited text does not
  support that stronger meaning. This case reached application acceptance and
  remains a factual-support failure.
- Russian holdout `C1` turns an increase after a firmware update into an increase
  caused by that update. The full passage explicitly says the cause is unknown.
  The model's quote omits that qualification and its explanation confirms only
  temporal ordering. The batch rejected other claims, but scoring correctly
  retains this false acceptance.

All 25 supplied quotation spans were exact substrings of the corresponding
claim's declared evidence, and all 34 explanations were nonempty and within the
protocol bound. Exact quotation validity therefore did not prevent semantic
false positives. The four empty supported-claim quotation lists in the English
case were separately retained as protocol failures.

The continuous monitor recorded a minimum available RAM of 4,785,389,568 bytes,
above its 2,500,000,000-byte stop floor, and stopped normally. Sampled per-call
free VRAM reached a minimum of 1,265 MiB; this is a sampled minimum, not a guarantee
about unobserved moments. Cleanup confirms the owned server stopped, only the
temporary alias was removed, original/user tags remained unchanged, and the
owner's loaded-model list was empty. Evaluator exit 1 represents the failed
quality gate, not failed cleanup.

### Provenance and limits

The run started before the source commit, so `environment.json` records Git HEAD
`6527ac23a18b0a6d9b120480bac4ddd81e339cf1` plus hashes of the actual working files.
Independent comparison binds that recorded snapshot to the later source commit
`4fd974d80e326cfcde5aecb663696e67e804e7f5`: 61 of 123 recorded file hashes match
Git blobs exactly; the other 62 match their Windows CRLF checkouts, with no
unexplained content mismatch. The evaluated cases equal the frozen loader output.
The audit implementation and evaluator match exactly:

- `review.py`: `1f36f8f135e16a6c3aeb8f612d712e3aa60ba41867a79e4fa8b520e59aab2319`.
- `evaluate_grounding04.py`: `1755e50ed8a2dba73027b5807bb35fdc17b4f268ec866c8b09eff0fab6c1f4b8`.

The ignored run directory retains `acceptance/environment.json`,
`acceptance/provider-trace.json`, `acceptance/result.json`, resource-monitor and
cleanup records, plus `independent-review.json`. A compact
[tracked failure recording](../evals/release04/regressions/structured-audit-false-acceptances.json)
preserves the three false-supported claims, full cited passages, frozen fact
anchors, unchanged recorded review rows and source hashes. It is failure evidence,
not a passing test; the provider trace stores parsed JSON rather than original
HTTP bytes. This check exercised the audit
on fixed claims; it did not establish successful end-to-end outline generation.
The separate EN/RU ledger-generation check remains subject to its own review.
No result from that separate check is inferred here.

**Semantic quality remains failed.** The ledger prevents a second independent
paraphrase when assembling notes, and protocol checks reject malformed support;
neither establishes that the writer or auditor always preserves source meaning.
Manual review and `validated=false` remain required. No unsupported claim or old
recording was rewritten to improve these scores.

The earlier [live failure](MODEL_EVALUATION_04_2026-11-03.md) and
[follow-up failure](MODEL_EVALUATION_04_FOLLOWUP_2026-11-03.md) remain historical
failures. Their recordings are preserved under [regressions](../evals/release04/regressions/).
Neither the ledger nor the new audit protocol retroactively changes those
results. Packaging, exports and upgrade preservation are separate checks. The
[subsequent transport and native verification](VERIFICATION_04_GROUNDING_2026-11-03.md)
records the new `629312e` candidate and keeps these semantic failures separate.
