from app.database.applicant_repository import get_applicant_names
from app.database.investment_repository import (
    get_investment_startup_names,
)
from app.matching.exact_matcher import compare_startup_names
from app.matching.fuzzy_matcher import suggest_similar_applicants

def main() -> None:
    investment_names = get_investment_startup_names()
    applicant_names = get_applicant_names()

    result = compare_startup_names(
        investment_names=investment_names,
        applicant_names=applicant_names,
    )

    print(f"Yatırım kayıtlarındaki farklı isim sayısı: {len(investment_names)}")
    print(f"Başvuru listesindeki farklı isim sayısı: {len(applicant_names)}")

    print("\nKESİN İSİM EŞLEŞMELERİ")

    for name in result["matched"]:
        print(f"- {name}")

    print(f"Toplam: {len(result['matched'])}")

    print("\nKESİN EŞLEŞME BULUNAMAYAN GİRİŞİMLER")

    for name in result["unmatched"]:
        print(f"\n- {name}")

        suggestions = suggest_similar_applicants(
            investment_name=name,
            applicant_names=applicant_names,
            threshold=75,
            limit=3,
        )

        if suggestions:
            print("  Kontrol edilmesi gereken benzer başvurular:")

            for suggestion in suggestions:
                print(
                    f"  → {suggestion.applicant_name} "
                    f"(benzerlik puanı: "
                    f"{suggestion.similarity_score:.1f}/100)"
                )
        else:
            print("  Belirlenen eşik üzerinde benzer başvuru bulunamadı.")

    print(f"\nToplam: {len(result['unmatched'])}")

if __name__ == "__main__":
    main()