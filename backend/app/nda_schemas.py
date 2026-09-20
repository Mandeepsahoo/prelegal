from typing import Literal

from pydantic import BaseModel, Field

# Caps on chat request size — this endpoint triggers a real, paid LLM call per
# request with no auth in front of it (see PL-4), so unbounded input would let
# a single caller drive arbitrarily large API costs.
MAX_MESSAGES_PER_REQUEST = 40
MAX_MESSAGE_LENGTH = 4000

_STRING_FIELDS = (
    "purpose",
    "effectiveDate",
    "governingLaw",
    "jurisdiction",
    "modifications",
)
_PARTY_STRING_FIELDS = ("name", "title", "company", "noticeAddress")


class PartyFields(BaseModel):
    """A party's details, as known so far. Every field defaults to "" (unknown)."""

    name: str = ""
    title: str = ""
    company: str = ""
    noticeAddress: str = ""


class NdaFields(BaseModel):
    """The full set of Mutual NDA fields, mirroring frontend/src/lib/nda/types.ts."""

    purpose: str = ""
    effectiveDate: str = ""
    termType: Literal["fixed", "until-terminated"] = "fixed"
    termYears: int = 1
    confidentialityType: Literal["fixed", "perpetuity"] = "fixed"
    confidentialityYears: int = 1
    governingLaw: str = ""
    jurisdiction: str = ""
    modifications: str = ""
    partyA: PartyFields = PartyFields()
    partyB: PartyFields = PartyFields()


class ChatTurnResult(BaseModel):
    """The assistant's structured response for a single chat turn.

    `fields` is the model's full current understanding of every field, not just
    what changed this turn — asking a structured-output model for a nullable
    "only what's new" patch turned out to be unreliable in practice (fields it
    had clearly just extracted came back empty). Always returning the complete
    picture sidesteps that, at the cost of the model needing to keep restating
    already-known values, which the system prompt asks it to do.
    """

    reply: str
    fields: NdaFields
    is_complete: bool


class ChatMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str = Field(max_length=MAX_MESSAGE_LENGTH)


class NdaChatRequest(BaseModel):
    messages: list[ChatMessage] = Field(max_length=MAX_MESSAGES_PER_REQUEST)
    fields: NdaFields


class NdaChatResponse(BaseModel):
    reply: str
    fields: NdaFields
    is_complete: bool


def _merge_party(previous: PartyFields, latest: PartyFields) -> PartyFields:
    updates = {
        field: getattr(latest, field)
        for field in _PARTY_STRING_FIELDS
        if getattr(latest, field)
    }
    return previous.model_copy(update=updates)


def merge_fields(previous: NdaFields, latest: NdaFields) -> NdaFields:
    """The model re-states its full understanding every turn; as a safety net
    against it dropping a value it doesn't happen to repeat, an empty string in
    `latest` falls back to whatever was already known rather than clearing it.
    Non-string fields (term/confidentiality type and length) always have a
    real default, so the latest value is trusted outright."""

    updates = {field: getattr(latest, field) for field in _STRING_FIELDS if getattr(latest, field)}
    return previous.model_copy(
        update={
            **updates,
            "termType": latest.termType,
            "termYears": latest.termYears,
            "confidentialityType": latest.confidentialityType,
            "confidentialityYears": latest.confidentialityYears,
            "partyA": _merge_party(previous.partyA, latest.partyA),
            "partyB": _merge_party(previous.partyB, latest.partyB),
        }
    )
