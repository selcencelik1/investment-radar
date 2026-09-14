from decimal import Decimal
from types import SimpleNamespace

from app.ai.investment_search import search_investments
from app.matching.investment_grouper import InvestmentGroup


def make_record(
        record_id: int,
        startup_name: str,
        sector: str,
        year: int,
        amount: str | None,
):
    return SimpleNamespace(
        id=record_id,
        startup_name=startup_name,
        sector=sector,
        investors="Demo Ventures",
        investor_countries="Türkiye",
        deal_amount_million_usd=(
            Decimal(amount)
            if amount is not None
            else None
        ),
        investment_stage="Seed Stage",
        announcement_date_text=f"January {year}",
        reporting_period=f"{year}-FY",
        source_url=f"https://example.com/{record_id}",
    )


def make_query() -> dict:
    return {
        "intent": "find_startups",
        "startup_name": None,
        "investor_name": None,
        "sectors": [],
        "start_year": None,
        "end_year": None,
        "minimum_amount_million_usd": None,
        "maximum_amount_million_usd": None,
        "minimum_investment_count": None,
        "only_applicants": False,
        "only_non_applicants": False,
        "needs_clarification": False,
        "clarification_question": None,
    }


def make_group(record, members=None):
    return InvestmentGroup(
        primary=record,
        members=members or [record],
        match_status="One source record",
    )


def test_filters_by_year_sector_and_amount():
    gaming = make_record(
        1,
        "Game Studio",
        "Gaming",
        2024,
        "6",
    )

    fintech = make_record(
        2,
        "Payment App",
        "Fintech",
        2024,
        "10",
    )

    older_gaming = make_record(
        3,
        "Old Game",
        "Gaming",
        2022,
        "20",
    )

    query = make_query()
    query["sectors"] = ["gaming"]
    query["start_year"] = 2023
    query["end_year"] = 2024
    query["minimum_amount_million_usd"] = 5

    results = search_investments(
        groups=[
            make_group(gaming),
            make_group(fintech),
            make_group(older_gaming),
        ],
        applicant_names=[],
        query=query,
    )

    assert len(results) == 1
    assert results[0]["startup_name"] == "Game Studio"


def test_filters_applicant_startups():
    applicant = make_record(
        1,
        "Applicant Startup",
        "SaaS",
        2025,
        "2",
    )

    non_applicant = make_record(
        2,
        "External Startup",
        "SaaS",
        2025,
        "3",
    )

    query = make_query()
    query["only_applicants"] = True

    results = search_investments(
        groups=[
            make_group(applicant),
            make_group(non_applicant),
        ],
        applicant_names=["Applicant Startup"],
        query=query,
    )

    assert len(results) == 1
    assert results[0]["is_applicant"] is True


def test_keeps_grouped_sources_as_one_investment():
    annual_record = make_record(
        1,
        "Demo Startup",
        "Gaming",
        2024,
        "5",
    )

    quarterly_record = make_record(
        2,
        "Demo Startup",
        "Gaming",
        2024,
        "5",
    )

    results = search_investments(
        groups=[
            make_group(
                annual_record,
                [annual_record, quarterly_record],
            )
        ],
        applicant_names=[],
        query=make_query(),
    )

    assert len(results) == 1
    assert results[0]["source_count"] == 2
    assert len(results[0]["source_urls"]) == 2


def test_filters_by_minimum_investment_count():
    first_round = make_record(
        1,
        "Multi Round Startup",
        "SaaS",
        2023,
        "2",
    )

    second_round = make_record(
        2,
        "Multi Round Startup",
        "SaaS",
        2024,
        "4",
    )

    single_round = make_record(
        3,
        "Single Round Startup",
        "SaaS",
        2024,
        "8",
    )

    query = make_query()
    query["minimum_investment_count"] = 2

    results = search_investments(
        groups=[
            make_group(first_round),
            make_group(second_round),
            make_group(single_round),
        ],
        applicant_names=[],
        query=query,
    )

    assert len(results) == 2

    assert {
        result["startup_name"]
        for result in results
    } == {"Multi Round Startup"}