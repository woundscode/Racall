# 0.4 follow-up evaluation — November 3, 2026

**Acceptance remains incomplete: English passed independent factual review;
the Russian outline failed.** The second live run completed four sequential
production calls without a RAM stop. Its failure was semantic, not a resource
exception. Nothing was published. The earlier
[evaluation report](MODEL_EVALUATION_04_2026-11-03.md) remains a separate record.

## Workflow and results

The owner authorized local testing and reported that the computer now has
healthy 16 GB RAM, replacing the previously faulty 32 GB. This is an owner
report, not a hardware diagnostic performed by Racall.

The revised presentation workflow assembles a deck in Python from the explicitly
selected saved outline revision. Assembly and exports do not regenerate accepted
text or call a model. This removes the additional writer/critic pair that could
change an already reviewed outline. It does not make an initially generated
outline factually reliable.

| Check                                                | Result                                                                         |
| ---------------------------------------------------- | ------------------------------------------------------------------------------ |
| English outline: all eight title/bullet/note records | Independent assistant review passed.                                           |
| Manual title/template save and service restart       | Saved revision 2 retained; original revision 1 remained readable.              |
| English deck assembled from revision 2               | Text, notes, slide IDs and evidence IDs preserved; no model call.              |
| English PPTX/PDF text and speaker notes              | Independent factual review passed, including notes and source appendices.      |
| Russian outline                                      | **Failed:** unsupported absence-of-results claim in slide 2 notes.             |
| Russian live deck/export                             | Not run: failed outline checkpoint stopped acceptance.                         |
| Worker shutdown                                      | Drained, with no unfinished completion.                                        |
| Owned runtime cleanup                                | Temporary alias removed, owned service stopped, original model tags unchanged. |

There were exactly four completed production calls: English writer and critic,
then Russian writer and critic. Their durations were approximately 58.27, 35.77,
59.84 and 55.30 seconds. A separate load-only request returned `done_reason=load`
with an empty response; it was not a generated answer or acceptance result.
No retry-until-pass run was performed.

English source quotations and offsets, selected context, citation IDs, dates,
planned versus actual status, and exclusion of the conflicting note were checked.
The notes retained non-approval of changes in the review-meeting context, rather
than asserting that no changes occurred. Literal model-generated `[E1]`/`[E2]`
markers remain in English bullets alongside canonical `[1]`/`[2]` source footers;
the independent review recorded this presentation issue without rewriting the
generated artifact.

After that live run, a deterministic formatter was added at the initial-outline
save boundary. An offline replay of the recorded English writer/critic responses
now maps complete generated evidence-marker groups to canonical source numbers.
It does not change user edits, assembly inputs or source quotations, and rejects
unknown or undeclared citation labels. This is a recorded-response regression
check, not a new live model pass. Its artifacts are in
`test-results/inline-citations04/`; the original live artifacts remain unchanged.

## Confirmed Russian false positive

The source says:

> Фактические результаты работы станции пока не получены.

Claim C8, in the generated speaker notes, says:

> На текущий момент результаты работы отсутствуют, а изменения графика или бюджета не были утверждены.

The first clause is stronger than the evidence. Results can already exist
without having been received by the intended recipient. The source establishes
receipt status, not that the results are absent. The second clause retains
non-approval in the meeting-slide context and is not the failure alleged here.
C1–C7 passed independent review; this unsupported clause made C8 fail.

The production critic accepted C1–C8 and the saved outline had `validated=true`.
The independent checkpoint rejected that outline and did not permit a Russian
deck to be assembled as a passing live result. The raw writer/critic inputs,
prompts, responses, expected rejected claim and counterexample are retained in
the [regression fixture](../evals/release04/regressions/results-not-received-versus-absent.json).
This is a known **unfixed** semantic false positive, not a mocked passing test.

### Separate manual correction and offline export

After live cleanup, a separate copy of the isolated Russian vault was used to
test the correction workflow. The rejected speaker note was explicitly replaced
with a close statement of the source: results have not yet been received;
temperatures were not reported at the meeting; schedule/budget changes were not
approved at that meeting. The copy saved outline revision 2 with the dark
template, assembled a deck from that revision, exported PPTX/PDF and reopened
the saved deck after service restart. Revision 1 remained readable.

The model setting was empty and forbidden-call hooks recorded zero provider,
credential-lookup and embedding calls. Independent textual review passed the
corrected outline, assembled deck, PPTX notes, and both exports' text/notes/source
appendices. The deck preserved the corrected slides exactly; both edited and
assembled materials retained `validated=false`.

Evidence is in `test-results/live04-20261103T162435/manual-ru/`, including
`result.json` and `manual-review.json`. The latter explicitly records
`original_live_ru_quality: failed_unchanged`. The original failed outline retained
its recorded digest. **This passes the manual correction and offline export
workflow; it does not pass the Russian model-quality gate.** Native presentation
rendering was not part of this independent textual review.

The primary reviewer separately rendered all four English live PDF pages, all
four pages of the corrected Russian dark-template PDF, and all four English
citation-replay PDF pages with Poppler. Visual inspection found no clipping,
overlap, missing Cyrillic glyphs or lost text. This checks PDF rendering only;
PowerPoint/LibreOffice rendering is still unverified.

