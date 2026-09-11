from app.models.investment_record import InvestmentRecord
from app.parser.normalizer import normalize_deal_amount
from app.source_language import KPMG_HTML_FIELDS


def map_to_investment_record(
    raw_record: dict[str, str]
) -> InvestmentRecord:
    return InvestmentRecord(
        ranking=int(raw_record[KPMG_HTML_FIELDS["ranking"]]),
        startup_name=raw_record[
            KPMG_HTML_FIELDS["startup_name"]
        ].strip(),
        sector=raw_record[KPMG_HTML_FIELDS["sector"]].strip(),
        investors=raw_record[KPMG_HTML_FIELDS["investors"]].strip(),
        investor_countries=raw_record[
            KPMG_HTML_FIELDS["investor_countries"]
        ].strip(),
        share_percentage=raw_record[
            KPMG_HTML_FIELDS["share_percentage"]
        ].strip(),
        deal_amount_million_usd=normalize_deal_amount(
            raw_record[KPMG_HTML_FIELDS["deal_amount"]]
        ),
        investment_stage=get_stage_value(raw_record),
    )


def get_stage_value(raw_record: dict[str, str]) -> str:
    stage = raw_record.get(KPMG_HTML_FIELDS["investment_stage"])

    if stage is not None:
        return stage.strip()

    transaction_type = raw_record.get(
        KPMG_HTML_FIELDS["transaction_type"]
    )

    if transaction_type is not None:
        return transaction_type.strip()

    raise ValueError(
        "Neither an investment stage nor a transaction type was found."
    )
