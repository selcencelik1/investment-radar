from bs4 import BeautifulSoup, Tag

from app.parser.exceptions import InvestmentTableNotFoundError
from app.source_language import (
    KPMG_HTML_HEADER_ALIASES,
    KPMG_REQUIRED_HTML_HEADERS,
    KPMG_STAGE_HTML_HEADERS,
)

REQUIRED_HEADERS = KPMG_REQUIRED_HTML_HEADERS
STAGE_HEADERS = KPMG_STAGE_HTML_HEADERS


def normalize_html_header(value: str) -> str:
    cleaned = " ".join(value.split())

    return KPMG_HTML_HEADER_ALIASES.get(cleaned, cleaned)


def find_investment_table(soup: BeautifulSoup) -> Tag:
    tables = soup.find_all("table")

    for table in tables:
        first_row = table.find("tr")

        if first_row is None:
            continue

        headers = {
            normalize_html_header(cell.get_text(" ", strip=True))
            for cell in first_row.find_all(["th", "td"])
        }

        has_required_headers = REQUIRED_HEADERS.issubset(headers)
        has_stage_header = bool(STAGE_HEADERS.intersection(headers))

        if has_required_headers and has_stage_header:
            return table
    raise InvestmentTableNotFoundError(
        "Investment table not found."
        )


def parse_investment_records(
    html: str
) -> list[dict[str, str]]:
    soup = BeautifulSoup(html, "lxml")
    table = find_investment_table(soup)

    rows = table.find_all("tr")

    if len(rows) < 2:
        raise RuntimeError("No data rows found in the table.")

    headers = [
        normalize_html_header(cell.get_text(" ", strip=True))
        for cell in rows[0].find_all(["th", "td"])
    ]

    investment_records = []

    for row in rows[1:]:
        cells = row.find_all(["th", "td"])

        values = [
            cell.get_text(" ", strip=True)
            for cell in cells
        ]

        if len(values) != len(headers):
            continue

        record = dict(zip(headers, values))
        investment_records.append(record)

    return investment_records
