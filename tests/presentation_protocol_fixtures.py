"""Adapt historical text to the private wire shape, without repairing its meaning.

Audit responses here are synthetic protocol fixtures, never new model verdicts.
Original recordings remain unchanged and keep their observed semantic failures.
"""


def ledger_from_slides(raw: dict, evidence: list[dict]) -> dict:
    passages = {item["id"]: item["quote"] for item in evidence}
    facts, slides, identities = [], [], {}

    def reference(text, labels):
        key = (text, tuple(labels))
        if key not in identities:
            identity = f"F{len(facts) + 1}"
            identities[key] = identity
            facts.append(
                {
                    "id": identity,
                    "text": text,
                    "evidence": [{"evidence_id": label, "quote": passages[label]} for label in labels],
                }
            )
        return identities[key]

    for slide in raw["slides"]:
        labels = slide["evidence_ids"]
        slides.append(
            {
                "layout": slide["layout"],
                "title_id": reference(slide["title"], labels),
                "bullet_ids": [reference(text, labels) for text in slide["bullets"]],
                "note_ids": [reference(slide["notes"], labels)] if slide["notes"] else [],
            }
        )
    return {"claims": facts, "slides": slides}


def audit_response(data: dict, rejected=(), uncertain=()) -> dict:
    passages = {item["id"]: item["quote"] for item in data["evidence"]}
    return {
        "reviews": [
            {
                "claim_id": claim["claim_id"],
                "verdict": (
                    "unsupported"
                    if claim["claim_id"] in rejected
                    else "uncertain"
                    if claim["claim_id"] in uncertain
                    else "supported"
                ),
                "support": []
                if claim["claim_id"] in (*rejected, *uncertain)
                else [{"evidence_id": key, "quote": passages[key]} for key in claim["evidence_ids"]],
                "reason": "Synthetic audit fixture; not a factual quality measurement.",
            }
            for claim in data["claims"]
        ]
    }
