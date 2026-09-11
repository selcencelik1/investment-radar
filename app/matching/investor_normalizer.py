import unicodedata

from app.source_language import (
    MISSING_INVESTOR_VALUES,
    SOURCE_DIACRITIC_TRANSLATION,
    UNKNOWN_INVESTOR_LABELS,
)

MISSING_VALUES = MISSING_INVESTOR_VALUES


def normalize_investor_name(value: str) -> str:
    normalized = unicodedata.normalize("NFC", value)
    normalized = normalized.casefold().replace("i\u0307", "i")

    # Normalize circumflex variants found in localized source names.
    normalized = normalized.translate(SOURCE_DIACRITIC_TRANSLATION)

    return " ".join(normalized.split())


def normalize_investor_list(value: str | None) -> tuple[str, ...]:
    normalized = normalize_investor_name(value or "")

    if normalized in MISSING_VALUES:
        return ()

    names = set()

    for part in normalized.split(","):
        name = part.strip()

        if not name:
            continue

        if name in UNKNOWN_INVESTOR_LABELS:
            name = "__undisclosed_investor__"

        names.add(name)

    return tuple(sorted(names))


def has_named_investor(investors: tuple[str, ...]) -> bool:
    return any(
        name != "__undisclosed_investor__"
        and name not in MISSING_VALUES
        for name in investors
    )
