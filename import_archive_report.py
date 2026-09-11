from app.pipeline.kpmg_pdf_pipeline import process_pdf_report


def main() -> None:
    result = process_pdf_report(
        report_page_url="https://kpmg.com/tr/tr/insights/2026/06/turkiye-startup-yatirimlari-2026.html",
        reporting_period="2026-Q1",
        save=False,
    )

    print(f"PDF: {result['pdf_url']}")
    print(f"Dönem: {result['reporting_period']}")
    print(f"Bulunan kayıt: {result['records_found']}")
    print(f"Yeni kaydedilen: {result['records_saved']}")


if __name__ == "__main__":
    main()
