
import requests

from app.database.pdf_investment_repository import (
    save_pdf_investment_records,
)
from app.parser.kpmg_pdf_parser import parse_pdf_deal_records
from app.parser.pdf_record_mapper import map_pdf_record


PDF_URL = (
    "https://assets.kpmg.com/content/dam/kpmgsites/tr/pdf/"
    "2026/03/turkish-startup-investments-review-q4-2025.pdf"
)


def main() -> None:
    response = requests.get(PDF_URL, timeout=60)
    response.raise_for_status()

    if not response.content.startswith(b"%PDF-"):
        raise RuntimeError("İndirilen içerik PDF değil.")

    raw_records = parse_pdf_deal_records(response.content)

    records = [
        map_pdf_record(record)
        for record in raw_records
    ]

    saved_count = save_pdf_investment_records(
        records=records,
        reporting_period="2025-FY",
        source_url=PDF_URL,
    )

    print(f"PDF'den çıkarılan kayıt: {len(records)}")
    print(f"Yeni kaydedilen kayıt: {saved_count}")


if __name__ == "__main__":
    main()