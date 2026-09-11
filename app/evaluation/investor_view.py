from dataclasses import dataclass

from app.matching.investor_normalizer import normalize_investor_name
from app.source_language import (
    INDIVIDUAL_INVESTOR_KEYWORDS,
    INSTITUTION_KEYWORDS,
    UNKNOWN_INVESTOR_LABELS,
)


UNKNOWN_INVESTORS = {
    "",
    "na",
    "n/a",
    *UNKNOWN_INVESTOR_LABELS,
}


@dataclass(frozen=True)
class InvestorRelation:
    investor_name: str
    normalized_investor_name: str
    investor_type: str
    startup_name: str
    sector: str
    reporting_period: str
    announcement_date_text: str | None
    deal_amount_million_usd: object
    investment_stage: str
    source_url: str


def classify_investor(investor_name: str) -> str:
    normalized = normalize_investor_name(investor_name)

    if any(
        keyword in normalized
        for keyword in INSTITUTION_KEYWORDS
    ):
        return "Fund / institutional investor candidate"

    if any(
        keyword in normalized
        for keyword in INDIVIDUAL_INVESTOR_KEYWORDS
    ):
        return "Individual investor candidate"

    return "Type needs review"


def split_investor_names(value: str | None) -> list[str]:
    if not value:
        return []

    names = []
    seen = set()

    for part in value.split(","):
        display_name = " ".join(part.split())
        normalized = normalize_investor_name(display_name)

        if normalized in UNKNOWN_INVESTORS:
            continue

        if not normalized or normalized in seen:
            continue

        seen.add(normalized)
        names.append(display_name)

    return names


def build_investor_relations(records: list) -> list[InvestorRelation]:
    relations = []

    for record in records:
        for investor_name in split_investor_names(record.investors):
            relations.append(
                InvestorRelation(
                    investor_name=investor_name,
                    normalized_investor_name=normalize_investor_name(
                        investor_name
                    ),
                    investor_type=classify_investor(investor_name),
                    startup_name=record.startup_name,
                    sector=record.sector,
                    reporting_period=record.reporting_period,
                    announcement_date_text=(
                        record.announcement_date_text
                    ),
                    deal_amount_million_usd=(
                        record.deal_amount_million_usd
                    ),
                    investment_stage=record.investment_stage,
                    source_url=record.source_url,
                )
            )

    return relations
