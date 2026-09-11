from io import BytesIO

import pdfplumber


EXPECTED_HEADERS = [
    "Target Company",
    "Sector",
    "Investors",
    "Announcement Date",
    "Financial Investor",
    "Investors' Origin",
    "Stake (%)",
    "Transaction Value ($)",
    "Investment Stage",
]


def clean_cell(value: str | None) -> str:
    if value is None:
        return ""

    return " ".join(value.split())


def remove_empty_columns(
    table: list[list[str | None]],
) -> list[list[str]]:
    if not table:
        return []

    width = len(table[0])

    if any(len(row) != width for row in table):
        raise ValueError("Table rows have inconsistent cell counts.")

    cleaned_table = [
        [clean_cell(cell) for cell in row]
        for row in table
    ]

    kept_columns = [
        column_index
        for column_index in range(width)
        if any(
            row[column_index] != ""
            for row in cleaned_table
        )
    ]

    return [
        [row[column_index] for column_index in kept_columns]
        for row in cleaned_table
    ]


def repair_investor_origin_column(
    table: list[list[str | None]],
) -> list[list[str]]:
    if not table:
        return []

    cleaned = [
        [clean_cell(cell) for cell in row]
        for row in table
    ]

    expected_split_headers = (
        EXPECTED_HEADERS[:6]
        + [""]
        + EXPECTED_HEADERS[6:]
    )

    if cleaned[0] != expected_split_headers:
        return cleaned

    if any(len(row) != 10 for row in cleaned):
        raise ValueError("The split table has inconsistent cell counts.")

    for row_number, row in enumerate(cleaned[1:], start=2):
        if row[6] not in ("", ","):
            raise ValueError(
                f"Row {row_number}: unexpected content in the extra "
                f"column: {row[6]!r}"
            )

    repaired = []

    for row in cleaned:
        repaired_row = row.copy()

        # Preserve the overflow comma in the country cell on the left.
        repaired_row[5] += repaired_row[6]
        del repaired_row[6]

        repaired.append(repaired_row)

    return repaired


def normalize_pdf_headers(table: list) -> list:
    if not table:
        return table

    aliases = {
        "Investor's Origin": "Investors' Origin",
        "Investor": "Investors",
        "Deal Value ($)": "Transaction Value ($)",
    }

    headers = []
    for cell in table[0]:
        header = clean_cell(cell)
        headers.append(aliases.get(header, header))

    return [headers, *table[1:]]


def parse_pdf_deal_records(pdf_bytes: bytes) -> list[dict]:
    records = []

    with pdfplumber.open(BytesIO(pdf_bytes)) as pdf:
        for page_number, page in enumerate(pdf.pages, start=1):
            page_text = page.extract_text() or ""

            # Select detailed deal lists instead of summary tables.
            if "deal list (" not in page_text.casefold():
                continue

            tables = page.extract_tables()
            matching_table_found = False

            for table in tables:
                if not table:
                    continue

                table = normalize_pdf_headers(table)
                table = repair_investor_origin_column(table)
                table = remove_empty_columns(table)
                headers = [
                    clean_cell(cell)
                    for cell in table[0]
                ]

                if headers != EXPECTED_HEADERS:
                    continue

                matching_table_found = True

                for row_number, row in enumerate(table[1:], start=2):
                    values = [
                        clean_cell(cell)
                        for cell in row
                    ]

                    if not any(values):
                        continue

                    if len(values) != len(EXPECTED_HEADERS):
                        raise ValueError(
                            f"Page {page_number}, row {row_number}: "
                            f"expected 9 cells, found {len(values)}."
                        )

                    if not values[0]:
                        raise ValueError(
                            f"Page {page_number}, row {row_number}: "
                            "company name is empty."
                        )

                    record = dict(zip(EXPECTED_HEADERS, values))

                    record["source_page"] = page_number
                    record["source_row"] = row_number

                    records.append(record)

            if not matching_table_found:
                raise ValueError(
                    f"Page {page_number}: a Deal List was found, but no "
                    "table matched the expected structure."
                )

    if not records:
        raise ValueError("No deal records found in the PDF.")

    return records
