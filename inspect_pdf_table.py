from io import BytesIO

import pdfplumber

from app.crawler.pdf_client import download_pdf


def main():
    pdf_url = (
        "https://assets.kpmg.com/content/dam/kpmgsites/"
        "tr/pdf/2024/05/turkish-startup-investments-q1-2024.pdf"
    )

    pdf_bytes = download_pdf(pdf_url)

    with pdfplumber.open(BytesIO(pdf_bytes)) as pdf:
        page_number = 21
        page = pdf.pages[page_number - 1]

        tables = page.extract_tables()

        print(f"\nİncelenen sayfa: {page_number}")
        print(f"Bulunan tablo sayısı: {len(tables)}")

        for table_number, table in enumerate(tables, start=1):
            print(f"\nTABLO {table_number}")
            print(f"Satır sayısı: {len(table)}")

            for row in table[:5]:
                print(f"Hücre sayısı: {len(row)}")
                print(row)

        if not tables:
            print("\nSAYFA METNİ")
            print((page.extract_text() or "")[:3000])


if __name__ == "__main__":
    main()