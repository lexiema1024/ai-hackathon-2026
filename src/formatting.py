"""Display formatting and input parsing helpers (pure functions)."""

from __future__ import annotations

import math
import re
from typing import Optional

MAX_AMOUNT = 1_000_000_000_000  # $1 trillion — anything above is treated as a typo


def fmt_currency(value, compact_from: float = 10_000_000) -> str:
    """$120,000 · $12.5M · $1.2B."""
    try:
        v = float(value)
    except (TypeError, ValueError):
        return "—"
    if math.isnan(v) or math.isinf(v):
        return "—"
    sign = "-" if v < 0 else ""
    v = abs(v)
    if v >= 1_000_000_000 and v >= compact_from:
        return f"{sign}${v / 1_000_000_000:,.1f}B"
    if v >= 1_000_000 and v >= compact_from:
        return f"{sign}${v / 1_000_000:,.1f}M"
    return f"{sign}${v:,.0f}"


def fmt_ratio(ratio: Optional[float]) -> str:
    if ratio is None:
        return "No cash buffer"
    if ratio >= 100:
        return ">100×"
    if ratio >= 10:
        return f"{ratio:.0f}×"
    return f"{ratio:.1f}×"


def fmt_months(months: Optional[float]) -> str:
    if months is None:
        return "Not constrained"
    if months <= 0:
        return "0 months"
    if months >= 120:
        return "10+ years"
    if months >= 24:
        return f"{months / 12:.1f} years"
    return f"{months:.1f} months"


def fmt_pct(fraction, digits: int = 0) -> str:
    try:
        return f"{float(fraction) * 100:.{digits}f}%"
    except (TypeError, ValueError):
        return "—"


def parse_amount(text) -> Optional[float]:
    """Parse '$120,000', '120k', '1.2m', '45 000' -> float. None if invalid.

    Negative numbers are invalid. Empty string is invalid.
    """
    if text is None:
        return None
    if isinstance(text, (int, float)):
        v = float(text)
        return v if (v >= 0 and not math.isnan(v) and v <= MAX_AMOUNT) else None
    s = str(text).strip().lower()
    if not s:
        return None
    s = s.replace("aud", "").replace("$", "").replace(",", "").replace(" ", "").replace("_", "")
    m = re.fullmatch(r"(\d+(?:\.\d+)?|\.\d+)([kmb])?", s)
    if not m:
        return None
    v = float(m.group(1))
    mult = {"k": 1e3, "m": 1e6, "b": 1e9}.get(m.group(2) or "", 1.0)
    v *= mult
    if v > MAX_AMOUNT:
        return None
    return round(v, 2)


def fmt_amount_input(value: float) -> str:
    """Canonical text shown inside a currency input after editing."""
    if value is None:
        return ""
    if float(value).is_integer():
        return f"${value:,.0f}"
    return f"${value:,.2f}"
