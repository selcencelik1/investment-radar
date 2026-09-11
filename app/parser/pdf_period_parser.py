import re
from io import BytesIO

import pdfplumber


def parse_pdf_period(cover_text: str, foreword_text: str) -> str:
    cover = " ".join(cover_text.casefold().split())
    foreword = " ".join(foreword_text.casefold().split())

    years = set(re.findall(r"\b20\d{2}\b", cover))

    if len(years) != 1:
        raise ValueError(
            "A single year could not be determined from the PDF cover."
        )

    year = next(iter(years))

    quarters = set(re.findall(r"\bq([1-4])\b", cover))

    annual_pattern = (
        r"\bannual\s+edition\s+of\s+(?:the\s+)?"
        r"turkish\s+startup\s+investments\s+review\b"
    )
    annual_evidence = re.search(annual_pattern, foreword) is not None

    if len(quarters) > 1:
        raise ValueError("Multiple quarters were found on the PDF cover.")

    if quarters:
        if annual_evidence:
            raise ValueError(
                "The PDF contains conflicting annual and quarterly "
                "period evidence."
            )

        quarter = next(iter(quarters))
        return f"{year}-Q{quarter}"

    if annual_evidence:
        return f"{year}-FY"

    raise ValueError(
        "The reporting period could not be determined from the PDF text."
    )


def parse_pdf_period_from_bytes(pdf_bytes: bytes) -> str:
    with pdfplumber.open(BytesIO(pdf_bytes)) as pdf:
        if not pdf.pages:
            raise ValueError("No pages were found in the PDF.")

        cover_text = pdf.pages[0].extract_text() or ""
        foreword_text = ""

        for page in pdf.pages[1:5]:
            text = page.extract_text() or ""

            if "foreword" in text.casefold():
                foreword_text = text
                break

    return parse_pdf_period(
        cover_text=cover_text,
        foreword_text=foreword_text,
    )
