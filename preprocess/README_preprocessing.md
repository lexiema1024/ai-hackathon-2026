Payment Times Data — Preprocessing

This folder contains the preprocessing pipeline for the Australian Government Payment Times Reports Register data used by the hackathon.

What this module does

The preprocessing pipeline converts the original government Excel workbook into a cleaner, analysis-ready Excel workbook without throwing away potentially useful information.

Main steps:

Read the original workbook.

Keep the relevant government report sheets.

Convert long government column descriptions into stable snake_case column names.

Remove Excel index columns and completely empty rows.

Remove the repeated column-name row contained in the source workbook.

Standardise ABNs as strings so identifiers are not accidentally converted to numbers.

Parse known date fields consistently.

Remove exact duplicate rows only.

Keep different reporting periods and revised/historical reports.

Add entity/reporting-period keys for downstream analysis.

Create derived views for the hackathon, especially standard_latest and historical_for_analysis.

Create data_dictionary and cleaning_summary sheets.

Files

preprocessing/
├── data_process.py
├── clean.xlsx
└── README.md

raw.xlsx is the original government dataset and should normally stay outside the Git repository if it is too large. The raw source is never modified by the script.

How to run

From this folder:

python data_process.py raw.xlsx clean.xlsx

If the raw file is stored elsewhere, use its path:

python data_process.py "C:\path\to\raw.xlsx" clean.xlsx

The script prints progress while processing and finishes with the exact output path and a list of sheets created.

Dataset structure

The cleaned workbook contains source sheets plus derived analysis sheets.

1. Standard report

What it contains

Current/standard payment-time reporting information for reporting entities, including:

Business identity (entity_name, abn, acn_arbn)

Report type and reporting period

Common payment terms

Average and median payment time

80th and 95th percentile payment time

Percentage of invoices paid within 30 days, 31–60 days, and over 60 days

Percentage paid within the payment term

Supply-chain-finance information

Procurement-fee information

Industry information

Report comments and changes

Why it matters

This is the main source for the company's current observed payment behaviour.

For the hackathon's payment-risk MVP, this is one of the most important sheets.

2. standard_latest

What it contains

A derived table containing the latest usable Standard report for each ABN.

The original Standard report sheet is preserved; this sheet is only a convenient analysis view.

Why it matters

This should normally be the first sheet used for a current company risk assessment.

Example workflow:

Company name / ABN
        ↓
Find company in standard_latest
        ↓
Read latest payment behaviour
        ↓
Use historical_for_analysis for trend
        ↓
Compare with industry
        ↓
Calculate payment risk

Important: repeated ABNs in the original data are not automatically duplicates. Different reporting periods and revised reports can be meaningful.

3. Historical Reports

What it contains

Historical payment reporting information across reporting periods, including:

Standard payment terms

Changes to standard terms

Shortest and longest standard terms

Invoice-count payment-time distributions

Invoice-value payment-time distributions

Invoice/payment practices

Procurement fees

Supply chain finance

Small-business procurement percentages

Business-name and reporting changes

Historical report/revision information

Industry information

Why it matters

Use this sheet to understand how payment behaviour has changed over time.

A company that recently moved from 25 days to 45 days may be more concerning than a company that has consistently paid around 45 days.

4. historical_for_analysis

What it contains

A derived analysis view of Historical Reports, sorted by entity and reporting period.

Why it matters

This is the convenient table to use when building historical features such as:

Payment-time trend

Improving vs worsening behaviour

Stability/volatility

Changes in payment terms

Changes in late-payment proportions

The original Historical Reports remains available when full detail is required.

5. Records of Non-compliance

What it contains

Records relating to reported non-compliance, including the entity, ABN, type of non-compliance and related reporting information.

Why it matters

This can be used as an additional regulatory risk signal.

It should not automatically determine the payment-risk score by itself. It is better treated as supporting evidence.

6. External Administration report

What it contains

Information about external administration appointments associated with reporting entities, including appointment type, administrator firm and appointment date.

Why it matters

External administration can be a potentially important financial-distress signal.

For the MVP, it can be an optional high-risk flag rather than a primary feature.

7. Has Nominee report

What it contains

Information about reporting nominees, including nominee name and identifying information.

Why it matters

This is mainly structural/reporting information. It may help explain how a reporting entity is represented in the reporting scheme, but it is not a core payment-risk feature.

8. AASB8 report

What it contains

Additional reporting information associated with AASB 8, including payment metrics and operating-segment-related information where available.

Why it matters

This is supplementary information that may help with more detailed analysis of complex businesses or business segments.

It is not required for the first payment-risk MVP.

9. No SB procurement report

What it contains

Reports associated with entities that do not have the relevant small-business procurement reporting activity.

Why it matters

This is mainly a context/data-availability signal. It should not be interpreted automatically as high payment risk.

10. Applications

What it contains

Accepted applications associated with reporting obligations, including extensions, modified reporting arrangements, volunteering/subsidiary entities, nominees and exempt entities where applicable.

Why it matters

Useful for understanding reporting status and exceptions. It is secondary to actual payment behaviour for the MVP.

11. Notices

What it contains

