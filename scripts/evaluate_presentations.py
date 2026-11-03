"""Opt-in, serial 0.4 presentation evaluation with independent review checkpoints."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import time
from pathlib import Path
from uuid import uuid4

ROOT = Path(__file__).resolve().parents[1]

FIXTURES = {
    "en": {
        "source": (
            "The Marigold station plan was approved on September 21, 2030. "
            "Its opening is scheduled for November 12, 2030. "
            "The plan specifies seven sensors and a planned capacity of 40 kW. "
            "The station's actual results have not yet been received."
        ),
        "note": (
            "At the review meeting, measured temperatures were not reported. "
            "Changes to the schedule or budget were not approved at this meeting."
        ),
        "question": (
            "Create exactly two short slides in English, with at most two bullets per slide. "
            "Slide 1: the station plan approval, scheduled opening, planned sensors and capacity. "
            "Slide 2: what the records say about actual results, measured temperatures and the "
            "meeting's decision on schedule or budget changes. Keep speaker notes short."
        ),
        "title": "Marigold review",
    },
    "ru": {
        "source": (
            "План станции «Лис» утверждён 21 сентября 2030 года. "
            "Открытие станции запланировано на 12 ноября 2030 года. "
            "По плану предусмотрены семь датчиков и плановая мощность 40 кВт. "
            "Фактические результаты работы станции пока не получены."
        ),
        "note": (
            "На совещании измеренные температуры не сообщались. "
            "Изменения графика или бюджета на этом совещании не утверждались."
        ),
        "question": (
            "Создай ровно два коротких слайда на русском, не более двух тезисов на каждом. "
            "Слайд 1: утверждение плана, запланированное открытие, предусмотренные датчики "
            "и мощность. Слайд 2: что известно из записей о результатах, измеренных температурах "
            "и решении совещания об изменениях графика или бюджета. Заметки докладчика короткие."
        ),
        "title": "Обзор станции «Лис»",
    },
}


def material_digest(material):
    return hashlib.sha256(json.dumps(material, ensure_ascii=False, sort_keys=True).encode()).hexdigest()


def review_checkpoint(session, label, material):
    """A distinct reviewer must approve this exact saved artifact before proceeding."""
    from model_evaluation03.guard import EvaluationStop, write_json

    fingerprint = material_digest(material)
    write_json(session.output / f"{label}.json", material)
    review = session.output / f"review-{label}.json"
    print(f"REVIEW {label}: {fingerprint}", flush=True)
    while not review.exists():
        session.guard.check()
        time.sleep(0.25)
    result = json.loads(review.read_text("utf-8"))
    if result.get("material_sha256") != fingerprint or result.get("verdict") != "pass":
        raise EvaluationStop(f"Independent review did not approve {label}: {result}")
    return result


def export_and_reopen(session, language, material):
    from io import BytesIO

    from model_evaluation03.guard import write_json
    from pptx import Presentation
    from pypdf import PdfReader

    calls = len(session.guard.calls)
    route = session.base + f"/materials/{material['id']}"
    version = material["presentation"]["revision"]
    texts = {}
    for kind in ("pptx", "pdf"):
        binary = session.api(route + f"/presentation/export?format={kind}&revision={version}", raw=True)
        (session.output / f"deck-{language}.{kind}").write_bytes(binary.content)
        if kind == "pdf":
            texts[kind] = [page.extract_text() for page in PdfReader(BytesIO(binary.content)).pages]
        else:
            deck = Presentation(BytesIO(binary.content))
            texts[kind] = [
                {
                    "text": [shape.text for shape in slide.shapes if shape.has_text_frame],
                    "notes": slide.notes_slide.notes_text_frame.text,
                }
                for slide in deck.slides
            ]
    write_json(session.output / f"exports-{language}-text.json", texts)
    session.restart()
    assert session.api(route) == material, "Saved deck changed after service restart"
    assert len(session.guard.calls) == calls, "Export/restart called a model"
    return {"offline_export_and_reopen": True, "calls": calls}


def evaluate_language(session, language):
    from model_evaluation03.guard import write_json

    fixture = FIXTURES[language]
    session.notebook = session.api("/notebooks", "POST", {"title": f"Synthetic 0.4 {language}"})["id"]
    imported = session.api(
        session.base + "/sources",
        "POST",
        files={"file": (f"station-{language}.md", fixture["source"].encode(), "text/markdown")},
    )
    session.wait(lambda: session.ready_source(imported["id"]))
    note = session.note("Meeting record", fixture["note"])
    excluded = session.note("Excluded conflicting record", "EXCLUDED_MARKER: Opening is November 22, 2030.")
    context = {"source_ids": [imported["id"]], "note_ids": [note["id"]]}
    write_json(
        session.output / f"fixture-{language}.json",
        {
            **fixture,
            "context": context,
            "excluded_note": excluded,
        },
    )
    job = session.api(
        session.base + "/jobs",
        "POST",
        {
            "request_id": str(uuid4()),
            "kind": "presentation_outline",
            "language": language,
            "question": fixture["question"],
            "title": fixture["title"],
            "context": context,
        },
    )
    outline = session.material(session.terminal(job))
    assert len(outline["presentation"]["slides"]) == 2, "Requested two-slide outline was not followed"
    outline_review = review_checkpoint(session, f"{language}-outline", outline)

    # Exercise a real manual save before the explicit, separately queued deck job.
    document = outline["presentation"]
    document["title"] += " — reviewed" if language == "en" else " — проверено"
    document["template"] = "light" if language == "en" else "dark"
    edited = session.api(
        session.base + f"/materials/{outline['id']}/presentation",
        "PATCH",
        {
            "expected_revision": 1,
            "presentation": document,
        },
    )
    assert edited["presentation"]["revision"] == 2
    assert (
        session.api(session.base + f"/materials/{outline['id']}/presentation/revisions/1")["presentation"][
            "title"
        ]
        == fixture["title"]
    )
    session.restart()
    calls_before_assembly = len(session.guard.calls)
    job = session.api(
        session.base + "/jobs",
        "POST",
        {
            "request_id": str(uuid4()),
            "kind": "presentation",
            "outline_id": outline["id"],
            "outline_revision": 2,
        },
    )
    deck = session.material(session.terminal(job))
    assert deck["outline_revision"] == 2 and deck["context"] == outline["context"]
    assert deck["presentation"]["slides"] == edited["presentation"]["slides"], (
        "Assembly changed the accepted text, citations, IDs or review state"
    )
    assert len(session.guard.calls) == calls_before_assembly, "Assembly called a model"
    write_json(session.output / f"{language}-deck.json", deck)
    exports = export_and_reopen(session, language, deck)
    deck_review = review_checkpoint(session, f"{language}-deck", deck)
    for call in session.guard.calls:
        assert "EXCLUDED_MARKER" not in json.dumps(call.get("data", {})), "Excluded note reached model"
    return {"outline_review": outline_review, "deck_review": deck_review, "offline_assembly": True, **exports}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", action="store_true")
    parser.add_argument("--model", help="Existing local Ollama alias; not created by this evaluator")
    parser.add_argument("--source-model", default="gemma4:12b")
    parser.add_argument("--endpoint", default="http://127.0.0.1:11434/v1")
    parser.add_argument("--observe-ollama", help="Separate user Ollama endpoint; must remain idle")
    parser.add_argument("--owned-pid", type=int, action="append", default=[])
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if not args.run:
        print("Validated two synthetic EN/RU fixtures. No model requests made.")
        return 0
    if not args.model or not args.output:
        parser.error("--run requires an explicit --model and new --output directory")
    args.output.mkdir(parents=True, exist_ok=False)
    sys.path.insert(0, str(ROOT / "apps/api"))
    os.environ["PYTHON_KEYRING_BACKEND"] = "keyring.backends.null.Keyring"
    for key in ("OPENNOTEBOOK_API_KEY", "OPENAI_API_KEY", "ANTHROPIC_API_KEY", "OLLAMA_API_KEY"):
        os.environ.pop(key, None)
    import keyring
    import keyring.backends.null
    from model_evaluation03.guard import write_json
    from model_evaluation03.runner import manifest
    from model_evaluation03.session import EvaluationSession
    from model_evaluation04.guard import MonitoredGuard
    from model_evaluation04.resources import ResourceMonitor

    keyring.set_keyring(keyring.backends.null.Keyring())
    monitor = ResourceMonitor(args.output, owned_pids=args.owned_pid)
    guard = MonitoredGuard(
        args.output,
        args.endpoint,
        args.model,
        args.source_model,
        max_calls=6,
        minutes=20,
        monitor=monitor,
        observe_endpoint=args.observe_ollama,
    )
    session = EvaluationSession(ROOT, args.output, guard, {})
    write_json(
        args.output / "environment.json",
        {
            "source": manifest(),
            "evaluator_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            "model": args.model,
            "max_calls": 6,
            "endpoint": guard.endpoint,
            "observed_user_ollama": args.observe_ollama,
            "minimum_available_ram_bytes": monitor.minimum_ram_bytes,
            "minutes": 20,
            "fixtures": FIXTURES,
            "sampling": "Production defaults; alias restricts GPU layers and context externally",
            "model_management": "No create/download/delete/unload calls in this evaluator",
            "review": "Independent assistant review; not owner hands-on acceptance",
        },
    )
    error = None
    try:
        with monitor, guard.instrument():
            session.start()
            try:
                for language in FIXTURES:
                    session.run_case(language, lambda language=language: evaluate_language(session, language))
                guard.wait_idle()
            finally:
                session.close()
    except BaseException as caught:
        error = f"{type(caught).__name__}: {caught}"
        print(error, flush=True)
    finally:
        session.save(status="stopped_incomplete" if error else "completed_with_separate_reviews", error=error)
    return 1 if error else 0


if __name__ == "__main__":
    raise SystemExit(main())
