from app.parser.normalizer import normalize_startup_name


def compare_startup_names(
    investment_names: list[str],
    applicant_names: list[str],
) -> dict[str, list[str]]:
    normalized_applicants = {
        normalize_startup_name(name)
        for name in applicant_names
        if name.strip()
    }

    matched = []
    unmatched = []

    for investment_name in sorted(set(investment_names)):
        normalized_name = normalize_startup_name(investment_name)

        if not normalized_name:
            continue

        if normalized_name in normalized_applicants:
            matched.append(investment_name)
        else:
            unmatched.append(investment_name)

    return {
        "matched": matched,
        "unmatched": unmatched,
    }