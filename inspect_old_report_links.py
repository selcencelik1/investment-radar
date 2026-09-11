import json
import time
from pathlib import Path
from urllib.parse import urljoin, urlsplit

import requests
from bs4 import BeautifulSoup

from app.crawler.kpmg_client import fetch_page
from app.crawler.pdf_discovery import discover_pdf_urls


def main() -> None:
    summary_path = (
        Path(__file__).resolve().parent
        / "data"
        / "archive_summary.json"
    )

    summary = json.loads(
        summary_path.read_text(encoding="utf-8")
    )

    failed_reports = [
        report
        for report in summary["reports"]
        if report["status"] == "NEEDS_REVIEW"
    ]

    print(f"İncelenecek başarısız kaynak: {len(failed_reports)}")

    for index, report in enumerate(failed_reports, start=1):
        page_url = report["url"]

        print(f"\n[{index}/{len(failed_reports)}] {page_url}")
        print(f"Önceki hata: {report['detail']}")

        try:
            html = fetch_page(page_url)
            soup = BeautifulSoup(html, "lxml")

            accepted_urls = set(
                discover_pdf_urls(html, page_url)
            )

            all_pdf_urls = set()

            for link in soup.find_all("a", href=True):
                absolute_url = urljoin(
                    page_url,
                    link["href"].strip(),
                )
                parsed = urlsplit(absolute_url)

                if parsed.scheme not in {"http", "https"}:
                    continue

                if not parsed.path.casefold().endswith(".pdf"):
                    continue

                if absolute_url in all_pdf_urls:
                    continue

                all_pdf_urls.add(absolute_url)

                print("\nPDF BAĞLANTISI")
                print(f"Metin: {link.get_text(' ', strip=True)}")
                print(f"Adres: {absolute_url}")
                print(f"Alan adı: {parsed.hostname}")
                print(
                    "Mevcut filtre: "
                    + (
                        "Kabul ediyor"
                        if absolute_url in accepted_urls
                        else "Dışarıda bırakıyor"
                    )
                )

            print(f"\nSayfadaki PDF bağlantısı: {len(all_pdf_urls)}")
            print(f"Filtrenin kabul ettiği: {len(accepted_urls)}")

            for element in soup.find_all(["iframe", "embed", "object"]):
                source = element.get("src") or element.get("data")

                if source:
                    print(
                        f"Gömülü içerik ({element.name}): "
                        f"{urljoin(page_url, source)}"
                    )

        except (requests.RequestException, ValueError) as error:
            print(f"Sayfa incelenemedi: {error}")

        if index < len(failed_reports):
            time.sleep(2)


if __name__ == "__main__":
    main()