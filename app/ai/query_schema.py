QUERY_SCHEMA = {
    "type": "object",
    "properties": {
        "intent": {
            "type": "string",
            "enum": [
                "find_startups",
                "find_investors",
                "startup_history",
                "compare_startups",
                "unknown",
            ],
        },
        "startup_name": {
            "type": ["string", "null"],
        },
        "investor_name": {
            "type": ["string", "null"],
        },
        "sectors": {
            "type": "array",
            "items": {
                "type": "string",
            },
        },
        "start_year": {
            "type": ["integer", "null"],
            "minimum": 2000,
            "maximum": 2100,
        },
        "end_year": {
            "type": ["integer", "null"],
            "minimum": 2000,
            "maximum": 2100,
        },
        "minimum_amount_million_usd": {
            "type": ["number", "null"],
            "minimum": 0,
        },
        "maximum_amount_million_usd": {
            "type": ["number", "null"],
            "minimum": 0,
        },
        "minimum_investment_count": {
            "type": ["integer", "null"],
            "minimum": 1,
        },
        "only_applicants": {
            "type": "boolean",
        },
        "only_non_applicants": {
            "type": "boolean",
        },
        "needs_clarification": {
            "type": "boolean",
        },
        "clarification_question": {
            "type": ["string", "null"],
        },
        "minimum_amount_inclusive": {
            "type": "boolean",
        },
        "maximum_amount_inclusive": {
            "type": "boolean",
        },

    },
    "required": [
        "intent",
        "startup_name",
        "investor_name",
        "sectors",
        "start_year",
        "end_year",
        "minimum_amount_million_usd",
        "maximum_amount_million_usd",
        "minimum_investment_count",
        "only_applicants",
        "only_non_applicants",
        "needs_clarification",
        "clarification_question",
        "minimum_amount_inclusive",
        "maximum_amount_inclusive",
    ],
    "additionalProperties": False,
}