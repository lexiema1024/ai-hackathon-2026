"""
Payment Times Reports Register - preprocessing pipeline

Usage:
    python data_process.py raw.xlsx clean.xlsx

What this script does:
- Reads the Australian Government Payment Times Reports Register workbook.
- Automatically detects the real column-header row.
- Cleans all available relevant sheets without changing the raw file.
- Standardises column names.
- Preserves information unless it is an exact duplicate or an Excel index column.
- Keeps different reporting periods and revised/historical reports.
- Creates derived views for the hackathon:
    * standard_latest
    * historical_for_analysis
    * data_dictionary
    * cleaning_summary
"""

from pathlib import Path
import argparse
import re
import sys

import pandas as pd


SHEETS_TO_KEEP = [
    "Standard report",
    "Historical Reports",
    "Records of Non-compliance",
    "External Administration report",
    "Has Nominee report",
    "AASB8 report",
    "No SB procurement report",
    "Applications",
    "Notices",
]


# Long government descriptions -> stable names.
COLUMN_MAP = {
    # Identity / reporting
    "Reporting entity's name as registered on the Business Names Register.": "entity_name",
    "Australian Business Number, a unique 11 digit number that identifies businesses to the government and community.": "abn",
    "Australian Company Number, a unique 9 digit number assigned to companies not registered as companies.": "acn_arbn",
    "Australian Company Number, a unique 9 digit number that identifies companies. Australian Registered Body Number, a unique nine-digit number assigned to entities not registered as companies.": "acn_arbn",
    "The type of report that has been published.": "report_type",
    "The type of report that has been published. Eg Original, Original 1, Original 2, Revised, Revised 1": "report_type",
    "Start date of the reporting period covered in the report.": "period_start",
    "End date of the reporting period covered in the report.": "period_end",
    "Indicates when the report has been revised by the entity": "revised_by_entity",
    "Indicates if the report has been modified by the Regulator": "modified_by_regulator",
    "Date the report was submitted.": "report_submitted_date",

    # Standard report
    "Indicates whether the entity has offered supply chain finance arrangement during the reporting period": "supply_chain_finance_offered",
    "Indicates whether the entity charged fees as part of the procurement process": "procurement_fee_charged",
    "Indicates whether any Australian laws, voluntary codes or agreements impose requirements on the entity's payment times and practices to small businesses": "payment_time_legal_requirements",
    "Most Common Payment Term (Statistical Mode)": "common_payment_term_days",
    "Range Of Most Common Payment Terms - Minimum": "common_payment_term_min_days",
    "Range Of Most Common Payment Terms - Maximum": "common_payment_term_max_days",
    "Estimated Most Common Payment Term For Next Period": "estimated_common_payment_term_next_days",
    "Estimated Minimum Common Payment Terms Next Period": "estimated_common_payment_term_min_next_days",
    "Estimated Maximum Common Payment Terms Next Period": "estimated_common_payment_term_max_next_days",
    "Whether the standard(i.e. default) payment terms is longer or shorter than the common payment term.": "standard_vs_common_term",
    "Percentage of payments that had a payment time that was less than or equal to the payment term": "pct_paid_within_payment_term",
    "Average of all payment times.": "avg_payment_time_days",
    "Median of all payment times.": "median_payment_time_days",
    "80th percentile of payment times which represents the number of days it took to make 80% of the payments": "p80_payment_time_days",
    "95th percentile of payment times which represents the number of days it took to make 95% of the payments": "p95_payment_time_days",
    "The total NUMBER of small business invoices paid (within 30 calendar days) divided by the total NUMBER of all small business invoices paid over the reporting period, expressed as a percentage.": "pct_invoices_0_30_days",
    "The total NUMBER of small business invoices paid (between 31 - 60 calendar days) divided by the total NUMBER of all small business invoices paid over the reporting period, expressed as a percentage.": "pct_invoices_31_60_days",
    "The total NUMBER of small business invoices paid (in 60 or more calendar days) divided by the total NUMBER of all small business invoices paid over the reporting period, expressed as a percentage.": "pct_invoices_60_plus_days",
    "Value of all small business trade credit payments (including any partial small business trade credit payments) as a percentage of the total value of all trade credit payments(i.e. including to non-small business suppliers).": "pct_payment_value_to_small_business",
    "Number of payments that were 'Peppol eInvoice enabled' as a percentage of the total number of payments .": "pct_peppol_einvoice_enabled",
    "Any additional written information to provide context or explanation in relation to the information provided in the report.": "additional_information",
    "Description of changes. This field is mandatory when the report is revised.": "changes_description",
    "Description of the ANZSIC Subdivision for reporting entity's main industry or business activity. Codes are based on the ATO's Business Industry Codes.": "anzsic_subdivision",
    "Industry division for reporting entity's main industry or business activity. Codes are based on the ATO's Business Industry Codes.": "industry_division",

    # Historical report
    "Name of the reporting entity's controlling corporation, if applicable. A controlling corporation is an Australian body corporate that isn’t a subsidiary of another Australian body corporate.": "controlling_corporation_name",
    "ABN of controlling corporation, if applicable.": "controlling_corporation_abn",
    "ACN of controlling corporation, if applicable.": "controlling_corporation_acn",
    "Head entity name is included if the reporting entity is a member of a group of related entities (such as a partnership, trust or foreign group) and the head entity isn’t a controlling corporation.": "head_entity_name",
    "ABN of head entity, if applicable.": "head_entity_abn",
    "ACN of head entity, if applicable.": "head_entity_acn",
    "Code for reporting entity's main industry or business activity. Codes are based on the ATO's Business Industry Codes.": "industry_code",
    "Reporting entity's standard (i.e. default) payment terms offered in their contracts to their small business suppliers at the start of the reporting period (in calendar days). It doesn't account for any supply chain finance arrangements.": "standard_payment_term_days",
    "Changes to the standard (i.e. default) payment terms offered by the reporting entity over the 6 month reporting period (in calendar days). If no change to the standard payment terms, the same number is repeated.": "standard_payment_term_change_days",
    "Explanation of any changes to the standard (i.e. default) payment terms offered by the reporting entity over the 6 month reporting period.": "standard_payment_term_change_explanation",
    "Shortest standard (i.e. default) payment terms offered in contracts by the reporting entity at the start of the 6 month reporting period to their small business suppliers (in calendar days).": "shortest_standard_payment_term_days",
    "Changes to the shortest standard payment terms offered by the reporting entity over the 6 month reporting period (in calendar days).": "shortest_term_change_days",
    "Explanation of any changes to the shortest standard payment terms offered by the reporting entity during the 6 month reporting period.": "shortest_term_change_explanation",
    "Longest standard (i.e. default) payment terms offered in contracts by the reporting entity at the start of the 6 month reporting period to their small business suppliers (in calendar days).": "longest_standard_payment_term_days",
    "Changes to the longest standard payment terms offered by the reporting entity over the 6 month reporting period (in calendar days).": "longest_term_change_days",
    "Explanation of changes to the longest standard payment terms offered by the reporting entity during the 6 month reporting period.": "longest_term_change_explanation",
    "The total NUMBER of small business invoices paid (within 20 calendar days) divided by the total NUMBER of all small business invoices paid over the reporting period, expressed as a percentage.": "pct_invoice_count_0_20_days",
    "The total NUMBER of small business invoices paid (between 21 - 30 calendar days) divided by the total NUMBER of all small business invoices paid over the reporting period, expressed as a percentage.": "pct_invoice_count_21_30_days",
    "The total NUMBER of small business invoices paid (between 31 - 60 calendar days) divided by the total NUMBER of all small business invoices paid over the reporting period, expressed as a percentage.": "pct_invoice_count_31_60_days",
    "The total NUMBER of small business invoices paid (between 61 - 90 calendar days) divided by the total NUMBER of all small business invoices paid over the reporting period, expressed as a percentage.": "pct_invoice_count_61_90_days",
    "The total NUMBER of small business invoices paid (between 91 - 120 calendar days) divided by the total NUMBER of all small business invoices paid over the reporting period, expressed as a percentage.": "pct_invoice_count_91_120_days",
    "The total NUMBER of small business invoices paid (over 120 calendar days) divided by the total NUMBER of all small business invoices paid over the reporting period, expressed as a percentage.": "pct_invoice_count_120_plus_days",
    "The total VALUE of small business invoices paid (within 20 calendar days) divided by the total VALUE of all small business invoices paid over the reporting period, expressed as a percentage.": "pct_invoice_value_0_20_days",
    "The total VALUE of small business invoices paid (between 21 - 30 calendar days) divided by the total VALUE of all small business invoices paid over the reporting period, expressed as a percentage.": "pct_invoice_value_21_30_days",
    "The total VALUE of small business invoices paid (between 31 - 60 calendar days) divided by the total VALUE of all small business invoices paid over the reporting period, expressed as a percentage.": "pct_invoice_value_31_60_days",
    "The total VALUE of small business invoices paid (between 61 - 90 calendar days) divided by the total VALUE of all small business invoices paid over the reporting period, expressed as a percentage.": "pct_invoice_value_61_90_days",
    "The total VALUE of small business invoices paid (between 91 - 120 calendar days) divided by the total VALUE of all small business invoices paid over the reporting period, expressed as a percentage.": "pct_invoice_value_91_120_days",
    "The total VALUE of small business invoices paid (over 120 calendar days) divided by the total VALUE of all small business invoices paid over the reporting period, expressed as a percentage.": "pct_invoice_value_120_plus_days",
    "Details of any practices or arrangements used by the reporting entity during the reporting period for the receiving or paying of small business invoices.": "invoice_payment_practices",
    "Details of any practices or arrangements used by reporting entity during the reporting period that required small business suppliers to pay an amount, such as a subscription or membership fee, to participate in the reporting entity's procurement processes, including to lodge a tender.": "procurement_supplier_fees",
    "Details of any practices or arrangements used by entity during the reporting period requiring small business suppliers to pay an amount, such as a subscription or membership fee, for the reporting entity to accept an invoice issued by the small business supplier.": "invoice_acceptance_fees",
    "The total value of all procurement by the reporting entity during the reporting period that was from small business suppliers. Expressed as a percentage of all procurement by the reporting entity.": "pct_procurement_from_small_business",
    "A description of any supply chain finance arrangements that are provided or used by the reporting entity for small business suppliers.": "supply_chain_finance_description",
    "The total value of small business invoices where these supply chain finance arrangements were used. Expressed as a percentage of all small business invoices paid by the reporting entity.": "pct_scf_invoice_value",
    "The total number of small business invoices where these supply chain finance arrangements were used. Expressed as a percentage of all small busines invoices paid by the reporting entity.": "pct_scf_invoice_count",
    "Details of any benefits, including commissions or other payments, received by the reporting entity from the provider of any supply chain finance arrangements.": "scf_benefits",
    "Statement on whether small business suppliers were required to agree to use supply chain finance arrangements to participate in the reporting entity's procurement process or to receive payments for invoices during the reporting period.": "scf_required_for_suppliers",
    "The new start date of the reporting entity’s income year (accounting period). Only used if there has been a change.": "new_income_year_start",
    "Information about any changes to the reporting entity’s business name that occurred during the reporting period.": "business_name_changes",
    "Information about any changes to any member entities whose income was below $10 million in the two most recent income years. These entities will cease to be a reporting entity.": "member_entity_changes",
    'The "Original report date" value is derived from the CreatedOn date of the "Previous Report" field within the Resubmission fields': "original_report_date",
    'The "Revised report date" value is derived from the CreatedOn of the revised/resubmitted Report': "revised_report_date",
    'The "Changes from prior report" value is derived from the "Summary of Changes" field from the Resubmission.': "changes_from_prior_report",
    "Name of the principal governing body of the reporting entity. The principal governing body has primary responsibility for the governance of the reporting entity.": "principal_governing_body",
    "Description of the principal governing body of the reporting entity. The principal governing body has primary responsibility for the governance of the reporting entity.": "principal_governing_body_description",
    "Description of the ANZSIC code for reporting entity's main industry or business activity. Codes are based on the ATO's Business Industry Codes.": "anzsic_code_description",
    "Industry division code for reporting entity's main industry or business activity. Codes are based on the ATO's Business Industry Codes.": "industry_division_code",

    # Other sheets
    "The type of non compliance": "non_compliance_type",
    "External Administrator Appointment  type": "external_administrator_appointment_type",
    "Firm Name Of External Administrator": "external_administrator_firm",
    "External Administrator Appointment Date": "external_administrator_appointment_date",
    "Name of the Reporting Nominee": "reporting_nominee_name",
    "ABN of the Reporting Nominee": "reporting_nominee_abn",
    "ACN/ARBN of the Reporting Nominee": "reporting_nominee_acn_arbn",
    "The type of application report that has been accepted. Eg Single Extension, Modified Extension, Modifiable Extension, Volunteering Entity, Subsidiary Entity, Reporting Nominee or Exempt Entity": "application_type",
    "Approved report due date for the following applications: Single Extension, Modifiable Extension or Modified Extension": "approved_report_due_date",
    "Approved commencement date for the following application types: Volunteering Entity, Subsidiary Entity or Reporting Nominee": "approved_commencement_date",
    "Approved reporting period start date for eligible exempt applications": "approved_period_start",
    "Approved reporting period end date for eligible exempt applications": "approved_period_end",
    "The notice type that has been accepted. E.g. Reporting Entity Ceased (Entity) - s10H, Subsidiary Reporting Entity Determination Revoked (Entity) - s10G(3)": "notice_type",
}


