from app.models.pdf_investment_record import PdfInvestmentRecord
from app.parser.normalizer import normalize_pdf_amount_to_million_usd


def parse_financial_investor(value: str) -> bool | None:
    normalized = value.strip().casefold()

    if normalized == "yes":
        return True

    if normalized == "no":
        return False

    if normalized in {"", "na", "n/a"}:
        return None

    raise ValueError(
        f"Invalid financial investor value: {value!r}"
    )


def map_pdf_record(raw_record: dict) -> PdfInvestmentRecord:
    raw_amount = raw_record["Transaction Value ($)"]
    amount_warning = None

    try:
        amount = normalize_pdf_amount_to_million_usd(raw_amount)
    except ValueError:
        amount = None
        amount_warning = (
            "The source amount format is ambiguous and was not "
            "converted to a numeric value."
        )

    return PdfInvestmentRecord(
        startup_name=raw_record["Target Company"].strip(),
        sector=raw_record["Sector"].strip(),
        investors=raw_record["Investors"].strip(),
        announcement_date_text=raw_record["Announcement Date"].strip(),
        financial_investor=parse_financial_investor(
            raw_record["Financial Investor"]
        ),
        investor_countries=raw_record["Investors' Origin"].strip(),
        share_percentage=raw_record["Stake (%)"].strip(),
        deal_amount_million_usd=amount,
        investment_stage=raw_record["Investment Stage"].strip(),
        source_page=int(raw_record["source_page"]),
        source_row=int(raw_record["source_row"]),
        raw_amount_text=raw_amount,
        amount_warning=amount_warning,
    )