Accepted regulatory notices relating to reporting entities.

Why it matters

Potentially useful as additional context or regulatory signals. It should be interpreted together with the actual payment data.

12. data_dictionary

What it contains

A machine-readable summary of every column in every cleaned/derived sheet, including:

Sheet name

Column name

Data type

Non-null count

Null percentage

Number of unique values

Why it matters

This is especially useful when giving the dataset to another AI model. The AI can use this sheet to understand the available variables instead of guessing what a column means.

13. cleaning_summary

What it contains

For each source sheet:

Number of rows before cleaning

Number of rows after cleaning

Number of empty/exact-duplicate rows removed

Why it matters

This provides a quick data-quality/audit trail for the preprocessing step.

Key risk features

For the payment-risk MVP, the most useful current-period variables are:

Column

Meaning

Risk use

avg_payment_time_days

Average number of days taken to pay

Core payment-speed signal

median_payment_time_days

Median payment time

Typical payment behaviour

p80_payment_time_days

Payment time by which 80% of payments were made

Captures slower tail

p95_payment_time_days

Payment time by which 95% of payments were made

Captures extreme late-payment behaviour

pct_invoices_0_30_days

% paid within 30 days

Positive/negative payment-speed signal

pct_invoices_31_60_days

% paid in 31–60 days

Delayed-payment signal

pct_invoices_60_plus_days

% paid after 60 days

Strong late-payment signal

pct_paid_within_payment_term

% paid within the stated payment term

Contract-performance signal

common_payment_term_days

Most common payment term

Expected contractual timing

standard_vs_common_term

Whether standard/default terms are longer or shorter than common terms

Terms context

industry_division

Main industry

Industry benchmarking

period_end

End of reporting period

Recency/trend

Historical variables can then be used to build trend and stability features.

Important interpretation rules

1. ABN is the main entity identifier

Use abn / entity_key to identify a company across reports whenever possible.

Company names can change. Do not use company name alone as the entity key when an ABN is available.

2. Do not treat repeated ABNs as duplicates

The same ABN can legitimately appear in multiple reporting periods or in revised reports.

Only exact duplicate rows should be removed automatically.

3. standard_latest is a derived convenience table

It is not a replacement for the historical data.

Use:

standard_latest → current risk assessment

historical_for_analysis → trend/history

Standard report / Historical Reports → full source detail

4. This dataset is NOT a default-prediction dataset

The data records observed payment behaviour. It does not provide a direct target variable saying that a company defaulted on a contract.

Therefore, do not make unsupported claims such as:

"This company has a 73% probability of default."

Unless the team later builds a properly labelled model, the product should be described as an:

AI Payment Risk Assessment based on observed payment behaviour

rather than a credit-default prediction model.

Recommended AI analysis workflow

When an AI model is given a prospective customer's information, use this order:

Identify the entity using ABN where possible.

Retrieve the latest record from standard_latest.

Examine average, median, P80 and P95 payment times.

Examine the proportions paid within 30 days, 31–60 days and over 60 days.

Compare actual payment behaviour with the stated/common payment term.

Compare the company with its industry where an appropriate benchmark is available.

Use historical_for_analysis to determine whether payment behaviour is improving, worsening or stable.

Optionally check non-compliance and external-administration information for additional signals.

Combine the evidence into an explainable risk assessment.

Recommend practical contract/payment safeguards for the small business supplier.

AI prompt template

The following context can be given to another AI together with the relevant rows from the cleaned dataset:

You are analysing the Australian Government Payment Times Reports Register dataset.

This dataset describes large businesses' observed payment practices to small business suppliers.

Important rules:
- Use ABN as the primary entity identifier where available.
- Do not treat repeated ABNs as duplicates; different reporting periods and revised reports can contain meaningful information.
- Use standard_latest for the latest current Standard report.
- Use historical_for_analysis for payment-behaviour trends.
- Use the data_dictionary to understand column definitions.
- The dataset does NOT contain a direct credit-default label.
- Do not claim that the data gives a probability of default unless a separate, properly labelled model has been built.
- Assess payment risk from observed payment behaviour and supporting signals.
- Distinguish facts directly supported by the dataset from inference.

For the selected company, analyse:
1. Average payment time
2. Median payment time
3. P80 payment time
4. P95 payment time
5. Percentage paid within 30 days
6. Percentage paid in 31–60 days
7. Percentage paid after 60 days
8. Percentage paid within the payment term
9. Common payment term
10. Historical trend
11. Industry comparison
12. Optional regulatory/distress signals

Return:
- Overall payment-risk level: Low / Medium / High
- Key evidence
- Positive signals
- Risk signals
- Historical trend
- Industry comparison
- Recommended payment terms or safeguards for a small-business supplier

Do not invent missing data. If a field is unavailable, say so explicitly.

Recommended role of this folder in the main repository

The main repository can treat this as a self-contained preprocessing module:

project-root/
├── preprocessing/
│   ├── data_process.py
│   ├── clean.xlsx
│   └── README.md
├── backend/
├── frontend/
├── ...
└── README.md

The root README should explain the whole hackathon product. This README should explain only the data/preprocessing component.