import requests

from app.crawler.kpmg_client import fetch_page
from app.crawler.pdf_discovery import discover_pdf_urls
from app.database.pdf_investment_repository import (
    save_pdf_investment_records,
)
from app.parser.kpmg_pdf_parser import parse_pdf_deal_records
from app.parser.pdf_record_mapper import map_pdf_record
from app.crawler.pdf_client import download_pdf

def process_pdf_report(
    report_page_url: str,
    reporting_period: str,
    save: bool = False,
    downloaded_pdf: tuple[str, bytes] | None = None,
) -> dict:
    if downloaded_pdf is not None:
        pdf_url, pdf_bytes = downloaded_pdf
    else:
        html = fetch_page(report_page_url)

        pdf_urls = discover_pdf_urls(
            html=html,
            page_url=report_page_url,
        )

        if len(pdf_urls) != 1:
            raise RuntimeError(
                f"Single PDF expected, "
                f"{len(pdf_urls)} found: {pdf_urls}"
            )

        pdf_url = pdf_urls[0]
        pdf_bytes = download_pdf(pdf_url)
    print("PDF downloaded, table dissolving started.", flush=True)

    raw_records = parse_pdf_deal_records(pdf_bytes)
    records = [
        map_pdf_record(record)
        for record in raw_records
    ]

    saved_count = 0

    if save:
        saved_count = save_pdf_investment_records(
            records=records,
            reporting_period=reporting_period,
            source_url=pdf_url,
        )

    return {
        "report_page_url": report_page_url,
        "pdf_url": pdf_url,
        "reporting_period": reporting_period,
        "records_found": len(records),
        "records_saved": saved_count,
        "save_enabled": save,
        "records": records,
    }