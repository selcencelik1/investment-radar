from dataclasses import dataclass
from datetime import date
from decimal import Decimal


@dataclass(frozen=True)
class ApplicantStartup:
    application_year: int

    applicant_full_name: str
    applicant_title: str
    applicant_phone: str
    applicant_email: str
    applicant_linkedin_url: str

    startup_name: str
    normalized_name: str
    website: str | None

    sector_nace_code: str
    company_legal_status: str
    headquarters_country: str
    founding_date: date
    startup_description: str
    problem_solution: str
    business_revenue_model: str
    startup_stage: str
    product_demo_url: str | None
    logo_url: str | None
    pitch_deck_url: str
    previous_program_participation: bool

    management_team_size: str
    management_team_description: str
    team_expertise: str

    active_customer_count: int
    mrr_usd: Decimal
    arr_usd: Decimal
    monthly_revenue_usd: Decimal
    annual_revenue_usd: Decimal
    previously_funded: bool
    investment_expectation_usd: Decimal
    investment_use_plan: str

    aviation_sector_experience: bool
    aviation_partners: str | None
    thy_group_relationship: str | None
    desired_thy_partnership: str
    additional_notes: str | None