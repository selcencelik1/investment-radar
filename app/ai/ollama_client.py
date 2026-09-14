import json

import requests

from app.ai.review_schema import REVIEW_BRIEF_SCHEMA


OLLAMA_CHAT_URL = "http://localhost:11434/api/chat"
DEFAULT_MODEL = "qwen3.5:4b"


class LocalAIError(RuntimeError):
    pass


def validate_structured_response(
        result: object,
        schema: dict,
) -> dict:
    if not isinstance(result, dict):
        raise LocalAIError(
            "The local model did not return a JSON object."
        )

    required_fields = set(schema.get("required", []))
    missing_fields = required_fields - set(result)

    if missing_fields:
        missing_text = ", ".join(sorted(missing_fields))

        raise LocalAIError(
            "The local model response is missing fields: "
            f"{missing_text}"
        )

    return result


def generate_structured_response(
        messages: list[dict],
        schema: dict,
        model: str = DEFAULT_MODEL,
        timeout: int = 180,
) -> dict:
    payload = {
        "model": model,
        "messages": messages,
        "format": schema,
        "stream": False,
        "think": False,
        "options": {
            "temperature": 0,
        },
    }

    try:
        response = requests.post(
            OLLAMA_CHAT_URL,
            json=payload,
            timeout=timeout,
        )

        response.raise_for_status()

    except requests.RequestException as error:
        raise LocalAIError(
            "The local AI service could not be reached. "
            "Make sure Ollama is running and the model is installed."
        ) from error

    try:
        response_body = response.json()
        content = response_body["message"]["content"]
        result = json.loads(content)

    except (
        ValueError,
        KeyError,
        TypeError,
        json.JSONDecodeError,
    ) as error:
        raise LocalAIError(
            "The local model returned an invalid response."
        ) from error

    return validate_structured_response(
        result=result,
        schema=schema,
    )


def generate_review_brief(
        messages: list[dict],
        model: str = DEFAULT_MODEL,
        timeout: int = 180,
) -> dict:
    return generate_structured_response(
        messages=messages,
        schema=REVIEW_BRIEF_SCHEMA,
        model=model,
        timeout=timeout,
    )