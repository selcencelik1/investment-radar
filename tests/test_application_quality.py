from datetime import date
from decimal import Decimal

from app.evaluation.application_quality import (
    get_application_quality_issues,
)


def get_valid_application_data() -> dict:
    return {
        "founding_date": date(2023, 5, 10),
        "mrr_usd": Decimal("5000"),
        "arr_usd": Decimal("60000"),
        "monthly_revenue_usd": Decimal("8000"),
        "previously_funded": True,
        "source_investment_count": 1,
        "investment_expectation_usd": Decimal("500000"),
        "aviation_sector_experience": True,
        "aviation_partners": "Example Airline",
        "today": date(2026, 9, 8),
    }


def test_returns_no_issues_for_consistent_application():
    issues = get_application_quality_issues(
        **get_valid_application_data()
    )

    assert issues == []


def test_detects_arr_and_mrr_inconsistency():
    application = get_valid_application_data()
    application["arr_usd"] = Decimal("50000")

    issues = get_application_quality_issues(**application)

    assert (
        "ARR does not equal MRR multiplied by 12"
        in issues
    )


def test_detects_mrr_above_monthly_revenue():
    application = get_valid_application_data()
    application["monthly_revenue_usd"] = Decimal("4000")

    issues = get_application_quality_issues(**application)

    assert (
        "MRR is greater than total monthly revenue"
        in issues
    )


def test_detects_funding_conflict():
    application = get_valid_application_data()
    application["previously_funded"] = False

    issues = get_application_quality_issues(**application)

    assert (
        "An investment was found in external sources, "
        "but the applicant reported no previous funding"
        in issues
    )


def test_detects_missing_aviation_partner():
    application = get_valid_application_data()
    application["aviation_partners"] = None

    issues = get_application_quality_issues(**application)

    assert (
        "Aviation experience was reported without "
        "naming a previous partner"
        in issues
    )


def test_detects_future_founding_date():
    application = get_valid_application_data()
    application["founding_date"] = date(2027, 1, 1)

    issues = get_application_quality_issues(**application)

    assert "Founding date is in the future" in issues


def test_detects_invalid_investment_expectation():
    application = get_valid_application_data()
    application["investment_expectation_usd"] = Decimal("0")

    issues = get_application_quality_issues(**application)

    assert (
        "Investment expectation must be greater than zero"
        in issues
    )