import json
from pathlib import Path

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

        html = fetch_page(report["url"])
        soup = BeautifulSoup(html, "lxml")
        tables = soup.find_all("table")

        print(f"HTML tablo sayısı: {len(tables)}")

        for index, table in enumerate(tables, start=1):
            rows = table.find_all("tr")

            print(f"\nTABLO {index}")
            print(f"Toplam satır: {len(rows)}")

            for row in rows[:3]:
                cells = [
                    cell.get_text(" ", strip=True)
                    for cell in row.find_all(["th", "td"])
                ]
                print(cells)


if __name__ == "__main__":
    main()