import json

import pytest
import requests

from app.ai.ollama_client import (
    LocalAIError,
    generate_review_brief,
    generate_structured_response,
)
from app.ai.review_schema import REVIEW_BRIEF_SCHEMA


def make_review_brief() -> dict:
    return {
        "company_summary": "Demo startup summary.",
        "business_model_summary": "B2B SaaS.",
        "traction_highlights": ["12 active customers"],
        "investment_history_summary": (
            "One reported investment was found."
        ),
        "data_quality_observations": [],
        "review_questions": [
            "How is customer growth measured?"
        ],
        "evidence_sources": [
            "https://example.com/report.pdf"
        ],
        "limitations": [
            "The summary uses only supplied records."
        ],
    }


class FakeResponse:
    def __init__(self, response_body: dict):
        self.response_body = response_body

    def raise_for_status(self) -> None:
        pass

    def json(self) -> dict:
        return self.response_body


def test_sends_structured_request_to_local_ollama(
    monkeypatch,
):
    captured_request = {}

    def fake_post(url, json, timeout):
        captured_request["url"] = url
        captured_request["payload"] = json
        captured_request["timeout"] = timeout

        return FakeResponse({
            "message": {
                "content": json_module.dumps(
                    make_review_brief()
                )
            }
        })

    json_module = json

    monkeypatch.setattr(
        "app.ai.ollama_client.requests.post",
        fake_post,
    )

    result = generate_review_brief(
        messages=[
            {
                "role": "user",
                "content": "Review the startup.",
            }
        ]
    )

    assert result["company_summary"] == (
        "Demo startup summary."
    )

    assert captured_request["url"] == (
        "http://localhost:11434/api/chat"
    )

    payload = captured_request["payload"]

    assert payload["model"] == "qwen3.5:4b"
    assert payload["format"] == REVIEW_BRIEF_SCHEMA
    assert payload["stream"] is False
    assert payload["think"] is False
    assert payload["options"]["temperature"] == 0


def test_raises_error_when_ollama_is_unavailable(
    monkeypatch,
):
    def fake_post(url, json, timeout):
        raise requests.ConnectionError()

    monkeypatch.setattr(
        "app.ai.ollama_client.requests.post",
        fake_post,
    )

    with pytest.raises(
        LocalAIError,
        match="local AI service could not be reached",
    ):
        generate_review_brief([])


def test_raises_error_for_invalid_model_json(
    monkeypatch,
):
    def fake_post(url, json, timeout):
        return FakeResponse({
            "message": {
                "content": "This is not JSON."
            }
        })

    monkeypatch.setattr(
        "app.ai.ollama_client.requests.post",
        fake_post,
    )

    with pytest.raises(
        LocalAIError,
        match="invalid response",
    ):
        generate_review_brief([])


def test_raises_error_when_required_field_is_missing(
    monkeypatch,
):
    incomplete_brief = make_review_brief()
    incomplete_brief.pop("review_questions")

    def fake_post(url, json, timeout):
        return FakeResponse({
            "message": {
                "content": json_module.dumps(
                    incomplete_brief
                )
            }
        })

    json_module = json

    monkeypatch.setattr(
        "app.ai.ollama_client.requests.post",
        fake_post,
    )

    with pytest.raises(
        LocalAIError,
        match="missing fields: review_questions",
    ):
        generate_review_brief([])

def test_generates_response_with_custom_schema(
        monkeypatch,
):
    custom_schema = {
        "type": "object",
        "properties": {
            "intent": {
                "type": "string",
            },
        },
        "required": ["intent"],
        "additionalProperties": False,
    }

    captured_request = {}

    def fake_post(url, json, timeout):
        captured_request["payload"] = json

        return FakeResponse({
            "message": {
                "content": '{"intent": "find_startups"}'
            }
        })

    monkeypatch.setattr(
        "app.ai.ollama_client.requests.post",
        fake_post,
    )

    result = generate_structured_response(
        messages=[
            {
                "role": "user",
                "content": "Find startups.",
            }
        ],
        schema=custom_schema,
    )

    assert result == {
        "intent": "find_startups",
    }

    assert (
        captured_request["payload"]["format"]
        == custom_schema
    )