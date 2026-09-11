import re
from urllib.parse import unquote, urlsplit


def is_investment_report_url(url: str) -> bool:
    parsed = urlsplit(url)

    if parsed.scheme not in {"http", "https"}:
        return False

    if parsed.hostname != "kpmg.com":
        return False

    path = unquote(parsed.path).casefold()

    if not path.startswith(("/tr/tr/", "/tr/en/")):
        return False


    normalized_path = re.sub(r"[-_]+", " ", path)

    report_phrases = (
        "turkiye startup yatirimlari",
        "turkish startup investments",
    )

    return any(
        phrase in normalized_path
        for phrase in report_phrases
    )