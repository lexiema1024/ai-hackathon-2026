"""
Mock data + mock "ML" for the PayLens prototype.

EVERYTHING in this file is demonstration data. The companies are fictional
and deliberately named "Demo…", "Example…" or "Sample…" so nobody mistakes
them for real organisations.

The public functions below return exactly the structures the real services
(Payment Times data + trained payment-delay model) are expected to return:

    search_company(query)            -> list[dict]
    get_company_features(company_id) -> dict | None
    get_company_history(company_id)  -> list[dict]
    predict_payment_risk(features)   -> dict

To go live, implement the same functions in a new module (for example
``src/real_services.py``) and point ``src/services.py`` at it. The UI only
ever talks to ``src/services.py``.
"""

from __future__ import annotations

import math
import re
from typing import Optional

# ---------------------------------------------------------------------------
# Demo dataset
# ---------------------------------------------------------------------------
# pct_* are shares of invoices (by count) paid in each window. They sum to 1.
# peer_slower_than_pct: share of comparable businesses this customer is SLOWER
# than (0.72 -> "slower than 72% of comparable businesses").

_COMPANIES: list[dict] = [
    {
        "company_id": "demo-logistics",
        "name": "Demo Logistics Group",
        "abn": "00 100 200 301",
        "industry": "Transport, postal & warehousing",
        "size_band": "Large business",
        "pct_within_30": 0.31,
        "pct_31_60": 0.49,
        "pct_over_60": 0.20,
        "avg_days_to_pay": 47,
        "trend": "worsening",
        "trend_delta_days": 9,
        "peer_slower_than_pct": 0.72,
        "peer_group": "Transport, postal & warehousing",
        "history_days": [36, 38, 39, 42, 45, 47],
    },
    {
        "company_id": "demo-retail",
        "name": "Demo Retail Holdings",
        "abn": "00 100 200 302",
        "industry": "Retail trade",
        "size_band": "Large business",
        "pct_within_30": 0.52,
        "pct_31_60": 0.36,
        "pct_over_60": 0.12,
        "avg_days_to_pay": 36,
        "trend": "stable",
        "trend_delta_days": 1,
        "peer_slower_than_pct": 0.55,
        "peer_group": "Retail trade",
        "history_days": [35, 37, 36, 35, 36, 36],
    },
    {
        "company_id": "example-infrastructure",
        "name": "Example Infrastructure Ltd",
        "abn": "00 100 200 303",
        "industry": "Construction",
        "size_band": "Large business",
        "pct_within_30": 0.18,
        "pct_31_60": 0.44,
        "pct_over_60": 0.38,
        "avg_days_to_pay": 61,
        "trend": "worsening",
        "trend_delta_days": 14,
        "peer_slower_than_pct": 0.88,
        "peer_group": "Construction",
        "history_days": [47, 50, 52, 55, 58, 61],
    },
    {
        "company_id": "sample-corporate",
        "name": "Sample Corporate Services",
        "abn": "00 100 200 304",
        "industry": "Professional, scientific & technical services",
        "size_band": "Large business",
        "pct_within_30": 0.78,
        "pct_31_60": 0.18,
        "pct_over_60": 0.04,
        "avg_days_to_pay": 24,
        "trend": "improving",
        "trend_delta_days": -6,
        "peer_slower_than_pct": 0.21,
        "peer_group": "Professional services",
        "history_days": [30, 29, 27, 26, 25, 24],
    },
    {
        "company_id": "demo-health",
        "name": "Demo Health Partners",
        "abn": "00 100 200 305",
        "industry": "Health care & social assistance",
        "size_band": "Large business",
        "pct_within_30": 0.66,
        "pct_31_60": 0.26,
        "pct_over_60": 0.08,
        "avg_days_to_pay": 29,
        "trend": "stable",
        "trend_delta_days": 0,
        "peer_slower_than_pct": 0.38,
        "peer_group": "Health care",
        "history_days": [29, 30, 28, 29, 30, 29],
    },
    {
        # Deliberately incomplete record: exercises "missing industry",
        # "missing history" and "no peer comparison" states in the UI.
        "company_id": "sample-manufacturing",
        "name": "Sample Manufacturing Co",
        "abn": "00 100 200 306",
        "industry": None,
        "size_band": "Large business",
        "pct_within_30": 0.60,
        "pct_31_60": 0.30,
        "pct_over_60": 0.10,
        "avg_days_to_pay": 33,
        "trend": None,
        "trend_delta_days": None,
        "peer_slower_than_pct": None,
        "peer_group": None,
        "history_days": None,
    },
]

_PERIODS = ["H2 2023", "H1 2024", "H2 2024", "H1 2025", "H2 2025", "H1 2026"]
_BY_ID = {c["company_id"]: c for c in _COMPANIES}

DATA_AS_OF = "Demo dataset · H1 2026 reporting period"
MODEL_NAME = "mock-logistic-v0 (demo)"


def _digits(value: str) -> str:
    return re.sub(r"\D", "", value or "")


def _public_company(c: dict) -> dict:
    return {
        "company_id": c["company_id"],
        "name": c["name"],
        "abn": c.get("abn"),
        "industry": c.get("industry"),
        "size_band": c.get("size_band"),
        "is_demo": True,
    }


# ---------------------------------------------------------------------------
# Public interface
# ---------------------------------------------------------------------------

