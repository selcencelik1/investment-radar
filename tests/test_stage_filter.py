import pytest

from app.evaluation.stage_filter import (
    StageEligibility,
    evaluate_stage,
)


@pytest.mark.parametrize(
    "stage",
    ["Tohum Aşaması", "Seed", "Seri A", "Series A"],
)
def test_accepts_eligible_stages(stage):
    assert evaluate_stage(stage) == StageEligibility.ELIGIBLE


@pytest.mark.parametrize(
    "stage",
    ["Satın Alım", "Halka Arz", "Series B", "Geç Aşama"],
)
def test_excludes_out_of_scope_stages(stage):
    assert evaluate_stage(stage) == StageEligibility.NOT_ELIGIBLE


@pytest.mark.parametrize(
    "stage",
    ["Erken Aşama", "Açıklanmadı", "", None],
)
def test_marks_uncertain_stages_for_review(stage):
    assert evaluate_stage(stage) == StageEligibility.NEEDS_REVIEW


def test_handles_uppercase_and_extra_spaces():
    assert (
        evaluate_stage("  SEED  ")
        == StageEligibility.ELIGIBLE
    )

def test_accepts_pdf_seed_stage():
    assert (
        evaluate_stage("Seed Stage")
        == StageEligibility.ELIGIBLE
    )


def test_requires_review_for_pdf_early_stage():
    assert (
        evaluate_stage("Early Stage")
        == StageEligibility.NEEDS_REVIEW
    )


def test_excludes_pdf_acquisition():
    assert (
        evaluate_stage("Acquisition")
        == StageEligibility.NOT_ELIGIBLE
    )