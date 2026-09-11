from sqlalchemy import select

from app.database.connection import SessionLocal
from app.database.models import InvestmentRecordEntity
from app.models.investment_record import InvestmentRecord


def save_investment_records(
    records: list[InvestmentRecord],
    reporting_period: str,
    source_url: str,
) -> int:
    saved_count = 0

    with SessionLocal() as session:
        for record in records:
            existing_record = session.scalar(
                select(InvestmentRecordEntity).where(
                    InvestmentRecordEntity.source_url == source_url,
                    InvestmentRecordEntity.ranking == record.ranking,
                )
            )

            if existing_record is not None:
                continue

            entity = InvestmentRecordEntity(
                reporting_period=reporting_period,
                source_url=source_url,
                ranking=record.ranking,
                startup_name=record.startup_name,
                sector=record.sector,
                investors=record.investors,
                investor_countries=record.investor_countries,
                share_percentage=record.share_percentage,
                deal_amount_million_usd=record.deal_amount_million_usd,
                investment_stage=record.investment_stage,
            )

            session.add(entity)
            saved_count += 1

        session.commit()

    return saved_count

def get_investment_startup_names() -> list[str]:
    with SessionLocal() as session:
        names = session.scalars(
            select(InvestmentRecordEntity.startup_name).distinct()
        ).all()

        return list(names)

def get_all_investment_records() -> list[InvestmentRecordEntity]:
    with SessionLocal() as session:
        records = session.scalars(
            select(InvestmentRecordEntity).order_by(
                InvestmentRecordEntity.startup_name,
                InvestmentRecordEntity.reporting_period,
            )
        ).all()

        return list(records)