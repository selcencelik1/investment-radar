import re

from app.ai.investment_search import search_investments
from app.ai.ollama_client import LocalAIError
from app.ai.query_interpreter import interpret_investment_question
from app.database.applicant_repository import get_applicant_names
from app.database.investment_repository import (
    get_all_investment_records,
)
from app.matching.investment_grouper import (
    group_investment_records,
)
from app.parser.normalizer import normalize_startup_name

FOLLOW_UP_REFERENCE = re.compile(
    r"\b(?:"
    r"those|these|them|which\s+ones|"
    r"bunlar\w*|şunlar\w*|onlar\w*|"
    r"kaç[ıi]\w*|kaç\s+tanesi|"
    r"hangisi|hangiler[ıi]\w*"
    r")\b",
    re.IGNORECASE,
)

EACH_ROUND_REFERENCE = re.compile(
    r"\b(?:each|every|both)\s+"
    r"(?:(?:investment|funding)\s+)?rounds?\b"
    r"|\bher\s+bir\s+(?:yatırım|tur)\b",
    re.IGNORECASE,
)


def get_previous_result_scope(
    question: str,
    conversation_history: list[dict] | None,
) -> tuple[set[str] | None, dict | None]:
    if not FOLLOW_UP_REFERENCE.search(question):
        return None, None

    for message in reversed(conversation_history or []):
        if message.get("role") != "assistant":
            continue

        previous_results = message.get("results")

        if not isinstance(previous_results, list):
            return None, None

        startup_keys = {
            normalize_startup_name(item["startup_name"])
            for item in previous_results
            if (
                isinstance(item, dict)
                and isinstance(item.get("startup_name"), str)
                and item["startup_name"].strip()
            )
        }

        previous_query = message.get("interpreted_query")

        return (
            startup_keys,
            previous_query
            if isinstance(previous_query, dict)
            else None,
        )

    return None, None


def research_investment_question(
    question: str,
    current_year: int | None = None,
    conversation_history: list[dict] | None = None,
) -> dict:
    interpreter_arguments = {
        "question": question,
        "current_year": current_year,
    }

    if conversation_history is not None:
        interpreter_arguments["conversation_history"] = (
            conversation_history
        )

    try:
        query = interpret_investment_question(
            **interpreter_arguments,
        )
    except LocalAIError as error:
        raise LocalAIError(
            f"Question interpretation failed: {error}"
        ) from error

    if query["needs_clarification"]:
        return {
            "query": query,
            "results": [],
            "clarification_question": query[
                "clarification_question"
            ],
        }

    query = query.copy()

    previous_startups, previous_query = (
        get_previous_result_scope(
            question,
            conversation_history,
        )
    )

    if (
        previous_query is not None
        and EACH_ROUND_REFERENCE.search(question)
        and query.get("minimum_investment_count") is None
    ):
        query["minimum_investment_count"] = (
            previous_query.get("minimum_investment_count")
        )

    records = get_all_investment_records()
    groups = group_investment_records(records)
    applicant_names = get_applicant_names()

    results = search_investments(
        groups=groups,
        applicant_names=applicant_names,
        query=query,
    )

    if previous_startups is not None:
        results = [
            result
            for result in results
            if normalize_startup_name(
                result["startup_name"]
            ) in previous_startups
        ]

    return {
        "query": query,
        "results": results,
        "clarification_question": None,
    }