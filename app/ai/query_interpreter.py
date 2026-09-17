from app.ai.ollama_client import (
    LocalAIError,
    generate_structured_response,
)
from app.ai.query_prompt import build_query_messages
from app.ai.query_schema import QUERY_SCHEMA
import re

VALID_INTENTS = {
    "find_startups",
    "find_investors",
    "startup_history",
    "compare_startups",
    "unknown",
}
STRICT_MINIMUM_AMOUNT = re.compile(
    r"\b(?:more than|greater than|above|over)\s+"
    r"\$?\s*\d[\d.,]*\s*"
    r"(?:million|m\b|usd\b|dollars?\b)"
    r"|\b\d[\d.,]*\s*milyon"
    r"(?:\s+dolar\w*)?\s+üzerinde\b",
    re.IGNORECASE,
)


def validate_investment_query(query: dict) -> dict:
    intent = query.get("intent")

    if intent not in VALID_INTENTS:
        raise LocalAIError(
            f"The local model returned an invalid intent: {intent!r}"
        )

    if (
        query.get("only_applicants")
        and query.get("only_non_applicants")
    ):
        raise LocalAIError(
            "The query cannot request applicants and "
            "non-applicants at the same time."
        )

    start_year = query.get("start_year")
    end_year = query.get("end_year")

    if (
        start_year is not None
        and end_year is not None
        and start_year > end_year
    ):
        raise LocalAIError(
            "The query start year cannot be later "
            "than the end year."
        )

    minimum_amount = query.get(
        "minimum_amount_million_usd"
    )
    maximum_amount = query.get(
        "maximum_amount_million_usd"
    )

    if (
        minimum_amount is not None
        and maximum_amount is not None
        and minimum_amount > maximum_amount
    ):
        raise LocalAIError(
            "The minimum investment amount cannot exceed "
            "the maximum investment amount."
        )

    if (
        query.get("needs_clarification")
        and not query.get("clarification_question")
    ):
        raise LocalAIError(
            "A clarification question is required."
        )

    return query


def interpret_investment_question(
        question: str,
        current_year: int | None = None,
        conversation_history: list[dict] | None = None,
) -> dict:
    messages = build_query_messages(
        question=question,
        current_year=current_year,
        conversation_history=conversation_history,
    )

    query = generate_structured_response(
        messages=messages,
        schema=QUERY_SCHEMA,
    )

    if (
            query.get("minimum_amount_million_usd") is not None
            and STRICT_MINIMUM_AMOUNT.search(question)
    ):
        query = {
            **query,
            "minimum_amount_inclusive": False,
        }

    return validate_investment_query(query)