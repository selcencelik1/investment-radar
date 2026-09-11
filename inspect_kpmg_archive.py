import json
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit

import requests
from defusedxml import ElementTree

from app.crawler.kpmg_client import fetch_page
from app.crawler.pdf_client import download_pdf
from app.crawler.pdf_discovery import discover_pdf_urls
from app.crawler.report_url_filter import is_investment_report_url
from app.database.pdf_investment_repository import (
    save_pdf_investment_records,
)
from app.parser.pdf_period_parser import parse_pdf_period_from_bytes
from app.parser.report_metadata_parser import parse_report_metadata
from app.pipeline.kpmg_pdf_pipeline import process_pdf_report
from app.pipeline.report_selection import select_reports_for_import


SITEMAP_URLS = [
    "https://kpmg.com/tr/tr/sitemap.xml",
    "https://kpmg.com/tr/en/sitemap.xml",
]


def local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def save_archive_summary(results: list[dict]) -> Path:
    project_directory = Path(__file__).resolve().parent
    output_path = project_directory / "data" / "archive_summary.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    summary = {
        "completed_at": datetime.now(timezone.utc).isoformat(),
        "total": len(results),
        "ready": sum(
            item["status"] == "READY"
            for item in results
        ),
        "needs_review": sum(
            item["status"] == "NEEDS_REVIEW"
            for item in results
        ),
        "out_of_scope": sum(
            item["status"] == "OUT_OF_SCOPE"
            for item in results
        ),
        "reports": results,
    }

    temporary_path = output_path.with_suffix(".json.tmp")

    with temporary_path.open("w", encoding="utf-8") as file:
        json.dump(
            summary,
            file,
            ensure_ascii=False,
            indent=2,
        )

    temporary_path.replace(output_path)

    return output_path


