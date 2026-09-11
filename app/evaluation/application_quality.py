from datetime import date
from decimal import Decimal


def get_application_quality_issues(
    *,
    founding_date: date,
    mrr_usd: Decimal,
    arr_usd: Decimal,
    monthly_revenue_usd: Decimal,
    previously_funded: bool,
    source_investment_count: int,
    investment_expectation_usd: Decimal,
    aviation_sector_experience: bool,
    aviation_partners: str | None,
    today: date | None = None,
) -> list[str]:
    reference_date = today or date.today()
    issues = []

    expected_arr = mrr_usd * Decimal("12")

    if abs(arr_usd - expected_arr) > Decimal("0.01"):
        issues.append(
            "ARR does not equal MRR multiplied by 12"
        )

    if mrr_usd > monthly_revenue_usd:
        issues.append(
            "MRR is greater than total monthly revenue"
        )

    if not previously_funded and source_investment_count > 0:
        issues.append(
            "An investment was found in external sources, "
            "but the applicant reported no previous funding"
        )

    if (
        aviation_sector_experience
        and not (aviation_partners or "").strip()
    ):
        issues.append(
            "Aviation experience was reported without "
            "naming a previous partner"
        )

    if founding_date > reference_date:
        issues.append(
            "Founding date is in the future"
        )

    if investment_expectation_usd <= 0:
        issues.append(
            "Investment expectation must be greater than zero"
        )

    return issues