from app.ai.answer_prompt import build_answer_messages
from app.ai.answer_schema import ANSWER_SCHEMA
from app.ai.ollama_client import (
    LocalAIError,
    generate_structured_response,
)


def validate_research_answer(
        answer: dict,
        supplied_result_count: int,
) -> dict:
    invalid_numbers = [
        number
        for number in answer["cited_result_numbers"]
        if (
            not isinstance(number, int)
            or number < 1
            or number > supplied_result_count
        )
    ]

    if invalid_numbers:
        raise LocalAIError(
            "The local model cited unavailable search results: "
            + ", ".join(map(str, invalid_numbers))
        )

    return answer


def generate_research_answer(
        question: str,
        interpreted_query: dict,
        results: list[dict],
        maximum_results: int = 100,
) -> dict:
    messages = build_answer_messages(
        question=question,
        interpreted_query=interpreted_query,
        results=results,
        maximum_results=maximum_results,
    )

    answer = generate_structured_response(
        messages=messages,
        schema=ANSWER_SCHEMA,
    )

    supplied_result_count = min(
        len(results),
        maximum_results,
    )

    answer = validate_research_answer(
        answer=answer,
        supplied_result_count=supplied_result_count,
    )

    # All records supplied to the model are evidence records.
    # Evidence selection is deterministic rather than model-controlled.
    answer["cited_result_numbers"] = list(
        range(1, supplied_result_count + 1)
    )

    return answer