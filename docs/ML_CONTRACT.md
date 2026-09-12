# PayLens ML Data Contract

Status: **Draft pending processed dataset from the data owner**

This document defines the handoff between the data pipeline and the payment-delay risk model. It intentionally does not invent the source dataset schema.

## Product boundary

The model estimates **payment-delay risk** for a prospective customer from historical reporting data. It does not estimate bankruptcy, insolvency, default, profitability, cash reserves, or contract exposure.

Contract value, available cash, monthly operating costs, upfront payment, and payment terms belong to the contract exposure engine. They must not be model features.

## Required data-owner handoff

The data owner must provide:

- A processed CSV or DataFrame sample and its file path
- A data dictionary with source meaning and units for every column
- The company identifier column
- The reporting-period column and its ordering rule
- The columns containing payment timing behaviour
- Row count, company count, and reporting-period coverage
- Missing-value summary
- Duplicate-row summary
- Any known fields that contain future or post-period information

## Training row definition

Pending confirmation from the dataset audit:

- Entity: one company in one reporting period
- Observation time: the reporting period represented by that row
- Features: values available at the end of period `t`
- Label: the same company's payment-delay outcome in the next available period `t+1`

Rows without a next period for the same company are not labelled training examples. They may still be used for inference if the required features are present.

## Candidate model features

Use only fields confirmed by the data audit. The preferred semantic feature names are:

```python
MODEL_FEATURES = [
    "pct_paid_30",
    "pct_paid_31_60",
    "pct_paid_over_60",
    "avg_days_to_pay",
    "payment_trend",
    "payment_volatility",
    "industry_percentile",
    "num_reporting_periods",
]
```

These names are a proposed canonical model schema, not claims about the source dataset. The feature adapter may map source columns to these names after the data audit.

Do not include:

- Any value from period `t+1` or later
- Future-derived aggregates
- Contract fields or small-business financial inputs
- Post-outcome fields
- Manually entered risk labels

## Target definition

Proposed target, pending class-balance review:

```text
high_payment_delay_next_period = 1
when next-period pct_paid_over_60 >= the agreed threshold
```

The threshold must be selected after inspecting the real target distribution. Record the final threshold and its rationale here before training. The final label must have enough positive and negative examples for temporal evaluation.

If the source data does not contain `pct_paid_over_60`, select an equivalent target based on an observed payment-delay field and document the mapping. Do not silently substitute default, bankruptcy, or insolvency terminology.

## Leakage audit checklist

Before training, mark each item as PASS or FAIL with evidence:

- [ ] Company identifier is used only for grouping and joins, not as a numeric predictor
- [ ] Reporting periods are parsed and sorted chronologically
- [ ] Every feature is available no later than period `t`
- [ ] The target is taken only from period `t+1`
- [ ] No full-dataset aggregate uses future periods when constructing a row
- [ ] No duplicate company-period rows remain
- [ ] No contract exposure fields enter the model
- [ ] Imputation and encoding are fitted on training data only
- [ ] Test periods occur after training periods
- [ ] The target threshold is chosen without using test labels

## Temporal split

Preferred split:

```text
oldest periods -> train
middle periods -> validation
latest periods -> test
```

The exact periods and row counts must be recorded after the audit. If the dataset is too shallow for three temporal windows, use the latest available period as test and report that evaluation is directional.

A test split is only suitable for ROC-AUC when it contains both positive and negative labels. Always report positive and negative counts alongside metrics.

## Model output contract

The model adapter must return the existing UI-compatible shape:

```python
{
    "probability": 0.0,  # inclusive range [0, 1]
    "level": "LOW",      # LOW | MODERATE | HIGH | CRITICAL
    "factors": [
        {"text": "...", "tone": "negative"}
    ],                    # maximum three items
    "confidence": "standard",  # or "limited"
    "model": "logistic-v1",
    "is_mock": False,
}
```

If the trained model or required features are unavailable, use a documented historical-risk fallback with `confidence: "limited"`. The application must remain usable.

## Pending decisions

- [ ] Confirm source file and schema
- [ ] Confirm company identifier
- [ ] Confirm reporting-period field and ordering
- [ ] Confirm target field and threshold
- [ ] Confirm final feature mapping
- [ ] Confirm train/validation/test periods
- [ ] Record leakage-audit evidence
- [ ] Record baseline and model metrics
