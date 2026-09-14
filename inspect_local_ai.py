import json
from pathlib import Path

from app.ai.ollama_client import (
    LocalAIError,
    generate_review_brief,
)
from app.ai.review_context import (
    build_investment_history,
    build_review_context,
)
from app.ai.review_prompt import build_review_messages
from app.importers.applicant_importer import (
    load_applicants_from_csv,
)


SAMPLE_CSV_PATH = Path("data/sample_applicants.csv")


def main() -> None:
    applicants = load_applicants_from_csv(
        SAMPLE_CSV_PATH
    )

    if not applicants:
        raise RuntimeError(
            "The sample CSV does not contain an applicant."
        )

    applicant = applicants[0]

    applicant_context = build_review_context(applicant)
    investment_history = build_investment_history([])

    messages = build_review_messages(
        applicant_context=applicant_context,
        investment_history=investment_history,
    )

    print("LOCAL AI REVIEW TEST")
    print(f"Startup: {applicant.startup_name}")
    print("Personal applicant information: excluded")
    print("Model: qwen3.5:4b")
    print("\nGenerating review brief...\n")

    try:
        review_brief = generate_review_brief(messages)

    except LocalAIError as error:
        print(f"Local AI error: {error}")
        return

    print(
        json.dumps(
            review_brief,
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()