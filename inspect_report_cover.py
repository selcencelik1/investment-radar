from io import BytesIO

import pdfplumber

from app.crawler.pdf_client import download_pdf
from app.parser.pdf_period_parser import parse_pdf_period_from_bytes
from app.parser.kpmg_pdf_parser import parse_pdf_deal_records
from app.parser.pdf_record_mapper import map_pdf_record

def main() -> None:
    pdf_url = (
        "https://assets.kpmg.com/content/dam/kpmgsites/"
        "tr/pdf/2023/05/turkish-startup-investments-2022.pdf"
    )

    pdf_bytes = download_pdf(pdf_url)

    with pdfplumber.open(BytesIO(pdf_bytes)) as pdf:
        print(f"Sayfa sayısı: {len(pdf.pages)}")
        print("\nKAPAK")
        print(pdf.pages[0].extract_text() or "Metin çıkarılamadı.")

    try:
        period = parse_pdf_period_from_bytes(pdf_bytes)
        print(f"\nOtomatik belirlenen dönem: {period}")
    except ValueError as error:
        print(f"\nDönem belirlenemedi: {error}")

    raw_records = parse_pdf_deal_records(pdf_bytes)
    records = []

    for raw_record in raw_records:
        try:
            records.append(map_pdf_record(raw_record))
        except ValueError as error:
            print("\nDÖNÜŞTÜRÜLEMEYEN KAYIT")
            print(raw_record)
            print(f"Hata: {error}")
            raise

    print(f"\nÇıkarılan kaynak kaydı: {len(raw_records)}")
    print(f"Modele dönüştürülen kayıt: {len(records)}")

    print("\nİLK 3 KAYIT")

    for record in records[:3]:
        print(record)


if __name__ == "__main__":
    main()