from litellm import completion

from .config import settings
from .nda_schemas import ChatMessage, ChatTurnResult, NdaFields

MODEL = "openrouter/openai/gpt-oss-120b"
EXTRA_BODY = {"provider": {"order": ["cerebras"]}}
REQUEST_TIMEOUT_SECONDS = 30

SYSTEM_PROMPT = """You are an assistant helping a user fill out a Common Paper Mutual \
Non-Disclosure Agreement (NDA) through natural conversation.

Fields you need, roughly in priority order:
- partyA / partyB: each needs a name, title, company, and notice address (usually an \
email or mailing address).
- purpose: why the two parties are sharing confidential information.
- governingLaw: the US state whose law governs the agreement.
- jurisdiction: where legal disputes would be resolved, e.g. "courts located in New \
Castle, DE".
- termType/termYears: how long the MNDA itself lasts ("fixed" for N years, or \
"until-terminated"). Default to 1 year fixed if the user has no preference.
- confidentialityType/confidentialityYears: how long confidentiality obligations last \
("fixed" for N years, or "perpetuity"). Default to 1 year fixed if the user has no \
preference.
- modifications: any custom changes to the standard terms. Optional — leave blank \
unless the user mentions something.
- effectiveDate: an ISO date (YYYY-MM-DD) the agreement starts. Default to today if \
not specified.

You will be told the fields already known so far, as JSON. Ask about only the next \
one or two things still missing, in a natural, conversational way — don't interrogate \
the user with a giant list, and don't re-ask about anything already known unless the \
user brings it up again.

Your "fields" output must be your FULL current understanding of every field, not just \
what changed this message: carry forward every value you were already told is known, \
and add anything you just learned or the user just corrected. Only leave a field at \
its default/blank if it is genuinely still unknown. Set is_complete to true once you \
have at least both parties, the purpose, governing law, and jurisdiction (the \
remaining fields can rely on their defaults), and tell the user in "reply" that their \
NDA is ready.
"""


class LlmError(RuntimeError):
    """Raised when the LLM call fails or returns something we can't parse."""


def _known_fields_message(fields: NdaFields) -> str:
    return "Known fields so far (JSON):\n" + fields.model_dump_json(indent=2)


def generate_chat_turn(messages: list[ChatMessage], current_fields: NdaFields) -> ChatTurnResult:
    llm_messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "system", "content": _known_fields_message(current_fields)},
        *[{"role": message.role, "content": message.content} for message in messages],
    ]

    try:
        response = completion(
            model=MODEL,
            messages=llm_messages,
            response_format=ChatTurnResult,
            reasoning_effort="low",
            extra_body=EXTRA_BODY,
            api_key=settings.openrouter_api_key,
            timeout=REQUEST_TIMEOUT_SECONDS,
        )
    except Exception as exc:  # litellm raises a variety of provider-specific errors
        raise LlmError("Failed to reach the AI assistant.") from exc

    raw_content = response.choices[0].message.content
    try:
        return ChatTurnResult.model_validate_json(raw_content)
    except ValueError as exc:
        raise LlmError("The AI assistant returned an unexpected response.") from exc
