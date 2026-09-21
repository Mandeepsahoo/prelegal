from app.documents.schemas import FieldValue, merge_field_values


def test_merge_applies_newly_known_values():
    previous = [FieldValue(label="Customer", value="")]
    latest = [FieldValue(label="Customer", value="Acme Inc")]

    merged = merge_field_values(previous, latest)

    assert merged == [FieldValue(label="Customer", value="Acme Inc")]


def test_merge_keeps_previous_value_when_latest_is_blank():
    previous = [FieldValue(label="Customer", value="Acme Inc")]
    latest = [FieldValue(label="Customer", value="")]

    merged = merge_field_values(previous, latest)

    assert merged == [FieldValue(label="Customer", value="Acme Inc")]


def test_merge_appends_new_labels_not_seen_before():
    previous = [FieldValue(label="Customer", value="Acme Inc")]
    latest = [FieldValue(label="Customer", value="Acme Inc"), FieldValue(label="Provider", value="Globex")]

    merged = merge_field_values(previous, latest)

    assert merged == [
        FieldValue(label="Customer", value="Acme Inc"),
        FieldValue(label="Provider", value="Globex"),
    ]


def test_merge_preserves_label_order_from_previous_first():
    previous = [FieldValue(label="B", value="2"), FieldValue(label="A", value="1")]
    latest = [FieldValue(label="A", value="1-updated")]

    merged = merge_field_values(previous, latest)

    assert [field.label for field in merged] == ["B", "A"]
    assert merged[1].value == "1-updated"
