from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class InvestmentRecord:
    ranking: int
    startup_name: str
    sector: str
    investors: str
    investor_countries: str
    share_percentage: str
    deal_amount_million_usd: Decimal | None
    investment_stage: str