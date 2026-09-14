from decimal import Decimal

from app.models.applicant_startup import ApplicantStartup

from app.matching.investment_grouper import InvestmentGroup

def decimal_to_float(value: Decimal) -> float:
    return float(value)


def build_review_context(
    applicant: ApplicantStartup,
) -> dict:
    return {
        "application": {
            "year": applicant.application_year,
        },
        "company": {
            "name": applicant.startup_name,
            "sector": applicant.sector_nace_code,
            "legal_status": applicant.company_legal_status,
            "headquarters_country": (
                applicant.headquarters_country
            ),
            "founding_date": (
                applicant.founding_date.isoformat()
            ),
            "description": applicant.startup_description,
            "problem_and_solution": (
                applicant.problem_solution
            ),
            "business_model": (
                applicant.business_revenue_model
            ),
            "stage": applicant.startup_stage,
            "previous_program_participation": (
                applicant.previous_program_participation
            ),
        },
        "team": {
            "management_team_size": (
                applicant.management_team_size
            ),
            "management_team_description": (
                applicant.management_team_description
            ),
            "expertise": applicant.team_expertise,
        },
        "financials": {
            "active_customer_count": (
                applicant.active_customer_count
            ),
            "mrr_usd": decimal_to_float(applicant.mrr_usd),
            "arr_usd": decimal_to_float(applicant.arr_usd),
            "monthly_revenue_usd": decimal_to_float(
                applicant.monthly_revenue_usd
            ),
            "annual_revenue_usd": decimal_to_float(
                applicant.annual_revenue_usd
            ),
            "previously_funded": applicant.previously_funded,
            "investment_expectation_usd": decimal_to_float(
                applicant.investment_expectation_usd
            ),
            "investment_use_plan": (
                applicant.investment_use_plan
            ),
        },
        "collaboration": {
            "aviation_experience": (
                applicant.aviation_sector_experience
            ),
            "aviation_partners": applicant.aviation_partners,
            "thy_group_relationship": (
                applicant.thy_group_relationship
            ),
            "desired_thy_partnership": (
                applicant.desired_thy_partnership
            ),
        },
    }

def build_investment_history(
    groups: list[InvestmentGroup],
) -> list[dict]:
    investment_history = []

    for group in groups:
        primary = group.primary
        amount = primary.deal_amount_million_usd

        sources = [
            {
                "reporting_period": member.reporting_period,
                "source_url": member.source_url,
                "source_page": member.source_page,
            }
            for member in group.members
        ]

        investment_history.append({
            "startup_name": primary.startup_name,
            "announcement_date": (
                primary.announcement_date_text
            ),
            "reporting_period": primary.reporting_period,
            "investors": primary.investors,
            "investor_countries": (
                primary.investor_countries
            ),
            "share_percentage": primary.share_percentage,
            "amount_million_usd": (
                float(amount) if amount is not None else None
            ),
            "investment_stage": primary.investment_stage,
            "grouping_status": group.match_status,
            "source_count": len(group.members),
            "sources": sources,
        })

    return investment_history

def build_database_review_context(
    applicant,
) -> dict:
    profile = applicant.startup_profile
    team = applicant.team_profile
    financial = applicant.financial_profile
    collaboration = applicant.collaboration_profile

    missing_sections = []

    context = {
        "application": {
            "year": applicant.application_year,
            "data_available": True,
        },
        "company": {
            "name": applicant.startup_name,
        },
        "team": {},
        "financials": {},
        "collaboration": {},
        "data_availability": {
            "missing_sections": missing_sections,
        },
    }

    if profile is None:
        missing_sections.append("startup_profile")
    else:
        context["company"].update({
            "sector": profile.sector_nace_code,
            "legal_status": profile.legal_status,
            "headquarters_country": (
                profile.headquarters_country
            ),
            "founding_date": (
                profile.founding_date.isoformat()
            ),
            "description": profile.description,
            "problem_and_solution": (
                profile.problem_solution
            ),
            "business_model": (
                profile.business_revenue_model
            ),
            "stage": profile.startup_stage,
            "previous_program_participation": (
                profile.previous_program_participation
            ),
        })

    if team is None:
        missing_sections.append("team_profile")
    else:
        context["team"] = {
            "management_team_size": (
                team.management_team_size
            ),
            "management_team_description": (
                team.management_team_description
            ),
            "expertise": team.team_expertise,
        }

    if financial is None:
        missing_sections.append("financial_profile")
    else:
        context["financials"] = {
            "active_customer_count": (
                financial.active_customer_count
            ),
            "mrr_usd": decimal_to_float(
                financial.mrr_usd
            ),
            "arr_usd": decimal_to_float(
                financial.arr_usd
            ),
            "monthly_revenue_usd": decimal_to_float(
                financial.monthly_revenue_usd
            ),
            "annual_revenue_usd": decimal_to_float(
                financial.annual_revenue_usd
            ),
            "previously_funded": (
                financial.previously_funded
            ),
            "investment_expectation_usd": decimal_to_float(
                financial.investment_expectation_usd
            ),
            "investment_use_plan": (
                financial.investment_use_plan
            ),
        }

    if collaboration is None:
        missing_sections.append("collaboration_profile")
    else:
        context["collaboration"] = {
            "aviation_experience": (
                collaboration.aviation_sector_experience
            ),
            "aviation_partners": (
                collaboration.aviation_partners
            ),
            "thy_group_relationship": (
                collaboration.thy_group_relationship
            ),
            "desired_thy_partnership": (
                collaboration.desired_thy_partnership
            ),
        }

    return context