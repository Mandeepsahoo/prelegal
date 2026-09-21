from typing import Literal

from pydantic import BaseModel, Field

# Same rationale as nda_schemas.py: this triggers a real, paid LLM call with
# no auth in front of it, so inputs are capped.
MAX_MESSAGES_PER_REQUEST = 40
MAX_MESSAGE_LENGTH = 4000


class DocumentTypeInfo(BaseModel):
    key: str
    name: str
    description: str
    is_special: bool


class FieldValue(BaseModel):
    label: str
    value: str = ""


class DocumentChatMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str = Field(max_length=MAX_MESSAGE_LENGTH)


class DocumentChatTurnResult(BaseModel):
    """The assistant's structured response for a single chat turn.

    Like NDA chat (see nda_schemas.ChatTurnResult), `fields` is the model's
    full current understanding of every known field, not a nullable patch -
    that turned out to be unreliable for this model/provider in practice.
    """

    reply: str
    fields: list[FieldValue]
    is_complete: bool


class DocumentChatRequest(BaseModel):
    document_key: str
    messages: list[DocumentChatMessage] = Field(max_length=MAX_MESSAGES_PER_REQUEST)
    fields: list[FieldValue] = Field(default_factory=list)


class DocumentChatResponse(BaseModel):
    reply: str
    fields: list[FieldValue]
    is_complete: bool
    document: str


class ClassifyRequest(BaseModel):
    description: str = Field(min_length=1, max_length=MAX_MESSAGE_LENGTH)


class ClassifyResponse(BaseModel):
    """The model's best guess at which supported document type (if any)
    matches a free-text description of what the user needs. Used both as the
    LLM's structured-output schema and the endpoint's response model."""

    matched_key: str | None
    reply: str


def merge_field_values(previous: list[FieldValue], latest: list[FieldValue]) -> list[FieldValue]:
    """Same "full restatement, prefer the previous value when a turn leaves
    it blank" pattern as nda_schemas.merge_fields, keyed by label since the
    field set is dynamic per document type rather than a fixed set of
    attributes."""

    previous_by_label = {field.label: field.value for field in previous}
    merged = dict(previous_by_label)
    for field in latest:
        if field.value.strip():
            merged[field.label] = field.value

    ordered_labels = list(previous_by_label) + [
        field.label for field in latest if field.label not in previous_by_label
    ]
    return [FieldValue(label=label, value=merged.get(label, "")) for label in ordered_labels]
