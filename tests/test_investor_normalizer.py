from app.matching.investor_normalizer import (
    has_named_investor,
    normalize_investor_list,
)


def test_ignores_order_and_spacing():
    first = normalize_investor_list(
        "Hedef Portföy, Findoor GSYF"
    )
    second = normalize_investor_list(
        "  Findoor GSYF,Hedef   Portföy "
    )

    assert first == second


def test_normalizes_circumflex_difference():
    first = normalize_investor_list(
        "İş Bankası Yapay Zekâ Fabrikası"
    )
    second = normalize_investor_list(
        "İş Bankası Yapay Zeka Fabrikası"
    )

    assert first == second


def test_normalizes_unknown_investor_translation():
    first = normalize_investor_list(
        "Arya VC, Açıklanmayan Yatırımcı"
    )
    second = normalize_investor_list(
        "Arya VC, Undisclosed Investor"
    )

    assert first == second
    assert has_named_investor(first)


def test_unknown_investor_alone_is_not_evidence():
    result = normalize_investor_list("Undisclosed Investor")

    assert not has_named_investor(result)


def test_handles_missing_values():
    for value in (None, "", "NA", "N/A", "Açıklanmadı"):
        result = normalize_investor_list(value)

        assert result == ()
        assert not has_named_investor(result)


def test_removes_repeated_names():
    result = normalize_investor_list(
        "Menlo Ventures, Menlo Ventures"
    )

    assert result == ("menlo ventures",)


def test_preserves_different_investor_lists():
    first = normalize_investor_list("Menlo Ventures")
    second = normalize_investor_list(
        "Menlo Ventures, Anthos Capital"
    )

    assert first != second


def test_preserves_turkish_letters():
    result = normalize_investor_list("Türk Telekom Ventures")

    assert result == ("türk telekom ventures",)