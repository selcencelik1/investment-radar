from decimal import Decimal
from types import SimpleNamespace

from app.matching.duplicate_matcher import find_pdf_duplicate_candidates


def make_record(**changes):
    values = {
        "startup_name": "Example",
        "deal_amount_million_usd": Decimal("1.5"),
        "investors": "Alpha Ventures, Beta Capital",
        "investment_stage": "Seed Stage",
        "reporting_period": "2025-FY",
        "announcement_date_text": "February 2025",
        "source_url": "https://example.com/annual.pdf",
        "source_page": 23,
    }
    values.update(changes)
    return SimpleNamespace(**values)


def make_html(**changes):
    values = {
        "reporting_period": "2025-Q1",
        "announcement_date_text": None,
        "source_url": "https://example.com/quarter.html",
        "source_page": None,
    }
    values.update(changes)
    return make_record(**values)


def test_matches_equivalent_investor_lists():
    html = make_html(investors="Beta Capital,Alpha Ventures")
    pdf = make_record()

    assert find_pdf_duplicate_candidates(html, [pdf]) == [pdf]


def test_keeps_different_quarter_investment_separate():
    html = make_html()
    january = make_record(announcement_date_text="January 2025")
    july = make_record(announcement_date_text="July 2025")

    assert find_pdf_duplicate_candidates(
        html, [january, july]
    ) == [january]


def test_different_amount_does_not_match():
    html = make_html()
    pdf = make_record(deal_amount_million_usd=Decimal("2.5"))

    assert find_pdf_duplicate_candidates(html, [pdf]) == []


def test_different_investor_does_not_match():
    html = make_html()
    pdf = make_record(investors="Other Ventures")

    assert find_pdf_duplicate_candidates(html, [pdf]) == []


def test_missing_amount_does_not_match():
    html = make_html(deal_amount_million_usd=None)
    pdf = make_record(deal_amount_million_usd=None)

    assert find_pdf_duplicate_candidates(html, [pdf]) == []


def test_unknown_investor_alone_does_not_match():
    html = make_html(investors="Açıklanmayan Yatırımcı")
    pdf = make_record(investors="Undisclosed Investor")

    assert find_pdf_duplicate_candidates(html, [pdf]) == []


def test_keeps_multiple_candidates_for_review():
    html = make_html()
    first = make_record()
    second = make_record(
        source_url="https://example.com/another.pdf",
    )

    assert len(
        find_pdf_duplicate_candidates(html, [first, second])
    ) == 2


def test_stage_conflict_does_not_overwrite_sources():
    html = make_html(investment_stage="Erken Aşama")
    pdf = make_record(investment_stage="Late Stage")

    assert find_pdf_duplicate_candidates(html, [pdf]) == [pdf]
    assert html.investment_stage == "Erken Aşama"
    assert pdf.investment_stage == "Late Stage"


def test_different_company_does_not_match():
    html = make_html()
    pdf = make_record(startup_name="Another Company")

    assert find_pdf_duplicate_candidates(html, [pdf]) == []


def test_missing_date_does_not_match():
    html = make_html()
    pdf = make_record(announcement_date_text=None)

    assert find_pdf_duplicate_candidates(html, [pdf]) == []