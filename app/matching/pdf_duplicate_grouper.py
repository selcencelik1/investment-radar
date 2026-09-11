from collections import Counter, defaultdict

from app.matching.investment_date_matcher import MONTHS
from app.matching.investor_normalizer import (
    has_named_investor,
    normalize_investor_list,
)
from app.parser.normalizer import normalize_startup_name


def clean_text(value: str | None) -> str:
    return " ".join((value or "").casefold().split())


def build_pdf_match_key(record):
    name = normalize_startup_name(record.startup_name)
    investors = normalize_investor_list(record.investors)
    amount = record.deal_amount_million_usd

    date_parts = clean_text(
        record.announcement_date_text
    ).split()

    if (
        not name
        or amount is None
        or not has_named_investor(investors)
        or len(date_parts) != 2
    ):
        return None

    month_name, year_text = date_parts

    if (
        month_name not in MONTHS
        or len(year_text) != 4
        or not year_text.isascii()
        or not year_text.isdigit()
        or not 2000 <= int(year_text) <= 2099
    ):
        return None

    return (
        name,
        int(year_text),
        MONTHS[month_name],
        amount,
        investors,
        clean_text(record.investment_stage),
        clean_text(record.share_percentage),
    )


def group_pdf_records(records: list) -> list[list]:
    buckets = defaultdict(list)
    groups = []

    for record in records:
        if record.source_page is None:
            raise ValueError("This function only holds PDF records.")

        key = build_pdf_match_key(record)

        if key is None or not record.source_url:
            groups.append([record])
        else:
            buckets[key].append(record)

    for bucket in buckets.values():
        source_counts = Counter(
            record.source_url
            for record in bucket
        )

        if any(count > 1 for count in source_counts.values()):

            groups.extend([record] for record in bucket)
        else:
            groups.append(bucket)

    return groups