# The government workbook has used short column names in some versions.
# These aliases make the script robust to both short and long header versions.
SHORT_COLUMN_MAP = {
    "business name": "entity_name",
    "business_name": "entity_name",
    "abn": "abn",
    "acn/arbn": "acn_arbn",
    "acn/arbn ": "acn_arbn",
    "type": "report_type",
    "report id": "report_id",
    "reportid": "report_id",
    "reporting period start date": "period_start",
    "reporting period end date": "period_end",
    "revised report": "revised_by_entity",
    "redacted report": "modified_by_regulator",
    "submitted date": "report_submitted_date",
    "supply chain finance offered": "supply_chain_finance_offered",
    "procurement fees charged": "procurement_fee_charged",
    "payment practices to small businesses - legal or voluntary obligations": "payment_time_legal_requirements",
    "common payment terms (days)": "common_payment_term_days",
    "common payment term (minimum)": "common_payment_term_min_days",
    "common payment term (maximum)": "common_payment_term_max_days",
    "forecast payment term": "estimated_common_payment_term_next_days",
    "forecast minimum payment term": "estimated_common_payment_term_min_next_days",
    "forecast maximum payment term": "estimated_common_payment_term_max_next_days",
    "receivable terms compared to common payment term": "standard_vs_common_term",
    "percentage of sb invoices paid within payment term": "pct_paid_within_payment_term",
    "average payment time (days)": "avg_payment_time_days",
    "median payment time (days)": "median_payment_time_days",
    "80th percentile payment time (days)": "p80_payment_time_days",
    "95th percentile payment time (days)": "p95_payment_time_days",
    "payments 30 days or less": "pct_invoices_0_30_days",
    "payments 31 - 60 days": "pct_invoices_31_60_days",
    "payments more than 60 days": "pct_invoices_60_plus_days",
    "percentage of small business trade credit payments": "pct_payment_value_to_small_business",
    "percentage peppol enabled small business procurement": "pct_peppol_einvoice_enabled",
    "report comments": "additional_information",
    "description of changes": "changes_description",
    "anzsic industry subdivision": "anzsic_subdivision",
    "industry division": "industry_division",
}


