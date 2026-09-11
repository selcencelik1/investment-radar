import csv
from pathlib import Path


SOURCE_FILE = Path("data/sample_applicants.csv")
OUTPUT_FILE = Path("data/demo_applicants.csv")


DEMO_STARTUPS = [
    {
        "applicant_full_name": "Alex Morgan",
        "applicant_email": "alex@aeroflow.example",
        "startup_name": "AeroFlow Labs",
        "sector_nace_code": "Aviation Technology / 6201",
        "startup_stage": "Product market fit with revenue",
        "startup_description": (
            "Airport operations coordination platform"
        ),
        "active_customer_count": "12",
        "mrr_usd": "5000",
        "arr_usd": "60000",
        "previously_funded": "yes",
        "investment_expectation_usd": "500000",
        "website_url": "https://aeroflow.example",
        "desired_thy_partnership": (
            "Airport operations pilot project"
        ),
    },
    {
        "applicant_full_name": "Jamie Taylor",
        "applicant_email": "jamie@gatesense.example",
        "startup_name": "GateSense AI",
        "sector_nace_code": "Artificial Intelligence / 6201",
        "startup_stage": "Prototype / MVP developed",
        "startup_description": (
            "Computer vision platform for airport gate operations"
        ),
        "active_customer_count": "3",
        "mrr_usd": "1800",
        "arr_usd": "21600",
        "previously_funded": "no",
        "investment_expectation_usd": "300000",
        "website_url": "https://gatesense.example",
        "desired_thy_partnership": (
            "Gate turnaround optimization pilot"
        ),
    },
    {
        "applicant_full_name": "Jordan Lee",
        "applicant_email": "jordan@cargomesh.example",
        "startup_name": "CargoMesh",
        "sector_nace_code": "Logistics Technology / 5229",
        "startup_stage": "Growth stage",
        "startup_description": (
            "Digital cargo capacity and routing platform"
        ),
        "active_customer_count": "48",
        "mrr_usd": "32000",
        "arr_usd": "384000",
        "previously_funded": "yes",
        "investment_expectation_usd": "1500000",
        "website_url": "https://cargomesh.example",
        "desired_thy_partnership": (
            "Air cargo capacity integration"
        ),
    },
    {
        "applicant_full_name": "Morgan Reed",
        "applicant_email": "morgan@securewing.example",
        "startup_name": "SecureWing",
        "sector_nace_code": "Cybersecurity / 6202",
        "startup_stage": "Product market fit with revenue",
        "startup_description": (
            "Cybersecurity monitoring for aviation systems"
        ),
        "active_customer_count": "9",
        "mrr_usd": "14000",
        "arr_usd": "168000",
        "previously_funded": "yes",
        "investment_expectation_usd": "900000",
        "website_url": "https://securewing.example",
        "desired_thy_partnership": (
            "Aviation security monitoring pilot"
        ),
    },
    {
        "applicant_full_name": "Casey Brown",
        "applicant_email": "casey@trippilot.example",
        "startup_name": "TripPilot",
        "sector_nace_code": "Travel Technology / 7990",
        "startup_stage": "Product market fit with revenue",
        "startup_description": (
            "B2B travel disruption management platform"
        ),
        "active_customer_count": "21",
        "mrr_usd": "11000",
        "arr_usd": "132000",
        "previously_funded": "no",
        "investment_expectation_usd": "650000",
        "website_url": "https://trippilot.example",
        "desired_thy_partnership": (
            "Passenger disruption communication pilot"
        ),
    },
    {
        "applicant_full_name": "Riley Chen",
        "applicant_email": "riley@runwayops.example",
        "startup_name": "RunwayOps",
        "sector_nace_code": "SaaS / 6201",
        "startup_stage": "Prototype / MVP developed",
        "startup_description": (
            "Maintenance workflow software for airport teams"
        ),
        "active_customer_count": "2",
        "mrr_usd": "900",
        "arr_usd": "10800",
        "previously_funded": "no",
        "investment_expectation_usd": "250000",
        "website_url": "https://runwayops.example",
        "desired_thy_partnership": (
            "Maintenance workflow validation project"
        ),
    },
]


DEMO_COMPANIONS = [
    {
        "applicant_full_name": "Taylor Smith",
        "applicant_email": "taylor@turnaroundcloud.example",
        "startup_name": "TurnaroundCloud",
        "website_url": "https://turnaroundcloud.example",
    },
    {
        "applicant_full_name": "Cameron White",
        "applicant_email": "cameron@visionramp.example",
        "startup_name": "VisionRamp",
        "website_url": "https://visionramp.example",
    },
    {
        "applicant_full_name": "Avery Wilson",
        "applicant_email": "avery@freightlink.example",
        "startup_name": "FreightLink",
        "website_url": "https://freightlink.example",
    },
    {
        "applicant_full_name": "Drew Harris",
        "applicant_email": "drew@aeroshield.example",
        "startup_name": "AeroShield",
        "website_url": "https://aeroshield.example",
    },
    {
        "applicant_full_name": "Parker Davis",
        "applicant_email": "parker@journeydesk.example",
        "startup_name": "JourneyDesk",
        "website_url": "https://journeydesk.example",
    },
    {
        "applicant_full_name": "Quinn Lewis",
        "applicant_email": "quinn@maintaincloud.example",
        "startup_name": "MaintainCloud",
        "website_url": "https://maintaincloud.example",
    },
]


def main() -> None:
    with SOURCE_FILE.open(
        encoding="utf-8",
        newline="",
    ) as source:
        reader = csv.DictReader(source)
        base_row = next(reader)
        fieldnames = reader.fieldnames

    if fieldnames is None:
        raise RuntimeError("The source CSV has no header.")

    expanded_startups = []

    for original, companion in zip(
            DEMO_STARTUPS,
            DEMO_COMPANIONS,
    ):
        expanded_startups.append(original)

        companion_record = original.copy()
        companion_record.update(companion)

        companion_mrr = (
                int(original["mrr_usd"]) + 2500
        )

        companion_record["mrr_usd"] = str(
            companion_mrr
        )
        companion_record["arr_usd"] = str(
            companion_mrr * 12
        )
        companion_record["monthly_revenue_usd"] = str(
            companion_mrr + 3000
        )
        companion_record["annual_revenue_usd"] = str(
            (companion_mrr + 3000) * 12
        )
        companion_record["active_customer_count"] = str(
            int(original["active_customer_count"]) + 5
        )

        expanded_startups.append(companion_record)

    demo_rows = []

    for index, overrides in enumerate(
            expanded_startups,
            start=1,
    ):
        row = base_row.copy()
        row.update(overrides)

        row["application_year"] = "2026"
        row["applicant_phone"] = (
            f"+90 555 000 {index:04d}"
        )
        row["applicant_linkedin_url"] = (
            f"https://linkedin.com/in/demo-applicant-{index}"
        )
        row["product_demo_url"] = (
            row["website_url"] + "/demo"
        )
        row["logo_url"] = (
            row["website_url"] + "/logo.png"
        )
        row["pitch_deck_url"] = (
            row["website_url"] + "/pitch"
        )

        demo_rows.append(row)

    with OUTPUT_FILE.open(
        "w",
        encoding="utf-8",
        newline="",
    ) as output:
        writer = csv.DictWriter(
            output,
            fieldnames=fieldnames,
        )
        writer.writeheader()
        writer.writerows(demo_rows)

    print(
        f"Created {OUTPUT_FILE} with "
        f"{len(demo_rows)} demo applications."
    )


if __name__ == "__main__":
    main()