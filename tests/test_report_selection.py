import pytest

from app.pipeline.report_selection import select_reports_for_import


def make_report(period, status="READY"):
    return {
        "url": f"https://example.com/{period}",
        "status": status,
        "period": period,
        "count": 10,
        "detail": "",
    }


def test_prefers_annual_report():
    reports = [
        make_report("2024-Q1"),
        make_report("2024-Q2"),
        make_report("2024-FY"),
    ]

    selected = select_reports_for_import(reports)

    assert [item["period"] for item in selected] == ["2024-FY"]


def test_uses_quarters_when_annual_is_missing():
    reports = [
        make_report("2026-Q2"),
        make_report("2026-Q1"),
    ]

    selected = select_reports_for_import(reports)

    assert [item["period"] for item in selected] == [
        "2026-Q1",
        "2026-Q2",
    ]


def test_failed_annual_does_not_hide_ready_quarter():
    reports = [
        make_report("2024-FY", "NEEDS_REVIEW"),
        make_report("2024-Q1"),
    ]

    selected = select_reports_for_import(reports)

    assert [item["period"] for item in selected] == ["2024-Q1"]


def test_excludes_out_of_scope_reports():
    reports = [
        make_report("2023-FY", "OUT_OF_SCOPE"),
        make_report("2025-FY"),
    ]

    selected = select_reports_for_import(reports)

    assert [item["period"] for item in selected] == ["2025-FY"]


def test_selects_each_year_independently():
    reports = [
        make_report("2026-Q1"),
        make_report("2025-Q1"),
        make_report("2025-FY"),
        make_report("2023-FY"),
    ]

    selected = select_reports_for_import(reports)

    assert [item["period"] for item in selected] == [
        "2023-FY",
        "2025-FY",
        "2026-Q1",
    ]


def test_rejects_duplicate_periods():
    reports = [
        make_report("2024-FY"),
        make_report("2024-FY"),
    ]

    with pytest.raises(ValueError, match="Multiple ready reports"):
        select_reports_for_import(reports)


def test_rejects_missing_period_for_ready_report():
    with pytest.raises(ValueError, match="missing its reporting period"):
        select_reports_for_import([make_report(None)])


def test_handles_empty_list():
    assert select_reports_for_import([]) == []
