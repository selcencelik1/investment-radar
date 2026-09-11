from app.source_language import (
    INVESTOR_LABEL_TRANSLATIONS,
    REVIEW_STATUS_TRANSLATIONS,
    SOURCE_VALUE_TRANSLATIONS,
)


REVIEW_STATUS_LABELS = REVIEW_STATUS_TRANSLATIONS


def display_source_value(value):
    if value is None:
        return None

    return SOURCE_VALUE_TRANSLATIONS.get(str(value), value)


def display_investors(value):
    if not isinstance(value, str):
        return value

    displayed_value = value

    for source_label, english_label in INVESTOR_LABEL_TRANSLATIONS.items():
        displayed_value = displayed_value.replace(
            source_label,
            english_label,
        )

    return displayed_value
