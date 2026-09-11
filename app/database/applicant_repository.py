from sqlalchemy import delete,select

from app.database.connection import SessionLocal
from app.database.models import (
    ApplicantContactEntity,
    ApplicantStartupEntity,
    CollaborationProfileEntity,
    FinancialProfileEntity,
    StartupProfileEntity,
    TeamProfileEntity,
)
from app.models.applicant_startup import ApplicantStartup
from app.parser.normalizer import normalize_startup_name
from sqlalchemy.orm import selectinload


def upsert_application_detail(
    session,
    entity_class,
    applicant_startup_id: int,
    values: dict,
) -> None:
    entity = session.scalar(
        select(entity_class).where(
            entity_class.applicant_startup_id
            == applicant_startup_id
        )
    )

    if entity is None:
        session.add(
            entity_class(
                applicant_startup_id=applicant_startup_id,
                **values,
            )
        )
        return

    for field_name, value in values.items():
        setattr(entity, field_name, value)


def save_applicants(
    applicants: list[ApplicantStartup],
    replace_application_year: int | None = None,
) -> tuple[int, int, int]:
    created_count = 0
    updated_count = 0
    removed_count = 0

    if replace_application_year is not None:
        if not applicants:
            raise ValueError(
                "An empty CSV cannot replace an application list."
            )

        mismatched_years = {
            applicant.application_year
            for applicant in applicants
            if applicant.application_year
            != replace_application_year
        }

        if mismatched_years:
            raise ValueError(
                "All CSV records must belong to the selected "
                "application year."
            )

    with SessionLocal() as session:
        if replace_application_year is not None:
            incoming_names = {
                applicant.normalized_name
                for applicant in applicants
            }

            existing_applications = session.scalars(
                select(ApplicantStartupEntity).where(
                    ApplicantStartupEntity.application_year
                    == replace_application_year
                )
            ).all()

            stale_application_ids = [
                application.id
                for application in existing_applications
                if application.normalized_name
                   not in incoming_names
            ]

            if stale_application_ids:
                detail_entities = (
                    ApplicantContactEntity,
                    StartupProfileEntity,
                    TeamProfileEntity,
                    FinancialProfileEntity,
                    CollaborationProfileEntity,
                )

                for entity_class in detail_entities:
                    session.execute(
                        delete(entity_class).where(
                            entity_class.applicant_startup_id.in_(
                                stale_application_ids
                            )
                        )
                    )

                session.execute(
                    delete(ApplicantStartupEntity).where(
                        ApplicantStartupEntity.id.in_(
                            stale_application_ids
                        )
                    )
                )

                removed_count = len(stale_application_ids)
        for applicant in applicants:
            application_entity = session.scalar(
                select(ApplicantStartupEntity).where(
                    ApplicantStartupEntity.normalized_name
                    == applicant.normalized_name,
                    ApplicantStartupEntity.application_year
                    == applicant.application_year,
                )
            )

            if application_entity is None:
                application_entity = ApplicantStartupEntity(
                    startup_name=applicant.startup_name,
                    normalized_name=applicant.normalized_name,
                    website=applicant.website,
                    application_year=applicant.application_year,
                )

                session.add(application_entity)
                session.flush()
                created_count += 1
            else:
                application_entity.startup_name = (
                    applicant.startup_name
                )
                application_entity.website = applicant.website
                updated_count += 1

            application_id = application_entity.id

            upsert_application_detail(
                session,
                ApplicantContactEntity,
                application_id,
                {
                    "full_name": applicant.applicant_full_name,
                    "title": applicant.applicant_title,
                    "phone": applicant.applicant_phone,
                    "email": applicant.applicant_email,
                    "linkedin_url": (
                        applicant.applicant_linkedin_url
                    ),
                },
            )

            upsert_application_detail(
                session,
                StartupProfileEntity,
                application_id,
                {
                    "sector_nace_code": applicant.sector_nace_code,
                    "legal_status": applicant.company_legal_status,
                    "headquarters_country": (
                        applicant.headquarters_country
                    ),
                    "founding_date": applicant.founding_date,
                    "description": applicant.startup_description,
                    "problem_solution": applicant.problem_solution,
                    "business_revenue_model": (
                        applicant.business_revenue_model
                    ),
                    "startup_stage": applicant.startup_stage,
                    "product_demo_url": applicant.product_demo_url,
                    "logo_url": applicant.logo_url,
                    "pitch_deck_url": applicant.pitch_deck_url,
                    "previous_program_participation": (
                        applicant.previous_program_participation
                    ),
                },
            )

            upsert_application_detail(
                session,
                TeamProfileEntity,
                application_id,
                {
                    "management_team_size": (
                        applicant.management_team_size
                    ),
                    "management_team_description": (
                        applicant.management_team_description
                    ),
                    "team_expertise": applicant.team_expertise,
                },
            )

            upsert_application_detail(
                session,
                FinancialProfileEntity,
                application_id,
                {
                    "active_customer_count": (
                        applicant.active_customer_count
                    ),
                    "mrr_usd": applicant.mrr_usd,
                    "arr_usd": applicant.arr_usd,
                    "monthly_revenue_usd": (
                        applicant.monthly_revenue_usd
                    ),
                    "annual_revenue_usd": (
                        applicant.annual_revenue_usd
                    ),
                    "previously_funded": (
                        applicant.previously_funded
                    ),
                    "investment_expectation_usd": (
                        applicant.investment_expectation_usd
                    ),
                    "investment_use_plan": (
                        applicant.investment_use_plan
                    ),
                },
            )

            upsert_application_detail(
                session,
                CollaborationProfileEntity,
                application_id,
                {
                    "aviation_sector_experience": (
                        applicant.aviation_sector_experience
                    ),
                    "aviation_partners": (
                        applicant.aviation_partners
                    ),
                    "thy_group_relationship": (
                        applicant.thy_group_relationship
                    ),
                    "desired_thy_partnership": (
                        applicant.desired_thy_partnership
                    ),
                    "additional_notes": (
                        applicant.additional_notes
                    ),
                },
            )

        session.commit()

    return created_count, updated_count, removed_count

