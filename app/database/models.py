from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    func,

)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class InvestmentRecordEntity(Base):
    __tablename__ = "investment_records"

    __table_args__ = (
        UniqueConstraint(
            "source_url",
            "ranking",
            name="uq_investment_source_ranking",
        ),
        UniqueConstraint(
            "source_url",
            "source_page",
            "source_row",
            name="uq_investment_source_page_row",
        ),
    )

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
    )

    reporting_period: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )

    source_url: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    ranking: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    startup_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    sector: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    investors: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    investor_countries: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    share_percentage: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    deal_amount_million_usd: Mapped[Decimal | None] = mapped_column(
        Numeric(20, 8),
        nullable=True,
    )

    investment_stage: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    source_page: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    source_row: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    announcement_date_text: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    financial_investor: Mapped[bool | None] = mapped_column(
        Boolean,
        nullable=True,
    )
    raw_amount_text: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    amount_warning: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

class ApplicantStartupEntity(Base):
    __tablename__ = "applicant_startups"

    __table_args__ = (
        UniqueConstraint(
            "normalized_name",
            "application_year",
            name="uq_applicant_name_year",
        ),
    )

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
    )

    startup_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    normalized_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    website: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    application_year: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    contact: Mapped["ApplicantContactEntity | None"] = relationship(
        uselist=False,
    )

    startup_profile: Mapped["StartupProfileEntity | None"] = relationship(
        uselist=False,
    )

    team_profile: Mapped["TeamProfileEntity | None"] = relationship(
        uselist=False,
    )

    financial_profile: Mapped[
        "FinancialProfileEntity | None"
    ] = relationship(
        uselist=False,
    )

    collaboration_profile: Mapped[
        "CollaborationProfileEntity | None"
    ] = relationship(
        uselist=False,
    )


class ApplicantContactEntity(Base):
    __tablename__ = "applicant_contacts"

    __table_args__ = (
        UniqueConstraint(
            "applicant_startup_id",
            name="uq_applicant_contact_startup",
        ),
    )

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
    )

    applicant_startup_id: Mapped[int] = mapped_column(
        ForeignKey(
            "applicant_startups.id",
            ondelete="CASCADE",
        ),
        nullable=False,
    )

    full_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    phone: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    email: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    linkedin_url: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

class StartupProfileEntity(Base):
    __tablename__ = "startup_profiles"

    __table_args__ = (
        UniqueConstraint(
            "applicant_startup_id",
            name="uq_startup_profile_application",
        ),
    )

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
    )

    applicant_startup_id: Mapped[int] = mapped_column(
        ForeignKey(
            "applicant_startups.id",
            ondelete="CASCADE",
        ),
        nullable=False,
    )

    sector_nace_code: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    legal_status: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    headquarters_country: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    founding_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
    )

    description: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    problem_solution: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    business_revenue_model: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    startup_stage: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )

    product_demo_url: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    logo_url: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    pitch_deck_url: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    previous_program_participation: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
    )

class TeamProfileEntity(Base):
    __tablename__ = "team_profiles"

    __table_args__ = (
        UniqueConstraint(
            "applicant_startup_id",
            name="uq_team_profile_application",
        ),
    )

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
    )

    applicant_startup_id: Mapped[int] = mapped_column(
        ForeignKey(
            "applicant_startups.id",
            ondelete="CASCADE",
        ),
        nullable=False,
    )

    management_team_size: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )

    management_team_description: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    team_expertise: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )


class FinancialProfileEntity(Base):
    __tablename__ = "financial_profiles"

    __table_args__ = (
        UniqueConstraint(
            "applicant_startup_id",
            name="uq_financial_profile_application",
        ),
    )

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
    )

    applicant_startup_id: Mapped[int] = mapped_column(
        ForeignKey(
            "applicant_startups.id",
            ondelete="CASCADE",
        ),
        nullable=False,
    )

    active_customer_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    mrr_usd: Mapped[Decimal] = mapped_column(
        Numeric(20, 2),
        nullable=False,
    )

    arr_usd: Mapped[Decimal] = mapped_column(
        Numeric(20, 2),
        nullable=False,
    )

    monthly_revenue_usd: Mapped[Decimal] = mapped_column(
        Numeric(20, 2),
        nullable=False,
    )

    annual_revenue_usd: Mapped[Decimal] = mapped_column(
        Numeric(20, 2),
        nullable=False,
    )

    previously_funded: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
    )

    investment_expectation_usd: Mapped[Decimal] = mapped_column(
        Numeric(20, 2),
        nullable=False,
    )

    investment_use_plan: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

class CollaborationProfileEntity(Base):
    __tablename__ = "collaboration_profiles"

    __table_args__ = (
        UniqueConstraint(
            "applicant_startup_id",
            name="uq_collaboration_profile_application",
        ),
    )

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
    )

    applicant_startup_id: Mapped[int] = mapped_column(
        ForeignKey(
            "applicant_startups.id",
            ondelete="CASCADE",
        ),
        nullable=False,
    )

    aviation_sector_experience: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
    )

    aviation_partners: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    thy_group_relationship: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    desired_thy_partnership: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    additional_notes: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

class StartupReviewEntity(Base):
    __tablename__ = "startup_reviews"

    __table_args__ = (
        UniqueConstraint(
            "normalized_startup_name",
            "application_year",
            name="uq_startup_review_name_year",
        ),
    )

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
    )

    startup_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    normalized_startup_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    application_year: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="Will be reviewed",
    )

    note: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    source_verified: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )