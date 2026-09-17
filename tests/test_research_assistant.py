from app.ai.research_assistant import (
    research_investment_question,
)


def make_query(
        needs_clarification=False,
) -> dict:
    return {
        "intent": "find_startups",
        "startup_name": None,
        "investor_name": None,
        "sectors": ["gaming"],
        "start_year": 2023,
        "end_year": 2024,
        "minimum_amount_million_usd": 5,
        "maximum_amount_million_usd": None,
        "minimum_investment_count": None,
        "only_applicants": False,
        "only_non_applicants": False,
        "needs_clarification": needs_clarification,
        "clarification_question": (
            "Which years should be searched?"
            if needs_clarification
            else None
        ),
    }


def test_researches_database_with_interpreted_query(
        monkeypatch,
):
    query = make_query()
    records = [object()]
    groups = [object()]
    expected_results = [
        {
            "startup_name": "Demo Games",
            "year": 2024,
        }
    ]

    monkeypatch.setattr(
        "app.ai.research_assistant."
        "interpret_investment_question",
        lambda question, current_year=None: query,
    )

    monkeypatch.setattr(
        "app.ai.research_assistant."
        "get_all_investment_records",
        lambda: records,
    )

    monkeypatch.setattr(
        "app.ai.research_assistant."
        "group_investment_records",
        lambda received_records: groups,
    )

    monkeypatch.setattr(
        "app.ai.research_assistant."
        "get_applicant_names",
        lambda: ["Applicant Startup"],
    )

    captured_search = {}

    def fake_search(groups, applicant_names, query):
        captured_search["groups"] = groups
        captured_search["applicant_names"] = applicant_names
        captured_search["query"] = query

        return expected_results

    monkeypatch.setattr(
        "app.ai.research_assistant.search_investments",
        fake_search,
    )

    result = research_investment_question(
        question="Find gaming startups.",
        current_year=2026,
    )

    assert result["query"] == query
    assert result["results"] == expected_results
    assert result["clarification_question"] is None
    assert captured_search["groups"] == groups
    assert captured_search["query"] == query


def test_does_not_read_database_when_clarification_is_needed(
        monkeypatch,
):
    query = make_query(needs_clarification=True)

    monkeypatch.setattr(
        "app.ai.research_assistant."
        "interpret_investment_question",
        lambda question, current_year=None: query,
    )

    def fail_if_called():
        raise AssertionError(
            "Database should not be read."
        )

    monkeypatch.setattr(
        "app.ai.research_assistant."
        "get_all_investment_records",
        fail_if_called,
    )

    result = research_investment_question(
        question="Find the relevant startups."
    )

    assert result["results"] == []
    assert (
        result["clarification_question"]
        == "Which years should be searched?"
    )

def test_follow_up_keeps_previous_startups_and_each_round_count(
    monkeypatch,
):
    query = make_query()
    query["start_year"] = 2024

    previous_query = make_query()
    previous_query["start_year"] = 2024
    previous_query["minimum_amount_million_usd"] = None
    previous_query["minimum_investment_count"] = 2

    history = [{
        "role": "assistant",
        "content": "Grand Games had two rounds.",
        "interpreted_query": previous_query,
        "results": [
            {"startup_name": "Grand Games"},
            {"startup_name": "Grand Games"},
        ],
    }]

    monkeypatch.setattr(
        "app.ai.research_assistant.interpret_investment_question",
        lambda **kwargs: query,
    )
    monkeypatch.setattr(
        "app.ai.research_assistant.get_all_investment_records",
        lambda: [],
    )
    monkeypatch.setattr(
        "app.ai.research_assistant.group_investment_records",
        lambda records: [],
    )
    monkeypatch.setattr(
        "app.ai.research_assistant.get_applicant_names",
        lambda: [],
    )

    captured = {}

    def fake_search(groups, applicant_names, query):
        captured["query"] = query.copy()
        return [
            {"startup_name": "Grand Games"},
            {"startup_name": "Agave Games"},
        ]

    monkeypatch.setattr(
        "app.ai.research_assistant.search_investments",
        fake_search,
    )

    result = research_investment_question(
        question="Which of those had each round above 5 million USD?",
        conversation_history=history,
    )

    assert captured["query"]["minimum_investment_count"] == 2
    assert result["results"] == [
        {"startup_name": "Grand Games"},
    ]

def test_turkish_kaci_follow_up_uses_previous_startups():
    from app.ai.research_assistant import get_previous_result_scope

    history = [{
        "role": "assistant",
        "content": "Grand Games had two rounds.",
        "interpreted_query": make_query(),
        "results": [
            {"startup_name": "Grand Games"},
        ],
    }]

    startup_keys, _ = get_previous_result_scope(
        "Kaçı 5 milyon USD üzerinde yatırım aldı?",
        history,
    )

    assert startup_keys == {"grand games"}