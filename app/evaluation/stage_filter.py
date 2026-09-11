from enum import Enum

from app.source_language import (
    ELIGIBLE_STAGE_LABELS,
    EXCLUDED_STAGE_LABELS,
)


class StageEligibility(str, Enum):
    ELIGIBLE = "ELIGIBLE"
    NEEDS_REVIEW = "NEEDS_REVIEW"
    NOT_ELIGIBLE = "NOT_ELIGIBLE"


ELIGIBLE_STAGES = {
    "seed",
    "seed stage",
    "series a",
    *ELIGIBLE_STAGE_LABELS,
}

EXCLUDED_STAGES = {
    "acquisition",
    "ipo",
    "late stage",
    "later stage",
    "series b",
    "series c",
    *EXCLUDED_STAGE_LABELS,
}


def evaluate_stage(stage: str | None) -> StageEligibility:
    if stage is None:
        return StageEligibility.NEEDS_REVIEW

    normalized_stage = " ".join(stage.casefold().split())

    if normalized_stage in ELIGIBLE_STAGES:
        return StageEligibility.ELIGIBLE

    if normalized_stage in EXCLUDED_STAGES:
        return StageEligibility.NOT_ELIGIBLE

    return StageEligibility.NEEDS_REVIEW