def search_company(query: str) -> list:
    """Case-insensitive search over name, industry and ABN digits.

    Returns [] for an empty query. Name prefix matches rank first.
    """
    q = (query or "").strip().lower()
    if not q:
        return []
    q_digits = _digits(q)
    tokens = [t for t in re.split(r"\s+", q) if t]

    scored = []
    for c in _COMPANIES:
        name = c["name"].lower()
        haystack = " ".join([name, (c.get("industry") or "").lower()])
        abn_digits = _digits(c.get("abn") or "")
        hit_text = all(t in haystack for t in tokens)
        hit_abn = len(q_digits) >= 3 and q_digits in abn_digits and q_digits == q.replace(" ", "")
        if not (hit_text or hit_abn):
            continue
        rank = 0 if name.startswith(q) else 1 if q in name else 2
        scored.append((rank, c["name"], c))
    scored.sort(key=lambda x: (x[0], x[1]))
    return [_public_company(c) for _, _, c in scored[:8]]


def list_suggested_companies() -> list:
    """Demo-only helper for the empty state ("Try a demo customer")."""
    return [_public_company(c) for c in _COMPANIES]


def get_company_features(company_id: str) -> Optional[dict]:
    """Model-ready features for one company, or None if unknown."""
    c = _BY_ID.get(company_id)
    if c is None:
        return None
    return {
        "company_id": c["company_id"],
        "name": c["name"],
        "abn": c.get("abn"),
        "industry": c.get("industry"),
        "size_band": c.get("size_band"),
        "pct_within_30": c.get("pct_within_30"),
        "pct_31_60": c.get("pct_31_60"),
        "pct_over_60": c.get("pct_over_60"),
        "avg_days_to_pay": c.get("avg_days_to_pay"),
        "trend": c.get("trend"),
        "trend_delta_days": c.get("trend_delta_days"),
        "peer_slower_than_pct": c.get("peer_slower_than_pct"),
        "peer_group": c.get("peer_group"),
        "data_as_of": DATA_AS_OF,
        "is_demo": True,
    }


def get_company_history(company_id: str) -> list:
    """Average days-to-pay per reporting period, oldest first. [] if none."""
    c = _BY_ID.get(company_id)
    if not c or not c.get("history_days"):
        return []
    return [
        {"period": p, "avg_days_to_pay": d}
        for p, d in zip(_PERIODS, c["history_days"])
    ]


def _level_for_probability(p: float) -> str:
    if p < 0.30:
        return "LOW"
    if p < 0.55:
        return "MODERATE"
    if p < 0.80:
        return "HIGH"
    return "CRITICAL"


def predict_payment_risk(features: dict) -> dict:
    """Mock payment-delay model: a fixed logistic function of the features.

    Stand-in for the trained model. Returns:
        probability  float 0-1  chance that payment runs materially late
        level        LOW | MODERATE | HIGH | CRITICAL
        factors      up to 3 {"text", "tone"} explanations
        confidence   "standard" | "limited"
        model        model identifier
        is_mock      True
    """
    f = features or {}
    missing = []

    def val(key, default):
        v = f.get(key)
        if v is None or (isinstance(v, float) and math.isnan(v)):
            missing.append(key)
            return default
        return v

    p31 = float(val("pct_31_60", 0.30))
    p60 = float(val("pct_over_60", 0.10))
    peer = float(val("peer_slower_than_pct", 0.50))
    trend = val("trend", None)
    trend_num = {"worsening": 1.0, "stable": 0.0, "improving": -1.0}.get(trend, 0.0)

    z = -2.8 + 2.2 * p31 + 6.0 * p60 + 1.6 * peer + 0.5 * trend_num
    prob = 1.0 / (1.0 + math.exp(-z))
    prob = min(max(prob, 0.02), 0.98)

    # --- explanations (max 3), strongest signals first -------------------
    candidates = []
    if trend == "worsening":
        candidates.append((0.9, "Payment speed has deteriorated over recent periods", "negative"))
    elif trend == "improving":
        candidates.append((0.5, "Payment speed has improved over recent periods", "positive"))
    elif trend == "stable":
        candidates.append((0.35, "Payment speed has been broadly stable", "neutral"))
    if p60 >= 0.15:
        candidates.append((p60 * 4, f"A relatively high share of payments ({p60:.0%}) exceed 60 days", "negative"))
    elif p60 <= 0.06 and "pct_over_60" not in missing:
        candidates.append((0.4, f"Few payments ({p60:.0%}) run beyond 60 days", "positive"))
    if "peer_slower_than_pct" not in missing:
        if peer >= 0.6:
            candidates.append((peer, f"Payment behaviour is slower than {peer:.0%} of peers", "negative"))
        elif peer <= 0.4:
            candidates.append((1 - peer, "Pays faster than most comparable businesses", "positive"))
        else:
            candidates.append((0.4, "Payment speed is broadly in line with peers", "neutral"))
    within30 = f.get("pct_within_30")
    if within30 is not None and within30 >= 0.6:
        candidates.append((within30 * 0.8, f"Most invoices ({within30:.0%}) are paid within 30 days", "positive"))
    elif within30 is not None and within30 < 0.35:
        candidates.append((0.7, f"Only {within30:.0%} of invoices are paid within 30 days", "negative"))
    elif within30 is not None:
        candidates.append((0.45, f"About {within30:.0%} of invoices are paid within 30 days", "neutral"))
    if missing:
        candidates.append((0.3, "Limited history available — estimate uses sector defaults", "neutral"))

    candidates.sort(key=lambda c: -c[0])
    factors = [{"text": t, "tone": tone} for _, t, tone in candidates[:3]]

    return {
        "probability": round(prob, 3),
        "level": _level_for_probability(prob),
        "factors": factors,
        "confidence": "limited" if missing else "standard",
        "model": MODEL_NAME,
        "is_mock": True,
    }
