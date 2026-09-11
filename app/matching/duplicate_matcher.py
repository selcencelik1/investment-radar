from app.matching.investment_date_matcher import (
    date_matches_report_period,
)
from app.matching.investor_normalizer import (
    has_named_investor,
    normalize_investor_list,
)
from app.parser.normalizer import normalize_startup_name


def find_pdf_duplicate_candidates(html_record, pdf_records) -> list:
    name = normalize_startup_name(html_record.startup_name)
    amount = html_record.deal_amount_million_usd
    investors = normalize_investor_list(html_record.investors)

    if not name or amount is None or not has_named_investor(investors):
        return []

    candidates = []

    for pdf_record in pdf_records:
        if pdf_record.source_page is None:
            continue

        if pdf_record.source_url == html_record.source_url:
            continue

        if normalize_startup_name(pdf_record.startup_name) != name:
            continue

        if pdf_record.deal_amount_million_usd != amount:
            continue

        if normalize_investor_list(pdf_record.investors) != investors:
            continue

        if not date_matches_report_period(
            pdf_record.announcement_date_text,
            html_record.reporting_period,
        ):
            continue

        candidates.append(pdf_record)

    return candidates