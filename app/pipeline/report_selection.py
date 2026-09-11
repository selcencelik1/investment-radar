import re


def select_reports_for_import(reports: list[dict]) -> list[dict]:
    reports_by_year = {}

    for report in reports:
        if report["status"] != "READY":
            continue

        period = report.get("period")

        if not isinstance(period, str):
            raise ValueError("A ready report is missing its reporting period.")

        match = re.fullmatch(r"(20\d{2})-(FY|Q[1-4])", period)

        if match is None:
            raise ValueError(f"Invalid report period: {period!r}")

        year = int(match.group(1))
        reports_by_year.setdefault(year, []).append(report)

    selected = []

    for year in sorted(reports_by_year):
        year_reports = reports_by_year[year]

        annual_reports = [
            report
            for report in year_reports
            if report["period"].endswith("-FY")
        ]

        candidates = annual_reports if annual_reports else year_reports


        periods = [report["period"] for report in candidates]

        if len(periods) != len(set(periods)):
            raise ValueError(
                f"{year}: Multiple ready reports exist for the same period."
            )

        selected.extend(
            sorted(candidates, key=lambda report: report["period"])
        )

    return selected
