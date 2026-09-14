import json

from app.ai.answer_generator import (
    generate_research_answer,
)
from app.ai.ollama_client import LocalAIError
from app.ai.research_assistant import (
    research_investment_question,
)


def main() -> None:
    question = input("Ask an investment question: ").strip()

    try:
        research = research_investment_question(
            question=question,
        )

        print("\nINTERPRETED QUERY")

        print(
            json.dumps(
                research["query"],
                ensure_ascii=False,
                indent=2,
            )
        )

        if research["clarification_question"]:
            print("\nCLARIFICATION REQUIRED")
            print(research["clarification_question"])
            return

        answer = generate_research_answer(
            question=question,
            interpreted_query=research["query"],
            results=research["results"],
        )

    except (ValueError, LocalAIError) as error:
        print(f"Research could not be completed: {error}")
        return

    print("\nLOCAL AI ANSWER")
    print(answer["answer"])


    print("\nMATCHING RECORDS")
    print(f"Result count: {len(research['results'])}")

    cited_numbers = set(
        answer["cited_result_numbers"]
    )

    for index, result in enumerate(
            research["results"],
            start=1,
    ):
        citation_marker = (
            "*"
            if index in cited_numbers
            else "-"
        )

        print(
            f"{citation_marker} [{index}] "
            f"{result['startup_name']} | "
            f"{result['sector']} | "
            f"{result['year']} | "
            f"{result['amount_million_usd']} million USD | "
            f"{result['investors']}"
        )

    print("\nLIMITATIONS")
    print(
        "- The answer uses only the records available in "
        "the local database."
    )
    print(
        "- The available records may not represent a startup's "
        "complete investment history."
    )
    print(
        "- A reported deal amount represents the total round amount, "
        "not necessarily one investor's contribution."
    )
    if answer["follow_up_suggestions"]:
        print("\nFOLLOW-UP SUGGESTIONS")

        for suggestion in answer["follow_up_suggestions"]:
            print(f"- {suggestion}")


if __name__ == "__main__":
    main()