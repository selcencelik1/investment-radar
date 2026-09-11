from decimal import Decimal, InvalidOperation
import re

from app.source_language import (
    LOCALIZED_COMPANY_SUFFIXES,
    NOT_DISCLOSED_LABEL,
    STARTUP_NAME_ALLOWED_CHARACTERS_PATTERN,
)


def normalize_deal_amount(value: str) -> Decimal | None:
    cleaned_value = value.strip()

    if not cleaned_value:
        return None

    if cleaned_value.casefold() == NOT_DISCLOSED_LABEL.casefold():
        return None

    cleaned_value = cleaned_value.replace("$", "").strip()

    if "," in cleaned_value:
        cleaned_value = cleaned_value.replace(".", "")
        cleaned_value = cleaned_value.replace(",", ".")

    try:
        return Decimal(cleaned_value)
    except InvalidOperation as error:
        raise ValueError(
            f"Investment amount could not be converted to a number: {value}"
        ) from error


def normalize_startup_name(name: str) -> str:
    normalized = name.casefold().strip()
    normalized = normalized.replace("i\u0307", "i")

    normalized = re.sub(
        STARTUP_NAME_ALLOWED_CHARACTERS_PATTERN,
        " ",
        normalized,
    )

    normalized = re.sub(
        r"\s+",
        " ",
        normalized,
    ).strip()

    for suffix in LOCALIZED_COMPANY_SUFFIXES:
        if normalized.endswith(suffix):
            normalized = normalized[:-len(suffix)].strip()
            break

    return normalized


def normalize_pdf_amount_to_million_usd(
    value: str,
) -> Decimal | None:
    cleaned = value.strip()

    if cleaned.upper() in {"", "NA", "N/A", "UNDISCLOSED"}:
        return None
    # Groups of three digits separated by at least two periods.
    # Example: 6.600.000
    if re.fullmatch(r"[0-9]{1,3}(?:\.[0-9]{3}){2,}", cleaned):
        amount_usd = Decimal(cleaned.replace(".", ""))
        return amount_usd / Decimal("1000000")
    # English number format: 200,000, 200000, or 200,000.50.
    valid_format = re.fullmatch(
        r"(?:\d{1,3}(?:,\d{3})+|\d+)(?:\.\d+)?",
        cleaned,
    )

    if valid_format is None:
        raise ValueError(
            f"Invalid PDF investment amount: {value!r}"
        )

    amount_usd = Decimal(cleaned.replace(",", ""))

    return amount_usd / Decimal("1000000")
