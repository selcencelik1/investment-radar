from dataclasses import dataclass

from app.crawler.kpmg_client import fetch_page
from app.database.investment_repository import save_investment_records
from app.parser.kpmg_parser import parse_investment_records
from app.parser.record_mapper import map_to_investment_record
from app.parser.report_metadata_parser import parse_report_metadata


@dataclass(frozen=True)
class ProcessingResult:
    report_title: str
    reporting_period: str
    source_url: str
    records_found: int
    records_saved: int


def process_report(report_url: str) -> ProcessingResult:
    html = fetch_page(report_url)

    metadata = parse_report_metadata(
        html,
        source_url=report_url,
    )
    raw_records = parse_investment_records(html)

    records = [
        map_to_investment_record(raw_record)
        for raw_record in raw_records
    ]

    saved_count = save_investment_records(
        records=records,
        reporting_period=metadata.reporting_period,
        source_url=report_url,
    )

    return ProcessingResult(
        report_title=metadata.title,
        reporting_period=metadata.reporting_period,
        source_url=report_url,
        records_found=len(records),
        records_saved=saved_count,
    )