The critic prompt SHA-256 remained
`a9f8f74ee9ed3da4321bbbb39d8835a92cfc6c47dc0a6c2add4a6f3bf2aecaeb`.
The model's critic response is not independent evidence that its answer is true.

## RAM investigation and controlled runtime

The earlier Ollama 0.40.11 log exposed a concrete RAM consumer: a host prompt
cache with an **8,192 MiB limit**. Its recorded size grew from 0 to 8.081,
729.540, 1,613.355 and **2,494.951 MiB** across sequential tasks. The old run also
kept model/draft weights, KV buffers, projector and compute buffers in system
memory. This identifies a substantial contributor to RAM pressure; it does not
prove a memory leak or a fault in the current RAM.

The new run used the installed **Ollama 0.40.14**, `gemma4:12b` (11.9B Q4_K_M),
and a unique alias reusing the existing weights with `num_gpu=40`, `num_ctx=4096`
and one parallel slot. No model weights were downloaded. A separately owned
service listened only on a distinct loopback port. Its process environment set:

```text
OLLAMA_NOPRUNE=true
OLLAMA_NUM_PARALLEL=1
OLLAMA_MAX_LOADED_MODELS=1
LLAMA_ARG_CACHE_RAM=0
```

The owned runner's actual startup log confirmed that the prompt cache was
disabled. This uses the native cache option, whose environment binding is present
in [llama.cpp b11963](https://github.com/ggml-org/llama.cpp/blob/b11963/common/arg.cpp#L1727-L1734),
the revision pinned by
[Ollama 0.40.14](https://github.com/ollama/ollama/blob/v0.40.14/LLAMA_CPP_VERSION).
Ollama passes the service environment into its native child through
[SetupLlamaServerCommandEnv](https://github.com/ollama/ollama/blob/v0.40.14/llm/llama_server.go#L448-L478).
This is not a new per-request `cache_ram` API parameter.

The owned service shared the existing model store. Startup pruning was disabled
only for that process because
[Ollama otherwise prunes at startup](https://github.com/ollama/ollama/blob/v0.40.14/server/routes.go#L2489-L2504).
The user's original service was not restarted or reconfigured. Its loaded-model
list was checked before production calls; a loaded model or failed observation
would stop the evaluation. Both services still share physical RAM and GPU memory,
so a separate port alone does not isolate hardware resources.

A Python background monitor sampled available system RAM and the owned process
tree's RSS every second, including during active completions. The stream's
cancellation checkpoint checked its failure state. Sampling errors, unwritable
evidence and RAM below **2,500,000,000 bytes** stop the evaluation; shutdown joins
the sampler with a bounded timeout and reports an explicit failure if it cannot
stop. RSS is diagnostic and can count shared pages more than once; the RAM limit
uses operating-system available memory.

| Measurement                              | Observed value                          |
| ---------------------------------------- | --------------------------------------- |
| Available RAM before owned runtime       | 10,134,339,584 bytes                    |
| Whole-run monitor samples                | 414                                     |
| Whole-run minimum sampled available RAM  | **4,569,309,184 bytes** (about 4.57 GB) |
| Acceptance monitor samples               | 389                                     |
| Acceptance minimum sampled available RAM | 4,571,234,304 bytes                     |
| Whole-run maximum sampled owned-tree RSS | 4,107,472,896 bytes                     |
| Monitor failure / shutdown               | No failure; stopped normally            |
| Available RAM after cleanup              | 9,861,660,672 bytes                     |
| Free VRAM after cleanup                  | 9,099 MiB                               |

These are one-second samples, not guaranteed instantaneous peaks. The new and
old runs used different Ollama versions, initial memory availability, cache
settings and call workflows. They are **not a controlled performance benchmark**,
and the RAM difference cannot be attributed solely to one change.

## Provenance and limits

- Source base commit: `68d81b15c365dd8f6daa20166e0aafc391a3b340`.
- Source-manifest SHA-256:
  `6d6105a08f7a08e4ab25b75c198d2fdaa7b4def7cad63dcfa3ce7a7846887f32`.
- Original model digest:
  `6114515d63c17436a7c0417d82820ac65ad643e2806c5a3c89cb62846436ed0b`.
- Temporary alias digest:
  `c9059a4b3435d1e6949939c24f4e746dc58c87a979b0634802082e2c0ba4111e`.
- Rejected Russian material SHA-256:
  `a1e129639be1ea690c3933350d026edbce309acd1dd5b313ac654320732d56cc`.

Ignored raw evidence is in `test-results/live04-20261103T162435/`: the before/alias
metadata, owned service configuration/log, cache verification, both resource
monitors, load-only response, acceptance source manifest, provider trace,
generated artifacts, independent review records, English exports and cleanup.
The earlier RAM diagnosis is in
`test-results/live04-20261103T124354Z/ram-diagnosis.json`.

Cleanup confirmed that the owned server stopped, its alias was removed, all
original model tags/digests were unchanged, and the user's loaded-model list was
empty. Only synthetic documents and an isolated vault were used.

The combined live quality gate remains failed/incomplete. English export review
covered text and notes, not native PowerPoint/LibreOffice rendering. Other
models, hardware, embeddings, macOS/Linux desktop behavior and owner hands-on
acceptance were not established by this run. Any subsequent manual correction
or offline export exercise must be recorded separately and must not relabel
this Russian live failure as a pass.
