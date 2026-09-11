from app.matching.fuzzy_matcher import suggest_similar_applicants


def test_suggests_name_with_typo():
    suggestions = suggest_similar_applicants(
        investment_name="Demo Robotics",
        applicant_names=["Demo Robotic", "Completely Different"],
    )

    assert len(suggestions) == 1
    assert suggestions[0].applicant_name == "Demo Robotic"
    assert suggestions[0].similarity_score >= 75


def test_returns_empty_list_for_unrelated_names():
    suggestions = suggest_similar_applicants(
        investment_name="AAAA",
        applicant_names=["ZZZZ"],
    )

    assert suggestions == []


def test_limits_suggestion_count():
    suggestions = suggest_similar_applicants(
        investment_name="Demo Robotics",
        applicant_names=[
            "Demo Robotic",
            "Demo Robotics",
            "Demo Robotics AI",
        ],
        threshold=0,
        limit=2,
    )

    assert len(suggestions) == 2

    assert (
        suggestions[0].similarity_score
        >= suggestions[1].similarity_score
    )


def test_handles_empty_applicant_list():
    suggestions = suggest_similar_applicants(
        investment_name="Demo Robotics",
        applicant_names=[],
    )

    assert suggestions == []