from app.database.applicant_repository import get_applicant_names
from app.database.investment_repository import (
    get_all_investment_records,
)
from app.evaluation.stage_filter import (
    StageEligibility,
    evaluate_stage,
)
from app.matching.fuzzy_matcher import suggest_similar_applicants
from app.parser.normalizer import normalize_startup_name


STAGE_LABELS = {
    StageEligibility.ELIGIBLE: "Aşama kriterine uygun",
    StageEligibility.NEEDS_REVIEW: "Aşama doğrulanmalı",
    StageEligibility.NOT_ELIGIBLE: "Aşama kriteri dışında",
}


def main() -> None:
    investments = get_all_investment_records()
    applicant_names = get_applicant_names()

    normalized_applicant_names = {
        normalize_startup_name(name)
        for name in applicant_names
        if name.strip()
    }

    for investment in investments:
        print(f"\nGirişim: {investment.startup_name}")
        print(f"Sektör: {investment.sector}")
        print(f"Rapor dönemi: {investment.reporting_period}")

        amount = investment.deal_amount_million_usd

        if amount is None:
            print("İşlem değeri: Açıklanmadı")
        else:
            print(f"İşlem değeri: {amount} milyon USD")

        stage_result = evaluate_stage(
            investment.investment_stage
        )

        print(f"Kaynak aşama: {investment.investment_stage}")
        print(f"Aşama değerlendirmesi: {STAGE_LABELS[stage_result]}")

        normalized_name = normalize_startup_name(
            investment.startup_name
        )

        if normalized_name in normalized_applicant_names:
            print("Başvuru durumu: Normalize edilmiş isim eşleşti")
        else:
            suggestions = suggest_similar_applicants(
                investment_name=investment.startup_name,
                applicant_names=applicant_names,
            )

            if suggestions:
                print("Başvuru durumu: Benzer isim var, kontrol gerekli")

                for suggestion in suggestions:
                    print(
                        f"  - {suggestion.applicant_name}: "
                        f"{suggestion.similarity_score:.1f}/100"
                    )
            else:
                print("Başvuru durumu: İsim eşleşmesi bulunamadı")

        print(f"Kaynak: {investment.source_url}")


if __name__ == "__main__":
    main()