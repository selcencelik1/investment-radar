from decimal import Decimal
from types import SimpleNamespace

from app.evaluation.investor_view import (
    build_investor_relations,
    classify_investor,
    split_investor_names,
)


def make_record(**changes):
    values = {
        "startup_name": "Example",
        "sector": "SaaS",
        "investors": "Alpha GSYF, Beta Ventures",
        "reporting_period": "2025-FY",
        "announcement_date_text": "February 2025",
        "deal_amount_million_usd": Decimal("2"),
        "investment_stage": "Seed Stage",
        "source_url": "https://example.com/report.pdf",
    }
    values.update(changes)
    return SimpleNamespace(**values)


def test_splits_multiple_investors():
    result = split_investor_names(
        "Alpha GSYF, Beta Ventures"
    )

    assert result == ["Alpha GSYF", "Beta Ventures"]


def test_removes_unknown_investor():
    result = split_investor_names(
        "Alpha GSYF, Undisclosed Investor"
    )

    assert result == ["Alpha GSYF"]


def test_removes_repeated_investor():
    result = split_investor_names(
        "Alpha GSYF, alpha   gsyf"
    )

    assert result == ["Alpha GSYF"]


def test_classifies_gsyf_candidate():
    assert classify_investor("Example GSYF") == (
        "Fund / institutional investor candidate"
    )


def test_classifies_venture_candidate():
    assert classify_investor("Example Ventures") == (
        "Fund / institutional investor candidate"
    )


def test_does_not_claim_unknown_type():
    assert classify_investor("Example Holding") == "Type needs review"


def test_builds_one_relation_per_investor():
    result = build_investor_relations([make_record()])

    assert len(result) == 2
    assert {
        relation.investor_name
        for relation in result
    } == {"Alpha GSYF", "Beta Ventures"}

    assert all(
        relation.startup_name == "Example"
        for relation in result
    )


def test_preserves_separate_startup_investments():
    first = make_record(startup_name="Startup A")
    second = make_record(
        startup_name="Startup B",
        investors="Alpha GSYF",
    )

    result = build_investor_relations([first, second])

    alpha_relations = [
        relation
        for relation in result
        if relation.normalized_investor_name == "alpha gsyf"
    ]

    assert {
        relation.startup_name
        for relation in alpha_relations
    } == {"Startup A", "Startup B"}