def clean_text(value):
    return re.sub(r"\s+", " ", str(value).strip()).lower()


def clean_name(name):
    """Create a stable snake_case name for an unmapped column."""
    s = str(name).strip()
    s = re.sub(r"[^0-9A-Za-z]+", "_", s).strip("_").lower()
    return s or "unnamed_column"


def detect_header_row(input_path, sheet_name):
    """
    Detect the actual column-header row.

    Some versions of the government workbook contain a descriptive row
    before the short machine-readable column names. We inspect the first
    few rows and choose the row containing familiar headers such as
    'Business Name' and 'ABN'.
    """
    preview = pd.read_excel(
        input_path,
        sheet_name=sheet_name,
        header=None,
        nrows=5,
    )

    for row_idx in range(len(preview)):
        values = {clean_text(v) for v in preview.iloc[row_idx].dropna()}
        if "business name" in values and "abn" in values:
            return row_idx

    # Fallback: use the first row if this sheet has no standard business-name/ABN header.
    return 0


def rename_columns(df):
    new_cols = []
    used = set()
    extra_n = 1

    for c in df.columns:
        original = str(c).strip()

        # Remove Excel-generated index columns.
        if original.lower().startswith("unnamed:"):
            new = None
        elif original in COLUMN_MAP:
            new = COLUMN_MAP[original]
        elif clean_text(original) in SHORT_COLUMN_MAP:
            new = SHORT_COLUMN_MAP[clean_text(original)]
        else:
            base = clean_name(original)
            new = f"extra_{base}"
            while new in used:
                extra_n += 1
                new = f"extra_{base}_{extra_n}"

        if new is not None:
            used.add(new)
        new_cols.append(new)

    keep = [i for i, x in enumerate(new_cols) if x is not None]
    out = df.iloc[:, keep].copy()
    out.columns = [new_cols[i] for i in keep]

    return out


