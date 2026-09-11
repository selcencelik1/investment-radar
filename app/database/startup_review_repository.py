from sqlalchemy import select

from app.database.connection import SessionLocal
from app.database.models import StartupReviewEntity
from app.parser.normalizer import normalize_startup_name

REVIEW_STATUSES = (
    "Will be reviewed",
    "Under review",
    "Reviewed",
    "Archived",
)


def save_startup_review(
    startup_name: str,
    status: str,
    note: str,
    source_verified: bool,
    application_year: int | None = None,
) -> None:
    cleaned_startup_name = startup_name.strip()

    if not cleaned_startup_name:
        raise ValueError("Company name cannot be empty.")

    if status not in REVIEW_STATUSES:
        raise ValueError(
            f"Invalid review status: {status}"
        )

    normalized_name = normalize_startup_name(
        cleaned_startup_name
    )

    cleaned_note = note.strip() or None

    with SessionLocal() as session:
        statement = select(StartupReviewEntity).where(
            StartupReviewEntity.normalized_startup_name
            == normalized_name
        )

        if application_year is None:
            statement = statement.where(
                StartupReviewEntity.application_year.is_(None)
            )
        else:
            statement = statement.where(
                StartupReviewEntity.application_year
                == application_year
            )

        existing_review = session.scalar(statement)

        if existing_review is None:
            review = StartupReviewEntity(
                startup_name=cleaned_startup_name,
                normalized_startup_name=normalized_name,
                application_year=application_year,
                status=status,
                note=cleaned_note,
                source_verified=source_verified,
            )

            session.add(review)
        else:
            existing_review.startup_name = cleaned_startup_name
            existing_review.status = status
            existing_review.note = cleaned_note
            existing_review.source_verified = source_verified

        session.commit()


def get_startup_review(
    startup_name: str,
    application_year: int | None = None,
) -> StartupReviewEntity | None:
    normalized_name = normalize_startup_name(startup_name)

    with SessionLocal() as session:
        statement = select(StartupReviewEntity).where(
            StartupReviewEntity.normalized_startup_name
            == normalized_name
        )

        if application_year is None:
            statement = statement.where(
                StartupReviewEntity.application_year.is_(None)
            )
        else:
            statement = statement.where(
                StartupReviewEntity.application_year
                == application_year
            )

        return session.scalar(statement)

def get_all_startup_reviews(
    application_year: int | None = None,
) -> list[StartupReviewEntity]:
    with SessionLocal() as session:
        statement = select(StartupReviewEntity)

        if application_year is not None:
            statement = statement.where(
                StartupReviewEntity.application_year
                == application_year
            )

        statement = statement.order_by(
            StartupReviewEntity.application_year.desc(),
            StartupReviewEntity.updated_at.desc(),
            StartupReviewEntity.startup_name,
        )

        reviews = session.scalars(statement).all()

        return list(reviews)