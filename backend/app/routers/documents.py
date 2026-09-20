from fastapi import APIRouter, Depends, HTTPException, status

from ..documents.catalog import DOCUMENT_TYPES, get_document_type, load_template_text
from ..documents.llm import LlmError, classify_document_request, generate_chat_turn
from ..documents.rendering import render_document
from ..documents.schemas import (
    ClassifyRequest,
    ClassifyResponse,
    DocumentChatRequest,
    DocumentChatResponse,
    DocumentTypeInfo,
    merge_field_values,
)
from ..documents.template_fields import extract_field_labels
from ..rate_limit import make_rate_limiter

router = APIRouter(prefix="/api/documents", tags=["documents"])

# Same reasoning as routers/nda.py: these endpoints have no auth in front of
# them but each triggers a real, paid LLM call, so they're rate-limited.
chat_rate_limit = make_rate_limiter(max_requests=20, window_seconds=60)
classify_rate_limit = make_rate_limiter(max_requests=20, window_seconds=60)


@router.get("/types", response_model=list[DocumentTypeInfo])
def list_document_types() -> list[DocumentTypeInfo]:
    return [
        DocumentTypeInfo(
            key=doc.key, name=doc.name, description=doc.description, is_special=doc.is_special
        )
        for doc in DOCUMENT_TYPES
    ]


@router.post("/classify", response_model=ClassifyResponse, dependencies=[Depends(classify_rate_limit)])
def classify(payload: ClassifyRequest) -> ClassifyResponse:
    try:
        return classify_document_request(payload.description)
    except LlmError as exc:
        raise HTTPException(status.HTTP_502_BAD_GATEWAY, str(exc)) from exc


@router.post("/chat", response_model=DocumentChatResponse, dependencies=[Depends(chat_rate_limit)])
def chat(payload: DocumentChatRequest) -> DocumentChatResponse:
    document_type = get_document_type(payload.document_key)
    if document_type is None or document_type.is_special:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Unknown document type.")

    if not payload.messages:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "At least one message is required.")

    field_labels = extract_field_labels(load_template_text(document_type))

    try:
        result = generate_chat_turn(document_type, field_labels, payload.messages, payload.fields)
    except LlmError as exc:
        raise HTTPException(status.HTTP_502_BAD_GATEWAY, str(exc)) from exc

    merged_fields = merge_field_values(payload.fields, result.fields)
    document = render_document(document_type, merged_fields)
    return DocumentChatResponse(
        reply=result.reply,
        fields=merged_fields,
        is_complete=result.is_complete,
        document=document,
    )
