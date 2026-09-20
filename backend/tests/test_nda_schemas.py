from app.nda_schemas import NdaFields, PartyFields, merge_fields


def test_merge_fields_applies_newly_known_values():
    previous = NdaFields(purpose="Evaluating a deal", governingLaw="")
    latest = NdaFields(purpose="Evaluating a deal", governingLaw="Delaware")

    merged = merge_fields(previous, latest)

    assert merged.purpose == "Evaluating a deal"
    assert merged.governingLaw == "Delaware"


def test_merge_fields_keeps_previous_value_when_latest_is_blank():
    previous = NdaFields(governingLaw="Delaware")
    latest = NdaFields(governingLaw="")

    merged = merge_fields(previous, latest)

    assert merged.governingLaw == "Delaware"


def test_merge_fields_trusts_latest_enum_and_numeric_fields_outright():
    previous = NdaFields(termType="fixed", termYears=1)
    latest = NdaFields(termType="until-terminated", termYears=1)

    merged = merge_fields(previous, latest)

    assert merged.termType == "until-terminated"


def test_merge_fields_merges_nested_party_fields():
    previous = NdaFields(partyA=PartyFields(name="Alice", company="Acme"))
    latest = NdaFields(partyA=PartyFields(name="Alice", company="Acme", title="CEO"))

    merged = merge_fields(previous, latest)

    assert merged.partyA.name == "Alice"
    assert merged.partyA.company == "Acme"
    assert merged.partyA.title == "CEO"


def test_merge_fields_keeps_previous_party_value_when_latest_is_blank():
    previous = NdaFields(partyA=PartyFields(name="Alice"))
    latest = NdaFields(partyA=PartyFields(name=""))

    merged = merge_fields(previous, latest)

    assert merged.partyA.name == "Alice"


def test_merge_fields_does_not_mutate_previous():
    previous = NdaFields(purpose="Original purpose")
    latest = NdaFields(purpose="Updated purpose")

    merge_fields(previous, latest)

    assert previous.purpose == "Original purpose"