def run_archive_scan(
    start_year: int,
    save: bool = False,
    on_progress=None,
) -> dict:
    current_year = datetime.now().year

    if type(start_year) is not int:
        raise ValueError("Start year must be integer.")

    if not 2000 <= start_year <= current_year:
        raise ValueError(
            f"Start year must be in 2000–{current_year}."
        )

    def notify(message: str) -> None:
        print(message, flush=True)

        if on_progress is not None:
            on_progress(message)

    notify(f"Research started for {start_year} and later years.")

    candidates = set()

    # 1. Site haritalarından rapor adaylarını bul.
    with requests.Session() as session:
        session.headers.update({
            "User-Agent": "InvestmentRadarResearch/0.1",
        })

        for sitemap_url in SITEMAP_URLS:
            notify(f"Scanning sitemap: {sitemap_url}")

            response = session.get(sitemap_url, timeout=30)
            response.raise_for_status()

            root = ElementTree.fromstring(response.content)
            document_type = local_name(root.tag)

            locations = {
                element.text.strip()
                for element in root.iter()
                if local_name(element.tag) == "loc"
                and element.text
                and element.text.strip()
            }

            notify(
                f"XML type: {document_type} — "
                f"URL count: {len(locations)}"
            )

            if document_type == "sitemapindex":
                raise RuntimeError(
                    "Turkey sitemap includes inner maps . "
                    "Current reader is waiting urlset ."
                )

            if document_type != "urlset":
                raise RuntimeError(
                    f"Unexpected XML type: {document_type}"
                )

            for location in locations:
                parsed_url = urlsplit(location)
                path = parsed_url.path.casefold()

                if parsed_url.hostname != "kpmg.com":
                    continue

                if not path.startswith(("/tr/tr/", "/tr/en/")):
                    continue

                searchable_path = (
                    path.replace("-", "").replace("_", "")
                )

                if "startup" in searchable_path:
                    candidates.add(location)

    report_candidates = sorted(
        url
        for url in candidates
        if is_investment_report_url(url)
    )

    notify(f"Total report candidates: {len(report_candidates)}")

    archive_results = []
    parsed_reports = {}

    # 2. Raporların dönemini belirle ve kayıtlarını oku.
    for index, report_url in enumerate(report_candidates, start=1):
        notify(
            f"[{index}/{len(report_candidates)}] "
            f"Processing: {report_url}"
        )

        reporting_period = None

        try:
            report_html = fetch_page(report_url)
            downloaded_pdf = None

            try:
                metadata = parse_report_metadata(
                    report_html,
                    source_url=report_url,
                )
                reporting_period = metadata.reporting_period

            except RuntimeError:
                notify(
                    "The reporting period could not be determined from the title; "
                    "inspecting the PDF"
                )

                pdf_urls = discover_pdf_urls(
                    html=report_html,
                    page_url=report_url,
                )

                if len(pdf_urls) != 1:
                    raise RuntimeError(
                        "Exactly one PDF was expected for period verification, "
                        f"{len(pdf_urls)} were found."
                    )

                pdf_url = pdf_urls[0]
                pdf_bytes = download_pdf(pdf_url)

                reporting_period = parse_pdf_period_from_bytes(
                    pdf_bytes
                )

                downloaded_pdf = (pdf_url, pdf_bytes)

                notify(
                    f"Reporting period detected from PDF: {reporting_period}"
                )

            report_year = int(reporting_period.split("-")[0])

            if report_year < start_year:
                archive_results.append({
                    "url": report_url,
                    "status": "OUT_OF_SCOPE",
                    "period": reporting_period,
                    "count": None,
                    "detail": (
                        f"Because {start_year} is earlier than start year "
                        " investment records didn't process."
                    ),
                })

                notify(f"Out of scope: {reporting_period}")
                continue

            result = process_pdf_report(
                report_page_url=report_url,
                reporting_period=reporting_period,
                save=False,
                downloaded_pdf=downloaded_pdf,
            )

            parsed_reports[report_url] = result

            archive_results.append({
                "url": report_url,
                "status": "READY",
                "period": reporting_period,
                "count": result["records_found"],
                "detail": "",
            })

            notify(
                f"Ready: {reporting_period} — "
                f"{result['records_found']} source record"
            )

        except (
            requests.RequestException,
            RuntimeError,
            ValueError,
            TimeoutError,
        ) as error:
            archive_results.append({
                "url": report_url,
                "status": "NEEDS_REVIEW",
                "period": reporting_period,
                "count": None,
                "detail": f"{type(error).__name__}: {error}",
            })

            notify(f"Needs review: {error}")

        finally:
            if index < len(report_candidates):
                time.sleep(2)

    # Tarama özetini aktarım başlamadan önce sakla.
    summary_path = save_archive_summary(archive_results)
    notify(f"Scan summary saved: {summary_path}")

    # 3. Yıllık rapor varsa o yılın çeyrek raporlarını seçme.
    selected_reports = select_reports_for_import(archive_results)

    notify("REPORTS SELECTED FOR IMPORT")

    for report in selected_reports:
        notify(
            f"- {report['period']} — "
            f"{report['count']} source record"
        )

    notify(f"Selected report count: {len(selected_reports)}")

    # 4. Yalnızca kayıt istenmişse seçilen raporları aktar.
    total_saved = 0

    if save:
        for report in selected_reports:
            parsed = parsed_reports[report["url"]]

            notify(f"Saving: {report['period']}")

            saved_count = save_pdf_investment_records(
                records=parsed["records"],
                reporting_period=report["period"],
                source_url=parsed["pdf_url"],
            )

            total_saved += saved_count

            notify(
                f"{report['period']}: "
                f"{saved_count} new records saved."
            )
    else:
        notify(
            "Research only; no records were written to the database."
        )

    notify(f"Research completed. New records: {total_saved}")

    preview_records = []

    for report in selected_reports:
        parsed = parsed_reports[report["url"]]

        for record in parsed["records"]:
            amount = record.deal_amount_million_usd

            preview_records.append({
                "Startup": record.startup_name,
                "Sector": record.sector,
                "Investor": record.investors,
                "Investment date (source)": (
                    record.announcement_date_text
                ),
                "Period": report["period"],
                "Deal amount (milyon USD)": (
                    float(amount) if amount is not None else None
                ),
                "Investment stage": record.investment_stage,
                "Source": parsed["pdf_url"],
                "Source page": record.source_page,
            })
    return {
        "start_year": start_year,
        "reports": archive_results,
        "selected_reports": selected_reports,
        "records_saved": total_saved,
        "save_enabled": save,
        "preview_records": preview_records,
    }


def main() -> None:
    try:
        start_year = int(
            input("Research start year: ").strip()
        )
    except ValueError:
        print("Year must be an integer.")
        return

    current_year = datetime.now().year

    if not 2000 <= start_year <= current_year:
        print(
            f"Enter a year between 2000 and {current_year}."
        )
        return

    save_answer = input(
        "Import the discovered and selected reports "
        "into the database? (yes/no): "
    ).strip().casefold()

    run_archive_scan(
        start_year=start_year,
        save=save_answer == "yes",
    )


if __name__ == "__main__":
    main()