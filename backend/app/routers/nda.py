from fastapi import APIRouter, Depends, HTTPException, status

from ..nda_llm import LlmError, generate_chat_turn
from ..nda_schemas import NdaChatRequest, NdaChatResponse, merge_fields
from ..rate_limit import make_rate_limiter

router = APIRouter(prefix="/api/nda", tags=["nda"])

# This endpoint has no auth in front of it (PL-4 deliberately keeps the NDA
# tool open) but does trigger a real, paid LLM call per request, so it's
# rate-limited per IP as a cost/abuse guard.
chat_rate_limit = make_rate_limiter(max_requests=20, window_seconds=60)


@router.post("/chat", response_model=NdaChatResponse, dependencies=[Depends(chat_rate_limit)])
def chat(payload: NdaChatRequest) -> NdaChatResponse:
    if not payload.messages:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "At least one message is required.")

    try:
        result = generate_chat_turn(messages=payload.messages, current_fields=payload.fields)
    except LlmError as exc:
        raise HTTPException(status.HTTP_502_BAD_GATEWAY, str(exc)) from exc

    merged_fields = merge_fields(payload.fields, result.fields)
    return NdaChatResponse(reply=result.reply, fields=merged_fields, is_complete=result.is_complete)
