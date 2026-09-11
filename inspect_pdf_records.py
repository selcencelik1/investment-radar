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
    # Rapor sayfasını indir.
    report_html = fetch_page(REPORT_PAGE_URL)

    # PDF adresini sayfanın bağlantılarından bul.
    pdf_urls = discover_pdf_urls(
        html=report_html,
        page_url=REPORT_PAGE_URL,
    )

    print(f"Bulunan PDF sayısı: {len(pdf_urls)}")

    for pdf_url in pdf_urls:
        print(pdf_url)

    if len(pdf_urls) != 1:
        raise RuntimeError(
            "Tek PDF bulunamadı. Bağlantılar incelenmeli."
        )

    # Bulunan PDF'yi indir.
    response = requests.get(pdf_urls[0], timeout=60)
    response.raise_for_status()

    if not response.content.startswith(b"%PDF-"):
        raise RuntimeError("İndirilen içerik PDF değil.")

    # PDF tablosunu oku.
    raw_records = parse_pdf_deal_records(response.content)

    print(f"\nÇıkarılan işlem kaydı: {len(raw_records)}")

    pages = sorted({
        record["source_page"]
        for record in raw_records
    })

    print(f"İşlenen sayfalar: {pages}")

    # Ham kayıtları uygulama modeline dönüştür.
    records = [
        map_pdf_record(record)
        for record in raw_records
    ]

    print(f"Modele dönüştürülen kayıt: {len(records)}")

    print("\nİLK 3 KAYIT")

    for record in records[:3]:
        print(record)


if __name__ == "__main__":
    main()