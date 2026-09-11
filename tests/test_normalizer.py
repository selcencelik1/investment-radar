from decimal import Decimal
from app.parser.normalizer import (
    normalize_pdf_amount_to_million_usd,
)
import pytest

from app.parser.normalizer import (
    normalize_deal_amount,
    normalize_startup_name,)


def test_normalizes_decimal_comma():
    result = normalize_deal_amount("23,0")

    assert result == Decimal("23.0")


def test_normalizes_value_with_whitespace():
    result = normalize_deal_amount("  5,5  ")

    assert result == Decimal("5.5")


def test_returns_none_when_amount_is_not_disclosed():
    result = normalize_deal_amount("Açıklanmadı")

    assert result is None


def test_returns_none_when_value_is_empty():
    result = normalize_deal_amount("")

    assert result is None


def test_raises_error_for_invalid_amount():
    with pytest.raises(
        ValueError,
        match="Investment amount could not be converted to a number"
    ):
        normalize_deal_amount("bilinmiyor")


def test_normalizes_uppercase_startup_name():
    result = normalize_startup_name("MİLVUS ROBOTICS")

    assert result == "milvus robotics"


def test_removes_company_suffix():
    result = normalize_startup_name("Example Yazılım A.Ş.")

    assert result == "example yazılım"


def test_removes_punctuation_and_extra_spaces():
    result = normalize_startup_name(
        "  Example---Robotics!!!  "
    )

    assert result == "example robotics"


def test_returns_same_result_for_equivalent_names():
    first = normalize_startup_name("Demo Robotics A.Ş.")
    second = normalize_startup_name("DEMO ROBOTICS")

    assert first == second

@pytest.mark.parametrize(
    "raw_value, expected",
    [
        ("200,000", Decimal("0.2")),
        ("2,000,000", Decimal("2")),
        ("21,150", Decimal("0.02115")),
        ("200000", Decimal("0.2")),
        ("200,000.50", Decimal("0.2000005")),
        ("0", Decimal("0")),
    ],
)
def test_converts_pdf_dollars_to_millions(raw_value, expected):
    assert normalize_pdf_amount_to_million_usd(raw_value) == expected


@pytest.mark.parametrize("raw_value", ["NA", "N/A", "", "Undisclosed"])
def test_handles_undisclosed_pdf_amount(raw_value):
    assert normalize_pdf_amount_to_million_usd(raw_value) is None


def test_rejects_turkish_decimal_format_in_pdf_amount():
    with pytest.raises(ValueError, match="Invalid PDF investment amount"):
        normalize_pdf_amount_to_million_usd("5,5")

def test_parses_multiple_dot_thousands_groups():
    from decimal import Decimal
    from app.parser.normalizer import normalize_pdf_amount_to_million_usd

    result = normalize_pdf_amount_to_million_usd("6.600.000")

    assert result == Decimal("6.6")


def test_preserves_pdf_decimal_amount():
    from decimal import Decimal
    from app.parser.normalizer import normalize_pdf_amount_to_million_usd

    result = normalize_pdf_amount_to_million_usd("135000.50")

    assert result == Decimal("0.1350005")


def test_rejects_malformed_dot_groups():
    import pytest
    from app.parser.normalizer import normalize_pdf_amount_to_million_usd

    with pytest.raises(ValueError, match="Invalid PDF investment amount"):
        normalize_pdf_amount_to_million_usd("6.60.000")
