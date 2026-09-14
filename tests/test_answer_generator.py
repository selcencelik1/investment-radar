import pytest

from app.ai.answer_generator import (
    generate_research_answer,
)
from app.ai.ollama_client import LocalAIError


def make_answer() -> dict:
    return {
        "answer": "Two matching startups were found.",
        "key_findings": [
            "Demo Games raised 6 million USD."
        ],
        "cited_result_numbers": [1],
        "limitations": [
            "Only available records were searched."
        ],
        "follow_up_suggestions": [
            "Filter the results by investor."
        ],
    }


def test_generates_answer_from_search_results(
        monkeypatch,
):
    captured_call = {}

    def fake_generate(messages, schema):
        captured_call["messages"] = messages
        captured_call["schema"] = schema
        return make_answer()

    monkeypatch.setattr(
        "app.ai.answer_generator."
        "generate_structured_response",
        fake_generate,
    )

    result = generate_research_answer(
        question="Which gaming startups were funded?",
        interpreted_query={
            "intent": "find_startups",
        },
        results=[
            {
                "startup_name": "Demo Games",
                "year": 2024,
                "amount_million_usd": 6,
            }
        ],
    )

    assert result["cited_result_numbers"] == [1]
    assert "Demo Games" in (
        captured_call["messages"][1]["content"]
    )


def test_rejects_citation_outside_supplied_results(
        monkeypatch,
):
    invalid_answer = make_answer()
    invalid_answer["cited_result_numbers"] = [2]

    monkeypatch.setattr(
        "app.ai.answer_generator."
        "generate_structured_response",
        lambda messages, schema: invalid_answer,
    )

    with pytest.raises(
        LocalAIError,
        match="cited unavailable search results",
    ):
        generate_research_answer(
            question="Which startup?",
            interpreted_query={
                "intent": "find_startups",
            },
            results=[
                {
                    "startup_name": "Demo Games",
                }
            ],
        )


def test_accepts_answer_without_citations_for_no_results(
        monkeypatch,
):
    empty_answer = make_answer()
    empty_answer["cited_result_numbers"] = []
    empty_answer["answer"] = (
        "No matching records were found."
    )

    monkeypatch.setattr(
        "app.ai.answer_generator."
        "generate_structured_response",
        lambda messages, schema: empty_answer,
    )

    result = generate_research_answer(
        question="Which startup?",
        interpreted_query={
            "intent": "find_startups",
        },
        results=[],
    )

    assert result["cited_result_numbers"] == []

def test_assigns_all_supplied_results_as_evidence(
        monkeypatch,
):
    answer = make_answer()
    answer["cited_result_numbers"] = []

    monkeypatch.setattr(
        "app.ai.answer_generator."
        "generate_structured_response",
        lambda messages, schema: answer,
    )

    result = generate_research_answer(
        question="Which startups were funded?",
        interpreted_query={
            "intent": "find_startups",
        },
        results=[
            {"startup_name": "First Startup"},
            {"startup_name": "Second Startup"},
        ],
    )

    assert result["cited_result_numbers"] == [1, 2]