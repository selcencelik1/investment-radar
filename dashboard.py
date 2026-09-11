import pandas as pd
import streamlit as st

from app.database.applicant_repository import (
    get_all_applicant_details,
    get_applicant_details,
    get_applicant_names,
    get_application_years,
    save_applicants,
)
from urllib.parse import urlsplit

from app.database.investment_repository import (
    get_all_investment_records,
)
from app.matching.investment_grouper import group_investment_records
from app.matching.fuzzy_matcher import suggest_similar_applicants
from app.parser.normalizer import normalize_startup_name
import json
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo
from inspect_kpmg_archive import run_archive_scan
from app.evaluation.investor_view import (
    classify_investor,
    split_investor_names,
)
from app.matching.investor_normalizer import normalize_investor_name
from app.importers.applicant_importer import (
    load_applicants_from_csv,
)
from app.evaluation.stage_filter import (
    StageEligibility,
    evaluate_stage,
)
from app.database.startup_review_repository import (
    REVIEW_STATUSES,
    get_all_startup_reviews,
    get_startup_review,
    save_startup_review,
)
from app.presentation_labels import (
    REVIEW_STATUS_LABELS,
    display_investors,
    display_source_value,
)
from app.evaluation.investor_view import UNKNOWN_INVESTORS
from app.evaluation.application_quality import (
    get_application_quality_issues,
)


def build_dataframe(
    application_year: int | None = None,
) -> pd.DataFrame:
    investments = get_all_investment_records()
    applicant_names = get_applicant_names(application_year)

    normalized_applicants = {
        normalize_startup_name(name)
        for name in applicant_names
        if name.strip()
    }

    rows = []

    groups = group_investment_records(investments)

    for group in groups:
        investment = group.primary
        normalized_name = normalize_startup_name(
            investment.startup_name
        )

        if normalized_name in normalized_applicants:
            application_status = ("Name matched")
            similar_names = ""
        else:
            suggestions = suggest_similar_applicants(
                investment_name=investment.startup_name,
                applicant_names=applicant_names,
            )

            if suggestions:
                application_status = "There is a similar name"
                similar_names = "; ".join(
                    f"{item.applicant_name} "
                    f"({item.similarity_score:.1f}/100)"
                    for item in suggestions
                )
            else:
                application_status = "No match found"
                similar_names = ""

        amount = investment.deal_amount_million_usd

        other_sources = [
            member
            for member in group.members
            if member.id != investment.id
        ]

        additional_source = (
            other_sources[0].source_url
            if other_sources
            else None
        )

        source_stages = " | ".join(
            f"{member.reporting_period}: "
            f"{display_source_value(member.investment_stage)}"
            for member in group.members
        )
        source_details = [
            {
                "Investment group": investment.id,
                "Startup name": member.startup_name,
                "Source record ID": member.id,
                "Reporting period": member.reporting_period,
                "Investment date": member.announcement_date_text,
                "Investor": display_investors(member.investors),
                "Amount (million USD)": (
                    str(member.deal_amount_million_usd)
                    if member.deal_amount_million_usd is not None
                    else None
                ),
                "Investment Stage": display_source_value(
                    member.investment_stage
                ),
                "Share Percentage": display_source_value(
                    member.share_percentage
                ),
                "Source Page": member.source_page,
                "Source Row": member.source_row,
                "Source URL": member.source_url,
                "Raw Amount": member.raw_amount_text,
                "Amount warning": display_source_value(
                    member.amount_warning
                ),

            }
            for member in group.members
        ]

        rows.append({
            "Startup": investment.startup_name,
            "Sector": display_source_value(investment.sector),
            "Reporting Period": investment.reporting_period,
            "Amount (million USD)": (
                float(amount) if amount is not None else None
            ),
            "Additional Source": additional_source,
            "Source Count": len(group.members),
            "Grouping": display_source_value(group.match_status),
            "Source Stages": source_stages,
            "Source Stage": display_source_value(
                investment.investment_stage
            ),
            "Investors": display_investors(investment.investors),
            "Investment Date": investment.announcement_date_text,
            "Applicant Match": application_status,
            "Similar Applicants": similar_names,
            "Source": investment.source_url,
            "Source Details": json.dumps(
                source_details,
                ensure_ascii=False,
            ),
            "Raw Amount": investment.raw_amount_text,
            "Amount Warning": display_source_value(
                investment.amount_warning
            ),

        })

    return pd.DataFrame(rows)

def build_applicant_comparison_dataframe(
    application_year: int | None,
    investment_data: pd.DataFrame,
) -> pd.DataFrame:
    applicants = get_all_applicant_details(application_year)
    reviews = get_all_startup_reviews(application_year)

    reviews_by_name = {
        (
            review.normalized_startup_name,
            review.application_year,
        ): review
        for review in reviews
    }
    investment_company_keys = (
        investment_data["Startup"]
        .fillna("")
        .map(normalize_startup_name)
    )

    rows = []

    for applicant in applicants:
        profile = applicant.startup_profile
        team = applicant.team_profile
        financial = applicant.financial_profile
        collaboration = applicant.collaboration_profile

        review = reviews_by_name.get(
            (
                applicant.normalized_name,
                applicant.application_year,
            )
        )
        investment_history = investment_data[
            investment_company_keys.eq(
                applicant.normalized_name
            )
        ].copy()

        disclosed_amounts = pd.to_numeric(
            investment_history["Amount (million USD)"],
            errors="coerce",
        )

        disclosed_total = disclosed_amounts.sum(
            min_count=1
        )

        investors_found = sorted({
            str(value).strip()
            for value in investment_history["Investors"].dropna()
            if str(value).strip()
        })

        parsed_investment_dates = pd.to_datetime(
            investment_history["Investment Date"],
            errors="coerce",
            format="mixed",
        )

        if parsed_investment_dates.notna().any():
            latest_index = parsed_investment_dates.idxmax()
            latest_investment_date = investment_history.loc[
                latest_index,
                "Investment Date",
            ]
        else:
            latest_investment_date = None

        source_investment_count = len(investment_history)

        if (
            profile is None
            or financial is None
            or collaboration is None
        ):
            quality_issues = [
                "Detailed application data is missing"
            ]
        else:
            quality_issues = get_application_quality_issues(
                founding_date=profile.founding_date,
                mrr_usd=financial.mrr_usd,
                arr_usd=financial.arr_usd,
                monthly_revenue_usd=(
                    financial.monthly_revenue_usd
                ),
                previously_funded=(
                    financial.previously_funded
                ),
                source_investment_count=(
                    source_investment_count
                ),
                investment_expectation_usd=(
                    financial.investment_expectation_usd
                ),
                aviation_sector_experience=(
                    collaboration.aviation_sector_experience
                ),
                aviation_partners=(
                    collaboration.aviation_partners
                ),
            )

        rows.append({
            "_company_key": applicant.normalized_name,
            "_selection_key": (
                f"{applicant.normalized_name}:"
                f"{applicant.application_year}"
            ),
            "Startup": applicant.startup_name,
            "Application Year": applicant.application_year,
            "Sector / NACE": (
                profile.sector_nace_code
                if profile is not None
                else None
            ),
            "Startup Stage": (
                profile.startup_stage
                if profile is not None
                else None
            ),
            "Legal Status": (
                profile.legal_status
                if profile is not None
                else None
            ),
            "Data Check Count": len(quality_issues),
            "Data Check Issues": " | ".join(quality_issues),
            "Headquarters": (
                profile.headquarters_country
                if profile is not None
                else None
            ),
            "Founding Date": (
                profile.founding_date
                if profile is not None
                else None
            ),
            "Business Model": (
                profile.business_revenue_model
                if profile is not None
                else None
            ),
            "Problem and Solution": (
                profile.problem_solution
                if profile is not None
                else None
            ),
            "Previous Program": (
                profile.previous_program_participation
                if profile is not None
                else None
            ),
            "Management Team Size": (
                team.management_team_size
                if team is not None
                else None
            ),
            "Team Expertise": (
                team.team_expertise
                if team is not None
                else None
            ),
            "Active Customers": (
                financial.active_customer_count
                if financial is not None
                else None
            ),
            "MRR (USD)": (
                financial.mrr_usd
                if financial is not None
                else None
            ),
            "ARR (USD)": (
                financial.arr_usd
                if financial is not None
                else None
            ),
            "Monthly Revenue (USD)": (
                financial.monthly_revenue_usd
                if financial is not None
                else None
            ),
            "Annual Revenue (USD)": (
                financial.annual_revenue_usd
                if financial is not None
                else None
            ),
            "Previously Funded": (
                financial.previously_funded
                if financial is not None
                else None
            ),
            "Funding Evidence": (
                "Applicant and sources indicate funding"
                if (
                        financial is not None
                        and financial.previously_funded
                        and source_investment_count > 0
                )
                else (
                    "Applicant indicates funding; no source record found"
                    if (
                            financial is not None
                            and financial.previously_funded
                    )
                    else (
                        "Source record found; applicant answered no"
                        if source_investment_count > 0
                        else "No funding evidence found"
                    )
                )
            ),
            "Investment Expectation (USD)": (
                financial.investment_expectation_usd
                if financial is not None
                else None
            ),
            "Investment Use Plan": (
                financial.investment_use_plan
                if financial is not None
                else None
            ),
            "Aviation Experience": (
                collaboration.aviation_sector_experience
                if collaboration is not None
                else None
            ),
            "Aviation Partners": (
                collaboration.aviation_partners
                if collaboration is not None
                else None
            ),
            "Previous THY Relationship": (
                collaboration.thy_group_relationship
                if collaboration is not None
                else None
            ),
            "Desired THY Partnership": (
                collaboration.desired_thy_partnership
                if collaboration is not None
                else None
            ),
            "Review Status": (
                REVIEW_STATUS_LABELS.get(
                    review.status,
                    review.status,
                )
                if review is not None
                else "Not reviewed"
            ),
            "Review Note": (
                review.note
                if review is not None
                else ""
            ),
            "Sources Verified": (
                review.source_verified
                if review is not None
                else False
            ),
            "Investments Found": source_investment_count,
            "Latest Investment Date": latest_investment_date,
            "Disclosed Deal Total (million USD)": (
                None
                if pd.isna(disclosed_total)
                else disclosed_total
            ),
            "Investors Found": ", ".join(investors_found),
        })

    return pd.DataFrame(rows)

