import requests

from app.crawler.kpmg_client import fetch_page
from app.crawler.pdf_discovery import discover_pdf_urls
from app.parser.kpmg_pdf_parser import parse_pdf_deal_records
from app.parser.pdf_record_mapper import map_pdf_record


REPORT_PAGE_URL = (
    "https://kpmg.com/tr/tr/insights/2025/02/"
    "kpmg_turkiye_startup_yatirimlari_2024.html"
)


def main() -> None:
    # Download the report page.
    report_html = fetch_page(REPORT_PAGE_URL)

    # Discover the PDF URL from the links on the report page.
    pdf_urls = discover_pdf_urls(
        html=report_html,
        page_url=REPORT_PAGE_URL,
    )

    print(f"PDF files found: {len(pdf_urls)}")

    for pdf_url in pdf_urls:
        print(f"PDF URL: {pdf_url}")

    if len(pdf_urls) != 1:
        raise RuntimeError(
            "Exactly one PDF was expected."
            "The discovered links must be reviewed."
        )

    # Download the discovered PDF.
    response = requests.get(pdf_urls[0], timeout=60)
    response.raise_for_status()

    if not response.content.startswith(b"%PDF-"):
        raise RuntimeError("The downloaded content is not a valid PDF.")

    # Extract raw investment records from the PDF tables.
    raw_records = parse_pdf_deal_records(response.content)

    print(f"\nInvestment records extracted: {len(raw_records)}")

    pages = sorted({
        record["source_page"]
        for record in raw_records
    })

    print(f"Pages processed: {pages}")

    # Convert raw records into application models.
    records = [
        map_pdf_record(record)
        for record in raw_records
    ]

    print(
        f"Records converted into application models: "
        f"{len(records)}"
    )

    print("\nFIRST 3 RECORDS")

    for record in records[:3]:
        print(record)


if __name__ == "__main__":
    main()