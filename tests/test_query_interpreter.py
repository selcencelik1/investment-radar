import pytest

from app.ai.ollama_client import LocalAIError
from app.ai.query_interpreter import (
    interpret_investment_question,
    validate_investment_query,
)


def make_query() -> dict:
    return {
        "intent": "find_startups",
        "startup_name": None,
        "investor_name": None,
        "sectors": ["Gaming"],
        "start_year": 2023,
        "end_year": 2024,
        "minimum_amount_million_usd": 5,
        "maximum_amount_million_usd": None,
        "minimum_investment_count": None,
        "only_applicants": False,
        "only_non_applicants": False,
        "needs_clarification": False,
        "clarification_question": None,
    }


def test_interprets_question_with_structured_schema(
        monkeypatch,
):
    expected_query = make_query()
    captured_call = {}

    def fake_generate(
            messages,
            schema,
            model="qwen3.5:4b",
            timeout=180,
    ):
        captured_call["messages"] = messages
        captured_call["schema"] = schema

        return expected_query

    monkeypatch.setattr(
        "app.ai.query_interpreter."
        "generate_structured_response",
        fake_generate,
    )

    result = interpret_investment_question(
        question=(
            "2023 ve 2024 yıllarında 5 milyon doların "
            "üzerinde yatırım alan oyun girişimleri hangileri?"
        ),
        current_year=2026,
    )

    assert result == expected_query
    assert captured_call["schema"]["type"] == "object"
    assert "2026" in captured_call["messages"][1]["content"]


def test_rejects_conflicting_applicant_filters():
    query = make_query()
    query["only_applicants"] = True
    query["only_non_applicants"] = True

    with pytest.raises(
        LocalAIError,
        match="applicants and non-applicants",
    ):
        validate_investment_query(query)


def test_rejects_reversed_year_range():
    query = make_query()
    query["start_year"] = 2025
    query["end_year"] = 2023

    with pytest.raises(
        LocalAIError,
        match="start year",
    ):
        validate_investment_query(query)


def test_rejects_reversed_amount_range():
    query = make_query()
    query["minimum_amount_million_usd"] = 10
    query["maximum_amount_million_usd"] = 2

    with pytest.raises(
        LocalAIError,
        match="minimum investment amount",
    ):
        validate_investment_query(query)


def test_requires_clarification_question():
    query = make_query()
    query["needs_clarification"] = True
    query["clarification_question"] = None

    with pytest.raises(
        LocalAIError,
        match="clarification question",
    ):
        validate_investment_query(query)


def test_rejects_unknown_intent_value():
    query = make_query()
    query["intent"] = "delete_database"

    with pytest.raises(
        LocalAIError,
        match="invalid intent",
    ):
        validate_investment_query(query)