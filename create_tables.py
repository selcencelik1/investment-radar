from app.database.base import Base
from app.database.connection import engine
from app.database.models import (
    ApplicantContactEntity,
    ApplicantStartupEntity,
    CollaborationProfileEntity,
    FinancialProfileEntity,
    InvestmentRecordEntity,
    StartupProfileEntity,
    StartupReviewEntity,
    TeamProfileEntity,
)


def create_tables() -> None:
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully.")


if __name__ == "__main__":
    create_tables()