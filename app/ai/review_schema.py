REVIEW_BRIEF_SCHEMA = {
    "type": "object",
    "properties": {
        "company_summary": {
            "type": "string",
        },
        "business_model_summary": {
            "type": "string",
        },
        "traction_highlights": {
            "type": "array",
            "items": {"type": "string"},
        },
        "investment_history_summary": {
            "type": "string",
        },
        "data_quality_observations": {
            "type": "array",
            "items": {"type": "string"},
        },
        "review_questions": {
            "type": "array",
            "items": {"type": "string"},
        },
        "evidence_sources": {
            "type": "array",
            "items": {"type": "string"},
        },
        "limitations": {
            "type": "array",
            "items": {"type": "string"},
        },
    },
    "required": [
        "company_summary",
        "business_model_summary",
        "traction_highlights",
        "investment_history_summary",
        "data_quality_observations",
        "review_questions",
        "evidence_sources",
        "limitations",
    ],
    "additionalProperties": False,
}