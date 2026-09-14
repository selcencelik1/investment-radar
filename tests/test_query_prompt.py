import json

import pytest

from app.ai.query_prompt import build_query_messages


def test_builds_query_messages_with_current_year():
    messages = build_query_messages(
        question=(
            "2023 ve 2024 yıllarında yatırım alan "
            "oyun girişimleri hangileri?"
        ),
        current_year=2026,
    )

    assert len(messages) == 2
    assert messages[0]["role"] == "system"
    assert messages[1]["role"] == "user"

    payload = json.loads(messages[1]["content"])

    assert payload["current_year"] == 2026
    assert payload["amount_unit"] == "million USD"
    assert (
        payload["user_question"]
        == (
            "2023 ve 2024 yıllarında yatırım alan "
            "oyun girişimleri hangileri?"
        )
    )


def test_keeps_turkish_characters():
    messages = build_query_messages(
        question="Son iki yılda yatırım alan girişimler hangileri?",
        current_year=2026,
    )

    assert "girişimler" in messages[1]["content"]


def test_removes_surrounding_spaces():
    messages = build_query_messages(
        question="  Good Job Games ne zaman yatırım aldı?  ",
        current_year=2026,
    )

    payload = json.loads(messages[1]["content"])

    assert (
        payload["user_question"]
        == "Good Job Games ne zaman yatırım aldı?"
    )


def test_rejects_empty_question():
    with pytest.raises(
        ValueError,
        match="Question cannot be empty",
    ):
        build_query_messages("   ")