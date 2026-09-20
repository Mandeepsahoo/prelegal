"""Renders a generic (non-Mutual-NDA) document from collected field values.

Unlike the Mutual NDA, these templates have no accompanying cover-page file
in this repo to weave values into, and different Common Paper template
families use inconsistent field-reference conventions (see template_fields.py) -
rewriting the legal prose itself to interpolate values would risk subtly
changing its meaning. Instead this renders a generated "Key Terms" cover
sheet (the collected field values) followed by the official, unmodified
Standard Terms text, mirroring the Mutual NDA's own cover-page + standard-terms
structure.
"""

import re

from .catalog import DocumentType, load_template_text
from .schemas import FieldValue

DRAFT_DISCLAIMER = (
    "*This document is a draft generated for convenience and is not legal advice. "
    "It should be reviewed by a qualified attorney before use.*"
)

# These templates wrap term references in <span class="..._link"> tags for
# semantic markup (see template_fields.py) with no accompanying CSS, so they'd
# just render as literal escaped text in the markdown preview. Strip the tags,
# keeping their inner text, rather than rendering raw (untrusted-feeling, and
# unnecessary) HTML on the frontend.
_SPAN_TAG_RE = re.compile(r"</?span[^>]*>")


def render_document(document_type: DocumentType, fields: list[FieldValue]) -> str:
    standard_terms = _SPAN_TAG_RE.sub("", load_template_text(document_type))

    key_terms_lines = [f"# {document_type.name}", "", DRAFT_DISCLAIMER, "", "## Key Terms", ""]
    known_fields = [field for field in fields if field.value.strip()]
    if known_fields:
        key_terms_lines.append("| Term | Value |")
        key_terms_lines.append("|:--- | :--- |")
        key_terms_lines.extend(f"| {field.label} | {field.value.strip()} |" for field in known_fields)
    else:
        key_terms_lines.append("_No terms have been filled in yet._")

    cover_sheet = "\n".join(key_terms_lines)
    return f"{cover_sheet}\n\n---\n\n{standard_terms}"