def clean_common(df):
    df = rename_columns(df)

    # Remove rows that accidentally repeat the column names.
    # This protects against a descriptive/header row appearing inside the data.
    if "abn" in df.columns:
        abn_text = df["abn"].astype("string").str.strip().str.lower()
        df = df.loc[abn_text.ne("abn")].copy()

    # Preserve ABNs as strings.
    if "abn" in df.columns:
        df["abn"] = (
            df["abn"]
            .astype("string")
            .str.replace(r"\.0$", "", regex=True)
            .str.replace(r"\s+", "", regex=True)
            .str.strip()
        )

    # Parse only known date-like columns.
    date_columns = {
        c for c in df.columns
        if c.endswith("_date")
        or c in {
            "period_start",
            "period_end",
            "new_income_year_start",
            "approved_period_start",
            "approved_period_end",
            "approved_report_due_date",
            "approved_commencement_date",
        }
    }

    for c in date_columns:
        df[c] = pd.to_datetime(df[c], errors="coerce", format="mixed")

    # Remove completely empty rows.
    df = df.dropna(how="all").copy()

    # Remove exact duplicates only.
    # Do NOT remove same-company/same-period revised reports automatically.
    before = len(df)
    df = df.drop_duplicates(keep="last").reset_index(drop=True)
    exact_duplicates_removed = before - len(df)

    return df, exact_duplicates_removed


