"""
Session-state model for the PayLens journey.

All functions take any MutableMapping (``st.session_state`` in the app, a plain
dict in tests) so the flow logic is testable without Streamlit.

Journey states
  INITIAL           no company selected, no results showing
  SEARCH            results for a query are visible
  NO_RESULTS        query returned nothing
  CUSTOMER_SELECTED profile shown, deal not analysed
  DEAL_ANALYSED     exposure result + simulator + comparison visible
"""

from __future__ import annotations

import copy
from typing import MutableMapping, Optional

from src.formatting import fmt_amount_input, parse_amount

TERM_OPTIONS = (30, 45, 60, 90)

DEFAULT_DEAL = {
    "contract_value": 120_000,
    "cash_reserve": 45_000,
    "monthly_cost": 25_000,
    "payment_terms_days": 60,
    "upfront_pct": 0,  # whole percent in the UI
}

DEFAULTS = {
    "search_query": "",
    "show_results": False,
    "selected_company_id": None,
    "selected_company_name": None,
    "in_contract_value": fmt_amount_input(DEFAULT_DEAL["contract_value"]),
    "in_cash": fmt_amount_input(DEFAULT_DEAL["cash_reserve"]),
    "in_monthly_cost": fmt_amount_input(DEFAULT_DEAL["monthly_cost"]),
    "in_terms": DEFAULT_DEAL["payment_terms_days"],
    "in_terms_last": DEFAULT_DEAL["payment_terms_days"],
    "in_upfront": DEFAULT_DEAL["upfront_pct"],
    "deal_analysed": False,
    "current_deal": None,
    "sim_upfront": DEFAULT_DEAL["upfront_pct"],
    "sim_terms": DEFAULT_DEAL["payment_terms_days"],
    "sim_terms_last": DEFAULT_DEAL["payment_terms_days"],
    "scroll_to": None,
    "toast": None,
    "analysis_count": 0,
}

AMOUNT_KEYS = {
    "in_contract_value": "contract_value",
    "in_cash": "cash_reserve",
    "in_monthly_cost": "monthly_cost",
}


def ensure_defaults(state: MutableMapping) -> None:
    for key, value in DEFAULTS.items():
        if key not in state:
            state[key] = copy.deepcopy(value)


def reset_state(state: MutableMapping) -> None:
    """New Analysis: return every part of the journey to its initial state."""
    for key, value in DEFAULTS.items():
        state[key] = copy.deepcopy(value)
    state["scroll_to"] = "top"


def journey_stage(state: MutableMapping) -> str:
    if state.get("selected_company_id"):
        return "DEAL_ANALYSED" if state.get("deal_analysed") else "CUSTOMER_SELECTED"
    if state.get("show_results"):
        return "SEARCH"
    return "INITIAL"


# --- search ---------------------------------------------------------------

def on_query_change(state: MutableMapping) -> None:
    query = (state.get("search_query") or "").strip()
    # Committing the already-selected company's name is not a new search.
    if query and query == (state.get("selected_company_name") or ""):
        state["show_results"] = False
        return
    state["show_results"] = bool(query)


def clear_search(state: MutableMapping) -> None:
    state["search_query"] = ""
    state["show_results"] = False


def select_company(state: MutableMapping, company_id: str, name: Optional[str] = None) -> None:
    changed = state.get("selected_company_id") != company_id
    state["selected_company_id"] = company_id
    state["selected_company_name"] = name
    state["show_results"] = False
    if name:
        state["search_query"] = name
    if changed:
        state["deal_analysed"] = False
        state["current_deal"] = None
    state["scroll_to"] = "customer"


# --- deal inputs ----------------------------------------------------------

def normalise_amount_field(state: MutableMapping, key: str) -> None:
    """on_change for currency fields: reformat valid input as $120,000."""
    value = parse_amount(state.get(key))
    if value is not None:
        state[key] = fmt_amount_input(value)


def sync_terms(state: MutableMapping, key: str) -> None:
    """Segmented controls return None when the active option is clicked
    again; keep the last valid choice instead."""
    last_key = f"{key}_last"
    if state.get(key) in TERM_OPTIONS:
        state[last_key] = state[key]
    else:
        state[key] = state.get(last_key, DEFAULT_DEAL["payment_terms_days"])


def read_terms(state: MutableMapping, key: str) -> int:
    v = state.get(key)
    if v in TERM_OPTIONS:
        return int(v)
    return int(state.get(f"{key}_last", DEFAULT_DEAL["payment_terms_days"]))


def read_deal_inputs(state: MutableMapping) -> dict:
    """Parsed deal inputs + per-field errors."""
    deal, errors = {}, {}
    for key, field in AMOUNT_KEYS.items():
        v = parse_amount(state.get(key))
        if v is None:
            errors[field] = "Enter an amount, e.g. 120,000"
        deal[field] = v
    deal["payment_terms_days"] = read_terms(state, "in_terms")
    try:
        deal["upfront_pct"] = int(min(max(int(state.get("in_upfront") or 0), 0), 100))
    except (TypeError, ValueError):
        deal["upfront_pct"] = 0
    return {"deal": deal, "errors": errors}


def analyse_deal(state: MutableMapping) -> bool:
    """Snapshot the inputs as the 'current deal' and seed the simulator."""
    parsed = read_deal_inputs(state)
    if parsed["errors"]:
        state["deal_analysed"] = False
        return False
    deal = parsed["deal"]
    state["current_deal"] = deal
    state["deal_analysed"] = True
    state["sim_upfront"] = deal["upfront_pct"]
    state["sim_terms"] = deal["payment_terms_days"]
    state["sim_terms_last"] = deal["payment_terms_days"]
    state["scroll_to"] = "exposure"
    state["analysis_count"] = int(state.get("analysis_count") or 0) + 1
    return True


def inputs_changed_since_analysis(state: MutableMapping) -> bool:
    if not state.get("deal_analysed") or not state.get("current_deal"):
        return False
    parsed = read_deal_inputs(state)
    if parsed["errors"]:
        return True
    return parsed["deal"] != state["current_deal"]


# --- simulator ------------------------------------------------------------

def revised_deal(state: MutableMapping) -> Optional[dict]:
    current = state.get("current_deal")
    if not current:
        return None
    revised = dict(current)
    try:
        revised["upfront_pct"] = int(min(max(int(state.get("sim_upfront") or 0), 0), 100))
    except (TypeError, ValueError):
        revised["upfront_pct"] = current["upfront_pct"]
    revised["payment_terms_days"] = read_terms(state, "sim_terms")
    return revised


def reset_simulator(state: MutableMapping) -> None:
    current = state.get("current_deal")
    if not current:
        return
    state["sim_upfront"] = current["upfront_pct"]
    state["sim_terms"] = current["payment_terms_days"]
    state["sim_terms_last"] = current["payment_terms_days"]


def apply_suggestion(state: MutableMapping, upfront_pct: int, terms: int) -> None:
    state["sim_upfront"] = int(upfront_pct)
    if terms in TERM_OPTIONS:
        state["sim_terms"] = int(terms)
        state["sim_terms_last"] = int(terms)
    state["toast"] = "Suggested terms applied to your revised deal."
