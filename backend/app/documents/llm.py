from litellm import completion

from ..config import settings
from .catalog import DOCUMENT_TYPES, DocumentType
from .schemas import ClassifyResponse, DocumentChatMessage, DocumentChatTurnResult, FieldValue

MODEL = "openrouter/openai/gpt-oss-120b"
EXTRA_BODY = {"provider": {"order": ["cerebras"]}}
REQUEST_TIMEOUT_SECONDS = 30


class LlmError(RuntimeError):
    """Raised when the LLM call fails or returns something we can't parse."""


def _chat_system_prompt(document_type: DocumentType, field_labels: list[str]) -> str:
    fields_list = "\n".join(f"- {label}" for label in field_labels)
    return f"""You are an assistant helping a user fill out a Common Paper {document_type.name} \
through natural conversation.

{document_type.description}

Fields you need to collect, referenced by its Standard Terms:
{fields_list}

Ask about only the next one or two things still missing, in a natural, conversational \
way - don't interrogate the user with a giant list, and don't re-ask about anything \
already known unless the user brings it up again.

Your "fields" output must be your FULL current understanding of every field you've \
learned so far, not just what changed this message: carry forward every value you \
were already told, and add anything you just learned or the user just corrected. \
Only leave a field blank if it's still genuinely unknown. Set is_complete to true once \
you have the most important fields (particularly who the parties are), and tell the \
user in "reply" that their document is ready.
"""


def _known_fields_message(fields: list[FieldValue]) -> str:
    if not fields:
        return "No fields are known yet."
    lines = "\n".join(f"- {field.label}: {field.value or '(unknown)'}" for field in fields)
    return f"Known fields so far:\n{lines}"


def generate_chat_turn(
    document_type: DocumentType,
    field_labels: list[str],
    messages: list[DocumentChatMessage],
    current_fields: list[FieldValue],
) -> DocumentChatTurnResult:
    llm_messages = [
        {"role": "system", "content": _chat_system_prompt(document_type, field_labels)},
        {"role": "system", "content": _known_fields_message(current_fields)},
        *[{"role": message.role, "content": message.content} for message in messages],
    ]

    try:
        response = completion(
            model=MODEL,
            messages=llm_messages,
            response_format=DocumentChatTurnResult,
            reasoning_effort="low",
            extra_body=EXTRA_BODY,
            api_key=settings.openrouter_api_key,
            timeout=REQUEST_TIMEOUT_SECONDS,
        )
    except Exception as exc:  # litellm raises a variety of provider-specific errors
        raise LlmError("Failed to reach the AI assistant.") from exc

    raw_content = response.choices[0].message.content
    try:
        return DocumentChatTurnResult.model_validate_json(raw_content)
    except ValueError as exc:
        raise LlmError("The AI assistant returned an unexpected response.") from exc


_CLASSIFY_SYSTEM_PROMPT = """You help route a user to the right legal document template. \
Available document types:
{catalog}

Given the user's free-text description of what they need, decide which single document \
type (by its key) best matches, if any matches reasonably well. If nothing is a good \
match, set matched_key to null and use "reply" to explain we don't support that, then \
suggest the closest available type by name. If there is a good match, set matched_key \
to its exact key and use "reply" to briefly confirm what you're about to help them \
create.
"""


def classify_document_request(description: str) -> ClassifyResponse:
    catalog_lines = "\n".join(f"- {doc.key}: {doc.name} - {doc.description}" for doc in DOCUMENT_TYPES)
    system_prompt = _CLASSIFY_SYSTEM_PROMPT.format(catalog=catalog_lines)

    try:
        response = completion(
            model=MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": description},
            ],
            response_format=ClassifyResponse,
            reasoning_effort="low",
            extra_body=EXTRA_BODY,
            api_key=settings.openrouter_api_key,
            timeout=REQUEST_TIMEOUT_SECONDS,
        )
    except Exception as exc:
        raise LlmError("Failed to reach the AI assistant.") from exc

    raw_content = response.choices[0].message.content
    try:
        result = ClassifyResponse.model_validate_json(raw_content)
    except ValueError as exc:
        raise LlmError("The AI assistant returned an unexpected response.") from exc

    # Defense in depth: don't trust the model's key even though structured
    # outputs should constrain it - validate it's a real, known document type.
    valid_keys = {doc.key for doc in DOCUMENT_TYPES}
    if result.matched_key is not None and result.matched_key not in valid_keys:
        result = ClassifyResponse(matched_key=None, reply=result.reply)

    return result
