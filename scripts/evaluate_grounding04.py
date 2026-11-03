"""Opt-in, bounded presentation-review regression and independent holdout check."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load_cases(root=ROOT):
    cases = []
    for name in (
        "meeting-approval-versus-global-change.json",
        "results-not-received-versus-absent.json",
    ):
        recorded = json.loads((root / "evals/release04/regressions" / name).read_text("utf-8"))
        original = recorded["critic_data"]
        evidence = {item["id"]: item for item in original["evidence"]}
        cases.append(
            {
                "id": name.removesuffix(".json"),
                "question": original["question"],
                "evidence": original["evidence"],
                "facts": [
                    {
                        "id": f"F{index}",
                        "text": claim["text"],
                        "evidence": [
                            {"evidence_id": key, "quote": evidence[key]["quote"]}
                            for key in claim["evidence_ids"]
                        ],
                    }
                    for index, claim in enumerate(original["claims"], 1)
                ],
                "expected_supported_claim_ids": [
                    claim["claim_id"]
                    for claim in original["claims"]
                    if claim["claim_id"] not in recorded["expected_rejected_claim_ids"]
                ],
                "origin": "Unchanged text from the historical failed live critic input",
            }
        )
    holdout = json.loads((root / "evals/release04/grounding-holdout.json").read_text("utf-8"))
    return cases + holdout["cases"]


def score_review(raw, expected, count):
    """Require every positive and negative control, not just rejection of a batch."""
    labels = {f"C{index}" for index in range(1, count + 1)}
    rows = raw.get("reviews") if isinstance(raw, dict) else None
    if not isinstance(rows, list) or len(rows) != count:
        return {"passed": False, "unscorable": "Missing review rows"}
    seen = {}
    for row in rows:
        if not isinstance(row, dict):
            return {"passed": False, "unscorable": "Malformed review row"}
        key, verdict = row.get("claim_id"), row.get("verdict")
        if key not in labels or key in seen or verdict not in {"supported", "unsupported", "uncertain"}:
            return {"passed": False, "unscorable": "Unknown, duplicate or malformed verdict"}
        seen[key] = verdict
    wanted = set(expected)
    if not wanted <= labels:
        raise ValueError("Gold labels do not match the supplied claims")
    accepted = {key for key, value in seen.items() if value == "supported"}
    return {
        "passed": accepted == wanted,
        "false_acceptances": sorted(accepted - wanted),
        "false_rejections": sorted(wanted - accepted),
        "observed": seen,
    }


def evaluate_case(provider, guard, case):
    from on_knowledge.features.presentations.errors import PresentationProtocolError, UnsupportedPresentation
    from on_knowledge.features.presentations.review import review_facts

    guard.case = case["id"]
    protocol = "accepted"
    initial_calls = len(guard.calls)
    try:
        review_facts(provider, case["question"], copy.deepcopy(case["facts"]), case["evidence"])
    except UnsupportedPresentation:
        protocol = "semantic_rejection"
    except PresentationProtocolError:
        protocol = "protocol_error"
    if len(guard.calls) != initial_calls + 1:
        return {
            "case": case["id"],
            "passed": False,
            "protocol": protocol,
            "unscorable": "The case did not make exactly one audit call",
        }
    score = score_review(
        guard.calls[-1].get("result"), case["expected_supported_claim_ids"], len(case["facts"])
    )
    return {
        "case": case["id"],
        **score,
        "protocol": protocol,
        "passed": score["passed"] and protocol != "protocol_error",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", action="store_true")
    parser.add_argument("--endpoint", default="http://127.0.0.1:11434/v1")
    parser.add_argument("--observe-ollama")
    parser.add_argument("--owned-pid", type=int, action="append", default=[])
    parser.add_argument("--model")
    parser.add_argument("--source-model", default="gemma4:12b")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    cases = load_cases()
    if not args.run:
        print(
            json.dumps(
                {"cases": len(cases), "claims": sum(len(c["facts"]) for c in cases), "inference": False}
            )
        )
        return 0
    if not args.model or not args.output:
        parser.error("--run requires an explicit model alias and a new output directory")
    args.output.mkdir(parents=True, exist_ok=False)
    sys.path.insert(0, str(ROOT / "apps/api"))
    os.environ["PYTHON_KEYRING_BACKEND"] = "keyring.backends.null.Keyring"
    for key in ("OPENNOTEBOOK_API_KEY", "OPENAI_API_KEY", "ANTHROPIC_API_KEY", "OLLAMA_API_KEY"):
        os.environ.pop(key, None)
    import keyring
    import keyring.backends.null
    from model_evaluation03.guard import write_json
    from model_evaluation03.runner import manifest
    from model_evaluation04.guard import MonitoredGuard
    from model_evaluation04.resources import ResourceMonitor
    from on_knowledge.providers import OpenAICompatible

    keyring.set_keyring(keyring.backends.null.Keyring())
    monitor = ResourceMonitor(args.output, owned_pids=args.owned_pid)
    guard = MonitoredGuard(
        args.output,
        args.endpoint,
        args.model,
        args.source_model,
        max_calls=len(cases),
        minutes=20,
        monitor=monitor,
        observe_endpoint=args.observe_ollama,
    )
    provider = OpenAICompatible({"provider": "ollama", "base_url": args.endpoint, "model": args.model})
    write_json(
        args.output / "environment.json",
        {
            "source": manifest(),
            "cases": cases,
            "max_calls": len(cases),
            "minutes": 20,
            "evaluator_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            "model_management": "No download or configuration changes by this evaluator",
            "gold_policy": "Frozen before inference; expected answers and rationale are not sent to the model",
        },
    )
    result = {"passed": False, "cases": [], "error": None}
    try:
        with monitor, guard.instrument():
            for case in cases:
                item = evaluate_case(provider, guard, case)
                result["cases"].append(item)
                write_json(args.output / "result.json", result)
                print(json.dumps(item, ensure_ascii=False), flush=True)
            result["passed"] = all(item["passed"] for item in result["cases"])
    except Exception as error:
        result["error"] = f"{type(error).__name__}: {error}"
        raise
    finally:
        write_json(args.output / "result.json", result)
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