def build_investor_dataframe(
    investment_dataframe: pd.DataFrame,
) -> pd.DataFrame:
    rows = []

    for _, investment in investment_dataframe.iterrows():
        investor_names = split_investor_names(
            investment["Investors"]
        )

        for investor_name in investor_names:
            rows.append({
                "_investor_key": normalize_investor_name(
                    investor_name
                ),
                "Investor": investor_name,
                "Investor Type": classify_investor(investor_name),
                "All Investors": investment["Investors"],
                "Startup": investment["Startup"],
                "Sector": investment["Sector"],
                "Investment Date": investment[
                    "Investment Date"
                ],
                "Reporting Period": investment["Reporting Period"],
                "Year": (
                    int(investment["_filter_year"])
                    if pd.notna(investment["_filter_year"])
                    else None
                ),
                "Amount (million USD)": investment[
                    "Amount (million USD)"
                ],
                "Investment Stage": investment["Source Stage"],
                "Source": investment["Source"],
            })

    return pd.DataFrame(rows)
def get_stage_group(stage: object) -> str:
    if pd.isna(stage):
        result = StageEligibility.NEEDS_REVIEW
    else:
        result = evaluate_stage(str(stage))

    labels = {
        StageEligibility.ELIGIBLE: "Seed–Series A",
        StageEligibility.NOT_ELIGIBLE: "Late stage / exit",
        StageEligibility.NEEDS_REVIEW: "Stage needs review",
    }

    return labels[result]
def show_archive_summary() -> None:
    summary_path = (
        Path(__file__).resolve().parent
        / "data"
        / "archive_summary.json"
    )

    with st.expander("Report scan summary", expanded=False):
        st.caption(
            "Results of the most recently completed scan. "
            "Ready means the report could be parsed; "
            "it does not mean the records were saved to the database."
        )

        try:
            content = summary_path.read_text(encoding="utf-8")
            summary = json.loads(content)

            reports = summary["reports"]

            if not isinstance(reports, list):
                raise ValueError("The report list is invalid.")

            status_labels = {
                "READY": "Ready",
                "NEEDS_REVIEW": "Needs review",
                "OUT_OF_SCOPE": "Before selected year",
            }

            rows = [
                {
                    "Status": status_labels[item["status"]],
                    "Reporting Period": item.get("period"),
                    "Source Record Count": item.get("count"),
                    "Details": item.get("detail", ""),
                    "Source": item["url"],
                }
                for item in reports
            ]

            completed_at = datetime.fromisoformat(
                summary["completed_at"]
            )

            if completed_at.tzinfo is None:
                raise ValueError("The scan timestamp has no timezone.")

            local_time = completed_at.astimezone(
                ZoneInfo("Europe/Istanbul")
            )

        except FileNotFoundError:
            st.info(
                "No scan summary is available yet. "
                "Run the archive scan first."
            )
            return

        except (OSError, ValueError, KeyError, TypeError):
            st.warning(
                "The scan summary could not be read or has an invalid format."
            )
            return

        st.caption(
            "Last scan: "
            f"{local_time:%d.%m.%Y %H:%M} (Turkey time)"
        )

        total_column, ready_column, review_column = st.columns(3)

        total_column.metric("Total reports", len(reports))
        ready_column.metric(
            "Ready",
            sum(item["status"] == "READY" for item in reports),
        )
        review_column.metric(
            "Needs review",
            sum(
                item["status"] == "NEEDS_REVIEW"
                for item in reports
            ),
        )
        out_of_scope = sum(
            item["status"] == "OUT_OF_SCOPE"
            for item in reports
        )
        st.caption(
            f"Reports before the selected start year: {out_of_scope}"
        )
        if not rows:
            st.info("No reports were found in the scan summary.")
            return

        st.dataframe(
            pd.DataFrame(rows),
            hide_index=True,
            column_config={
                "Source": st.column_config.LinkColumn("Report page"),
            },
        )

        st.caption(
            "Annual and quarterly reports may include the same deals. "
            "Source record counts are not unique investment counts."
        )

