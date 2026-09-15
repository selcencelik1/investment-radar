import json
from datetime import datetime


QUERY_SYSTEM_PROMPT = """
You interpret questions about startup investment records.

Convert the user's question into the required structured query.

Rules:
- Do not answer the question.
- Do not generate SQL.
- Do not invent startup, investor, sector, or investment information.
- Use find_startups when the user asks which startups match conditions.
- Use find_investors when the user asks about investors or funds.
- Use startup_history when the user asks about one startup's investments.
- Use compare_startups when multiple named startups are compared.
- Use unknown when the request is unrelated to available investment data.
- A year range includes both its start and end years.
- "Last two years" means the current year and the previous year.
- Amount fields use millions of US dollars.
- Use only_applicants only when the user explicitly asks for applicants.
- Use only_non_applicants only when the user explicitly asks for
  startups that did not apply.
- Use conversation_history only to resolve references in the latest
  question, such as "these startups", "the same years", or "only
  applicants".
- Inherit previous filters only when the latest question clearly
  refers to the previous conversation.
- A standalone new question must not inherit unrelated old filters.
- The latest user question always has priority.
- If essential information is missing, set needs_clarification to true
  and provide one short clarification question.
- For "above", "more than", or "üzerinde", set
  minimum_amount_inclusive to false.
- For "at least", "minimum", or "en az", set
  minimum_amount_inclusive to true.
- For "below", "less than", or "altında", set
  maximum_amount_inclusive to false.
- For "at most", "maximum", or "en fazla", set
  maximum_amount_inclusive to true.
- When an amount boundary is absent, its inclusive flag must be true.
- The user may write in Turkish or English.
"""


def build_query_messages(
        question: str,
        current_year: int | None = None,
        conversation_history: list[dict] | None = None,
) -> list[dict]:
    cleaned_question = question.strip()

    if not cleaned_question:
        raise ValueError("Question cannot be empty.")

    if current_year is None:
        current_year = datetime.now().year

    safe_history = []

    for message in (conversation_history or [])[-6:]:
        role = message.get("role")
        content = message.get("content")

        if role not in {"user", "assistant"}:
            continue

        if not isinstance(content, str):
            continue

        history_item = {
            "role": role,
            "content": content[:2000],
        }

        interpreted_query = message.get(
            "interpreted_query"
        )

        if isinstance(interpreted_query, dict):
            history_item["interpreted_query"] = (
                interpreted_query
            )

        safe_history.append(history_item)

    context = {
        "current_year": current_year,
        "amount_unit": "million USD",
        "conversation_history": safe_history,
        "user_question": cleaned_question,
    }

    return [
        {
            "role": "system",
            "content": QUERY_SYSTEM_PROMPT.strip(),
        },
        {
            "role": "user",
            "content": json.dumps(
                context,
                ensure_ascii=False,
            ),
        },
    ]