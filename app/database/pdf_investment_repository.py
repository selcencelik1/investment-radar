from sqlalchemy import select

from app.database.connection import SessionLocal
from app.database.models import InvestmentRecordEntity
from app.models.pdf_investment_record import PdfInvestmentRecord


def save_pdf_investment_records(
    records: list[PdfInvestmentRecord],
    reporting_period: str,
    source_url: str,
) -> int:
    saved_count = 0

    with SessionLocal() as session:
        existing_locations = set(
            session.execute(
                select(
                    InvestmentRecordEntity.source_page,
                    InvestmentRecordEntity.source_row,
                ).where(
                    InvestmentRecordEntity.source_url == source_url
                )
            ).all()
        )

        for record in records:
            location = (
                record.source_page,
                record.source_row,
            )

            if location in existing_locations:
                continue

            entity = InvestmentRecordEntity(
                reporting_period=reporting_period,
                source_url=source_url,
                ranking=None,
                startup_name=record.startup_name,
                sector=record.sector,
                investors=record.investors,
                investor_countries=record.investor_countries,
                share_percentage=record.share_percentage,
                deal_amount_million_usd=record.deal_amount_million_usd,
                investment_stage=record.investment_stage,
                source_page=record.source_page,
                source_row=record.source_row,
                announcement_date_text=record.announcement_date_text,
                financial_investor=record.financial_investor,
                raw_amount_text=record.raw_amount_text,
                amount_warning=record.amount_warning,
            )

            session.add(entity)
            existing_locations.add(location)
            saved_count += 1

        session.commit()

    return saved_count