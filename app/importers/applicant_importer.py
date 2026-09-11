from datetime import datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path

import pandas as pd

from app.models.applicant_startup import ApplicantStartup
from app.parser.normalizer import normalize_startup_name
from app.source_language import (
    FALSE_VALUE_LABELS,
    TRUE_VALUE_LABELS,
    TURKISH_APPLICANT_COLUMN_ALIASES,
)


REQUIRED_COLUMNS = {
    "application_year",
    "applicant_full_name",
    "applicant_title",
    "applicant_phone",
    "applicant_email",
    "applicant_linkedin_url",
    "startup_name",
    "sector_nace_code",
    "company_legal_status",
    "headquarters_country",
    "founding_date",
    "startup_description",
    "problem_solution",
    "business_revenue_model",
    "startup_stage",
    "website_url",
    "product_demo_url",
    "logo_url",
    "pitch_deck_url",
    "previous_program_participation",
    "management_team_size",
    "management_team_description",
    "team_expertise",
    "active_customer_count",
    "mrr_usd",
    "arr_usd",
    "monthly_revenue_usd",
    "annual_revenue_usd",
    "previously_funded",
    "investment_expectation_usd",
    "investment_use_plan",
    "aviation_sector_experience",
    "aviation_partners",
    "thy_group_relationship",
    "desired_thy_partnership",
    "additional_notes",
}

def normalize_csv_header(header: object) -> str:
    return " ".join(
        str(header)
        .replace("\n", " ")
        .replace("\r", " ")
        .replace("*", " ")
        .split()
    )

def get_required_text(
    row: pd.Series,
    column: str,
    row_number: int,
) -> str:
    value = row[column]

    if pd.isna(value):
        raise ValueError(
            f"Row {row_number}: {column} cannot be empty."
        )

    text = str(value).strip()

    if not text:
        raise ValueError(
            f"Row {row_number}: {column} cannot be empty."
        )

    return text


def get_optional_text(
    row: pd.Series,
    column: str,
) -> str | None:
    value = row[column]

    if pd.isna(value):
        return None

    text = str(value).strip()

    return text or None


def parse_integer(
    row: pd.Series,
    column: str,
    row_number: int,
) -> int:
    value = get_required_text(row, column, row_number)

    try:
        numeric_value = Decimal(value)
    except InvalidOperation as error:
        raise ValueError(
            f"Row {row_number}: {column} must be an integer."
        ) from error

    if numeric_value != numeric_value.to_integral_value():
        raise ValueError(
            f"Row {row_number}: {column} must be an integer."
        )

    result = int(numeric_value)

    if result < 0:
        raise ValueError(
            f"Row {row_number}: {column} cannot be negative."
        )

    return result


def parse_money(
    row: pd.Series,
    column: str,
    row_number: int,
) -> Decimal:
    value = get_required_text(row, column, row_number)

    cleaned_value = (
        value
        .replace("$", "")
        .replace(",", "")
        .strip()
    )

    try:
        result = Decimal(cleaned_value)
    except InvalidOperation as error:
        raise ValueError(
            f"Row {row_number}: {column} must be a valid amount."
        ) from error

    if result < 0:
        raise ValueError(
            f"Row {row_number}: {column} cannot be negative."
        )

    return result


def parse_boolean(
    row: pd.Series,
    column: str,
    row_number: int,
) -> bool:
    value = get_required_text(
        row,
        column,
        row_number,
    ).casefold()

    if value in TRUE_VALUE_LABELS:
        return True

    if value in FALSE_VALUE_LABELS:
        return False

    raise ValueError(
        f"Row {row_number}: {column} must be true or false."
    )


def parse_date(
    row: pd.Series,
    column: str,
    row_number: int,
):
    value = get_required_text(row, column, row_number)

    accepted_formats = (
        "%Y-%m-%d",
        "%d.%m.%Y",
    )

    for date_format in accepted_formats:
        try:
            return datetime.strptime(
                value,
                date_format,
            ).date()
        except ValueError:
            continue

    raise ValueError(
        f"Row {row_number}: {column} must use "
        "YYYY-MM-DD or DD.MM.YYYY format."
    )


