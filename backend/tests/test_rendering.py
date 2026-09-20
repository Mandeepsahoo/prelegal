from app.documents.catalog import get_document_type
from app.documents.rendering import render_document
from app.documents.schemas import FieldValue


def test_renders_key_terms_table_and_standard_terms():
    doc = get_document_type("sla")
    fields = [FieldValue(label="Provider", value="Acme Inc"), FieldValue(label="Customer", value="")]

    rendered = render_document(doc, fields)

    assert "# Service Level Agreement" in rendered
    assert "## Key Terms" in rendered
    assert "| Provider | Acme Inc |" in rendered
    assert "Customer" not in rendered.split("## Key Terms")[1].split("---")[0]
    assert "Target Uptime" in rendered  # from the real standard terms text


def test_renders_placeholder_when_no_fields_known():
    doc = get_document_type("dpa")
    rendered = render_document(doc, [])
    assert "_No terms have been filled in yet._" in rendered


def test_includes_draft_disclaimer():
    doc = get_document_type("baa")
    rendered = render_document(doc, [])
    assert "not legal advice" in rendered


def test_strips_span_tags_from_standard_terms():
    doc = get_document_type("sla")
    rendered = render_document(doc, [])
    standard_terms = rendered.split("---", 1)[1]
    assert "<span" not in standard_terms
    assert "</span>" not in standard_terms
    # The inner text (the actual field reference) must survive the strip.
    assert "Target Uptime" in standard_terms
