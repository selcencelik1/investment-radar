from dataclasses import dataclass

from rapidfuzz import fuzz

from app.parser.normalizer import normalize_startup_name


@dataclass(frozen=True)
class MatchSuggestion:
    investment_name: str
    applicant_name: str
    similarity_score: float


def suggest_similar_applicants(
    investment_name: str,
    applicant_names: list[str],
    threshold: float = 75.0,
    limit: int = 3,
) -> list[MatchSuggestion]:
    normalized_investment = normalize_startup_name(investment_name)

    if not normalized_investment:
        return []

    suggestions = []

    for applicant_name in sorted(set(applicant_names)):
        normalized_applicant = normalize_startup_name(applicant_name)

        if not normalized_applicant:
            continue

        score = fuzz.ratio(
            normalized_investment,
            normalized_applicant,
        )

        if score >= threshold:
            suggestions.append(
                MatchSuggestion(
                    investment_name=investment_name,
                    applicant_name=applicant_name,
                    similarity_score=score,
                )
            )

    suggestions.sort(
        key=lambda suggestion: suggestion.similarity_score,
        reverse=True,
    )

    return suggestions[:limit]