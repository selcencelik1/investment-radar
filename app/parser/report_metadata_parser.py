import re

from bs4 import BeautifulSoup

from app.models.report_metadata import ReportMetadata
from app.source_language import (
    ANNUAL_REPORT_EXPRESSIONS,
    REPORT_QUARTER_PATTERNS,
)


def parse_report_metadata(
    html: str,
    source_url: str | None = None,
) -> ReportMetadata:
    soup = BeautifulSoup(html, "lxml")

    heading = soup.find("h1")
    title_element = heading if heading is not None else soup.title

    if title_element is None:
        raise RuntimeError("Report title not found.")

    title = title_element.get_text(" ", strip=True)
    normalized_title = title.casefold().replace("i\u0307", "i")
    normalized_title = " ".join(normalized_title.split())

    year_match = re.search(r"\b20\d{2}\b", title)

    if year_match is None:
        raise RuntimeError("Report year not found.")

    year = year_match.group()

    quarters = [
        quarter
        for quarter, pattern in REPORT_QUARTER_PATTERNS.items()
        if re.search(pattern, normalized_title)
    ]

    if len(quarters) == 1:
        period = f"{year}-{quarters[0]}"
    elif not quarters and any(
        expression in normalized_title
        for expression in ANNUAL_REPORT_EXPRESSIONS
    ):
        period = f"{year}-FY"
    else:
        raise RuntimeError(
            "The reporting period could not be determined from the title."
        )

    return ReportMetadata(
        title=title,
        reporting_period=period,
    )
