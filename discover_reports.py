from app.crawler.kpmg_client import fetch_page
from app.crawler.report_discovery import discover_report_urls
from app.pipeline.kpmg_pipeline import process_report


def main() -> None:
    discovery_url = "https://kpmg.com/tr/tr/insights.html"

    html = fetch_page(discovery_url)

    report_urls = discover_report_urls(
        html=html,
        base_url="https://kpmg.com",
    )

    print(f"Bulunan rapor sayısı: {len(report_urls)}")

    for report_url in report_urls:
        print(f"\nİşleniyor: {report_url}")

        try:
            result = process_report(report_url)
        except Exception as error:
            print(
                f"Rapor işlenemedi: "
                f"{type(error).__name__}: {error}"
            )
            continue

        print(f"Başlık: {result.report_title}")
        print(f"Dönem: {result.reporting_period}")
        print(f"Bulunan yatırım kaydı: {result.records_found}")
        print(f"Yeni kaydedilen kayıt: {result.records_saved}")


if __name__ == "__main__":
    main()