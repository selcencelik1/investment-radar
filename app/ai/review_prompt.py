import json

SYSTEM_PROMPT = """
You prepare factual review briefs for startup applications.

Follow these rules:
1. Use only the supplied application and investment data.
2. Do not make an investment recommendation.
3. Do not score, rank, approve, or reject the startup.
4. Do not invent missing information.
5. Clearly distinguish applicant-provided claims from external
   investment records.
6. Treat missing and inconsistent values as review points.
7. Keep the output concise and professional.
8. Write the output in English.
9. Return only valid JSON that follows the supplied schema.
""".strip()


def build_review_messages(
    applicant_context: dict,
    investment_history: list[dict],
) -> list[dict]:
    payload = {
        "task": (
            "Prepare a review brief that helps a human reviewer "
            "understand the startup and identify questions that "
            "require further verification."
        ),
        "applicant_provided_data": applicant_context,
        "external_investment_records": investment_history,
    }

    return [
        {
            "role": "system",
            "content": SYSTEM_PROMPT,
        },
        {
            "role": "user",
            "content": json.dumps(
                payload,
                ensure_ascii=False,
                indent=2,
            ),
        },
    ]