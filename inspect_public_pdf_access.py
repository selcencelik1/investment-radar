import json
import time
from pathlib import Path
from urllib.parse import urljoin, urlsplit, urlunsplit

import requests
from bs4 import BeautifulSoup

from app.crawler.kpmg_client import fetch_page


def main() -> None:
    summary_path = (
        Path(__file__).resolve().parent
        / "data"
        / "archive_summary.json"
    )

    summary = json.loads(
        summary_path.read_text(encoding="utf-8")
    )

    for report in summary["reports"]:
        if report["status"] != "NEEDS_REVIEW":
            continue

        print(f"\nSAYFA: {report['url']}")

        try:
            html = fetch_page(report["url"])
            soup = BeautifulSoup(html, "lxml")
            candidates = set()

            for link in soup.find_all("a", href=True):
                original_url = urljoin(
                    report["url"],
                    link["href"].strip(),
                )
                parsed = urlsplit(original_url)

                if parsed.hostname != "author.kpmg.com":
                    continue

                if not parsed.path.startswith("/content/dam/kpmg/tr/pdf/"):
                    continue

                if not parsed.path.casefold().endswith(".pdf"):
                    continue

                candidate_path = parsed.path.replace(
                    "/content/dam/kpmg/",
                    "/content/dam/kpmgsites/",
                    1,
                )

                candidate = urlunsplit((
                    "https",
                    "assets.kpmg.com",
                    candidate_path,
                    parsed.query,
                    "",
                ))

                candidates.add(candidate)

            if not candidates:
                print("Uygun herkese açık adres adayı üretilemedi.")

            for candidate in sorted(candidates):
                print(f"ADAY: {candidate}")

                with requests.get(
                    candidate,
                    stream=True,
                    timeout=(10, 20),
                    allow_redirects=False,
                ) as response:
                    print(f"HTTP: {response.status_code}")
                    print(
                        "İçerik türü:",
                        response.headers.get("Content-Type"),
                    )

                    if response.is_redirect:
                        print(
                            "Yönlendirme:",
                            response.headers.get("Location"),
                        )

                    elif response.status_code == 200:
                        first_bytes = next(
                            response.iter_content(chunk_size=16),
                            b"",
                        )

                        print(
                            "PDF imzası:",
                            first_bytes.startswith(b"%PDF-"),
                        )

                time.sleep(2)

        except requests.RequestException as error:
            print(f"Erişim kontrolü başarısız: {error}")


if __name__ == "__main__":
    main()