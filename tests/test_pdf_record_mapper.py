from decimal import Decimal

import pytest

from app.parser.pdf_record_mapper import (
    map_pdf_record,
    parse_financial_investor,
)


def test_maps_pdf_record():
    raw_record = {
        "Target Company": "Abonesepeti",
        "Sector": "SaaS",
        "Investors": "FonOrion",
        "Announcement Date": "December 2025",
        "Financial Investor": "Yes",
        "Investors' Origin": "Türkiye",
        "Stake (%)": "NA",
        "Transaction Value ($)": "200,000",
        "Investment Stage": "Seed Stage",
        "source_page": 23,
        "source_row": 2,
    }

    result = map_pdf_record(raw_record)

    assert result.startup_name == "Abonesepeti"
    assert result.announcement_date_text == "December 2025"
    assert result.financial_investor is True
    assert result.deal_amount_million_usd == Decimal("0.2")
    assert result.investment_stage == "Seed Stage"
    assert result.source_page == 23
    assert result.source_row == 2


@pytest.mark.parametrize(
    "value, expected",
    [
        ("Yes", True),
        ("No", False),
        ("NA", None),
        ("", None),
    ],
)
def test_parses_financial_investor(value, expected):
    assert parse_financial_investor(value) is expected


def test_rejects_unknown_financial_investor_value():
    with pytest.raises(ValueError, match="Invalid financial investor value"):
        parse_financial_investor("Maybe")

@pytest.mark.parametrize(
    "raw_amount, expected_amount, expects_warning",
    [
        ("133,81", None, True),
        ("133,810", Decimal("0.13381"), False),
        ("NA", None, False),
    ],
)
def test_preserves_raw_amount_and_reports_ambiguity(
    raw_amount,
    expected_amount,
    expects_warning,
):
    raw_record = {
        "Target Company": "Example",
        "Sector": "Foodtech",
        "Investors": "Example Ventures",
        "Announcement Date": "August 2022",
        "Financial Investor": "Yes",
        "Investors' Origin": "Türkiye",
        "Stake (%)": "NA",
        "Transaction Value ($)": raw_amount,
        "Investment Stage": "Seed Stage",
        "source_page": 36,
        "source_row": 8,
    }

    result = map_pdf_record(raw_record)

    assert result.raw_amount_text == raw_amount
    assert result.deal_amount_million_usd == expected_amount
    assert bool(result.amount_warning) is expects_warning

    # Orijinal veri değiştirilmemeli.
    assert raw_record["Transaction Value ($)"] == raw_amount
