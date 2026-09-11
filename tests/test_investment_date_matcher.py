import pytest

from app.matching.investment_date_matcher import (
    date_matches_report_period,
)


@pytest.mark.parametrize(
    "date_text, period, expected",
    [
        ("January 2025", "2025-Q1", True),
        ("March 2025", "2025-Q1", True),
        ("April 2025", "2025-Q1", False),
        ("July 2025", "2025-Q1", False),
        ("July 2025", "2025-Q3", True),
        ("December 2025", "2025-Q4", True),
        ("December 2025", "2025-FY", True),
        ("January 2024", "2025-Q1", False),
        ("  FEBRUARY   2025  ", "2025-Q1", True),
        (None, "2025-Q1", False),
        ("NA", "2025-Q1", False),
        ("Unknown 2025", "2025-Q1", False),
        ("January 2025", "2025-Q5", False),
    ],
)
def test_date_matches_report_period(date_text, period, expected):
    assert date_matches_report_period(date_text, period) is expected