def add_record_keys(df):
    if "abn" in df.columns:
        df["entity_key"] = df["abn"].astype("string").str.strip()
    else:
        df["entity_key"] = pd.NA

    if "period_start" in df.columns and "period_end" in df.columns:
        df["reporting_period_key"] = (
            df["period_start"].dt.strftime("%Y-%m-%d").fillna("")
            + "__"
            + df["period_end"].dt.strftime("%Y-%m-%d").fillna("")
        )
    else:
        df["reporting_period_key"] = pd.NA

    df["entity_period_key"] = (
        df["entity_key"].fillna("")
        + "__"
        + df["reporting_period_key"].fillna("")
    )

    return df


def make_standard_latest(standard):
    """
    One row per ABN for the latest usable Standard report.
    The full Standard report remains available separately.
    """
    df = standard.copy()

    if "report_type" in df.columns:
        report_type = df["report_type"].astype("string").str.strip().str.lower()
        mask = report_type.eq("standard")
        if mask.any():
            df = df.loc[mask].copy()

    if "abn" not in df.columns:
        return df

    sort_columns = ["abn"]

    if "period_end" in df.columns:
        sort_columns.append("period_end")
    if "report_submitted_date" in df.columns:
        sort_columns.append("report_submitted_date")

    df = df.sort_values(sort_columns, na_position="first")
    latest = df.drop_duplicates(subset=["abn"], keep="last").reset_index(drop=True)
    latest["is_latest_standard_report"] = True

    return latest


def make_data_dictionary(frames):
    rows = []

    for sheet_name, df in frames.items():
        for col in df.columns:
            rows.append(
                {
                    "sheet": sheet_name,
                    "column": col,
                    "dtype": str(df[col].dtype),
                    "non_null_count": int(df[col].notna().sum()),
                    "null_pct": round(float(df[col].isna().mean() * 100), 2),
                    "unique_count": int(df[col].nunique(dropna=True)),
                }
            )

    return pd.DataFrame(rows)


