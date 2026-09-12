"""Deterministic, plain-English recommendations. No guarantees, no advice
beyond what the numbers support."""

from __future__ import annotations

from typing import Optional

from src.formatting import fmt_currency
from src.risk_engine import LEVEL_RANK


def _title_level(level: str) -> str:
    return level.capitalize()


def build_recommendations(current: dict, revised: Optional[dict] = None,
                          suggestion: Optional[dict] = None, limit: int = 4) -> list:
    """Return up to ``limit`` recommendations as {title, body, tone}.

    ``current`` / ``revised`` are analyse_contract() results; ``suggestion``
    is risk_engine.suggest_structure() output for the current deal.
    """
    target = revised or current
    inp = target["inputs"]
    recs = []

    # 1. Outcome of restructuring
    if revised is not None:
        delta = current["score"] - revised["score"]
        dropped = LEVEL_RANK[revised["level"]] < LEVEL_RANK[current["level"]]
        if delta >= 5 and dropped:
            recs.append((100, {
                "title": "This revised structure materially reduces your exposure",
                "body": f"Exposure falls from {current['score']} to {revised['score']} "
                        f"({_title_level(current['level'])} → {_title_level(revised['level'])}) "
                        "with the same customer. Use these terms as your negotiating position.",
                "tone": "positive"}))
        elif delta >= 5:
            recs.append((90, {
                "title": "The revised terms help, but exposure remains "
                         f"{_title_level(revised['level']).lower()}",
                "body": f"Exposure falls by {delta} points. Combine several levers to move "
                        "into a lower band.",
                "tone": "neutral"}))
        elif delta <= -5:
            recs.append((95, {
                "title": "These revised terms increase your exposure",
                "body": "Longer terms or a smaller upfront payment leave more of your working "
                        "capital tied up in this customer.",
                "tone": "negative"}))

    if target["flags"]["no_contract"]:
        return [r for _, r in sorted(recs, key=lambda x: -x[0])][:limit]

    # 2. Upfront payment
    if inp["upfront_pct"] < 0.2 and target["score"] >= 56:
        body = "An upfront or deposit payment reduces the amount outstanding and adds to your cash buffer."
        if suggestion and suggestion.get("status") == "upfront":
            s = suggestion["suggestion"]
            body = (f"Around {s['upfront_pct']}% upfront would bring exposure to "
                    f"{_title_level(s['level'])} at {s['terms']}-day terms, under current assumptions.")
        recs.append((80, {"title": "Consider requesting a higher upfront payment",
                          "body": body, "tone": "action"}))

    # 3. Payment terms
    if inp["payment_terms_days"] > 30 and target["score"] >= 31:
        recs.append((70, {
            "title": "Negotiate shorter payment terms",
            "body": f"Moving from {inp['payment_terms_days']}-day to 30-day terms could reduce the "
                    "time your working capital remains exposed.",
            "tone": "action"}))

    # 4. Contract size vs cash
    ratio = target["contract_to_cash_ratio"]
    if (ratio is None and target["net_exposure"] > 0) or (ratio is not None and ratio >= 1):
        recs.append((75, {
            "title": "Reduce initial exposure or use staged billing",
            "body": "The contract is large relative to your current cash position. Milestone "
                    "invoices keep less money outstanding at any one time.",
            "tone": "action"}))

    # 5. Runway check
    runway = target["effective_runway_months"]
    months_out = target["expected_days_outstanding"] / 30.0
    if runway is not None and target["net_exposure"] > 0 and runway < months_out:
        recs.append((65, {
            "title": "Line up a cash buffer before you start",
            "body": f"Your cash covers about {runway:.1f} months of costs, less than the "
                    f"~{target['expected_days_outstanding']:.0f} days you may wait to be paid. "
                    "Consider a finance facility or delaying other commitments.",
            "tone": "action"}))

    # 6. Customer risk
    p = inp["payment_probability"]
    if p >= 0.55 and target["score"] >= 31:
        recs.append((55, {
            "title": "Protect yourself contractually",
            "body": "Given this customer's payment history, agree clear due dates, late-payment "
                    "terms and invoice promptly on delivery.",
            "tone": "action"}))

    # 7. Low exposure
    if target["level"] == "LOW":
        recs.append((60, {
            "title": "Exposure looks manageable",
            "body": f"With {fmt_currency(target['net_exposure'])} outstanding, this deal sits "
                    "comfortably within your cash position under current assumptions. Standard "
                    "invoicing discipline still applies.",
            "tone": "positive"}))

    recs.sort(key=lambda x: -x[0])
    return [r for _, r in recs][:limit]
