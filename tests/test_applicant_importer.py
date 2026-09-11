import pytest

import csv
from datetime import date
from decimal import Decimal

from app.importers.applicant_importer import (
    REQUIRED_COLUMNS,
    load_applicants_from_csv,
)
from app.source_language import (
    TURKISH_APPLICANT_COLUMN_ALIASES,
)

VALID_APPLICANT = {
    "application_year": "2026",
    "applicant_full_name": "Ada Example",
    "applicant_title": "Founder and CEO",
    "applicant_phone": "+90 555 000 0000",
    "applicant_email": "ada@example.com",
    "applicant_linkedin_url": "https://linkedin.com/in/ada-example",
    "startup_name": "Demo Aviation Ltd. Şti.",
    "sector_nace_code": "Aviation Technology / 6201",
    "company_legal_status": "Limited Company",
    "headquarters_country": "Turkey",
    "founding_date": "10.05.2023",
    "startup_description": "AI based airport operations platform",
    "problem_solution": "Reduces manual airport operation processes",
    "business_revenue_model": "B2B SaaS subscription",
    "startup_stage": "Product market fit with revenue",
    "website_url": "https://demo-aviation.example",
    "product_demo_url": "https://demo-aviation.example/demo",
    "logo_url": "https://demo-aviation.example/logo.png",
    "pitch_deck_url": "https://demo-aviation.example/pitch",
    "previous_program_participation": "yes",
    "management_team_size": "3",
    "management_team_description": (
        "Three cofounders with software and aviation experience"
    ),
    "team_expertise": "Artificial intelligence and airport operations",
    "active_customer_count": "12",
    "mrr_usd": "5000",
    "arr_usd": "60000",
    "monthly_revenue_usd": "8000",
    "annual_revenue_usd": "96000",
    "previously_funded": "yes",
    "investment_expectation_usd": "500000",
    "investment_use_plan": (
        "Product development and international sales"
    ),
    "aviation_sector_experience": "yes",
    "aviation_partners": "Example Airline",
    "thy_group_relationship": "No previous relationship",
    "desired_thy_partnership": (
        "Airport baggage operations pilot project"
    ),
    "additional_notes": "No additional notes",
}

def write_applicant_csv(
    file_path,
    row=None,
    columns=None,
):
    selected_columns = (
        sorted(REQUIRED_COLUMNS)
        if columns is None
        else columns
    )

    selected_row = {
        column: value
        for column, value in (row or VALID_APPLICANT).items()
        if column in selected_columns
    }

    with file_path.open(
        "w",
        encoding="utf-8",
        newline="",
    ) as csv_file:
        writer = csv.DictWriter(
            csv_file,
            fieldnames=selected_columns,
        )
        writer.writeheader()
        writer.writerow(selected_row)
def test_loads_complete_applicant_record(tmp_path):
    csv_file = tmp_path / "applicants.csv"
    write_applicant_csv(csv_file)

    applicants = load_applicants_from_csv(csv_file)

    assert len(applicants) == 1

    applicant = applicants[0]

    assert applicant.startup_name == "Demo Aviation Ltd. Şti."
    assert applicant.normalized_name == "demo aviation"
    assert applicant.application_year == 2026
    assert applicant.founding_date == date(2023, 5, 10)
    assert applicant.active_customer_count == 12
    assert applicant.mrr_usd == Decimal("5000")
    assert applicant.previously_funded is True
    assert applicant.aviation_sector_experience is True

def test_raises_error_when_required_column_is_missing(
    tmp_path,
):
    csv_file = tmp_path / "missing_column.csv"

    columns = sorted(
        REQUIRED_COLUMNS - {"website_url"}
    )

    write_applicant_csv(
        csv_file,
        columns=columns,
    )

    with pytest.raises(
        ValueError,
        match="Missing CSV columns: website_url",
    ):
        load_applicants_from_csv(csv_file)


def test_loads_turkish_form_export_with_external_year(
    tmp_path,
):
    csv_file = tmp_path / "turkish_form_export.csv"

    reverse_aliases = {
        target_header: source_header
        for source_header, target_header
        in TURKISH_APPLICANT_COLUMN_ALIASES.items()
    }

    turkish_row = {
        reverse_aliases[column]: value
        for column, value in VALID_APPLICANT.items()
        if column != "application_year"
    }

    # Gerçek form dışa aktarımında başlıklarda yıldız ve
    # satır sonu bulunabileceğini de deniyoruz.
    full_name = turkish_row.pop("Adınız Soyadınız")
    turkish_row["Adınız Soyadınız\n*"] = full_name

    with csv_file.open(
        "w",
        encoding="utf-8",
        newline="",
    ) as output_file:
        writer = csv.DictWriter(
            output_file,
            fieldnames=list(turkish_row),
        )
        writer.writeheader()
        writer.writerow(turkish_row)

    applicants = load_applicants_from_csv(
        csv_file,
        application_year=2026,
    )

    assert len(applicants) == 1

    applicant = applicants[0]

    assert applicant.application_year == 2026
    assert applicant.applicant_full_name == "Ada Example"
    assert applicant.startup_name == "Demo Aviation Ltd. Şti."
    assert applicant.normalized_name == "demo aviation"
    assert applicant.mrr_usd == Decimal("5000")
    assert applicant.previously_funded is True