def main(input_path, output_path):
    input_path = Path(input_path)
    output_path = Path(output_path)

    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    if output_path.suffix.lower() != ".xlsx":
        output_path = output_path.with_suffix(".xlsx")

    output_path.parent.mkdir(parents=True, exist_ok=True)

    print("=" * 60)
    print("Payment Times Reports Register - preprocessing")
    print("=" * 60)
    print(f"Input : {input_path.resolve()}")
    print(f"Output: {output_path.resolve()}")
    print()

    print("[1/5] Opening workbook...")
    xls = pd.ExcelFile(input_path)
    available = set(xls.sheet_names)
    print(f"      Found {len(xls.sheet_names)} sheets.")

    cleaned = {}
    cleaning_summary = []

    print("\n[2/5] Cleaning source sheets...")

    for sheet in SHEETS_TO_KEEP:
        if sheet not in available:
            print(f"      - {sheet}: not found, skipped")
            continue

        print(f"      - {sheet}: detecting header...")
        header_row = detect_header_row(input_path, sheet)
        raw = pd.read_excel(
            input_path,
            sheet_name=sheet,
            header=header_row,
        )

        rows_before = len(raw)
        df, exact_duplicates_removed = clean_common(raw)
        rows_after = len(df)
        df = add_record_keys(df)

        cleaned[sheet] = df

        cleaning_summary.append(
            {
                "sheet": sheet,
                "header_row_used_zero_indexed": header_row,
                "rows_before_cleaning": rows_before,
                "rows_after_cleaning": rows_after,
                "exact_duplicate_rows_removed": exact_duplicates_removed,
                "columns_after_cleaning": len(df.columns),
            }
        )

        print(
            f"        {rows_after:,} rows x {len(df.columns):,} columns"
        )

    print("\n[3/5] Creating derived views...")

    if "Standard report" in cleaned:
        cleaned["standard_latest"] = make_standard_latest(
            cleaned["Standard report"]
        )
        print(
            f"      - standard_latest: "
            f"{len(cleaned['standard_latest']):,} rows"
        )

    if "Historical Reports" in cleaned:
        hist = cleaned["Historical Reports"].copy()

        sort_columns = [c for c in ["abn", "period_end"] if c in hist.columns]
        if sort_columns:
            hist = hist.sort_values(sort_columns, na_position="first")

        cleaned["historical_for_analysis"] = hist
        print(
            f"      - historical_for_analysis: "
            f"{len(hist):,} rows"
        )

    print("\n[4/5] Creating metadata...")
    data_dictionary = make_data_dictionary(cleaned)
    cleaning_summary = pd.DataFrame(cleaning_summary)

    print("\n[5/5] Writing cleaned workbook...")
    with pd.ExcelWriter(output_path, engine="openpyxl") as writer:
        for sheet_name, df in cleaned.items():
            df.to_excel(
                writer,
                sheet_name=sheet_name[:31],
                index=False,
            )

        data_dictionary.to_excel(
            writer,
            sheet_name="data_dictionary",
            index=False,
        )

        cleaning_summary.to_excel(
            writer,
            sheet_name="cleaning_summary",
            index=False,
        )

    print()
    print("=" * 60)
    print(f"SUCCESS: {output_path.resolve()}")
    print("=" * 60)
    print("\nSheets created:")
    for sheet_name, df in cleaned.items():
        print(
            f"  - {sheet_name}: "
            f"{len(df):,} rows x {len(df.columns):,} columns"
        )

    print("\nCleaning rules:")
    print("  - Empty rows removed")
    print("  - Exact duplicate rows removed")
    print("  - Repeated ABNs were NOT treated as duplicates")
    print("  - Historical/revised reports were retained")
    print("  - Excel index columns were removed")
    print("  - ABNs were preserved as strings")
    print("  - Date fields were standardised")
    print("  - Unmapped columns were preserved as extra_*")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Clean the Australian Government Payment Times Reports Register."
    )
    parser.add_argument(
        "input",
        help="Original government Excel file, e.g. raw.xlsx",
    )
    parser.add_argument(
        "output",
        help="Output cleaned Excel file, e.g. clean.xlsx",
    )

    args = parser.parse_args()

    try:
        main(args.input, args.output)
    except Exception as exc:
        print(f"\nERROR: {exc}", file=sys.stderr)
        sys.exit(1)