def get_applicant_names(
    application_year: int | None = None,
) -> list[str]:
    with SessionLocal() as session:
        statement = select(
            ApplicantStartupEntity.startup_name
        ).distinct()

        if application_year is not None:
            statement = statement.where(
                ApplicantStartupEntity.application_year
                == application_year
            )

        statement = statement.order_by(
            ApplicantStartupEntity.startup_name
        )

        names = session.scalars(statement).all()

        return list(names)


def get_application_years() -> list[int]:
    with SessionLocal() as session:
        statement = (
            select(ApplicantStartupEntity.application_year)
            .distinct()
            .order_by(
                ApplicantStartupEntity.application_year.desc()
            )
        )

        years = session.scalars(statement).all()

        return list(years)

def get_applicant_details(
    startup_name: str,
    application_year: int | None = None,
) -> list[ApplicantStartupEntity]:
    normalized_name = normalize_startup_name(startup_name)

    with SessionLocal() as session:
        statement = (
            select(ApplicantStartupEntity)
            .options(
                selectinload(
                    ApplicantStartupEntity.contact
                ),
                selectinload(
                    ApplicantStartupEntity.startup_profile
                ),
                selectinload(
                    ApplicantStartupEntity.team_profile
                ),
                selectinload(
                    ApplicantStartupEntity.financial_profile
                ),
                selectinload(
                    ApplicantStartupEntity.collaboration_profile
                ),
            )
            .where(
                ApplicantStartupEntity.normalized_name
                == normalized_name
            )
        )

        if application_year is not None:
            statement = statement.where(
                ApplicantStartupEntity.application_year
                == application_year
            )

        statement = statement.order_by(
            ApplicantStartupEntity.application_year.desc()
        )

        applicants = session.scalars(statement).all()

        return list(applicants)
def get_all_applicant_details(
    application_year: int | None = None,
) -> list[ApplicantStartupEntity]:
    with SessionLocal() as session:
        statement = (
            select(ApplicantStartupEntity)
            .options(
                selectinload(
                    ApplicantStartupEntity.contact
                ),
                selectinload(
                    ApplicantStartupEntity.startup_profile
                ),
                selectinload(
                    ApplicantStartupEntity.team_profile
                ),
                selectinload(
                    ApplicantStartupEntity.financial_profile
                ),
                selectinload(
                    ApplicantStartupEntity.collaboration_profile
                ),
            )
        )

        if application_year is not None:
            statement = statement.where(
                ApplicantStartupEntity.application_year
                == application_year
            )

        statement = statement.order_by(
            ApplicantStartupEntity.startup_name
        )

        applicants = session.scalars(statement).all()

        return list(applicants)