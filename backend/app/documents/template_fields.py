"""Extracts the fill-in fields a Common Paper Standard Terms template
references, so the chat knows what to ask about without anyone hand-authoring
a field list per document type.

These templates mark fill-in terms with spans like
`<span class="coverpage_link">Customer</span>` or
`<span class="keyterms_link">Governing Law</span>` - the class name varies
per document family (coverpage_link, orderform_link, keyterms_link,
businessterms_link, sow_link, ...) but always ends in "_link", and the same
field is referenced many times (e.g. "Customer" appears dozens of times), so
this dedupes to the first-seen order.
"""

import re

_FIELD_SPAN_RE = re.compile(r'<span class="[a-z]+_link"[^>]*>(.*?)</span>', re.DOTALL)
_POSSESSIVE_RE = re.compile(r"[’']s$")


def extract_field_labels(template_text: str) -> list[str]:
    seen: dict[str, None] = {}
    for match in _FIELD_SPAN_RE.finditer(template_text):
        label = _POSSESSIVE_RE.sub("", match.group(1).strip())
        if label and label not in seen:
            seen[label] = None
    return list(seen)
