from fastapi import APIRouter, HTTPException, status

from ..nda_llm import LlmError, generate_chat_turn
from ..nda_schemas import NdaChatRequest, NdaChatResponse, merge_fields

router = APIRouter(prefix="/api/nda", tags=["nda"])


@router.post("/chat", response_model=NdaChatResponse)
def chat(payload: NdaChatRequest) -> NdaChatResponse:
    if not payload.messages:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "At least one message is required.")

    try:
        result = generate_chat_turn(messages=payload.messages, current_fields=payload.fields)
    except LlmError as exc:
        raise HTTPException(status.HTTP_502_BAD_GATEWAY, str(exc)) from exc

    merged_fields = merge_fields(payload.fields, result.fields)
    return NdaChatResponse(reply=result.reply, fields=merged_fields, is_complete=result.is_complete)
