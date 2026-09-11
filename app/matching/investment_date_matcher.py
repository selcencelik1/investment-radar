import re


MONTHS = {
    "january": 1,
    "february": 2,
    "march": 3,
    "april": 4,
    "may": 5,
    "june": 6,
    "july": 7,
    "august": 8,
    "september": 9,
    "october": 10,
    "november": 11,
    "december": 12,
}


def date_matches_report_period(
    announcement_date: str | None,
    reporting_period: str,
) -> bool:
    date_text = " ".join(
        (announcement_date or "").casefold().split()
    )

    date_match = re.fullmatch(r"([a-z]+) (20\d{2})", date_text)
    period_match = re.fullmatch(
        r"(20\d{2})-(Q[1-4]|FY)",
        reporting_period.strip().upper(),
    )

    if date_match is None or period_match is None:
        return False

    month = MONTHS.get(date_match.group(1))

    if month is None:
        return False

    date_year = int(date_match.group(2))
    report_year = int(period_match.group(1))

    if date_year != report_year:
        return False

    period = period_match.group(2)

    if period == "FY":
        return True

    quarter = (month - 1) // 3 + 1

    return period == f"Q{quarter}"