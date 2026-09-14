ANSWER_SCHEMA = {
    "type": "object",
    "properties": {
        "answer": {
            "type": "string",
        },
        "key_findings": {
            "type": "array",
            "items": {
                "type": "string",
            },
        },
        "cited_result_numbers": {
            "type": "array",
            "items": {
                "type": "integer",
                "minimum": 1,
            },
        },
        "limitations": {
            "type": "array",
            "items": {
                "type": "string",
            },
        },
        "follow_up_suggestions": {
            "type": "array",
            "items": {
                "type": "string",
            },
        },
    },
    "required": [
        "answer",
        "key_findings",
        "cited_result_numbers",
        "limitations",
        "follow_up_suggestions",
    ],
    "additionalProperties": False,
}