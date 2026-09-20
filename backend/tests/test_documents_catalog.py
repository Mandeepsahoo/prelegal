from app.documents.catalog import DOCUMENT_TYPES, get_document_type, load_template_text


def test_catalog_loads_all_eleven_document_types():
    assert len(DOCUMENT_TYPES) == 11


def test_mutual_nda_entries_are_folded_into_one_special_type():
    nda_entries = [doc for doc in DOCUMENT_TYPES if doc.key == "mutual-nda"]
    assert len(nda_entries) == 1
    assert nda_entries[0].is_special is True
    assert nda_entries[0].filename == "Mutual-NDA.md"


def test_keys_are_unique():
    keys = [doc.key for doc in DOCUMENT_TYPES]
    assert len(keys) == len(set(keys))


def test_only_mutual_nda_is_special():
    special = [doc for doc in DOCUMENT_TYPES if doc.is_special]
    assert [doc.key for doc in special] == ["mutual-nda"]


def test_get_document_type_returns_none_for_unknown_key():
    assert get_document_type("not-a-real-document") is None


def test_get_document_type_returns_match():
    doc = get_document_type("dpa")
    assert doc is not None
    assert doc.filename == "DPA.md"


def test_load_template_text_reads_real_file():
    doc = get_document_type("sla")
    text = load_template_text(doc)
    assert "Service Level Agreement" in text
