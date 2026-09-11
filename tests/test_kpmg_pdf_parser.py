from app.parser.kpmg_pdf_parser import remove_empty_columns
import pytest

from app.parser.kpmg_pdf_parser import (
    EXPECTED_HEADERS,
    repair_investor_origin_column,
)

def test_removes_completely_empty_column():
    table = [
        ["Company", "", "Amount"],
        ["Example A", None, "200,000"],
        ["Example B", "", "500,000"],
    ]

    result = remove_empty_columns(table)

    assert result == [
        ["Company", "Amount"],
        ["Example A", "200,000"],
        ["Example B", "500,000"],
    ]


def test_preserves_column_with_missing_value():
    table = [
        ["Company", "Amount"],
        ["Example A", None],
        ["Example B", "500,000"],
    ]

    result = remove_empty_columns(table)

    assert result == [
        ["Company", "Amount"],
        ["Example A", ""],
        ["Example B", "500,000"],
    ]


def test_preserves_unnamed_column_containing_data():
    table = [
        ["Company", ""],
        ["Example A", "Important information"],
    ]

    result = remove_empty_columns(table)

    assert result == [
        ["Company", ""],
        ["Example A", "Important information"],
    ]

def test_repairs_stray_comma_column():
    headers = EXPECTED_HEADERS[:6] + [""] + EXPECTED_HEADERS[6:]

    table = [
        headers,
        [
            "Example",
            "SaaS",
            "Example Ventures",
            "June 2025",
            "Yes",
            "Türkiye",
            ",",
            "NA",
            "200,000",
            "Seed Stage",
        ],
    ]

    result = repair_investor_origin_column(table)

    assert result[0] == EXPECTED_HEADERS
    assert len(result[1]) == 9
    assert result[1][5] == "Türkiye,"
    assert result[1][6] == "NA"
    assert result[1][7] == "200,000"


def test_rejects_unexpected_content_in_extra_column():
    headers = EXPECTED_HEADERS[:6] + [""] + EXPECTED_HEADERS[6:]

    table = [
        headers,
        [
            "Example",
            "SaaS",
            "Example Ventures",
            "June 2025",
            "Yes",
            "Türkiye",
            "USA",
            "NA",
            "200,000",
            "Seed Stage",
        ],
    ]

    with pytest.raises(ValueError, match="unexpected content"):
        repair_investor_origin_column(table)

def test_normalizes_investor_origin_header_without_changing_data():
    from app.parser.kpmg_pdf_parser import normalize_pdf_headers

    table = [
        ["Target Company", "Investor's Origin"],
        ["Example", "Türkiye"],
    ]

    result = normalize_pdf_headers(table)

    assert result == [
        ["Target Company", "Investors' Origin"],
        ["Example", "Türkiye"],
    ]
    assert table[0][1] == "Investor's Origin"


def test_preserves_standard_investor_origin_header():
    from app.parser.kpmg_pdf_parser import normalize_pdf_headers

    table = [
        ["Target Company", "Investors' Origin"],
        ["Example", "Türkiye"],
    ]

    assert normalize_pdf_headers(table) == table

def test_normalizes_2024_q1_headers():
    from app.parser.kpmg_pdf_parser import (
        EXPECTED_HEADERS,
        normalize_pdf_headers,
    )

    headers = [
        "Target Company",
        "Sector",
        "Investor",
        "Announcement\nDate",
        "Financial\nInvestor",
        "Investor's Origin",
        "Stake (%)",
        "Deal Value ($)",
        "Investment\nStage",
    ]
    row = [
        "Apollo IoT",
        "SaaS",
        "Nevzat Aydın (Private Investor)",
        "January 2024",
        "No",
        "Türkiye",
        "NA",
        "135,000",
        "Seed Stage",
    ]

    result = normalize_pdf_headers([headers, row])

    assert result[0] == EXPECTED_HEADERS
    assert result[1] == row
