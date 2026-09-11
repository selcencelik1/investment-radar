from dataclasses import dataclass


@dataclass(frozen=True)
class ReportMetadata:
    title: str
    reporting_period: str