def load_applicants_from_csv(
    file_path: str | Path,
    application_year: int | None = None,
) -> list[ApplicantStartup]:
    dataframe = pd.read_csv(file_path)

    normalized_aliases = {
        normalize_csv_header(source_header): target_header
        for source_header, target_header
        in TURKISH_APPLICANT_COLUMN_ALIASES.items()
    }

    dataframe = dataframe.rename(
        columns={
            original_header: normalized_aliases.get(
                normalize_csv_header(original_header),
                normalize_csv_header(original_header),
            )
            for original_header in dataframe.columns
        }
    )

    if (
        "application_year" not in dataframe.columns
        and application_year is not None
    ):
        dataframe["application_year"] = application_year

    missing_columns = REQUIRED_COLUMNS - set(dataframe.columns)
    if missing_columns:
        missing_text = ", ".join(sorted(missing_columns))

        raise ValueError(
            f"Missing CSV columns: {missing_text}"
        )

    applicants = []

    for index, row in dataframe.iterrows():
        row_number = index + 2

        if row.isna().all():
            continue

        startup_name = get_required_text(
            row,
            "startup_name",
            row_number,
        )

        applicant = ApplicantStartup(
            application_year=parse_integer(
                row,
                "application_year",
                row_number,
            ),
            applicant_full_name=get_required_text(
                row,
                "applicant_full_name",
                row_number,
            ),
            applicant_title=get_required_text(
                row,
                "applicant_title",
                row_number,
            ),
            applicant_phone=get_required_text(
                row,
                "applicant_phone",
                row_number,
            ),
            applicant_email=get_required_text(
                row,
                "applicant_email",
                row_number,
            ),
            applicant_linkedin_url=get_required_text(
                row,
                "applicant_linkedin_url",
                row_number,
            ),
            startup_name=startup_name,
            normalized_name=normalize_startup_name(
                startup_name
            ),
            website=get_required_text(
                row,
                "website_url",
                row_number,
            ),
            sector_nace_code=get_required_text(
                row,
                "sector_nace_code",
                row_number,
            ),
            company_legal_status=get_required_text(
                row,
                "company_legal_status",
                row_number,
            ),
            headquarters_country=get_required_text(
                row,
                "headquarters_country",
                row_number,
            ),
            founding_date=parse_date(
                row,
                "founding_date",
                row_number,
            ),
            startup_description=get_required_text(
                row,
                "startup_description",
                row_number,
            ),
            problem_solution=get_required_text(
                row,
                "problem_solution",
                row_number,
            ),
            business_revenue_model=get_required_text(
                row,
                "business_revenue_model",
                row_number,
            ),
            startup_stage=get_required_text(
                row,
                "startup_stage",
                row_number,
            ),
            product_demo_url=get_optional_text(
                row,
                "product_demo_url",
            ),
            logo_url=get_optional_text(
                row,
                "logo_url",
            ),
            pitch_deck_url=get_required_text(
                row,
                "pitch_deck_url",
                row_number,
            ),
            previous_program_participation=parse_boolean(
                row,
                "previous_program_participation",
                row_number,
            ),
            management_team_size=get_required_text(
                row,
                "management_team_size",
                row_number,
            ),
            management_team_description=get_required_text(
                row,
                "management_team_description",
                row_number,
            ),
            team_expertise=get_required_text(
                row,
                "team_expertise",
                row_number,
            ),
            active_customer_count=parse_integer(
                row,
                "active_customer_count",
                row_number,
            ),
            mrr_usd=parse_money(
                row,
                "mrr_usd",
                row_number,
            ),
            arr_usd=parse_money(
                row,
                "arr_usd",
                row_number,
            ),
            monthly_revenue_usd=parse_money(
                row,
                "monthly_revenue_usd",
                row_number,
            ),
            annual_revenue_usd=parse_money(
                row,
                "annual_revenue_usd",
                row_number,
            ),
            previously_funded=parse_boolean(
                row,
                "previously_funded",
                row_number,
            ),
            investment_expectation_usd=parse_money(
                row,
                "investment_expectation_usd",
                row_number,
            ),
            investment_use_plan=get_required_text(
                row,
                "investment_use_plan",
                row_number,
            ),
            aviation_sector_experience=parse_boolean(
                row,
                "aviation_sector_experience",
                row_number,
            ),
            aviation_partners=get_optional_text(
                row,
                "aviation_partners",
            ),
            thy_group_relationship=get_optional_text(
                row,
                "thy_group_relationship",
            ),
            desired_thy_partnership=get_required_text(
                row,
                "desired_thy_partnership",
                row_number,
            ),
            additional_notes=get_optional_text(
                row,
                "additional_notes",
            ),
        )

        applicants.append(applicant)

    return applicants