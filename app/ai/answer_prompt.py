import json


ANSWER_SYSTEM_PROMPT = """
You are a local research assistant for startup investment records.

Answer the user's question using only the supplied search results.

Rules:
- Do not invent startups, investors, dates, amounts, or sources.
- Do not use outside knowledge.
- Do not provide an investment recommendation, score, ranking,
  approval, or rejection.
- Do not mention a source or report title in the answer.
- Preserve the distinction between separate investment rounds.
- Treat amounts as total reported round amounts, not necessarily
  one investor's contribution.
- If no records were found, clearly say that no matching record
  exists in the available dataset.
- Mention that the dataset may not represent a startup's complete
  investment history when appropriate.
- Answer in Turkish when the user writes in Turkish.
- Answer in English when the user writes in English.
- Keep the answer concise and factual.
- cited_result_numbers must contain only the supplied result numbers.
"""


def build_answer_messages(
        question: str,
        interpreted_query: dict,
        results: list[dict],
        maximum_results: int = 100,
) -> list[dict]:
    if maximum_results < 1:
        raise ValueError(
            "Maximum results must be at least 1."
        )

    visible_results = results[:maximum_results]

    numbered_results = [
        {
            "result_number": index,
            **result,
        }
        for index, result in enumerate(
            visible_results,
            start=1,
        )
    ]

    payload = {
        "user_question": question,
        "interpreted_query": interpreted_query,
        "total_matching_records": len(results),
        "supplied_record_count": len(numbered_results),
        "results_were_truncated": (
            len(results) > len(numbered_results)
        ),
        "search_results": numbered_results,
    }

    return [
        {
            "role": "system",
            "content": ANSWER_SYSTEM_PROMPT.strip(),
        },
        {
            "role": "user",
            "content": json.dumps(
                payload,
                ensure_ascii=False,
                default=str,
            ),
        },
    ]