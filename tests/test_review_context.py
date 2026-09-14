import json
from datetime import date
from decimal import Decimal

from app.ai.review_context import (
    build_database_review_context,
    build_investment_history,
    build_review_context,
)
from app.models.applicant_startup import ApplicantStartup
from types import SimpleNamespace

from app.matching.investment_grouper import InvestmentGroup

def make_applicant() -> ApplicantStartup:
    return ApplicantStartup(
        application_year=2026,
        applicant_full_name="Ada Example",
        applicant_title="Founder",
        applicant_phone="+90 555 000 0000",
        applicant_email="ada@example.com",
        applicant_linkedin_url=(
            "https://linkedin.com/in/ada-example"
        ),
        startup_name="Demo Aviation",
        normalized_name="demo aviation",
        website="https://demo.example",
        sector_nace_code="Aviation Technology / 6201",
        company_legal_status="Limited Company",
        headquarters_country="Turkey",
        founding_date=date(2023, 5, 10),
        startup_description=(
            "AI-based airport operations platform"
        ),
        problem_solution=(
            "Reduces manual airport operation processes"
        ),
        business_revenue_model="B2B SaaS subscription",
        startup_stage="Product-market fit with revenue",
        product_demo_url="https://demo.example/product",
        logo_url="https://demo.example/logo.png",
        pitch_deck_url="https://demo.example/pitch",
        previous_program_participation=True,
        management_team_size="3",
        management_team_description=(
            "Three co-founders with aviation experience"
        ),
        team_expertise=(
            "Artificial intelligence and airport operations"
        ),
        active_customer_count=12,
        mrr_usd=Decimal("5000"),
        arr_usd=Decimal("60000"),
        monthly_revenue_usd=Decimal("8000"),
        annual_revenue_usd=Decimal("96000"),
        previously_funded=True,
        investment_expectation_usd=Decimal("500000"),
        investment_use_plan=(
            "Product development and international sales"
        ),
        aviation_sector_experience=True,
        aviation_partners="Example Airline",
        thy_group_relationship="No previous relationship",
        desired_thy_partnership=(
            "Airport operations pilot project"
        ),
        additional_notes="No additional notes",
    )


def test_builds_company_review_context():
    context = build_review_context(make_applicant())

    assert context["application"]["year"] == 2026
    assert context["company"]["name"] == "Demo Aviation"
    assert context["company"]["sector"] == (
        "Aviation Technology / 6201"
    )
    assert context["financials"]["mrr_usd"] == 5000.0
    assert context["financials"]["previously_funded"] is True
    assert context["collaboration"]["aviation_experience"] is True


def test_excludes_personal_information():
    context = build_review_context(make_applicant())
    serialized_context = json.dumps(context)

    forbidden_values = [
        "Ada Example",
        "+90 555 000 0000",
        "ada@example.com",
        "linkedin.com/in/ada-example",
    ]

    for value in forbidden_values:
        assert value not in serialized_context

def test_builds_grouped_investment_history():
    annual_record = SimpleNamespace(
        startup_name="Demo Aviation",
        reporting_period="2025-FY",
        announcement_date_text="February 2025",
        investors="Example Ventures",
        investor_countries="Turkey",
        share_percentage="10%",
        deal_amount_million_usd=Decimal("1.5"),
        investment_stage="Seed Stage",
        source_url="https://example.com/annual.pdf",
        source_page=24,
    )

    quarterly_record = SimpleNamespace(
        startup_name="Demo Aviation",
        reporting_period="2025-Q1",
        announcement_date_text="February 2025",
        investors="Example Ventures",
        investor_countries="Turkey",
        share_percentage="10%",
        deal_amount_million_usd=Decimal("1.5"),
        investment_stage="Seed Stage",
        source_url="https://example.com/q1.pdf",
        source_page=18,
    )

    groups = [
        InvestmentGroup(
            primary=annual_record,
            members=[annual_record, quarterly_record],
            match_status="Grouped by rule",
        )
    ]

    history = build_investment_history(groups)

    assert len(history) == 1
    assert history[0]["startup_name"] == "Demo Aviation"
    assert history[0]["amount_million_usd"] == 1.5
    assert history[0]["source_count"] == 2
    assert len(history[0]["sources"]) == 2

def test_builds_context_from_database_entity():
    applicant = SimpleNamespace(
        application_year=2026,
        startup_name="Demo Aviation",
        contact=SimpleNamespace(
            full_name="Ada Example",
            phone="+90 555 000 0000",
            email="ada@example.com",
            linkedin_url=(
                "https://linkedin.com/in/ada-example"
            ),
        ),
        startup_profile=SimpleNamespace(
            sector_nace_code="Aviation Technology / 6201",
            legal_status="Limited Company",
            headquarters_country="Turkey",
            founding_date=date(2023, 5, 10),
            description="Airport operations platform",
            problem_solution="Reduces manual processes",
            business_revenue_model="B2B SaaS",
            startup_stage="Product-market fit with revenue",
            previous_program_participation=True,
        ),
        team_profile=SimpleNamespace(
            management_team_size="3",
            management_team_description="Three co-founders",
            team_expertise="AI and aviation operations",
        ),
        financial_profile=SimpleNamespace(
            active_customer_count=12,
            mrr_usd=Decimal("5000"),
            arr_usd=Decimal("60000"),
            monthly_revenue_usd=Decimal("8000"),
            annual_revenue_usd=Decimal("96000"),
            previously_funded=True,
            investment_expectation_usd=Decimal("500000"),
            investment_use_plan="Product and sales",
        ),
        collaboration_profile=SimpleNamespace(
            aviation_sector_experience=True,
            aviation_partners="Example Airline",
            thy_group_relationship="No previous relationship",
            desired_thy_partnership="Operations pilot",
        ),
    )

    context = build_database_review_context(applicant)

    assert context["company"]["name"] == "Demo Aviation"
    assert context["financials"]["mrr_usd"] == 5000.0
    assert context["team"]["management_team_size"] == "3"

    serialized_context = json.dumps(context)

    assert "Ada Example" not in serialized_context
    assert "ada@example.com" not in serialized_context
    assert "+90 555" not in serialized_context
    assert "linkedin.com" not in serialized_context

def test_builds_partial_context_when_sections_are_missing():
    applicant = SimpleNamespace(
        application_year=2025,
        startup_name="Legacy Startup",
        contact=SimpleNamespace(
            full_name="Private Person",
            phone="+90 555 111 2233",
            email="private@example.com",
            linkedin_url="https://linkedin.com/in/private",
        ),
        startup_profile=None,
        team_profile=None,
        financial_profile=None,
        collaboration_profile=None,
    )

    context = build_database_review_context(applicant)

    assert context["company"]["name"] == "Legacy Startup"
    assert context["application"]["year"] == 2025
    assert context["data_availability"]["missing_sections"] == [
        "startup_profile",
        "team_profile",
        "financial_profile",
        "collaboration_profile",
    ]

    serialized_context = json.dumps(context)

    assert "Private Person" not in serialized_context
    assert "private@example.com" not in serialized_context
    assert "+90 555" not in serialized_context
    assert "linkedin.com" not in serialized_context