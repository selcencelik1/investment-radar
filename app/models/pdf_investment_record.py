from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class PdfInvestmentRecord:
    startup_name: str
    sector: str
    investors: str
    announcement_date_text: str
    financial_investor: bool | None
    investor_countries: str
    share_percentage: str
    deal_amount_million_usd: Decimal | None
    investment_stage: str
    source_page: int
    source_row: int
    raw_amount_text: str | None = None
    amount_warning: str | None = None