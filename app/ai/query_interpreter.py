from app.ai.ollama_client import (
    LocalAIError,
    generate_structured_response,
)
from app.ai.query_prompt import build_query_messages
from app.ai.query_schema import QUERY_SCHEMA


VALID_INTENTS = {
    "find_startups",
    "find_investors",
    "startup_history",
    "compare_startups",
    "unknown",
}


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
) -> dict:
    messages = build_query_messages(
        question=question,
        current_year=current_year,
    )

    query = generate_structured_response(
        messages=messages,
        schema=QUERY_SCHEMA,
    )

    return validate_investment_query(query)