"""Loads the supported document types from the repo-root catalog.json and
template files, so their names/descriptions stay in sync with that single
source of truth instead of being duplicated here.
"""

import json
from pathlib import Path

from pydantic import BaseModel

APP_DIR = Path(__file__).resolve().parent.parent
BACKEND_DIR = APP_DIR.parent
REPO_ROOT = BACKEND_DIR.parent
TEMPLATES_DIR = REPO_ROOT / "templates"
CATALOG_PATH = REPO_ROOT / "catalog.json"

_MUTUAL_NDA_FILENAME = "Mutual-NDA.md"
_MUTUAL_NDA_COVERPAGE_FILENAME = "Mutual-NDA-coverpage.md"


class DocumentType(BaseModel):
    key: str
    name: str
    description: str
    filename: str
    # The Mutual NDA has its own hand-built chat/template flow (frontend/src/lib/nda/*)
    # predating this generic system; special types are listed for the picker but
    # routed to that dedicated flow instead of the generic chat/render endpoints.
    is_special: bool = False


def _slug(filename: str) -> str:
    return Path(filename).stem.lower().replace("_", "-")


def _load_document_types() -> list[DocumentType]:
    raw = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
    types: list[DocumentType] = []
    for entry in raw:
        if entry["filename"] == _MUTUAL_NDA_COVERPAGE_FILENAME:
            continue  # folded into the single "mutual-nda" entry below
        is_nda = entry["filename"] == _MUTUAL_NDA_FILENAME
        types.append(
            DocumentType(
                key="mutual-nda" if is_nda else _slug(entry["filename"]),
                name=entry["name"],
                description=entry["description"],
                filename=entry["filename"],
                is_special=is_nda,
            )
        )
    return types


DOCUMENT_TYPES: list[DocumentType] = _load_document_types()
_BY_KEY = {doc.key: doc for doc in DOCUMENT_TYPES}


def get_document_type(key: str) -> DocumentType | None:
    return _BY_KEY.get(key)


def load_template_text(document_type: DocumentType) -> str:
    return (TEMPLATES_DIR / document_type.filename).read_text(encoding="utf-8")
