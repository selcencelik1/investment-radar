from app.ai.investment_search import search_investments
from app.ai.query_interpreter import (
    interpret_investment_question,
)
from app.database.applicant_repository import (
    get_applicant_names,
)
from app.database.investment_repository import (
    get_all_investment_records,
)
from app.matching.investment_grouper import (
    group_investment_records,
)


def research_investment_question(
        question: str,
        current_year: int | None = None,
) -> dict:
    query = interpret_investment_question(
        question=question,
        current_year=current_year,
    )

    if query["needs_clarification"]:
        return {
            "query": query,
            "results": [],
            "clarification_question": query[
                "clarification_question"
            ],
        }

    records = get_all_investment_records()
    groups = group_investment_records(records)
    applicant_names = get_applicant_names()

    results = search_investments(
        groups=groups,
        applicant_names=applicant_names,
        query=query,
    )

    return {
        "query": query,
        "results": results,
        "clarification_question": None,
    }