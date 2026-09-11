from collections import Counter
from dataclasses import dataclass

from app.matching.duplicate_matcher import find_pdf_duplicate_candidates
from app.matching.pdf_duplicate_grouper import group_pdf_records


@dataclass
class InvestmentGroup:
    primary: object
    members: list
    match_status: str


def group_investment_records(records: list) -> list[InvestmentGroup]:
    pdf_records = [
        record
        for record in records
        if record.source_page is not None
    ]

    pdf_groups = group_pdf_records(pdf_records)

    pdf_id_to_group = {
        record.id: group_index
        for group_index, members in enumerate(pdf_groups)
        for record in members
    }

    proposals = {}

    for record in records:
        if record.ranking is None or record.source_page is not None:
            continue

        candidates = find_pdf_duplicate_candidates(record, pdf_records)

        proposals[record.id] = {
            pdf_id_to_group[candidate.id]
            for candidate in candidates
        }

    target_counts = Counter(
        group_index
        for candidate_groups in proposals.values()
        for group_index in candidate_groups
    )

    attachments = {}
    attached_html_ids = set()

    for html_id, candidate_groups in proposals.items():
        if len(candidate_groups) != 1:
            continue

        group_index = next(iter(candidate_groups))

        if target_counts[group_index] != 1:
            continue

        attachments[group_index] = html_id
        attached_html_ids.add(html_id)

    records_by_id = {record.id: record for record in records}
    groups = []

    for group_index, pdf_members in enumerate(pdf_groups):
        # Gösterim tercihi: yıllık rapor, ardından kayıt ID'si.
        primary = min(
            pdf_members,
            key=lambda record: (
                not record.reporting_period.endswith("-FY"),
                record.id,
            ),
        )

        members = sorted(pdf_members, key=lambda record: record.id)

        if group_index in attachments:
            members.append(
                records_by_id[attachments[group_index]]
            )

        groups.append(
            InvestmentGroup(
                primary=primary,
                members=members,
                match_status=(
                    "Grouped by rule"
                    if len(members) > 1
                    else "One source record"
                ),
            )
        )

    for record in records:
        if record.source_page is not None:
            continue

        if record.id in attached_html_ids:
            continue

        groups.append(
            InvestmentGroup(
                primary=record,
                members=[record],
                match_status=(
                    "Uncertain match — kept separate"
                    if proposals.get(record.id)
                    else "Single source record"
                ),
            )
        )

    return sorted(
        groups,
        key=lambda group: (
            group.primary.startup_name.casefold(),
            group.primary.id,
        ),
    )