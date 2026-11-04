# Independent fact-checking experiment for 0.4

Status: **shelved before download or inference**. On November 4, the owner
declined downloading the proposed model and CPU dependencies. No new verifier
is integrated and no model weights or packages were downloaded for this
experiment. Racall has no runtime dependency on this prototype. Retaining 0.4
in development until automatic checking improves does not authorize requiring
this additional model. The design below records an untested candidate, not an
accepted implementation or publication decision.

## Why change the mechanism

The existing Gemma writer/auditor shares a semantic failure: it can accept a
stronger interpretation even when given exact quotations and an explicit
instruction to preserve qualifications. The frozen audit has three false
acceptances among 34 claims. Isolating one claim repeated a known failure;
another prompt revision or per-claim request loop is not the next proposed fix.
See the [preserved evidence](GROUNDING_04_FOLLOWUP_2026-11-03.md).

The proposed experiment uses a separately trained natural-language-inference
classifier on CPU. It classifies a source/claim pair as entailment, neutral or
contradiction. This is an independent acceptance condition, not a claim that a
classifier score is the probability a statement is true. Its benefit on Racall's
actual errors must be measured before any product integration.

## Pinned candidate and resource budget

Candidate: [MoritzLaurer/mDeBERTa-v3-base-mnli-xnli](https://huggingface.co/MoritzLaurer/mDeBERTa-v3-base-mnli-xnli),
whose model card declares MIT and English/Russian NLI training. The experiment
pins revision `8adb042d524ecd5c26d3e3ba0e3fbcf7e2d0864c`.
The safetensors file is 557,652,046 bytes, SHA-256
`65af59b1ff4450b09ecbf13ca35c840dbf038b26ff8e10e5ea89ca724828ed1e`.
[Author's revision](https://huggingface.co/MoritzLaurer/mDeBERTa-v3-base-mnli-xnli/commit/8adb042d524ecd5c26d3e3ba0e3fbcf7e2d0864c).

Proposed first run: a separate CPU-only Python environment/process, FP32,
batch size 1 and two compute threads. FP32 weights alone require approximately
1.04 GiB; a 4-GiB process budget and a 4-GB disk budget for the model/environment
are proposed limits, not measured consumption. The parent continuously checks
available physical memory and Windows commit headroom and stops its owned
worker if either drops below 2.5 GB. No concurrent Ollama inference, new GPU
configuration, production dependency change or model-server change is needed.

Downloading the roughly 580-MB model/tokenizer set and the separate CPU
dependencies was proposed and declined. The current environment lacks these
packages. Preparation and fake-adapter tests do not establish a successful model
run. Package compatibility was not finalized; preliminary latest-version
metadata cannot be treated as an installable lockfile.

## Input and decision contract

- Premise: all complete saved passages cited by this fact, with passage
  boundaries retained. A writer's selected substring cannot replace the full
  passage. Unknown/missing source IDs are an error.
- Hypothesis: the exact original fact text, including a title or conjunction.
  Do not translate, repair, split with another model or exempt headings.
- The verifier receives neither gold labels nor the user's question or the
  previous critic's explanation as evidence.
- The pinned model permits **512 tokens for the entire pair**. Tokenize without
  truncation; overlong input abstains without invoking the model. Do not select
  the highest-scoring window or drop a qualification to fit the input.
- Verify the configured mapping `entailment / neutral / contradiction`, record
  all raw scores and coverage status, and preserve exact input/model hashes.
  Unexpected labels or unavailable verification do not fall back to acceptance
  by the old critic.
- The initial diagnostic policy is fixed before inference: top label entailment
  with score at least 0.9. This is an uncalibrated diagnostic threshold, not a
  product confidence guarantee and not a slider tuned against the holdout.

## First milestone: unchanged 34-claim diagnostic

The ignored `test-results/nli04-spike/` harness is prepared separately from the
application. Its default action is a dry preparation/check. A real run requires
an explicit local model directory and a new output directory, with offline-only
loading, safetensors and remote custom code disabled.

Evaluate all 34 existing claims, at most one forward pass per claim and no
semantic retries, within 900 seconds. Retain semantic failures; stop on runtime
or resource failures and label an interrupted run incomplete. Gold is compared
outside the inference worker after its decisions. Count false acceptances,
false rejections, abstentions and technical failures separately; abstaining on
a positive control still reduces positive coverage. Rejecting everything does
not pass. The prior 23 positive and 11 negative labels are unchanged.

The first gate retains zero false acceptance and acceptance of all 23 positives
on these known regressions. The data are already known to developers, so this
is a regression check, not a fresh blind estimate. Only a promising measured
result warrants separate calibration and a newly frozen, independently reviewed
holdout. Calibration must not select a threshold on that holdout.

Preparation verification on November 4 passed 31 fake-adapter contract tests,
Ruff lint/format and an independent review. These cover unchanged input hashes,
gold separation, context-limit abstention, resource limits during loading and
inference, post-run file integrity and cleanup of owned processes. They establish
the harness behavior only; no real classifier result is available yet.

## Remaining limits even if the diagnostic passes

The corpus contains topic-like headings, multi-passage conjunctions and mixed
English/Russian pairs. A verifier must preserve their gold meanings rather than
silently narrowing the feature to easy single sentences. The model's published
XNLI accuracy is not evidence that these specific cases pass.

Saved retrieval passages may themselves end at document/note chunk boundaries.
An untruncated classifier input therefore does not prove coverage of the whole
source paragraph. Long-context tests must include qualifications at those
boundaries; a later integration needs pinned surrounding context or an explicit
insufficient-coverage outcome. Source coverage is separate from model scores.

An additional fresh holdout, real writer-to-verifier EN/RU workflows, resource
measurements and cross-platform packaging would still be required. CPU ONNX or
quantization is a later optimization with its own accuracy checks. No result
from a small benchmark establishes universal factual truth, and no model is
added to the distributed application on research findings alone.
