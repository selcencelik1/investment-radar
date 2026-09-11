from app.matching.exact_matcher import compare_startup_names


def test_matches_names_after_normalization():
    result = compare_startup_names(
        investment_names=["Demo Robotics"],
        applicant_names=["DEMO ROBOTICS A.Ş."],
    )

    assert result["matched"] == ["Demo Robotics"]
    assert result["unmatched"] == []


def test_separates_unmatched_startups():
    result = compare_startup_names(
        investment_names=["Demo Robotics", "Example AI"],
        applicant_names=["Demo Robotics"],
    )

    assert result["matched"] == ["Demo Robotics"]
    assert result["unmatched"] == ["Example AI"]


def test_does_not_repeat_the_same_investment_name():
    result = compare_startup_names(
        investment_names=["Demo Robotics", "Demo Robotics"],
        applicant_names=["Demo Robotics"],
    )

    assert result["matched"] == ["Demo Robotics"]


def test_handles_empty_applicant_list():
    result = compare_startup_names(
        investment_names=["Example AI"],
        applicant_names=[],
    )

    assert result["matched"] == []
    assert result["unmatched"] == ["Example AI"]