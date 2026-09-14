import re
from collections import Counter
from decimal import Decimal

from app.matching.investment_grouper import InvestmentGroup
from app.parser.normalizer import normalize_startup_name


def extract_record_year(record: object) -> int | None:
    announcement_date = (
        getattr(record, "announcement_date_text", None) or ""
    )

    date_match = re.search(
        r"\b(20\d{2})\b",
        announcement_date,
    )

    if date_match is not None:
        return int(date_match.group(1))

    reporting_period = (
        getattr(record, "reporting_period", "") or ""
    )

    period_match = re.match(
        r"^(20\d{2})-(?:FY|Q[1-4])$",
        reporting_period,
        flags=re.IGNORECASE,
    )

    if period_match is not None:
        return int(period_match.group(1))

    return None


def contains_text(value: str | None, search: str) -> bool:
    return search.casefold() in (value or "").casefold()


def search_investments(
        groups: list[InvestmentGroup],
        applicant_names: list[str],
        query: dict,
) -> list[dict]:
    applicant_keys = {
        normalize_startup_name(name)
        for name in applicant_names
        if name and name.strip()
    }

    results = []

    for group in groups:
        record = group.primary
        startup_key = normalize_startup_name(
            record.startup_name
        )

        is_applicant = startup_key in applicant_keys
        record_year = extract_record_year(record)
        amount = record.deal_amount_million_usd

        if query["startup_name"]:
            searched_startup = normalize_startup_name(
                query["startup_name"]
            )

            if searched_startup not in startup_key:
                continue

        if query["investor_name"]:
            if not contains_text(
                record.investors,
                query["investor_name"],
            ):
                continue

        sectors = query["sectors"]

        if sectors and not any(
            contains_text(record.sector, sector)
            for sector in sectors
        ):
            continue

        if query["start_year"] is not None:
            if (
                record_year is None
                or record_year < query["start_year"]
            ):
                continue

        if query["end_year"] is not None:
            if (
                record_year is None
                or record_year > query["end_year"]
            ):
                continue

        minimum_amount = query[
            "minimum_amount_million_usd"
        ]

        if minimum_amount is not None:
            if (
                amount is None
                or amount < Decimal(str(minimum_amount))
            ):
                continue

        maximum_amount = query[
            "maximum_amount_million_usd"
        ]

        if maximum_amount is not None:
            if (
                amount is None
                or amount > Decimal(str(maximum_amount))
            ):
                continue

        if query["only_applicants"] and not is_applicant:
            continue

        if query["only_non_applicants"] and is_applicant:
            continue

        source_urls = sorted({
            member.source_url
            for member in group.members
            if getattr(member, "source_url", None)
        })

        results.append({
            "startup_name": record.startup_name,
            "sector": record.sector,
            "year": record_year,
            "announcement_date": (
                record.announcement_date_text
            ),
            "investors": record.investors,
            "investor_countries": (
                record.investor_countries
            ),
            "amount_million_usd": (
                float(amount)
                if amount is not None
                else None
            ),
            "investment_stage": record.investment_stage,
            "is_applicant": is_applicant,
            "source_count": len(group.members),
            "source_urls": source_urls,
        })

    minimum_count = query["minimum_investment_count"]

    if minimum_count is not None:
        investment_counts = Counter(
            normalize_startup_name(
                result["startup_name"]
            )
            for result in results
        )

        results = [
            result
            for result in results
            if investment_counts[
                normalize_startup_name(
                    result["startup_name"]
                )
            ] >= minimum_count
        ]

    return sorted(
        results,
        key=lambda result: (
            result["year"] is None,
            -(result["year"] or 0),
            result["startup_name"].casefold(),
        ),
    )