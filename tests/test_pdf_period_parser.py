import pytest

from app.parser.pdf_period_parser import parse_pdf_period


def test_detects_annual_report():
    cover = "Turkish Startup Investments Review\n2023"
    foreword = (
        "Welcome to the annual edition of the Turkish Startup "
        "Investments Review with the collaboration of KPMG Turkey."
    )

    assert parse_pdf_period(cover, foreword) == "2023-FY"


def test_detects_quarter_from_cover():
    cover = "Turkish Startup Investments Review Q2 2024"

    assert parse_pdf_period(cover, "") == "2024-Q2"


def test_does_not_assume_year_only_means_annual():
    with pytest.raises(ValueError, match="could not be determined"):
        parse_pdf_period("Turkish Startup Investments Review 2023", "")


def test_ignores_comparison_year_in_foreword():
    cover = "Turkish Startup Investments Review 2023"
    foreword = (
        "Welcome to the annual edition of the Turkish Startup "
        "Investments Review. Funding declined compared with 2022."
    )

    assert parse_pdf_period(cover, foreword) == "2023-FY"


def test_rejects_multiple_cover_years():
    with pytest.raises(ValueError, match="single year"):
        parse_pdf_period("Investments Review 2023 2024", "")


def test_ignores_foreword_footer_quarter_for_annual_report():
    cover = "Turkish Startup Investments Review 2023"
    foreword = (
        "Welcome to the annual edition of the Turkish Startup "
        "Investments Review.\n"
        "Turkish Startup Investments Review Q4 2023 3"
    )

    assert parse_pdf_period(cover, foreword) == "2023-FY"


def test_rejects_conflicting_period_evidence():
    cover = "Turkish Startup Investments Review Q1 2023"
    foreword = (
        "Welcome to the annual edition of the Turkish Startup "
        "Investments Review."
    )

    with pytest.raises(ValueError, match="conflicting annual and quarterly"):
        parse_pdf_period(cover, foreword)


def test_does_not_use_unrelated_annual_statement():
    cover = "Turkish Startup Investments Review 2023"
    foreword = "The annual funding total increased."

    with pytest.raises(ValueError, match="could not be determined"):
        parse_pdf_period(cover, foreword)