def main() -> None:
    st.set_page_config(
        page_title="Investment Radar",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    if st.session_state.pop("_restore_list_filters", False):
        saved_filters = st.session_state.get(
            "_saved_list_filters",
            {},
        )

        for key, value in saved_filters.items():
            st.session_state[key] = value

    def prepare_csv(dataframe: pd.DataFrame) -> bytes:
        export_data = dataframe.copy()

        def safe_cell(value):
            if isinstance(value, str):
                if value.lstrip().startswith(("=", "+", "-", "@")):
                    return "'" + value
            return value

        for column in export_data.columns:
            export_data[column] = export_data[column].map(safe_cell)

        return export_data.to_csv(index=False).encode("utf-8-sig")

    def show_records(dataframe: pd.DataFrame) -> None:
        visible_data = dataframe.drop(
            columns=["Source Details", "Additional Source"],
            errors="ignore",
        )

        st.dataframe(
            visible_data,
            hide_index=True,
            column_config={
                "Source": st.column_config.LinkColumn("Primary source"),
            },
        )

        if "Source Details" not in dataframe.columns:
            return

        source_rows = []

        for value in dataframe["Source Details"]:
            if isinstance(value, str) and value:
                source_rows.extend(json.loads(value))

        if not source_rows:
            return

        with st.expander(
                f"Source details — {len(source_rows)} source records"
        ):
            st.caption(
                "All source records in the same investment group are shown. "
                "Different dates, stages, and other fields are preserved "
                "exactly as stated in each source. "
                "The investment group number is only an internal reference."
            )

            st.dataframe(
                pd.DataFrame(source_rows),
                hide_index=True,
                column_config={
                    "Source": st.column_config.LinkColumn("Open source"),
                },
            )

    def get_review_reasons(row: pd.Series) -> list[str]:
        reasons = []

        if pd.isna(row.get("_filter_year")):
            reasons.append("Investment year could not be determined")

        amount_warning = row.get("Amount Warning")

        if (
                isinstance(amount_warning, str)
                and amount_warning.strip()
        ):
            reasons.append("Investment amount could not be parsed")

        investors = str(row.get("Investors") or "").strip().casefold()

        if investors in UNKNOWN_INVESTORS:
            reasons.append("Investor information is missing")

        primary_stage = row.get("Source Stage")

        if pd.isna(primary_stage):
            primary_stage = None

        primary_stage_result = evaluate_stage(primary_stage)

        if primary_stage_result == StageEligibility.NEEDS_REVIEW:
            reasons.append("Investment stage needs review")

        source_details_text = row.get("Source Details")

        if isinstance(source_details_text, str) and source_details_text:
            try:
                source_details = json.loads(source_details_text)

                stage_results = {
                    evaluate_stage(
                        source.get("Investment Stage")
                    ).value
                    for source in source_details
                }

                if len(stage_results) > 1:
                    reasons.append(
                        "Investment stage conflicts across sources"
                    )

            except (json.JSONDecodeError, TypeError):
                reasons.append("Source details could not be read")

        return reasons

    def prepare_website_url(value: str | None) -> str | None:
        if value is None:
            return None

        website = value.strip()

        if not website:
            return None

        parsed = urlsplit(website)

        if parsed.scheme in {"http", "https"}:
            return website

        if not parsed.scheme:
            return "https://" + website

        return None

    def show_applicant_details(
            startup_name: str,
            application_year: int | None,
    ) -> None:
        applicant_details = get_applicant_details(
            startup_name=startup_name,
            application_year=application_year,
        )

        if not applicant_details:
            st.caption(
                "No application record was found for this startup "
                "in the selected application year."
            )
            return

        applicant = applicant_details[0]

        contact = applicant.contact
        profile = applicant.startup_profile
        team = applicant.team_profile
        financial = applicant.financial_profile
        collaboration = applicant.collaboration_profile

        with st.expander(
                "Application details",
                expanded=False,
        ):
            st.caption(
                f"Application year: {applicant.application_year}"
            )

            if any(
                item is None
                for item in (
                    contact,
                    profile,
                    team,
                    financial,
                    collaboration,
                )
            ):
                st.warning(
                    "Some detailed application records are missing. "
                    "This may be an older application imported before "
                    "the expanded CSV structure was introduced."
                )

            st.subheader("Startup profile")

            first_column, second_column = st.columns(2)

            first_column.write(
                f"**Startup:** {applicant.startup_name}"
            )
            first_column.write(
                "**Sector / NACE:** "
                + (
                    profile.sector_nace_code
                    if profile is not None
                    else "Not available"
                )
            )
            first_column.write(
                "**Legal status:** "
                + (
                    profile.legal_status
                    if profile is not None
                    else "Not available"
                )
            )

            second_column.write(
                "**Headquarters:** "
                + (
                    profile.headquarters_country
                    if profile is not None
                    else "Not available"
                )
            )
            second_column.write(
                "**Founding date:** "
                + (
                    profile.founding_date.strftime("%d.%m.%Y")
                    if profile is not None
                    else "Not available"
                )
            )
            second_column.write(
                "**Application stage:** "
                + (
                    profile.startup_stage
                    if profile is not None
                    else "Not available"
                )
            )

            if profile is not None:
                st.write("**Description**")
                st.write(profile.description)

                st.write("**Problem and solution**")
                st.write(profile.problem_solution)

                st.write("**Business and revenue model**")
                st.write(profile.business_revenue_model)

                links = pd.DataFrame([
                    {
                        "Website": prepare_website_url(
                            applicant.website
                        ),
                        "Product / Demo": prepare_website_url(
                            profile.product_demo_url
                        ),
                        "Pitch Deck": prepare_website_url(
                            profile.pitch_deck_url
                        ),
                        "Logo": prepare_website_url(
                            profile.logo_url
                        ),
                    }
                ])

                st.dataframe(
                    links,
                    hide_index=True,
                    column_config={
                        "Website": st.column_config.LinkColumn(
                            "Website"
                        ),
                        "Product / Demo": st.column_config.LinkColumn(
                            "Product / Demo"
                        ),
                        "Pitch Deck": st.column_config.LinkColumn(
                            "Pitch Deck"
                        ),
                        "Logo": st.column_config.LinkColumn(
                            "Logo"
                        ),
                    },
                )

            st.divider()
            st.subheader("Applicant contact")

            if contact is None:
                st.caption("Contact information is not available.")
            else:
                first_column, second_column = st.columns(2)

                first_column.write(
                    f"**Name:** {contact.full_name}"
                )
                first_column.write(
                    f"**Title:** {contact.title}"
                )
                first_column.write(
                    f"**Phone:** {contact.phone}"
                )

                second_column.write(
                    f"**Email:** {contact.email}"
                )
                second_column.write(
                    f"**LinkedIn:** {contact.linkedin_url}"
                )

            st.divider()
            st.subheader("Team")

            if team is None:
                st.caption("Team information is not available.")
            else:
                st.write(
                    "**Management team size:** "
                    f"{team.management_team_size}"
                )
                st.write("**Management team**")
                st.write(team.management_team_description)
                st.write("**Technical and sector expertise**")
                st.write(team.team_expertise)

            st.divider()
            st.subheader("Financial information")

            if financial is None:
                st.caption("Financial information is not available.")
            else:
                metric_columns = st.columns(4)

                metric_columns[0].metric(
                    "Active customers",
                    financial.active_customer_count,
                )
                metric_columns[1].metric(
                    "MRR",
                    f"${financial.mrr_usd:,.0f}",
                )
                metric_columns[2].metric(
                    "ARR",
                    f"${financial.arr_usd:,.0f}",
                )
                metric_columns[3].metric(
                    "Investment expectation",
                    (
                        f"${financial.investment_expectation_usd:,.0f}"
                    ),
                )

                revenue_columns = st.columns(2)

                revenue_columns[0].metric(
                    "Monthly revenue",
                    f"${financial.monthly_revenue_usd:,.0f}",
                )
                revenue_columns[1].metric(
                    "Annual revenue",
                    f"${financial.annual_revenue_usd:,.0f}",
                )

                st.write(
                    "**Previously funded:** "
                    + (
                        "Yes"
                        if financial.previously_funded
                        else "No"
                    )
                )
                st.write("**Planned use of investment**")
                st.write(financial.investment_use_plan)

            st.divider()
            st.subheader("Aviation and THY collaboration")

            if collaboration is None:
                st.caption(
                    "Collaboration information is not available."
                )
            else:
                st.write(
                    "**Previous aviation or travel-sector experience:** "
                    + (
                        "Yes"
                        if collaboration.aviation_sector_experience
                        else "No"
                    )
                )
                st.write("**Previous aviation partners**")
                st.write(
                    collaboration.aviation_partners
                    or "Not provided"
                )

                st.write("**Previous THY Group relationship**")
                st.write(
                    collaboration.thy_group_relationship
                    or "Not provided"
                )

                st.write("**Desired THY partnership**")
                st.write(
                    collaboration.desired_thy_partnership
                )

                if collaboration.additional_notes:
                    st.write("**Additional notes**")
                    st.write(collaboration.additional_notes)

    def show_startup_review_form(
            startup_name: str,
            application_year: int | None,
    ) -> None:
        existing_review = get_startup_review(
            startup_name,
            application_year=application_year,
        )

        if existing_review is None:
            current_status = REVIEW_STATUSES[0]
            current_note = ""
            current_source_verified = False
        else:
            current_status = existing_review.status
            current_note = existing_review.note or ""
            current_source_verified = existing_review.source_verified

        normalized_name = normalize_startup_name(startup_name)

        with st.expander(
                "Review status and notes",
                expanded=existing_review is not None,
        ):
            if existing_review is None:
                st.caption(
                    "This startup has not been added to the review list."
                )
            else:
                st.caption(
                    "This startup is already in the review list. "
                    "Update the fields and save again."
                )

            with st.form(
                    key=f"startup_review_form_{normalized_name}",
            ):
                status = st.selectbox(
                    "Review status",
                    options=REVIEW_STATUSES,
                    index=REVIEW_STATUSES.index(current_status),
                    format_func=lambda value: REVIEW_STATUS_LABELS.get(
                        value,
                        value,
                    ),
                )

                note = st.text_area(
                    "Review note",
                    value=current_note,
                    placeholder=(
                        "Add research notes about this startup..."
                    ),
                    height=140,
                )

                source_verified = st.checkbox(
                    "I verified the sources",
                    value=current_source_verified,
                )

                submitted = st.form_submit_button(
                    "Save review",
                    type="primary",
                )

            if submitted:
                save_startup_review(
                    startup_name=startup_name,
                    status=status,
                    note=note,
                    source_verified=source_verified,
                    application_year=application_year,
                )

                st.success(
                    "Review saved successfully."
                )
    def show_company_investment_summary(
            history: pd.DataFrame,
    ) -> None:
        timeline = history.copy()

        timeline["_parsed_date"] = pd.to_datetime(
            timeline["Investment Date"],
            errors="coerce",
            format="mixed",
        )

        dated_records = timeline[
            timeline["_parsed_date"].notna()
        ]

        if dated_records.empty:
            first_investment = "Not available"
            last_investment = "Not available"
        else:
            first_row = dated_records.loc[
                dated_records["_parsed_date"].idxmin()
            ]
            last_row = dated_records.loc[
                dated_records["_parsed_date"].idxmax()
            ]

            first_investment = first_row[
                "Investment Date"
            ]
            last_investment = last_row[
                "Investment Date"
            ]

        amounts = pd.to_numeric(
            timeline["Amount (million USD)"],
            errors="coerce",
        )

        disclosed_amount_total = amounts.sum(min_count=1)

        if pd.isna(disclosed_amount_total):
            amount_text = "Not available"
        else:
            amount_text = f"{disclosed_amount_total:,.2f}"

        first_column, second_column, third_column, fourth_column = (
            st.columns(4)
        )

        first_column.metric(
            "Investments found",
            len(timeline),
        )
        second_column.metric(
            "First investment",
            first_investment,
        )
        third_column.metric(
            "Latest investment",
            last_investment,
        )
        fourth_column.metric(
            "Disclosed deal amounts",
            f"{amount_text} million USD",
        )

        st.caption(
            "This is the sum of disclosed round or transaction amounts "
            "in the available sources, not the startup's verified total funding."
        )

        timeline = timeline.sort_values(
            "_parsed_date",
            ascending=False,
            na_position="last",
        )

        timeline_view = timeline[
            [
                "Investment Date",
                "Reporting Period",
                "Investors",
                "Amount (million USD)",
                "Source Stage",
                "Source Count",
                "Source",
            ]
        ].rename(
            columns={
                "Investment Date": "Investment Date",
                "Source Stage": "Investment Stage",
            }
        )

        st.subheader("Investment timeline")

        st.dataframe(
            timeline_view,
            hide_index=True,
            column_config={
                "Source": st.column_config.LinkColumn(
                    "Open primary source"
                ),
            },
        )

    def show_investor_detail(
            investor_data: pd.DataFrame,
            investor_key: str,
    ) -> None:
        investor_history = investor_data[
            investor_data["_investor_key"].eq(investor_key)
        ].copy()

        if investor_history.empty:
            st.warning(
                "This investor is not available under the current filters."
            )
            return

        investor_name = investor_history[
            "Investor"
        ].iloc[0]

        st.header(investor_name)

        startup_count = (
            investor_history["Startup"]
            .fillna("")
            .map(normalize_startup_name)
            .nunique()
        )

        first_column, second_column = st.columns(2)

        first_column.metric(
            "Portfolio startups",
            startup_count,
        )

        second_column.metric(
            "Investment records",
            len(investor_history),
        )

        visible_history = investor_history.drop(
            columns=["_investor_key"],
            errors="ignore",
        )

        st.subheader("Portfolio startups")

        st.dataframe(
            visible_history,
            hide_index=True,
            column_config={
                "Source": st.column_config.LinkColumn(
                    "Open source"
                ),
            },
        )

        st.download_button(
            "Download investor portfolio CSV",
            data=prepare_csv(visible_history),
            file_name="investor_portfolio.csv",
            mime="text/csv",
            key="investor_detail_download",
        )
        st.divider()
        st.subheader("Review selected applicant")

        review_target = st.selectbox(
            "Open an applicant",
            options=[
                None,
                *selected_applications,
            ],
            format_func=lambda value: (
                "Select an applicant"
                if value is None
                else startup_labels[value]
            ),
            key="comparison_review_target",
        )

        if review_target is not None:
            selected_application = (
                comparison_candidates[
                    comparison_candidates[
                        "_selection_key"
                    ].eq(review_target)
                ].iloc[0]
            )

            reviewed_startup_name = (
                selected_application["Startup"]
            )
            reviewed_application_year = int(
                selected_application[
                    "Application Year"
                ]
            )

            show_applicant_details(
                startup_name=reviewed_startup_name,
                application_year=(
                    reviewed_application_year
                ),
            )

            show_startup_review_form(
                startup_name=reviewed_startup_name,
                application_year=(
                    reviewed_application_year
                ),
            )

        st.caption(
            "The deal amount is the total funding round amount; "
            "it is not the amount contributed by one investor."
        )

    def show_company_groups(
            records: pd.DataFrame,
            key_prefix: str,
    ) -> None:
        if records.empty:
            st.info("No startups found.")
            return

        grouped_data = records.copy()
        grouped_data["_company_key"] = (
            grouped_data["Startup"]
            .fillna("")
            .map(normalize_startup_name)
        )

        company_rows = []

        for company_key, history in grouped_data.groupby(
                "_company_key",
                sort=True,
        ):
            sectors = sorted({
                str(value).strip()
                for value in history["Sector"].dropna()
                if str(value).strip()
            })

            company_rows.append({
                "_company_key": company_key,
                "Startup": history["Startup"].iloc[0],
                "Investment Count": len(history),
                "Sector": ", ".join(sectors),
            })

        companies = pd.DataFrame(company_rows)

        st.metric("Startups found", len(companies))
        st.caption(
            "Counts reflect deduplicated investment records under the "
            "current filters."
        )

        sort_choice = st.selectbox(
            "Sort startups",
            options=[
                "Investment count: high to low",
                "Startup name: A–Z",
            ],
            key=f"{key_prefix}_sort",
        )

        if sort_choice == "Investment count: high to low":
            companies = companies.sort_values(
                ["Investment Count", "Startup"],
                ascending=[False, True],
            )
        else:
            companies = companies.sort_values(
                "_company_key"
            )

        page_size = 20
        page_count = (len(companies) + page_size - 1) // page_size

        page = st.selectbox(
            "Page",
            options=list(range(1, page_count + 1)),
            key=f"{key_prefix}_page",
        )

        start = (page - 1) * page_size
        visible = companies.iloc[start:start + page_size]

        st.caption(
            f"Of {len(companies)} startups, "
            f"{start + 1}–{start + len(visible)} shown."
        )
        table_version = st.session_state.get("_table_version", 0)

        event = st.dataframe(
            visible.drop(columns=["_company_key"]),
            hide_index=True,
            on_select="rerun",
            selection_mode="single-row",
            key=f"{key_prefix}_table_{table_version}",
        )

        st.caption(
            "Select a startup row to open its details."
        )

        if event.selection.rows:
            selected_position = event.selection.rows[0]
            selected_key = visible.iloc[selected_position]["_company_key"]

            filter_keys = [
                "applicant_search",
                "discovery_search",
                "discovery_sectors",
                "discovery_sort",
                "discovery_page",
                "similar_sort",
                "similar_page",
            ]

            st.session_state["_saved_list_filters"] = {
                key: st.session_state[key]
                for key in filter_keys
                if key in st.session_state
            }

            st.session_state["_selected_company"] = selected_key
            st.rerun()

    st.title("Investment Radar")

    st.caption(
        "Explore startup investment histories, review investors, "
        "and manage your research list."
    )

    st.sidebar.title("Control Panel")

    source_panel = st.sidebar.expander(
        "Data sources",
        expanded=False,
    )

    if source_panel.button(
            "Refresh sources",
            key="refresh_sources",
            use_container_width=True,
    ):
        st.session_state.pop("_source_update_result", None)

        with source_panel.status(
                "Refreshing sources…",
                expanded=True,
        ) as update_status:
            progress_message = st.empty()

            try:
                result = run_archive_scan(
                    start_year=2000,
                    save=True,
                    on_progress=progress_message.text,
                )

            except Exception:
                update_status.update(
                    label="Refresh failed",
                    state="error",
                    expanded=True,
                )

                st.error(
                    "The refresh could not be completed because of an error. "
                    "Some reports may have been saved. "
                    "See the terminal output for details."
                )

                import traceback
                traceback.print_exc()

            else:
                st.session_state["_source_update_result"] = {
                    "records_saved": result["records_saved"],
                    "ready_count": sum(
                        report["status"] == "READY"
                        for report in result["reports"]
                    ),
                    "failed_count": sum(
                        report["status"] == "NEEDS_REVIEW"
                        for report in result["reports"]
                    ),
                    "candidate_count": len(result["reports"]),
                }

                update_status.update(
                    label="Source scan completed",
                    state="complete",
                    expanded=False,
                )

    update_result = st.session_state.get("_source_update_result")

    if update_result is not None:
        source_panel.success(
            f"Last refresh: "
            f"{update_result['records_saved']} new records · "
            f"{update_result['ready_count']} reports processed"
        )
        if update_result["failed_count"]:
            source_panel.warning(
                f"{update_result['failed_count']} sources could not be processed."
            )

        if update_result["candidate_count"] == 0:
            source_panel.warning(
                "No report candidates were found."
            )

    def reset_year_filter_navigation():
        for key in (
                "discovery_page",
                "similar_page",
                "_selected_company",
                "_saved_list_filters",
                "_restore_list_filters",
                "selected_investor",
                "investor_search",
                "investor_types",
                "investor_sectors",
                "_selected_investor_key",

        ):
            st.session_state.pop(key, None)
            st.session_state.pop(key, None)

        st.session_state["_table_version"] = (
            st.session_state.get("_table_version", 0) + 1
        )



    st.sidebar.subheader("Data management")
    with st.sidebar.expander("Upload applicant list", expanded=False):
        st.caption(
            "Upload the CSV exported from the application form. "
            "Turkish form headers and canonical English headers "
            "are supported."
        )

        upload_application_year = st.number_input(
            "Year assigned to uploaded file",
            min_value=2000,
            max_value=datetime.now().year + 1,
            value=datetime.now().year,
            step=1,
            key="upload_application_year",
            help=(
                "This year is used when the uploaded CSV does not "
                "contain an application_year column."
            ),
        )
        replace_existing_applications = st.checkbox(
            "Replace existing applications for this year",

            value=True,
            key="replace_existing_applications",
            help=(
                "When enabled, applications from the selected year "
                "that are not present in the uploaded CSV are removed "
                "from the applicant list."
            ),
        )
        st.divider()

        st.caption(
            "The bundled demo file contains fictional applicants "
            "and is safe to use in presentations."
        )

        if st.button(
            "Replace 2026 applications with demo data",
            key="load_demo_applicants",
        ):
            demo_applicants = load_applicants_from_csv(
                "data/demo_applicants.csv",
                application_year=2026,
            )

            (
                demo_created_count,
                demo_updated_count,
                demo_removed_count,
            ) = save_applicants(
                demo_applicants,
                replace_application_year=2026,
            )

            st.success(
                "The 2026 applicant list was replaced with "
                "fictional demo data."
            )

            demo_result_columns = st.columns(3)

            demo_result_columns[0].metric(
                "Created",
                demo_created_count,
            )
            demo_result_columns[1].metric(
                "Updated",
                demo_updated_count,
            )
            demo_result_columns[2].metric(
                "Removed",
                demo_removed_count,
            )

            st.session_state["_table_version"] = (
                st.session_state.get(
                    "_table_version",
                    0,
                ) + 1
            )

        uploaded_applicants_file = st.file_uploader(            "Choose applicant CSV",
            type=["csv"],
            key="applicant_csv_upload",
        )

        if uploaded_applicants_file is not None:
            try:
                uploaded_applicants_file.seek(0)

                uploaded_applicants = load_applicants_from_csv(
                    uploaded_applicants_file,
                    application_year=int(upload_application_year),
                )
                preview_rows = [
                    {
                        "Startup": applicant.startup_name,
                        "Normalized Name": (
                            applicant.normalized_name
                        ),
                        "Website": applicant.website,
                        "Application Year": applicant.application_year,
                    }
                    for applicant in uploaded_applicants
                ]

                st.success(
                    f"Successfully read {len(uploaded_applicants)} "
                    "applicant records."
                )

                st.dataframe(
                    pd.DataFrame(preview_rows),
                    hide_index=True,
                )

                if st.button(
                        "Save applicants to database",
                        type="primary",
                        key="save_uploaded_applicants",
                ):
                    (
                        created_count,
                        updated_count,
                        removed_count,
                    ) = save_applicants(
                        uploaded_applicants,
                        replace_application_year=(
                            int(upload_application_year)
                            if replace_existing_applications
                            else None
                        ),
                    )

                    st.success(
                        "Application list saved successfully."
                    )

                    result_columns = st.columns(3)

                    result_columns[0].metric(
                        "Created",
                        created_count,
                    )
                    result_columns[1].metric(
                        "Updated",
                        updated_count,
                    )
                    result_columns[2].metric(
                        "Removed",
                        removed_count,
                    )

                    if removed_count:
                        st.caption(
                            f"{removed_count} applications were removed "
                            "because they were not present in the uploaded "
                            f"{int(upload_application_year)} list."
                        )

                    st.session_state["_table_version"] = (
                            st.session_state.get(
                                "_table_version",
                                0,
                            ) + 1
                    )


            except (

                    ValueError,

                    UnicodeDecodeError,

            ) as error:
                st.error(f"Could not read CSV: {error}")

    st.sidebar.divider()
    st.sidebar.subheader("Filters")

    application_years = get_application_years()

    selected_application_year = st.sidebar.selectbox(
        "Filter by application year",
        options=[
            None,
            *application_years,
        ],
        format_func=lambda year: (
            "All application years"
            if year is None
            else str(year)
        ),
        key="application_year_filter",
        on_change=reset_year_filter_navigation,
        help=(
            "Selects the application year used for applicant matching."
        ),
    )

    filter_start_year = st.sidebar.selectbox(
        "Investment start year",
        options=[
            None,
            *range(datetime.now().year, 1999, -1),
        ],
        format_func=lambda year: (
            "All years" if year is None else f"{year} and later"
        ),
        key="investment_year_filter",
        on_change=reset_year_filter_navigation,
        help=(
            "Shows available investment records from the selected year onward."
        ),
    )
    columns = [
        "Startup",
        "Sector",
        "Investors",
        "Investment Date",
        "Reporting Period",
        "Amount (million USD)",
        "Source Stage",
        "Applicant Match",
        "Similar Applicants",
        "Source",
        "Additional Source",
        "Source Count",
        "Grouping",
        "Source Stages",
        "Source Details",
        "Raw Amount",
        "Amount Warning",
    ]

    dataframe = build_dataframe(
        application_year=selected_application_year,
    ).reindex(columns=columns)
    dataframe["Stage Group"] = (
        dataframe["Source Stage"].map(get_stage_group)
    )
    stage_group_options = [
        "Seed–Series A",
        "Stage needs review",
        "Late stage / exit",
    ]

    selected_stage_groups = st.sidebar.multiselect(
        "Investment Stage",
        options=stage_group_options,
        default=stage_group_options,
        key="investment_stage_filter",
        on_change=reset_year_filter_navigation,
        help=(
            "Filters records by the stage stated in the source. "
            "It does not determine overall investment eligibility."
        ),
    )

    if selected_stage_groups:
        dataframe = dataframe[
            dataframe["Stage Group"].isin(
                selected_stage_groups
            )
        ].copy()
    else:
        dataframe = dataframe.iloc[0:0].copy()

    investment_years = pd.to_numeric(
        dataframe["Investment Date"]
        .astype("string")
        .str.extract(r"\b(20\d{2})\b", expand=False),
        errors="coerce",
    )

    report_years = pd.to_numeric(
        dataframe["Reporting Period"]
        .astype("string")
        .str.extract(
            r"^(20\d{2})-(?:FY|Q[1-4])$",
            expand=False,
        ),
        errors="coerce",
    )

    dataframe["_filter_year"] = investment_years.fillna(report_years)

    dataframe["Year Basis"] = [
        (
            "Investment Date"
            if pd.notna(investment_year)
            else (
                "Reporting period — investment year unavailable"
                if pd.notna(report_year)
                else "Year unavailable"
            )
        )
        for investment_year, report_year in zip(
            investment_years,
            report_years,
        )
    ]

    total_record_count = len(dataframe)
    unknown_year_count = int(dataframe["_filter_year"].isna().sum())

    if filter_start_year is not None:
        dataframe = dataframe[
            dataframe["_filter_year"] >= filter_start_year
            ].copy()

    st.caption(
        (
            f"Year filter: {filter_start_year} and later"
            if filter_start_year is not None
            else "Year filter: all years"
        )
        + f" · Investments shown: {len(dataframe)}"
        + f" / Total investments: {total_record_count}"
    )

    fallback_count = int(
        dataframe["Year Basis"]
        .eq("Reporting period — investment year unavailable")
        .sum()
    )

    if fallback_count:
        st.caption(
            f"The reporting period was used for {fallback_count} records "
            "whose investment year could not be determined."
        )

    if filter_start_year is not None and unknown_year_count:
        st.warning(
            f"{unknown_year_count} records are excluded because their "
            "investment year could not be determined."
        )
    if dataframe.empty:
        st.session_state.pop("_selected_company", None)

        st.warning(
            "No investment records match the selected filters."
        )

        st.caption(
            "Try changing the investment start year or stage filters."
        )

    quick_search = st.text_input(
        "Quick search",
        placeholder="Search for a startup or investor...",
        key="quick_search",
    )

    if quick_search.strip():
        search_text = quick_search.strip()
        normalized_search = normalize_startup_name(search_text)
        normalized_investor_search = normalize_investor_name(
            search_text
        )

        company_results = (
            dataframe.assign(
                _company_key=(
                    dataframe["Startup"]
                    .fillna("")
                    .map(normalize_startup_name)
                )
            )
            .loc[
                lambda frame: frame["_company_key"].str.contains(
                    normalized_search,
                    regex=False,
                    na=False,
                )
            ]
            .drop_duplicates("_company_key")
            .head(8)
        )

        quick_investor_data = build_investor_dataframe(
            dataframe
        )

        if quick_investor_data.empty:
            investor_results = quick_investor_data
        else:
            investor_results = (
                quick_investor_data.loc[
                    quick_investor_data[
                        "_investor_key"
                    ].str.contains(
                        normalized_investor_search,
                        regex=False,
                        na=False,
                    )
                ]
                .drop_duplicates("_investor_key")
                .head(8)
            )

        company_column, investor_column = st.columns(2)

        with company_column:
            st.markdown("**Startups**")

            if company_results.empty:
                st.caption("No matching startup found.")
            else:
                for _, company in company_results.iterrows():
                    if st.button(
                            company["Startup"],
                            key=(
                                    "quick_company_"
                                    + company["_company_key"]
                            ),
                            use_container_width=True,
                    ):
                        st.session_state["_selected_company"] = (
                            company["_company_key"]
                        )

                        st.session_state.pop(
                            "_investor_detail_key",
                            None,
                        )

                        st.rerun()

        with investor_column:
            st.markdown("**Investors**")

            if investor_results.empty:
                st.caption("No matching investor found.")
            else:
                for _, investor in investor_results.iterrows():
                    if st.button(
                            investor["Investor"],
                            key=(
                                    "quick_investor_"
                                    + investor["_investor_key"]
                            ),
                            use_container_width=True,
                    ):
                        st.session_state["_investor_detail_key"] = (
                            investor["_investor_key"]
                        )

                        st.session_state.pop(
                            "_selected_company",
                            None,
                        )

                        st.rerun()
    investor_detail_key = st.session_state.get(
        "_investor_detail_key"
    )

    if investor_detail_key is not None:
        if st.button("← Back to investors"):
            st.session_state.pop(
                "_investor_detail_key",
                None,
            )
            st.rerun()

        investor_detail_data = build_investor_dataframe(
            dataframe
        )

        show_investor_detail(
            investor_data=investor_detail_data,
            investor_key=investor_detail_key,
        )

        return
    selected_company = st.session_state.get("_selected_company")

    if selected_company is not None:
        if st.button("← Back to startups"):
            st.session_state.pop("_selected_company", None)
            st.session_state["_restore_list_filters"] = True

            st.session_state["_table_version"] = (
                    st.session_state.get("_table_version", 0) + 1
            )

            st.rerun()

        company_keys = (
            dataframe["Startup"]
            .fillna("")
            .map(normalize_startup_name)
        )

        history = dataframe[
            company_keys == selected_company
            ].copy()

        if history.empty:
            st.warning(
                "This startup is not available under the current filters."
            )
            return

        company_name = history["Startup"].iloc[0]

        sectors = sorted({
            str(value).strip()
            for value in history["Sector"].dropna()
            if str(value).strip()
        })

        application_statuses = sorted({
            str(value).strip()
            for value in history["Applicant Match"].dropna()
            if str(value).strip()
        })

        st.sidebar.header(company_name)

        st.write(
            "Sector: "
            + (", ".join(sectors) or "Not available")
        )

        st.write(
            "Applicant list match: "
            + (
                    ", ".join(application_statuses)
                    or "Not available"
            )
        )

        startup_review = get_startup_review(
            company_name,
            application_year=selected_application_year,
        )

        if startup_review is None:
            st.caption(
                "Review status: Not in review list"
            )
        else:
            verification_text = (
                "Sources verified"
                if startup_review.source_verified
                else "Sources not verified"
            )

            st.caption(
                f"Review status: {REVIEW_STATUS_LABELS.get(startup_review.status, startup_review.status)} "
                f"· {verification_text}"
            )
        show_applicant_details(
            startup_name=company_name,
            application_year=selected_application_year,
        )

        st.caption(
            (
                "Available investment records from all years are shown."
                if filter_start_year is None
                else (
                    f"Available investment records from {filter_start_year} "
                    "onward are shown."
                )
            )
            + " The full investment history may not be available."
        )

        show_company_investment_summary(history)

        show_startup_review_form(
            company_name,
            application_year=selected_application_year,
        )

        with st.expander(
                "All investment and source details",
                expanded=False,
        ):
            show_records(history)



        st.download_button(
            label="Download startup investment history CSV",
            data=prepare_csv(history),
            file_name="startup_investment_history.csv",
            mime="text/csv",
            key="company_detail_download",
        )

        st.info(
            "Matching source records are grouped according to defined rules. "
            "Primary and additional source links, including conflicting "
            "stage descriptions, are preserved in the table."
        )

        return

    applicant_names = sorted({
        name.strip()
        for name in get_applicant_names(
            selected_application_year
        )
        if name and name.strip()
    })

    normalized_investment_names = (
        dataframe["Startup"]
        .fillna("")
        .map(normalize_startup_name)
    )

    (
        applicants_tab,
        discovery_tab,
        investors_tab,
        shortlist_tab,
        data_quality_tab,
    ) = st.tabs(
        [
            "Applicants",
            "Startups",
            "Investors",
            "Review Workspace",
            "Data Quality",
        ],
        default=(
            "Investors"
            if st.session_state.pop(
                "_open_investor_tab",
                False,
            )
            else (
                "Startups"
                if "_saved_list_filters" in st.session_state
                else "Applicants"
            )
        ),
    )
    with applicants_tab:
        st.caption(
            "Applicants in the selected year and the investment records "
            "found for them in available sources."
        )

        applicant_search = st.text_input(
            "Search applicants",
            key="applicant_search",
        )

        search_name = normalize_startup_name(applicant_search)

        visible_applicants = [
            name
            for name in applicant_names
            if search_name in normalize_startup_name(name)
        ]

        st.metric("Applicants shown", len(visible_applicants))

        if not applicant_names:
            st.info("No applicant list has been uploaded yet.")
        elif not visible_applicants:
            st.info("No matching applicant found.")

        visible_applicant_keys = {
            normalize_startup_name(name)
            for name in visible_applicants
        }

        applicant_investments = dataframe[
            normalized_investment_names.isin(
                visible_applicant_keys
            )
        ].copy()

        if not applicant_investments.empty:
            show_company_groups(
                applicant_investments,
                key_prefix="applicants",
            )

        applicants_with_investments = {
            normalize_startup_name(name)
            for name in applicant_investments["Startup"]
        }

        applicants_without_investments = [
            name
            for name in visible_applicants
            if normalize_startup_name(name)
               not in applicants_with_investments
        ]

        if applicants_without_investments:
            with st.expander(
                    "Applicants with no matching investment records "
                    f"— {len(applicants_without_investments)}"
            ):
                st.caption(
                    "This does not mean these startups received no investment; "
                    "it only means no name match was found in the scanned sources."
                )

                st.dataframe(
                    pd.DataFrame({
                        "Startup": applicants_without_investments,
                    }),
                    hide_index=True,
                )

    with discovery_tab:
        st.caption(
            "All startups with investment records, regardless of application status."
        )

        discovery = dataframe.copy()

        discovery_search = st.text_input(
            "Search discovered startups",
            key="discovery_search",
        )

        sectors = st.multiselect(
            "Sector",
            options=sorted(
                discovery["Sector"].dropna().unique().tolist()
            ),
            key="discovery_sectors",
        )

        if discovery_search.strip():
            discovery = discovery[
                discovery["Startup"].str.contains(
                    discovery_search.strip(),
                    case=False,
                    regex=False,
                    na=False,
                )
            ]

        if sectors:
            discovery = discovery[
                discovery["Sector"].isin(sectors)
            ]

        if discovery.empty:
            st.metric("Startups found", 0)
            st.info(
                "No funded startups match these filters."
            )
        else:
            show_company_groups(
                discovery,
                key_prefix="discovery",
            )

            st.download_button(
                label="Download investment records CSV",
                data=prepare_csv(discovery),
                file_name="discovered_investments.csv",
                mime="text/csv",
                key="download_discovery",
            )




    with investors_tab:
        st.caption(
        "Investors found in the sources and the startups they invested in · "
    )

        investor_data = build_investor_dataframe(dataframe)
        st.caption(
            (
                "All years"
                if filter_start_year is None
                else f"{filter_start_year} and later"
            )
        )

        if investor_data.empty:
            st.metric("Investors shown", 0)
            st.info(
                "No investor records match the selected filters."
            )
        else:
            def reset_selected_investor():
                st.session_state.pop(
                    "_selected_investor_key",
                    None,
                )
            investor_search = st.text_input(
                "Search investors",
                key="investor_search",
                on_change=reset_selected_investor,
            )

            investor_types = st.multiselect(
                "Investor Type",
                options=sorted(
                    investor_data["Investor Type"]
                    .dropna()
                    .unique()
                    .tolist()
                ),
                key="investor_types",
                on_change=reset_selected_investor,
            )

            investor_sectors = st.multiselect(
                "Investment sector",
                options=sorted(
                    investor_data["Sector"]
                    .dropna()
                    .unique()
                    .tolist()
                ),
                key="investor_sectors",
                on_change=reset_selected_investor,
            )

            filtered_investors = investor_data.copy()

            if investor_search.strip():
                search_key = normalize_investor_name(
                    investor_search
                )

                filtered_investors = filtered_investors[
                    filtered_investors[
                        "_investor_key"
                    ].str.contains(
                        search_key,
                        regex=False,
                        na=False,
                    )
                ]

            if investor_types:
                filtered_investors = filtered_investors[
                    filtered_investors[
                        "Investor Type"
                    ].isin(investor_types)
                ]

            if investor_sectors:
                filtered_investors = filtered_investors[
                    filtered_investors[
                        "Sector"
                    ].isin(investor_sectors)
                ]

            summaries = []

            for investor_key, history in filtered_investors.groupby(
                "_investor_key",
                sort=True,
            ):
                startup_count = (
                    history["Startup"]
                    .fillna("")
                    .map(normalize_startup_name)
                    .nunique()
                )

                sectors = sorted({
                    str(value).strip()
                    for value in history["Sector"].dropna()
                    if str(value).strip()
                })

                summaries.append({
                    "_investor_key": investor_key,
                    "Investor": (
                        history["Investor"].iloc[0]
                    ),
                    "Investor Type": (
                        history["Investor Type"].iloc[0]
                    ),
                    "Portfolio Startup Count": startup_count,
                    "Investment Record Count": len(history),
                    "Sectors": ", ".join(sectors),
                })

            summary_dataframe = pd.DataFrame(
                summaries,
                columns=[
                    "_investor_key",
                    "Investor",
                    "Investor Type",
                    "Portfolio Startup Count",
                    "Investment Record Count",
                    "Sectors",
                ],
            ).sort_values(
                [
                    "Portfolio Startup Count",
                    "Investor",
                ],
                ascending=[False, True],
            )
            if summary_dataframe.empty:
                st.info(
                    "No investors or venture capital funds match this search."
                )

            st.metric(
                "Investors shown",
                len(summary_dataframe),
            )

            table_version = st.session_state.get(
                "_table_version",
                0,
            )

            investor_event = st.dataframe(
                summary_dataframe.drop(columns=["_investor_key"]),
                hide_index=True,
                on_select="rerun",
                selection_mode="single-row",
                key=f"investor_summary_table_{table_version}",
            )

            st.caption(
                "Select an investor row to open details."
            )

            investor_labels = dict(zip(
                summary_dataframe["_investor_key"],
                summary_dataframe["Investor"],
            ))

            selected_investor = st.session_state.get(
                "_selected_investor_key",
                "",
            )

            if investor_event.selection.rows:
                selected_position = investor_event.selection.rows[0]

                selected_key = summary_dataframe.iloc[
                    selected_position
                ]["_investor_key"]

                st.session_state["_investor_detail_key"] = (
                    selected_key
                )

                st.rerun()

            available_investor_keys = set(
                summary_dataframe["_investor_key"]
            )

            if selected_investor not in available_investor_keys:
                selected_investor = ""
                st.session_state.pop(
                    "_selected_investor_key",
                    None,
                )

            if selected_investor:
                investor_history = filtered_investors[
                    filtered_investors["_investor_key"]
                    == selected_investor
                ].drop(columns=["_investor_key"])

                investor_name = investor_labels[selected_investor]

                st.subheader(investor_name)

                startup_count = (
                    investor_history["Startup"]
                    .fillna("")
                    .map(normalize_startup_name)
                    .nunique()
                )

                first_column, second_column = st.columns(2)

                first_column.metric(
                    "Portfolio startups",
                    startup_count,
                )
                second_column.metric(
                    "Investment records",
                    len(investor_history),
                )

                co_investor_rows = []

                for _, investment in investor_history.iterrows():
                    all_investors = split_investor_names(
                        investment["All Investors"]
                    )

                    for co_investor_name in all_investors:
                        co_investor_key = normalize_investor_name(
                            co_investor_name
                        )

                        if co_investor_key == selected_investor:
                            continue

                        co_investor_rows.append({
                            "_co_investor_key": co_investor_key,
                            "Co-investor": co_investor_name,
                            "Startup": investment["Startup"],
                            "Sector": investment["Sector"],
                            "Investment Date": investment[
                                "Investment Date"
                            ],
                        })

                if co_investor_rows:
                    co_investor_data = pd.DataFrame(
                        co_investor_rows
                    )

                    co_investor_summary_rows = []

                    for (
                            co_investor_key,
                            co_history,
                    ) in co_investor_data.groupby(
                        "_co_investor_key",
                        sort=True,
                    ):
                        shared_startups = sorted({
                            str(value).strip()
                            for value in co_history["Startup"].dropna()
                            if str(value).strip()
                        })

                        shared_sectors = sorted({
                            str(value).strip()
                            for value in co_history["Sector"].dropna()
                            if str(value).strip()
                        })

                        co_investor_summary_rows.append({
                            "Co-investor": (
                                co_history["Co-investor"].iloc[0]
                            ),
                            "Shared Investment Count": len(co_history),
                            "Shared Startups": ", ".join(
                                shared_startups
                            ),
                            "Sectors": ", ".join(
                                shared_sectors
                            ),
                        })

                    co_investor_summary = pd.DataFrame(
                        co_investor_summary_rows
                    ).sort_values(
                        [
                            "Shared Investment Count",
                            "Co-investor",
                        ],
                        ascending=[False, True],
                    )

                    st.subheader("Co-investors")

                    st.dataframe(
                        co_investor_summary,
                        hide_index=True,
                        use_container_width=True,
                    )

                    st.caption(
                        "Co-investors are derived from names appearing together "
                        "in the same investment record."
                    )

                else:
                    st.caption(
                        "No co-investor was found for this investor in the "
                        "available sources."
                    )

                st.subheader("Portfolio startups")

                st.dataframe(
                    investor_history,
                    hide_index=True,
                    column_config={
                        "Source": st.column_config.LinkColumn(
                            "Open source"
                        ),
                    },
                )

                st.download_button(
                    label="Download investor portfolio CSV",
                    data=prepare_csv(investor_history),
                    file_name="investor_portfolio.csv",
                    mime="text/csv",
                    key="investor_history_download",
                )

                st.caption(
                    "The deal amount is the total funding round amount, "
                    "not the amount contributed by one investor."
                )

    with shortlist_tab:
        st.caption(
            "Filter applications by sector, select startups and "
            "choose the fields you want to compare. Saved review "
            "statuses are shown below."
        )
        st.subheader("Applicant comparison")

        applicant_comparison = (
            build_applicant_comparison_dataframe(
                selected_application_year,
                dataframe,
            )
        )

        if applicant_comparison.empty:
            st.info(
                "No detailed application records are available "
                "for the selected application year."
            )
        else:
            sector_options = sorted(
                applicant_comparison["Sector / NACE"]
                .dropna()
                .astype(str)
                .unique()
                .tolist()
            )

            selected_comparison_sectors = st.multiselect(
                "Filter by sector",
                options=sector_options,
                key="comparison_sectors",
            )

            comparison_candidates = applicant_comparison.copy()

            if selected_comparison_sectors:
                comparison_candidates = comparison_candidates[
                    comparison_candidates["Sector / NACE"].isin(
                        selected_comparison_sectors
                    )
                ].copy()
            only_with_data_issues = st.checkbox(
                "Show only applications with data issues",
                value=False,
                key="comparison_only_data_issues",
            )
            issue_options = sorted({
                issue
                for value in comparison_candidates[
                    "Data Check Issues"
                ].fillna("")
                for issue in value.split(" | ")
                if issue
            })

            selected_data_issues = st.multiselect(
                "Filter by data issue",
                options=issue_options,
                key="comparison_data_issues",
            )

            if selected_data_issues:
                comparison_candidates = comparison_candidates[
                    comparison_candidates[
                        "Data Check Issues"
                    ].fillna("").map(
                        lambda value: any(
                            selected_issue
                            in value.split(" | ")
                            for selected_issue
                            in selected_data_issues
                        )
                    )
                ].copy()

            if only_with_data_issues:
                comparison_candidates = comparison_candidates[
                    comparison_candidates[
                        "Data Check Count"
                    ].gt(0)
                ].copy()

            if comparison_candidates.empty:
                st.info(
                    "No applications match the selected "
                    "sector and data-check filters."
                )

            startup_labels = {
                row["_selection_key"]: (
                    f"{row['Startup']} "
                    f"({row['Application Year']})"
                )
                for _, row in comparison_candidates.iterrows()
            }

            selected_applications = st.multiselect(
                "Select startups",
                options=list(startup_labels),
                format_func=lambda value: startup_labels[value],
                max_selections=10,
                key="comparison_applications",
            )

            hidden_columns = {
                "_company_key",
                "_selection_key",
                "Startup",
                "Application Year",
                "Sector / NACE",
            }

            available_comparison_columns = [
                column
                for column in applicant_comparison.columns
                if column not in hidden_columns
            ]

            default_comparison_columns = [
                "Startup Stage",
                "Management Team Size",
                "Active Customers",
                "MRR (USD)",
                "ARR (USD)",
                "Previously Funded",
                "Investment Expectation (USD)",
                "Aviation Experience",
                "Desired THY Partnership",
                "Review Status",
                "Investments Found",
                "Latest Investment Date",
                "Disclosed Deal Total (million USD)",
                "Funding Evidence",
                "Data Check Count",
                "Data Check Issues",
            ]

            selected_comparison_columns = st.multiselect(
                "Select comparison fields",
                options=available_comparison_columns,
                default=[
                    column
                    for column in default_comparison_columns
                    if column in available_comparison_columns
                ],
                key="comparison_fields",
            )

            st.metric(
                "Applications matching filters",
                len(comparison_candidates),
            )

            if not selected_applications:
                st.info(
                    "Select at least one startup to display "
                    "the comparison table."
                )
            elif not selected_comparison_columns:
                st.info(
                    "Select at least one comparison field."
                )
            else:
                selected_rows = comparison_candidates[
                    comparison_candidates["_selection_key"].isin(
                        selected_applications
                    )
                ].copy()

                visible_columns = [
                    "Startup",
                    "Application Year",
                    "Sector / NACE",
                    *selected_comparison_columns,
                ]

                comparison_table = selected_rows.reindex(
                    columns=visible_columns
                )

                st.dataframe(
                    comparison_table,
                    hide_index=True,
                    use_container_width=True,
                )

                st.subheader("Bulk review update")

                review_editor_columns = [
                    "Startup",
                    "Application Year",
                    "Review Status",
                    "Sources Verified",
                    "Review Note",
                ]

                review_editor_data = selected_rows.reindex(
                    columns=review_editor_columns
                ).copy()

                review_editor_data["Review Status"] = (
                    review_editor_data["Review Status"].replace(
                        "Not reviewed",
                        REVIEW_STATUSES[0],
                    )
                )

                selection_token = abs(
                    hash(tuple(selected_applications))
                )

                edited_reviews = st.data_editor(
                    review_editor_data,
                    hide_index=True,
                    use_container_width=True,
                    num_rows="fixed",
                    disabled=[
                        "Startup",
                        "Application Year",
                    ],
                    column_config={
                        "Review Status": (
                            st.column_config.SelectboxColumn(
                                "Review Status",
                                options=list(REVIEW_STATUSES),
                                required=True,
                            )
                        ),
                        "Sources Verified": (
                            st.column_config.CheckboxColumn(
                                "Sources Verified"
                            )
                        ),
                        "Review Note": (
                            st.column_config.TextColumn(
                                "Review Note",
                                width="large",
                            )
                        ),
                    },
                    key=(
                        f"bulk_review_editor_"
                        f"{selection_token}"
                    ),
                )

                if st.button(
                    "Save review updates",
                    type="primary",
                    key=(
                        f"save_bulk_reviews_"
                        f"{selection_token}"
                    ),
                ):
                    for _, edited_review in (
                        edited_reviews.iterrows()
                    ):
                        save_startup_review(
                            startup_name=(
                                edited_review["Startup"]
                            ),
                            application_year=int(
                                edited_review[
                                    "Application Year"
                                ]
                            ),
                            status=(
                                edited_review["Review Status"]
                            ),
                            note=str(
                                edited_review["Review Note"]
                                or ""
                            ),
                            source_verified=bool(
                                edited_review[
                                    "Sources Verified"
                                ]
                            ),
                        )

                    st.success(
                        f"Saved {len(edited_reviews)} "
                        "review updates."
                    )

                    st.session_state["_table_version"] = (
                        st.session_state.get(
                            "_table_version",
                            0,
                        ) + 1
                    )

                    st.rerun()

                st.download_button(
                    "Download selected comparison CSV",
                    data=prepare_csv(comparison_table),
                    file_name="applicant_comparison.csv",
                    mime="text/csv",
                    key="download_applicant_comparison",
                )

        st.divider()
        st.subheader("Saved review list")

        startup_reviews = get_all_startup_reviews(
            selected_application_year
        )
        valid_application_keys = {
            (
                row["_company_key"],
                row["Application Year"],
            )
            for _, row in applicant_comparison.iterrows()
        }

        startup_reviews = [
            review
            for review in startup_reviews
            if (
                review.normalized_startup_name,
                review.application_year,
            )
            in valid_application_keys
        ]

        review_rows = [
            {
                "_company_key": (
                    review.normalized_startup_name
                ),
                "Startup": review.startup_name,
                "Status": review.status,
                "Sources verified": (
                    "Yes" if review.source_verified else "No"
                ),
                "Note": review.note or "",
                "Last Updated": review.updated_at,
            }
            for review in startup_reviews
        ]

        shortlist = pd.DataFrame(
            review_rows,
            columns=[
                "_company_key",
                "Startup",
                "Status",
                "Sources verified",
                "Note",
                "Last Updated",
            ],
        )

        if shortlist.empty:
            st.info(
                "No startups have been added to the review list."
            )
        else:
            status_counts = shortlist["Status"].value_counts()

            status_columns = st.columns(len(REVIEW_STATUSES))

            for column, status in zip(
                    status_columns,
                    REVIEW_STATUSES,
            ):
                column.metric(
                    REVIEW_STATUS_LABELS.get(status, status),
                    int(status_counts.get(status, 0)),
                )

            unverified_count = int(
                shortlist["Sources verified"]
                .eq("No")
                .sum()
            )

            st.caption(
                f"Startups with unverified sources: "
                f"{unverified_count}"
            )

            st.divider()
            shortlist_search = st.text_input(
                "Search review list",
                key="shortlist_search",
            )

            shortlist_statuses = st.multiselect(
                "Review status",
                options=REVIEW_STATUSES,
                key="shortlist_statuses",
                format_func=lambda value: REVIEW_STATUS_LABELS.get(
                    value,
                    value,
                ),
            )

            if shortlist_search.strip():
                shortlist = shortlist[
                    shortlist["Startup"].str.contains(
                        shortlist_search.strip(),
                        case=False,
                        regex=False,
                        na=False,
                    )
                ]

            if shortlist_statuses:
                shortlist = shortlist[
                    shortlist["Status"].isin(
                        shortlist_statuses
                    )
                ]

            st.metric(
                "Startups in review list",
                len(shortlist),
            )

            table_version = st.session_state.get(
                "_table_version",
                0,
            )

            shortlist_display = shortlist.drop(
                columns=["_company_key"]
            ).copy()
            shortlist_display["Status"] = shortlist_display[
                "Status"
            ].map(
                lambda value: REVIEW_STATUS_LABELS.get(value, value)
            )

            event = st.dataframe(
                shortlist_display,
                hide_index=True,
                on_select="rerun",
                selection_mode="single-row",
                key=f"shortlist_table_{table_version}",
            )

            st.caption(
                "Select a row to open startup details."
            )

            if event.selection.rows:
                selected_position = event.selection.rows[0]
                selected_key = shortlist.iloc[
                    selected_position
                ]["_company_key"]

                available_company_keys = set(
                    dataframe["Startup"]
                    .fillna("")
                    .map(normalize_startup_name)
                )

                if selected_key not in available_company_keys:
                    st.warning(
                        "This startup has no investments under the current "
                        "year filter. Change the start year or select All years."
                    )
                else:
                    st.session_state["_selected_company"] = (
                        selected_key
                    )
                    st.rerun()

            st.download_button(
                "Download review list CSV",
                data=prepare_csv(
                    shortlist.drop(columns=["_company_key"])
                ),
                file_name="review_list.csv",
                mime="text/csv",
                key="download_shortlist",
            )

    with data_quality_tab:
        st.caption(
            "Investment records that could not be interpreted confidently "
            "or contain inconsistencies across sources. This view highlights "
            "records for human review; it does not make decisions."
        )

        review_data = dataframe.copy()

        review_data["Review Reason"] = review_data.apply(
            lambda row: " | ".join(get_review_reasons(row)),
            axis=1,
        )

        review_data = review_data[
            review_data["Review Reason"].ne("")
        ].copy()

        if review_data.empty:
            st.success(
                "No investment records require review under the current year filter."
            )
        else:
            review_reason_options = sorted({
                reason
                for value in review_data["Review Reason"]
                for reason in value.split(" | ")
            })

            selected_review_reasons = st.multiselect(
                "Review reason",
                options=review_reason_options,
                key="review_reasons",
            )

            review_search = st.text_input(
                "Search startups",
                key="review_search",
            )

            if selected_review_reasons:
                review_data = review_data[
                    review_data["Review Reason"].map(
                        lambda value: any(
                            reason in value.split(" | ")
                            for reason in selected_review_reasons
                        )
                    )
                ]

            if review_search.strip():
                review_data = review_data[
                    review_data["Startup"].str.contains(
                        review_search.strip(),
                        case=False,
                        regex=False,
                        na=False,
                    )
                ]

            first_column, second_column = st.columns(2)

            first_column.metric(
                "Investments requiring review",
                len(review_data),
            )

            second_column.metric(
                "Startups requiring review",
                review_data["Startup"]
                .fillna("")
                .map(normalize_startup_name)
                .nunique(),
            )

            review_columns = [
                "Startup",
                "Investment Date",
                "Reporting Period",
                "Investors",
                "Amount (million USD)",
                "Source Stage",
                "Review Reason",
                "Raw Amount",
                "Amount Warning",
                "Source",
            ]

            st.dataframe(
                review_data.reindex(columns=review_columns),
                hide_index=True,
                column_config={
                    "Source": st.column_config.LinkColumn(
                        "Open source"
                    ),
                },
            )

            st.download_button(
                "Download review queue CSV",
                data=prepare_csv(
                    review_data.reindex(columns=review_columns)
                ),
                file_name="investment_review_queue.csv",
                mime="text/csv",
                key="download_review_records",
            )
    with st.sidebar.expander(
            "Data coverage and methodology",
            expanded=False,
    ):
        st.write(
            "Results are limited to sources that could be accessed and imported."
        )
        st.write(
            "Source records describing the same investment are grouped by "
            "rules; original source records are never deleted."
        )
        st.write(
            "Transaction amounts are neither an individual investor's exact "
            "contribution nor a startup's complete funding total."
        )
        st.write(
            "Matches and automated labels should be verified by the user."
        )


if __name__ == "__main__":
    main()
