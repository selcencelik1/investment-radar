from app.database.investment_repository import get_all_investment_records
from app.matching.duplicate_matcher import find_pdf_duplicate_candidates


def main() -> None:
    records = get_all_investment_records()

    html_records = [
        record
        for record in records
        if record.ranking is not None
        and record.source_page is None
    ]

    pdf_records = [
        record
        for record in records
        if record.source_page is not None
    ]

    single_match_count = 0

    for html_record in html_records:
        candidates = find_pdf_duplicate_candidates(
            html_record,
            pdf_records,
        )

        print(f"\n{html_record.startup_name} — HTML ID={html_record.id}")

        if not candidates:
            print("Eşleşme bulunamadı; ayrı kalacak.")
            continue

        if len(candidates) > 1:
            print(
                f"{len(candidates)} aday bulundu; "
                "otomatik birleştirilmeyecek."
            )
        else:
            single_match_count += 1
            print("Tek eşleşme adayı bulundu.")

        for candidate in candidates:
            print(
                f"  PDF ID={candidate.id} | "
                f"{candidate.announcement_date_text} | "
                f"{candidate.deal_amount_million_usd} milyon USD"
            )
            print(
                f"  Kaynak aşamaları: "
                f"{html_record.investment_stage!r} / "
                f"{candidate.investment_stage!r}"
            )

    print(f"\nTek adayla eşleşen HTML kaydı: {single_match_count}")
    print("Hiçbir kayıt değiştirilmedi veya silinmedi.")


if __name__ == "__main__":
    main()