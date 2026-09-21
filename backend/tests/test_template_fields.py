from app.documents.template_fields import extract_field_labels


def test_extracts_unique_labels_in_first_seen_order():
    text = (
        '<span class="coverpage_link">Customer</span> and '
        '<span class="coverpage_link">Provider</span> agree. '
        '<span class="coverpage_link">Customer</span> again.'
    )
    assert extract_field_labels(text) == ["Customer", "Provider"]


def test_strips_possessive_suffix_and_dedupes_with_base_form():
    text = (
        '<span class="keyterms_link">Customer</span> and '
        '<span class="keyterms_link">Customer’s</span> and '
        "<span class=\"keyterms_link\">Customer's</span>"
    )
    assert extract_field_labels(text) == ["Customer"]


def test_matches_any_class_ending_in_link():
    text = (
        '<span class="orderform_link">A</span> '
        '<span class="businessterms_link">B</span> '
        '<span class="sow_link">C</span>'
    )
    assert extract_field_labels(text) == ["A", "B", "C"]


def test_ignores_spans_with_unrelated_classes():
    text = '<span class="header_2">Not a field</span> <span class="coverpage_link">Customer</span>'
    assert extract_field_labels(text) == ["Customer"]


def test_real_sla_template_extracts_expected_fields():
    from app.documents.catalog import get_document_type, load_template_text

    doc = get_document_type("sla")
    labels = extract_field_labels(load_template_text(doc))
    assert "Target Uptime" in labels
    assert "Provider" in labels
    assert "Customer" in labels
