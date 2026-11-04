"""Read complete normalized source blocks without changing the search index."""

import hashlib

from ...documents.models import NormalizedDocument
from ...storage import ConflictError, Store
from ..sources.repository import Sources
from .errors import ContextUnavailable
from .evidence import representative_groups


def source_blocks(
    store: Store, notebook: str, reference: dict, *, limit: int, max_chars: int
) -> tuple[list[dict], int]:
    source = store.source(notebook, reference["id"])
    if source["version"] != reference["version"]:
        raise ConflictError("Selected source changed before reading its document.")
    try:
        document = NormalizedDocument.model_validate(Sources(store).document(notebook, source))
    except (OSError, ValueError, TypeError) as error:
        raise ContextUnavailable("Reimport the source to restore its saved document.") from error
    passages, total = [], 0
    for index, element in enumerate(document.elements):
        if not element.text.strip():
            continue
        total += 1
        end = len(element.text)
        if end > max_chars:
            continue
        key = hashlib.sha256(f"{source['id']}:{source['version']}:{index}:0:{end}".encode()).hexdigest()
        passages.append(
            {
                "id": key,
                "source_id": source["id"],
                "version": source["version"],
                "title": source["title"],
                "quote": element.text,
                "location": {
                    **element.model_dump(exclude={"text"}),
                    "element": index,
                    "offset_start": 0,
                    "offset_end": end,
                },
            }
        )
    return representative_groups([passages], limit=limit), total
