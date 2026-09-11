from app.crawler.kpmg_client import fetch_page
from app.crawler.report_discovery import discover_report_urls
from app.pipeline.kpmg_pipeline import process_report


DISCOVERY_URL = "https://kpmg.com/tr/tr/insights.html"
BASE_URL = "https://kpmg.com"


def synchronize_kpmg_reports() -> None:
    print("KPMG report control started.")

    discovery_html = fetch_page(DISCOVERY_URL)

    report_urls = discover_report_urls(
        html=discovery_html,
        base_url=BASE_URL,
    )

    print(f"Discovered report number: {len(report_urls)}")

    for report_url in report_urls:
        try:
            result = process_report(report_url)

            print(
                f"{result.reporting_period}: "
                f"{result.records_found} record found, "
                f"{result.records_saved} new record saved."
            )

        except Exception as error:
            print(f"Record could not be processed: {report_url}")
            print(f"Error: {error}")

    print("KPMG report control is done.")