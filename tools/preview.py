"""
Render approximate static previews of each PayLens journey state using the
Streamlit stub (for environments where Streamlit itself isn't installed),
then screenshot them with Playwright.

    python tools/preview.py [out_dir]
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tests.streamlit_stub import install  # noqa: E402

APP = str(ROOT / "app.py")


def states():
    st = install()
    yield "01_initial", st.run(APP)
    st.set("search_query", "demo").run(APP)
    yield "02_search", st
    st.set("search_query", "zzz").run(APP)
    yield "03_no_results", st
    st.click("btn_clear").run(APP)
    st.click("qp_demo-logistics").run(APP)
    yield "04_customer", st
    st.click("btn_analyse_deal").run(APP)
    yield "05_analysed", st
    st.set("sim_upfront", 30).run(APP)
    st.set("sim_terms", 30).run(APP)
    yield "06_simulated", st
    st.click("btn_apply").run(APP) if not st.buttons()["btn_apply"]["disabled"] else None
    yield "07_applied", st
    st2 = install()
    st2.run(APP)
    st2.click("qp_sample-manufacturing").run(APP)
    st2.set("in_cash", "0").run(APP)
    st2.set("in_monthly_cost", "abc").run(APP)
    yield "08_edge_missing_data", st2


def main(out_dir: str):
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    pages = []
    for name, st in states():
        p = out / f"{name}.html"
        p.write_text(st.to_html(f"PayLens · {name}"))
        pages.append(p)
    from playwright.sync_api import sync_playwright
    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        for width, tag in ((1440, "desktop"), (390, "mobile")):
            page = browser.new_page(viewport={"width": width, "height": 900}, device_scale_factor=1)
            for p in pages:
                page.goto(p.as_uri())
                page.wait_for_timeout(150)
                page.screenshot(path=str(out / f"{p.stem}_{tag}.png"), full_page=True)
                overflow = page.evaluate("document.documentElement.scrollWidth - window.innerWidth")
                if overflow > 1:
                    print(f"[warn] {p.stem} {tag}: horizontal overflow {overflow}px")
            page.close()
        browser.close()
    print("wrote", len(pages), "states to", out)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else str(ROOT / "preview"))
