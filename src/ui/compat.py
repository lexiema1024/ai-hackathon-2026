"""
Thin wrappers that keep PayLens working across Streamlit versions.

Streamlit adds/renames keyword arguments over time (e.g. ``width`` replacing
``use_container_width``, keyed containers, ``st.segmented_control``). These
helpers feature-detect once and degrade gracefully instead of crashing.
"""

from __future__ import annotations

import inspect
from contextlib import contextmanager
from functools import lru_cache

import streamlit as st


@lru_cache(maxsize=None)
def _params(fn_name: str) -> frozenset:
    fn = getattr(st, fn_name, None)
    if fn is None:
        return frozenset()
    try:
        return frozenset(inspect.signature(fn).parameters)
    except (TypeError, ValueError):
        return frozenset()


def supports_keyed_containers() -> bool:
    return "key" in _params("container")


def container(key: str | None = None):
    """st.container with a CSS hook class ``st-key-<key>`` when supported."""
    if key and supports_keyed_containers():
        return st.container(key=key)
    return st.container()


def columns(spec, gap: str = "medium", vertical_alignment: str | None = None):
    kwargs = {"gap": gap}
    if vertical_alignment and "vertical_alignment" in _params("columns"):
        kwargs["vertical_alignment"] = vertical_alignment
    return st.columns(spec, **kwargs)


def button(label: str, key: str, *, type: str = "secondary", full_width: bool = False, **kwargs) -> bool:
    params = _params("button")
    if full_width:
        if "width" in params:
            kwargs["width"] = "stretch"
        elif "use_container_width" in params:
            kwargs["use_container_width"] = True
    return st.button(label, key=key, type=type, **kwargs)


def segmented(label: str, options, key: str, format_func=None, on_change=None, args=None):
    """Single-select segmented control; falls back to a horizontal radio."""
    format_func = format_func or str
    if hasattr(st, "segmented_control"):
        kwargs = dict(options=options, selection_mode="single", key=key,
                      format_func=format_func, on_change=on_change, args=args)
        if "width" in _params("segmented_control"):
            kwargs["width"] = "stretch"
        return st.segmented_control(label, **kwargs)
    return st.radio(label, options=options, key=key, format_func=format_func,
                    horizontal=True, on_change=on_change, args=args)


def toast(message: str) -> None:
    fn = getattr(st, "toast", None)
    if fn is not None:
        try:
            fn(message)
        except Exception:
            pass


def scroll_to(anchor_id: str) -> None:
    """Smooth-scroll the main page to an element id (best effort)."""
    try:
        import streamlit.components.v1 as components
    except Exception:
        return
    js = f"""
    <script>
    (function() {{
      try {{
        const doc = window.parent.document;
        const go = () => {{
          const el = doc.getElementById("{anchor_id}");
          if (el) {{ el.scrollIntoView({{behavior: "smooth", block: "start"}}); return true; }}
          return false;
        }};
        if (!go()) {{ let n = 0; const t = setInterval(() => {{ if (go() || ++n > 20) clearInterval(t); }}, 100); }}
      }} catch (e) {{}}
    }})();
    </script>"""
    try:
        components.html(js, height=0)
    except Exception:
        pass


@contextmanager
def safe_section(name: str, fallback_message: str | None = None):
    """Render a section; on any error show a calm inline message, never a trace."""
    try:
        yield
    except Exception:  # noqa: BLE001 - deliberate UI guard
        import logging
        logging.getLogger("paylens.ui").exception("Section %s failed", name)
        from src.ui.components import empty_state
        st.markdown(empty_state("error"), unsafe_allow_html=True)
