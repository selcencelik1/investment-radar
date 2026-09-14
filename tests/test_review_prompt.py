import json

from app.ai.review_prompt import build_review_messages
from app.ai.review_schema import REVIEW_BRIEF_SCHEMA


def test_builds_system_and_user_messages():
    applicant_context = {
        "company": {
            "name": "Demo Aviation",
        }
    }

    investment_history = [
        {
            "startup_name": "Demo Aviation",
            "amount_million_usd": 1.5,
        }
    ]

    messages = build_review_messages(
        applicant_context,
        investment_history,
    )

    assert len(messages) == 2
    assert messages[0]["role"] == "system"
    assert messages[1]["role"] == "user"

    payload = json.loads(messages[1]["content"])

    assert payload["applicant_provided_data"] == (
        applicant_context
    )
    assert payload["external_investment_records"] == (
        investment_history
    )


def test_prompt_prohibits_automated_investment_decisions():
    messages = build_review_messages({}, [])

    system_prompt = messages[0]["content"]

    assert "Do not make an investment recommendation" in (
        system_prompt
    )
    assert "Do not score, rank, approve, or reject" in (
        system_prompt
    )
    assert "Do not invent missing information" in system_prompt


def test_schema_requires_all_review_sections():
    required_fields = set(REVIEW_BRIEF_SCHEMA["required"])

    assert required_fields == {
        "company_summary",
        "business_model_summary",
        "traction_highlights",
        "investment_history_summary",
        "data_quality_observations",
        "review_questions",
        "evidence_sources",
        "limitations",
    }


def test_prompt_does_not_contain_personal_information():
    applicant_context = {
        "company": {
            "name": "Demo Aviation",
        }
    }

    messages = build_review_messages(
        applicant_context,
        [],
    )

    serialized_messages = json.dumps(messages)

    assert "Ada Example" not in serialized_messages
    assert "ada@example.com" not in serialized_messages
    assert "+90 555" not in serialized_messages