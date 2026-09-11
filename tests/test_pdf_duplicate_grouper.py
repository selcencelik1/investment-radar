from decimal import Decimal
from types import SimpleNamespace

from app.matching.pdf_duplicate_grouper import group_pdf_records


def make_record(record_id, source_url, **changes):
    values = {
        "id": record_id,
        "source_url": source_url,
        "source_page": 23,
        "source_row": 2,
        "startup_name": "Example",
        "announcement_date_text": "January 2025",
        "deal_amount_million_usd": Decimal("2"),
        "investors": "Alpha Ventures",
        "investment_stage": "Seed Stage",
        "share_percentage": "NA",
    }
    values.update(changes)
    return SimpleNamespace(**values)


def test_groups_same_investment_from_different_pdfs():
    first = make_record(1, "https://example.com/q1.pdf")
    second = make_record(2, "https://example.com/annual.pdf")

    groups = group_pdf_records([first, second])

    assert len(groups) == 1
    assert {record.id for record in groups[0]} == {1, 2}


def test_preserves_different_investment_dates():
    first = make_record(1, "https://example.com/q1.pdf")
    second = make_record(
        2,
        "https://example.com/annual.pdf",
        announcement_date_text="July 2025",
    )

    assert len(group_pdf_records([first, second])) == 2


def test_preserves_different_amounts():
    first = make_record(1, "https://example.com/q1.pdf")
    second = make_record(
        2,
        "https://example.com/annual.pdf",
        deal_amount_million_usd=Decimal("3"),
    )

    assert len(group_pdf_records([first, second])) == 2


def test_does_not_merge_missing_amounts():
    first = make_record(
        1,
        "https://example.com/q1.pdf",
        deal_amount_million_usd=None,
    )
    second = make_record(
        2,
        "https://example.com/annual.pdf",
        deal_amount_million_usd=None,
    )

    assert len(group_pdf_records([first, second])) == 2


def test_preserves_ambiguous_same_source_rows():
    first = make_record(1, "https://example.com/q1.pdf")
    second = make_record(
        2,
        "https://example.com/q1.pdf",
        source_row=3,
    )
    third = make_record(3, "https://example.com/annual.pdf")

    groups = group_pdf_records([first, second, third])

    assert len(groups) == 3
    assert sorted(
        record.id
        for group in groups
        for record in group
    ) == [1, 2, 3]


def test_preserves_stage_conflicts():
    first = make_record(1, "https://example.com/q1.pdf")
    second = make_record(
        2,
        "https://example.com/annual.pdf",
        investment_stage="Late Stage",
    )

    assert len(group_pdf_records([first, second])) == 2


def test_handles_empty_input():
    assert group_pdf_records([]) == []