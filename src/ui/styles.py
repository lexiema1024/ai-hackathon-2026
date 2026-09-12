"""
PayLens stylesheet.

Two layers:
  1. ``pl-*`` classes — our own HTML components (fully controlled).
  2. A small, defensive set of overrides for Streamlit widgets, scoped with
     stable hooks (data-testid attributes and ``st-key-*`` container classes).
     If a selector ever stops matching after a Streamlit upgrade the widget
     simply falls back to the theme in .streamlit/config.toml — nothing breaks.
"""

FONT_IMPORT = (
    "@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');"
)

CSS = """
:root {
  /* Brand palette */
  --primary: #006BDE;
  --primary-hover: #005BBE;
  --background: #F2F2F7;
  --surface: #FFFFFF;
  --accent-light: #C5EDFC;
  --text-primary: #000000;
  --text-secondary: #8A8A8E;
  --danger: #FF3B30;
  --border: #E5E5EA;

  /* Internal aliases (every rule below reads these) */
  --pl-ink: var(--text-primary);
  --pl-primary: var(--primary);
  --pl-primary-hover: var(--primary-hover);
  --pl-primary-tint: rgba(0, 107, 222, 0.08);
  --pl-accent: var(--accent-light);
  --pl-accent-tint: #EEF9FE;
  --pl-bg: var(--background);
  --pl-card: var(--surface);
  --pl-text: var(--text-primary);
  --pl-muted: var(--text-secondary);
  --pl-faint: var(--text-secondary);
  --pl-border: var(--border);
  --pl-border-soft: #EFEFF4;
  --pl-subtle: var(--background);
  --pl-low: #248A3D;      --pl-low-bg: #E7F6EA;
  --pl-moderate: #BF7E00; --pl-moderate-bg: #FFF6DF;
  --pl-high: #E86A10;     --pl-high-bg: #FFF1E5;
  --pl-critical: var(--danger); --pl-critical-bg: #FFECEB;
  --pl-radius: 16px;
  --pl-shadow: 0 1px 2px rgba(0, 0, 0, 0.04), 0 4px 16px rgba(0, 0, 0, 0.04);
  --pl-font: "Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
}

/* ---------- App shell ------------------------------------------------- */
.stApp { background: var(--pl-bg); color: var(--pl-text); }
.stApp, .stApp p, .stApp label, .stApp input, .stApp button, .stApp textarea,
.stApp li, .stApp td, .stApp th, .stMarkdown, .stApp summary { font-family: var(--pl-font); }
header[data-testid="stHeader"], [data-testid="stToolbar"], [data-testid="stDecoration"],
[data-testid="stStatusWidget"], #MainMenu, footer { display: none !important; }
[data-testid="stMainBlockContainer"], .block-container {
  max-width: 1200px; padding-top: 1.1rem !important; padding-bottom: 2.5rem !important;
  padding-left: 2rem; padding-right: 2rem;
}
[data-testid="stSidebar"], [data-testid="collapsedControl"] { display: none; }
[data-testid="stElementContainer"]:has(iframe[height="0"]),
.element-container:has(iframe[height="0"]) { display: none; }
.stApp button [data-testid="stMarkdownContainer"], .stApp button p { color: inherit; }
.pl-anchor { position: relative; top: -16px; height: 0; }

/* ---------- Typography primitives ------------------------------------- */
.pl-eyebrow { font-size: 12px; font-weight: 600; letter-spacing: .08em; text-transform: uppercase; color: var(--pl-accent); }
.pl-eyebrow--blue { color: var(--pl-primary); }
.pl-label-caps { font-size: 11.5px; font-weight: 600; letter-spacing: .08em; text-transform: uppercase; color: var(--pl-muted); }
.pl-section-head { margin: 2.25rem 0 .25rem; }
.pl-section-head--center { text-align: center; }
.pl-section-title { font-size: 26px; line-height: 1.25; font-weight: 650; letter-spacing: -0.015em; color: var(--pl-ink); margin-top: 6px; }
.pl-section-lead { font-size: 15px; line-height: 1.55; color: var(--pl-muted); margin-top: 6px; max-width: 640px; }
.pl-small { font-size: 12.5px; color: var(--pl-muted); line-height: 1.5; }
.pl-subhead { font-size: 13px; font-weight: 600; color: var(--pl-text); margin: 18px 0 8px; }
.pl-footnote { margin-top: 16px; font-size: 11.5px; color: var(--pl-faint); }
.pl-icon { flex: 0 0 auto; }
.pl-text--low { color: var(--pl-low); } .pl-text--moderate { color: var(--pl-moderate); }
.pl-text--high { color: var(--pl-high); } .pl-text--critical { color: var(--pl-critical); }
.stApp code { font-size: 12px; background: var(--pl-subtle); color: var(--pl-ink); padding: 1px 5px; border-radius: 5px; }

/* ---------- Cards ----------------------------------------------------- */
.pl-card { background: var(--pl-card); border: 1px solid var(--pl-border); border-radius: var(--pl-radius);
  padding: 26px 28px; box-shadow: var(--pl-shadow); position: relative; }
.pl-accent { border-top: 3px solid var(--pl-border); }
.pl-accent--low { border-top-color: var(--pl-low); } .pl-accent--moderate { border-top-color: var(--pl-moderate); }
.pl-accent--high { border-top-color: var(--pl-high); } .pl-accent--critical { border-top-color: var(--pl-critical); }
.pl-card-head { margin-bottom: 18px; }
.pl-card-head--tight { margin-bottom: 4px; }
.pl-card-title { font-size: 16px; font-weight: 650; color: var(--pl-ink); }
.pl-card-title--lg { font-size: 20px; letter-spacing: -0.01em; }
.pl-card-meta { font-size: 13px; color: var(--pl-muted); margin-top: 3px; }
.pl-grid-2 { display: grid; grid-template-columns: 7fr 5fr; gap: 20px; align-items: stretch; }

/* ---------- Badges ---------------------------------------------------- */
.pl-badge { display: inline-flex; align-items: center; gap: 7px; font-size: 11.5px; font-weight: 700;
  letter-spacing: .08em; padding: 5px 11px 5px 9px; border-radius: 999px; border: 1px solid transparent; line-height: 1; white-space: nowrap; }
.pl-badge i { width: 7px; height: 7px; border-radius: 50%; background: currentColor; display: inline-block; }
.pl-badge--sm { font-size: 10.5px; padding: 4px 9px 4px 8px; gap: 6px; }
.pl-badge--low { color: var(--pl-low); background: var(--pl-low-bg); border-color: rgba(36,138,61,.2); }
.pl-badge--moderate { color: var(--pl-moderate); background: var(--pl-moderate-bg); border-color: rgba(191,126,0,.22); }
.pl-badge--high { color: var(--pl-high); background: var(--pl-high-bg); border-color: rgba(232,106,16,.22); }
.pl-badge--critical { color: var(--pl-critical); background: var(--pl-critical-bg); border-color: rgba(255,59,48,.22); }

/* ---------- Navigation ------------------------------------------------ */
.st-key-pl_nav { padding: 2px 0 14px; border-bottom: 1px solid var(--pl-border); margin-bottom: 6px; }
.pl-brand { display: flex; align-items: center; gap: 10px; }
.pl-wordmark { font-size: 20px; font-weight: 700; letter-spacing: -0.02em; color: var(--pl-ink); }
.pl-proto { font-size: 11px; font-weight: 600; color: var(--pl-primary); border: 1px solid rgba(0,107,222,.25);
  background: var(--pl-primary-tint); padding: 3px 8px; border-radius: 999px; margin-left: 4px; }

/* ---------- Buttons (Streamlit) --------------------------------------- */
.stApp .stButton > button, .stApp [data-testid^="stBaseButton-primary"], .stApp [data-testid^="stBaseButton-secondary"] {
  border-radius: 10px; min-height: 44px; padding: 0 18px; font-weight: 600;
  transition: background-color .15s ease, border-color .15s ease, color .15s ease, box-shadow .15s ease; }
.stApp .stButton > button p { font-weight: 600; font-size: 14.5px; }
.stApp button[kind="primary"], .stApp [data-testid="stBaseButton-primary"] {
  background: var(--pl-primary); border: 1px solid var(--pl-primary); color: #fff; }
.stApp button[kind="primary"]:hover, .stApp [data-testid="stBaseButton-primary"]:hover {
  background: var(--pl-primary-hover); border-color: var(--pl-primary-hover); color: #fff; }
.stApp button[kind="primary"]:focus-visible, .stApp [data-testid="stBaseButton-primary"]:focus-visible {
  box-shadow: 0 0 0 3px rgba(0,107,222,.3); }
.stApp button[kind="secondary"], .stApp [data-testid="stBaseButton-secondary"] {
  background: #fff; border: 1px solid var(--pl-border); color: var(--pl-text); }
.stApp button[kind="secondary"]:hover, .stApp [data-testid="stBaseButton-secondary"]:hover {
  border-color: var(--pl-primary); color: var(--pl-primary); background: #fff; }
.stApp .stButton > button:disabled, .stApp .stButton > button:disabled:hover {
  background: var(--pl-subtle) !important; border-color: var(--pl-border) !important; color: var(--pl-faint) !important;
  opacity: 1; cursor: not-allowed; box-shadow: none; }

/* ---------- Hero ------------------------------------------------------ */
[class*="st-key-pl_hero"] { background: linear-gradient(140deg, var(--primary) 0%, var(--primary-hover) 100%); border-radius: 22px;
  padding: 3.2rem 3.4rem 2.6rem; position: relative; overflow: hidden; gap: .9rem; margin-top: 10px; }
[class*="st-key-pl_hero"]::after { content: ""; position: absolute; right: -140px; top: -160px; width: 460px; height: 460px;
  border-radius: 50%; border: 1px solid rgba(255,255,255,.10); pointer-events: none;
  box-shadow: 0 0 0 70px rgba(255,255,255,.025), 0 0 0 140px rgba(255,255,255,.018); }
[class*="st-key-pl_hero"] > * { position: relative; z-index: 1; }
.pl-hero-copy { max-width: 720px; margin-bottom: 10px; }
.pl-hero-title { font-size: 44px; line-height: 1.1; font-weight: 700; letter-spacing: -0.025em; margin: 14px 0 14px; }
.pl-hero-sub { font-size: 17px; line-height: 1.55; max-width: 560px; }
.pl-hero-copy--dark .pl-hero-title { color: #fff; }
.pl-hero-copy--dark .pl-hero-sub { color: rgba(255,255,255,.78); }
.pl-hero-copy--light .pl-hero-title { color: var(--pl-ink); }
.pl-hero-copy--light .pl-hero-sub { color: var(--pl-muted); }
.pl-hero-copy--light .pl-eyebrow { color: var(--pl-primary); }
.pl-hero-helper { display: flex; align-items: center; gap: 8px; font-size: 13px; color: var(--pl-muted); }
.pl-hero-helper--dark { color: rgba(255,255,255,.7); }
.pl-hero-helper--dark .pl-icon { color: var(--pl-accent); }

[class*="st-key-pl_hero"] [data-baseweb="input"] { background: #fff !important; border-radius: 12px !important;
  border: 1px solid transparent !important; min-height: 52px; }
[class*="st-key-pl_hero"] [data-baseweb="input"]:focus-within { box-shadow: 0 0 0 3px rgba(197,237,252,.85) !important; }
[class*="st-key-pl_hero"] [data-baseweb="base-input"] { background: transparent !important; }
[class*="st-key-pl_hero"] input { font-size: 16px !important; color: var(--pl-text) !important; padding-left: 46px !important;
  background: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='18' height='18' viewBox='0 0 24 24' fill='none' stroke='%238A8A8E' stroke-width='2' stroke-linecap='round'%3E%3Ccircle cx='11' cy='11' r='6.5'/%3E%3Cpath d='M16 16l4 4'/%3E%3C/svg%3E") no-repeat 16px center !important; }
[class*="st-key-pl_hero"] .stButton > button { min-height: 52px; border-radius: 12px; }
[class*="st-key-pl_hero"] button[kind="primary"], [class*="st-key-pl_hero"] [data-testid="stBaseButton-primary"] {
  background: var(--pl-accent); border-color: var(--pl-accent); color: var(--pl-primary-hover); }
[class*="st-key-pl_hero"] button[kind="primary"]:hover, [class*="st-key-pl_hero"] [data-testid="stBaseButton-primary"]:hover {
  background: #FFFFFF; border-color: #FFFFFF; color: var(--pl-primary-hover); }
[class*="st-key-pl_hero"] button[kind="secondary"], [class*="st-key-pl_hero"] [data-testid="stBaseButton-secondary"] {
  background: transparent; border-color: rgba(255,255,255,.35); color: #fff; }
[class*="st-key-pl_hero"] button[kind="secondary"]:hover, [class*="st-key-pl_hero"] [data-testid="stBaseButton-secondary"]:hover {
  background: rgba(255,255,255,.08); border-color: rgba(255,255,255,.7); color: #fff; }
[class*="st-key-pl_hero"] .stButton > button:disabled, [class*="st-key-pl_hero"] .stButton > button:disabled:hover {
  background: transparent !important; border-color: rgba(255,255,255,.16) !important; color: rgba(255,255,255,.34) !important; }
.st-key-pl_hero_compact { padding: 2rem 2.6rem 1.7rem; }
.st-key-pl_hero_compact .pl-hero-title { font-size: 28px; margin: 8px 0 4px; }
.st-key-pl_hero_compact .pl-hero-title br, .st-key-pl_hero_compact .pl-hero-sub { display: none; }
.st-key-pl_hero_compact::after { right: -220px; top: -260px; }

/* ---------- Initial state: steps + quick picks ------------------------ */
.pl-steps { display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; margin-top: 8px; }
.pl-step { background: var(--pl-card); border: 1px solid var(--pl-border); border-radius: 14px; padding: 20px 22px; }
.pl-step-icon { width: 34px; height: 34px; border-radius: 10px; background: var(--pl-primary-tint); color: var(--pl-primary);
  display: flex; align-items: center; justify-content: center; margin-bottom: 14px; }
.pl-step-num { font-size: 11.5px; font-weight: 600; color: var(--pl-faint); letter-spacing: .04em; }
.pl-step-title { font-size: 15.5px; font-weight: 650; color: var(--pl-ink); margin-top: 2px; }
.pl-step-body { font-size: 13.5px; line-height: 1.5; color: var(--pl-muted); margin-top: 6px; }
.pl-quickpick-label { font-size: 13px; font-weight: 600; color: var(--pl-muted); margin-top: 6px; }
.st-key-pl_quickpicks .stButton > button { min-height: 38px; border-radius: 999px; padding: 0 14px; }
.st-key-pl_quickpicks .stButton > button p { font-size: 13.5px; font-weight: 500; }

/* ---------- Search results ------------------------------------------- */
.st-key-pl_results { background: var(--pl-card); border: 1px solid var(--pl-border); border-radius: var(--pl-radius);
  padding: 18px 24px 10px; box-shadow: var(--pl-shadow); gap: 0; }
.pl-results-head { font-size: 13px; font-weight: 600; color: var(--pl-text); padding-bottom: 10px; display: flex; gap: 6px; }
.pl-results-query { color: var(--pl-muted); font-weight: 500; }
[class*="st-key-pl_row_"] { border-top: 1px solid var(--pl-border-soft); padding: 12px 0; }
[class*="st-key-pl_row_"] .stButton > button { min-height: 38px; }
.pl-result { display: flex; align-items: center; gap: 14px; }
.pl-result-avatar { width: 38px; height: 38px; border-radius: 10px; background: var(--pl-subtle); color: var(--pl-ink);
  font-weight: 700; display: flex; align-items: center; justify-content: center; font-size: 15px; flex: 0 0 auto; }
.pl-result--selected .pl-result-avatar { background: var(--pl-primary); color: #fff; }
.pl-result-name { font-size: 15px; font-weight: 600; color: var(--pl-text); }
.pl-result-meta { font-size: 13px; color: var(--pl-muted); margin-top: 2px; }
.pl-tag { font-size: 10.5px; font-weight: 600; color: var(--pl-muted); background: var(--pl-subtle); padding: 2px 7px;
  border-radius: 6px; margin-left: 6px; vertical-align: 2px; }
.pl-empty { display: flex; gap: 14px; align-items: flex-start; background: var(--pl-card); border: 1px dashed #D1D1D6;
  border-radius: 14px; padding: 18px 20px; }
.pl-empty-icon { width: 38px; height: 38px; border-radius: 50%; background: var(--pl-subtle); color: var(--pl-primary);
  display: flex; align-items: center; justify-content: center; flex: 0 0 auto; }
.pl-empty-title { font-size: 15px; font-weight: 650; color: var(--pl-ink); }
.pl-empty-body { font-size: 13.5px; color: var(--pl-muted); margin-top: 3px; line-height: 1.5; }
.pl-notice { display: flex; gap: 9px; align-items: flex-start; font-size: 13px; line-height: 1.45; padding: 10px 12px;
  border-radius: 10px; background: var(--pl-subtle); color: var(--pl-text); margin: 4px 0 12px; }
.pl-notice .pl-icon { margin-top: 1px; color: var(--pl-primary); }
.pl-notice--negative { background: var(--pl-moderate-bg); }
.pl-notice--negative .pl-icon { color: var(--pl-moderate); }
.pl-notice--positive { background: var(--pl-low-bg); }
.pl-notice--positive .pl-icon { color: var(--pl-low); }

/* ---------- Customer profile ----------------------------------------- */
.pl-customer-head { display: flex; justify-content: space-between; align-items: flex-end; gap: 16px; margin: 2.4rem 0 18px; }
.pl-customer-name { font-size: 30px; font-weight: 700; letter-spacing: -0.02em; color: var(--pl-ink); margin: 6px 0 10px; line-height: 1.15; }
.pl-chips { display: flex; flex-wrap: wrap; gap: 8px; }
.pl-chip { font-size: 12.5px; color: var(--pl-text); background: #fff; border: 1px solid var(--pl-border); padding: 4px 10px; border-radius: 999px; }
.pl-chip--muted { color: var(--pl-muted); font-style: italic; }
.pl-chip--demo { color: var(--pl-primary); border-color: rgba(0,107,222,.25); background: var(--pl-primary-tint); }
.pl-asof { font-size: 12px; color: var(--pl-faint); white-space: nowrap; }
.pl-stack { display: flex; gap: 3px; height: 14px; border-radius: 999px; overflow: hidden; background: var(--pl-subtle); }
.pl-seg { display: block; height: 100%; }
.pl-seg--1, .pl-dot--1 { background: var(--pl-primary); }
.pl-seg--2, .pl-dot--2 { background: #8FD0F7; }
.pl-seg--3, .pl-dot--3 { background: var(--pl-high); }
.pl-legend { display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; margin-top: 16px; }
.pl-legend-key { display: flex; align-items: center; gap: 7px; font-size: 12.5px; color: var(--pl-muted); }
.pl-dot { width: 9px; height: 9px; border-radius: 3px; display: inline-block; flex: 0 0 auto; }
.pl-legend-val { font-size: 26px; font-weight: 650; color: var(--pl-ink); margin-top: 4px; letter-spacing: -0.01em; font-variant-numeric: tabular-nums; }
.pl-kv-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-top: 20px; }
.pl-kv { background: var(--pl-subtle); border-radius: 12px; padding: 14px 16px; }
.pl-kv-label { font-size: 12px; color: var(--pl-muted); margin-bottom: 6px; }
.pl-kv-strong { font-size: 15px; font-weight: 650; color: var(--pl-text); }
.pl-kv-na { color: var(--pl-muted); font-weight: 500; }
.pl-kv-sub { font-size: 12.5px; color: var(--pl-muted); margin-top: 3px; line-height: 1.4; }
.pl-trend { display: inline-flex; align-items: center; gap: 6px; font-size: 15px; font-weight: 650; color: var(--pl-text); }
.pl-trend--bad { color: var(--pl-high); } .pl-trend--good { color: var(--pl-low); }
.pl-trend--na { color: var(--pl-muted); font-weight: 500; }
.pl-spark { margin-top: 20px; }
.pl-spark-head { display: flex; justify-content: space-between; font-size: 12.5px; color: var(--pl-muted); margin-bottom: 6px; }
.pl-spark-now { color: var(--pl-text); font-weight: 600; }
.pl-spark-svg { width: 100%; height: 64px; display: block; overflow: visible; }
.pl-spark-line { fill: none; stroke: var(--pl-primary); stroke-width: 2; vector-effect: non-scaling-stroke; }
.pl-spark-area { fill: rgba(0,107,222,.07); stroke: none; }
.pl-spark-dot { fill: #fff; stroke: var(--pl-primary); stroke-width: 1.5; vector-effect: non-scaling-stroke; }
.pl-spark-last { fill: var(--pl-primary); stroke: #fff; stroke-width: 2; vector-effect: non-scaling-stroke; }
.pl-spark-axis { display: flex; justify-content: space-between; font-size: 11.5px; color: var(--pl-faint); margin-top: 4px; }
.pl-spark--empty { display: flex; align-items: center; gap: 8px; font-size: 13px; color: var(--pl-muted);
  background: var(--pl-subtle); border-radius: 10px; padding: 12px 14px; }

.pl-risk-level { display: flex; align-items: center; gap: 12px; margin: 10px 0 4px; }
.pl-risk-word { font-size: 34px; font-weight: 700; letter-spacing: -0.02em; line-height: 1.1; }
.pl-risk-prob { font-size: 13.5px; color: var(--pl-muted); margin-bottom: 14px; }
.pl-risk-prob strong { color: var(--pl-text); font-weight: 650; }

/* ---------- Meter ----------------------------------------------------- */
.pl-meter { margin: 6px 0 10px; }
.pl-meter-track { position: relative; display: flex; height: 6px; border-radius: 999px; }
.pl-meter-band { height: 100%; display: block; }
.pl-meter-band:first-child { border-radius: 999px 0 0 999px; }
.pl-meter-band:nth-child(4) { border-radius: 0 999px 999px 0; }
.pl-band--low { background: #CDEBD5; } .pl-band--moderate { background: #F7E4B2; }
.pl-band--high { background: #FBD5B8; } .pl-band--critical { background: #FFCAC6; }
.pl-meter-marker { position: absolute; top: 50%; width: 14px; height: 14px; border-radius: 50%; background: #fff;
  border: 3px solid var(--pl-ink); transform: translate(-50%, -50%); box-shadow: 0 1px 3px rgba(0,0,0,.15); }
.pl-marker--low { border-color: var(--pl-low); } .pl-marker--moderate { border-color: var(--pl-moderate); }
.pl-marker--high { border-color: var(--pl-high); } .pl-marker--critical { border-color: var(--pl-critical); }
.pl-meter-labels { display: flex; margin-top: 7px; }
.pl-meter-labels span { font-size: 11px; color: var(--pl-faint); }

/* ---------- Reasons / bullets ---------------------------------------- */
.stApp ul.pl-reasons { list-style: none; margin: 0; padding: 0; display: flex; flex-direction: column; gap: 10px; }
.stApp ul.pl-reasons li { display: flex; gap: 10px; align-items: flex-start; font-size: 14px; line-height: 1.45;
  color: var(--pl-text); margin: 0; padding: 0; }
.pl-reasons li .pl-icon { margin-top: 1px; color: var(--pl-muted); }
.pl-reasons li.pl-tone--negative .pl-icon { color: var(--pl-high); }
.pl-reasons li.pl-tone--negative.pl-lvl--critical .pl-icon { color: var(--pl-critical); }
.pl-reasons li.pl-tone--negative.pl-lvl--moderate .pl-icon,
.pl-reasons li.pl-tone--negative.pl-lvl--low .pl-icon { color: var(--pl-moderate); }
.pl-reasons li.pl-tone--positive .pl-icon { color: var(--pl-low); }
.pl-reasons li.pl-tone--neutral .pl-icon { color: var(--pl-primary); }

/* ---------- Transition ------------------------------------------------ */
.pl-transition { text-align: center; margin: 3.2rem auto 1.4rem; max-width: 680px; }
.pl-transition-line { width: 1px; height: 36px; background: linear-gradient(var(--pl-bg), var(--pl-border)); margin: 0 auto 18px; }
.pl-equation { display: inline-flex; align-items: center; gap: 10px; margin-bottom: 18px; }
.pl-eq-pill { display: inline-flex; align-items: center; gap: 7px; font-size: 13px; font-weight: 600; color: var(--pl-ink);
  background: #fff; border: 1px solid var(--pl-border); border-radius: 999px; padding: 6px 13px; }
.pl-eq-pill .pl-icon { color: var(--pl-primary); }
.pl-eq-pill--accent { border-color: var(--pl-accent); background: var(--pl-accent-tint); }
.pl-eq-sign { color: var(--pl-muted); display: inline-flex; }
.pl-transition-title { font-size: 30px; font-weight: 700; letter-spacing: -0.02em; color: var(--pl-ink); }
.pl-transition-body { font-size: 15.5px; line-height: 1.6; color: var(--pl-muted); margin-top: 10px; }

/* ---------- Deal form (Streamlit widgets inside our card) ------------- */
.st-key-pl_deal, .st-key-pl_sim { background: var(--pl-card); border: 1px solid var(--pl-border);
  border-radius: var(--pl-radius); padding: 26px 28px 24px; box-shadow: var(--pl-shadow); gap: .85rem; }
.st-key-pl_sim { border-top: 3px solid var(--pl-primary); }
.stApp [data-testid="stWidgetLabel"] p, .stApp [data-testid="stWidgetLabel"] label {
  font-size: 13px !important; font-weight: 600 !important; color: var(--pl-muted) !important; }
.st-key-pl_deal [data-baseweb="input"], .st-key-pl_sim [data-baseweb="input"] {
  border-radius: 10px !important; background: #fff !important; border: 1px solid var(--pl-border) !important; min-height: 46px; }
.st-key-pl_deal [data-baseweb="input"]:focus-within { border-color: var(--pl-primary) !important; box-shadow: 0 0 0 3px rgba(0,107,222,.14) !important; }
.st-key-pl_deal [data-baseweb="base-input"] { background: transparent !important; }
.st-key-pl_deal input { font-size: 16px !important; font-weight: 600 !important; color: var(--pl-text) !important; font-variant-numeric: tabular-nums; }
.pl-field-hint { font-size: 12px; margin-top: -8px; }
.pl-field-hint--muted { color: var(--pl-faint); }
.pl-field-hint--error { color: var(--pl-critical); font-weight: 500; }

/* Segmented control */
.stApp [data-testid="stButtonGroup"] button { min-height: 42px; border-radius: 10px; font-weight: 600; white-space: nowrap;
  border: 1px solid var(--pl-border); background: #fff; color: var(--pl-muted); }
.stApp [data-testid="stButtonGroup"] button:hover { border-color: var(--pl-primary); color: var(--pl-primary); }
.stApp [data-testid="stBaseButton-segmented_controlActive"] { background: var(--pl-primary) !important;
  border-color: var(--pl-primary) !important; color: #fff !important; }
.stApp [data-testid="stBaseButton-segmented_controlActive"] p { color: #fff !important; }

/* Slider */
.stApp [data-testid="stSlider"] [role="slider"] { box-shadow: 0 0 0 5px rgba(0,107,222,.16); }
.stApp [data-testid="stSliderThumbValue"] { font-weight: 650; color: var(--pl-ink); font-family: var(--pl-font); }
.stApp [data-testid="stSliderTickBarMin"], .stApp [data-testid="stSliderTickBarMax"] { color: var(--pl-faint); font-size: 12px; }

/* ---------- Exposure result ------------------------------------------ */
.pl-card--placeholder { border-style: dashed; box-shadow: none; background: rgba(255,255,255,.6); min-height: 100%; }
.pl-placeholder-title { font-size: 20px; font-weight: 650; color: var(--pl-ink); margin: 10px 0 6px; }
.pl-placeholder-body { font-size: 14px; color: var(--pl-muted); }
.stApp ul.pl-placeholder-list { list-style: none; padding: 0; margin: 16px 0 0; display: grid; gap: 10px; }
.stApp ul.pl-placeholder-list li { display: flex; gap: 10px; align-items: center; font-size: 14px; color: var(--pl-text);
  background: var(--pl-subtle); border-radius: 10px; padding: 11px 14px; margin: 0; }
.pl-placeholder-list .pl-icon { color: var(--pl-primary); }
.pl-exp-top { display: flex; justify-content: space-between; align-items: center; }
.pl-score { display: flex; align-items: baseline; gap: 8px; margin: 8px 0 6px; }
.pl-score-num { font-size: 64px; font-weight: 700; letter-spacing: -0.035em; line-height: 1; color: var(--pl-ink); font-variant-numeric: tabular-nums; }
.pl-score-den { font-size: 18px; color: var(--pl-faint); font-weight: 500; }
.pl-metrics { display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px; margin-top: 22px; }
.pl-metric { background: var(--pl-subtle); border-radius: 12px; padding: 13px 14px; min-width: 0; }
.pl-metric-label { font-size: 11.5px; color: var(--pl-muted); }
.pl-metric-value { font-size: 18px; font-weight: 650; color: var(--pl-ink); margin-top: 4px; font-variant-numeric: tabular-nums; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.pl-metric-sub { font-size: 11px; color: var(--pl-faint); margin-top: 3px; line-height: 1.35; }

/* ---------- Simulator ------------------------------------------------- */
.pl-live { display: flex; align-items: center; gap: 10px; justify-content: flex-end; font-size: 13px; color: var(--pl-muted); }
.pl-live-dot { width: 8px; height: 8px; border-radius: 50%; background: var(--pl-primary); box-shadow: 0 0 0 4px var(--pl-accent); }
.pl-live-score { font-size: 22px; font-weight: 700; font-variant-numeric: tabular-nums; }
.pl-sim-title { font-size: 16px; font-weight: 650; color: var(--pl-ink); }
.pl-sim-sub { font-size: 13px; color: var(--pl-muted); margin-top: 2px; }
.pl-suggest { background: var(--pl-accent-tint);
  border: 1px solid var(--pl-accent); border-radius: 12px; padding: 14px 16px; }
.pl-suggest--good { background: var(--pl-low-bg); border-color: rgba(36,138,61,.25); }
.pl-suggest--muted { background: var(--pl-subtle); border-color: var(--pl-border); }
.pl-suggest-label { display: flex; align-items: center; gap: 7px; font-size: 12.5px; font-weight: 600; color: var(--pl-muted); }
.pl-suggest-label .pl-icon { color: var(--pl-primary); }
.pl-suggest--good .pl-suggest-label .pl-icon { color: var(--pl-low); }
.pl-suggest-value { font-size: 30px; font-weight: 700; color: var(--pl-ink); letter-spacing: -0.02em; margin-top: 2px; }
.pl-suggest-body { font-size: 13px; color: var(--pl-muted); line-height: 1.45; margin-top: 2px; }

/* ---------- Before / after ------------------------------------------- */
.pl-compare { display: grid; grid-template-columns: 1fr 76px 1fr; align-items: stretch; margin-top: 8px; }
.pl-ccard { background: var(--pl-card); border: 1px solid var(--pl-border); border-radius: var(--pl-radius); padding: 24px 26px; box-shadow: var(--pl-shadow); }
.pl-ccard--current { background: #FAFAFC; box-shadow: none; }
.pl-ccard--current .pl-ccard-score span { opacity: .85; }
.pl-compare--improved .pl-ccard--revised { box-shadow: 0 1px 2px rgba(0,0,0,.05), 0 10px 30px rgba(0,107,222,.10); }
.pl-ccard-label { font-size: 11.5px; font-weight: 600; letter-spacing: .08em; text-transform: uppercase; color: var(--pl-muted); }
.pl-ccard-score { display: flex; align-items: baseline; gap: 6px; margin: 8px 0 10px; }
.pl-ccard-score span { font-size: 56px; font-weight: 700; letter-spacing: -0.035em; line-height: 1; font-variant-numeric: tabular-nums; }
.pl-ccard-score small { font-size: 16px; color: var(--pl-faint); }
.pl-crows { margin-top: 18px; border-top: 1px solid var(--pl-border-soft); }
.pl-crow { display: flex; justify-content: space-between; gap: 12px; padding: 10px 0; border-bottom: 1px solid var(--pl-border-soft); font-size: 13.5px; }
.pl-crow span:first-child { color: var(--pl-muted); }
.pl-crow span:last-child { color: var(--pl-text); font-weight: 600; text-align: right; font-variant-numeric: tabular-nums; }
.pl-crow--changed span:last-child { color: var(--pl-primary); }
.pl-crow--changed span:first-child::after { content: "changed"; font-size: 10px; font-weight: 600; color: var(--pl-primary);
  background: var(--pl-primary-tint); border-radius: 5px; padding: 1px 6px; margin-left: 8px; vertical-align: 1px; }
.pl-compare-mid { display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 10px; }
.pl-compare-arrow { width: 42px; height: 42px; border-radius: 50%; background: #fff; border: 1px solid var(--pl-border);
  color: var(--pl-primary); display: flex; align-items: center; justify-content: center; box-shadow: var(--pl-shadow); }
.pl-delta { font-size: 12px; font-weight: 700; color: var(--pl-muted); display: inline-flex; align-items: center; gap: 3px; white-space: nowrap; }
.pl-delta--down { color: var(--pl-low); } .pl-delta--up { color: var(--pl-critical); }
.pl-insight { margin-top: 22px; background: var(--pl-primary); border-radius: var(--pl-radius); padding: 26px 30px; color: #fff; }
.pl-insight-line { font-size: 24px; font-weight: 650; letter-spacing: -0.015em; line-height: 1.3; color: #fff; }
.pl-insight-line em { font-style: normal; color: var(--pl-accent); }
.pl-insight--same .pl-insight-line { font-size: 18px; color: rgba(255,255,255,.85); }
.pl-insight-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; margin-top: 20px; }
.pl-insight-item { border-top: 1px solid rgba(255,255,255,.16); padding-top: 12px; }
.pl-insight-k { display: flex; align-items: center; gap: 7px; font-size: 12px; color: rgba(255,255,255,.62); }
.pl-insight-v { font-size: 17px; font-weight: 650; color: #fff; margin-top: 5px; }
.pl-insight-v--good { color: var(--pl-accent); } .pl-insight-v--bad { color: #FFD3D0; }
.pl-insight-s { font-size: 12.5px; color: rgba(255,255,255,.66); margin-top: 3px; line-height: 1.4; }

/* ---------- Recommendations ------------------------------------------ */
.pl-recs { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; margin-top: 14px; }
.pl-rec { display: flex; gap: 14px; background: var(--pl-card); border: 1px solid var(--pl-border); border-radius: 14px; padding: 18px 20px; }
.pl-rec-icon { width: 32px; height: 32px; border-radius: 9px; display: flex; align-items: center; justify-content: center;
  flex: 0 0 auto; background: var(--pl-primary-tint); color: var(--pl-primary); }
.pl-rec--positive .pl-rec-icon { background: var(--pl-low-bg); color: var(--pl-low); }
.pl-rec--negative .pl-rec-icon { background: var(--pl-critical-bg); color: var(--pl-critical); }
.pl-rec--neutral .pl-rec-icon { background: var(--pl-subtle); color: var(--pl-muted); }
.pl-rec:last-child:nth-child(odd) { grid-column: 1 / -1; }
.pl-rec-title { font-size: 15px; font-weight: 650; color: var(--pl-ink); line-height: 1.35; }
.pl-rec-body { font-size: 13.5px; color: var(--pl-muted); line-height: 1.5; margin-top: 4px; }

/* ---------- About / methodology / footer ----------------------------- */
.pl-about { display: flex; gap: 14px; background: #E9E9EE; border-radius: 14px; padding: 20px 22px; margin-top: 3rem; }
.pl-about-icon { color: var(--pl-primary); margin-top: 1px; }
.pl-about-title { font-size: 14px; font-weight: 650; color: var(--pl-ink); }
.pl-about-body { font-size: 13.5px; color: var(--pl-muted); line-height: 1.6; margin-top: 4px; max-width: 860px; }
.pl-about-meta { display: flex; flex-wrap: wrap; gap: 6px 18px; font-size: 12px; color: var(--pl-faint); margin-top: 10px; }
.stApp [data-testid="stExpander"] details { border: 1px solid var(--pl-border); border-radius: 12px; background: #fff; }
.stApp [data-testid="stExpander"] summary p { font-size: 14px; font-weight: 600; color: var(--pl-ink); }
.pl-table-wrap { overflow-x: auto; }
.stApp table.pl-table { width: 100%; border-collapse: collapse; font-size: 13px; margin: 0 0 14px; }
.stApp table.pl-table th { text-align: left; font-size: 11.5px; font-weight: 600; color: var(--pl-muted); padding: 8px 10px;
  border-bottom: 1px solid var(--pl-border); background: transparent; }
.stApp table.pl-table td { padding: 10px; border-bottom: 1px solid var(--pl-border-soft); color: var(--pl-text); vertical-align: top; }
.pl-num { text-align: right !important; font-variant-numeric: tabular-nums; }
.pl-method-bands { display: flex; flex-wrap: wrap; gap: 8px 18px; font-size: 12.5px; color: var(--pl-muted); margin-bottom: 12px; }
.pl-method-bands span { display: inline-flex; align-items: center; gap: 6px; }
.pl-footer { display: flex; justify-content: space-between; align-items: center; gap: 12px; flex-wrap: wrap;
  border-top: 1px solid var(--pl-border); margin-top: 2.4rem; padding-top: 18px; }
.pl-footer-brand { display: flex; align-items: center; gap: 8px; font-weight: 700; color: var(--pl-ink); font-size: 15px; }
.pl-footer-meta { font-size: 12.5px; color: var(--pl-faint); }

/* ---------- Subtle reveal -------------------------------------------- */
@keyframes plFadeUp { from { opacity: 0; transform: translateY(6px); } to { opacity: 1; transform: none; } }
.pl-customer-head, .pl-grid-2, .pl-card--exposure, .pl-recs { animation: plFadeUp .35s ease-out both; }
@media (prefers-reduced-motion: reduce) { .pl-customer-head, .pl-grid-2, .pl-card--exposure, .pl-recs { animation: none; } }

/* ---------- Responsive ----------------------------------------------- */
@media (max-width: 1000px) {
  .pl-metrics { grid-template-columns: 1fr 1fr; }
}
@media (max-width: 860px) {
  .pl-grid-2 { grid-template-columns: 1fr; }
  .pl-recs { grid-template-columns: 1fr; }
  .pl-steps { grid-template-columns: 1fr; }
}
@media (max-width: 720px) {
  [data-testid="stMainBlockContainer"], .block-container { padding-left: 1rem; padding-right: 1rem; }
  .st-key-pl_nav [data-testid="stHorizontalBlock"] { flex-wrap: nowrap !important; gap: .75rem !important; }
  .st-key-pl_nav [data-testid="stColumn"] { min-width: 0 !important; width: auto !important; flex: 1 1 auto !important; }
  .st-key-pl_nav [data-testid="stColumn"]:last-child { flex: 0 0 auto !important; }
  .st-key-pl_nav .stButton > button { min-height: 38px; padding: 0 12px; }
  .pl-proto { display: none; }
  .pl-hero-title br { display: none; }
  .st-key-pl_hero_compact { padding: 1.6rem 1.35rem 1.4rem; }
  .st-key-pl_hero_compact .pl-hero-title { font-size: 22px; }
  .pl-live { justify-content: flex-start; }
  .stApp [data-testid="stButtonGroup"] button { padding: 0 6px; min-height: 40px; }
  .stApp [data-testid="stButtonGroup"] button p { font-size: 13.5px; }
  .pl-rec:last-child:nth-child(odd) { grid-column: auto; }
  [class*="st-key-pl_hero"] { padding: 2rem 1.35rem 1.6rem; border-radius: 18px; }
  .pl-hero-title { font-size: 31px; }
  .pl-hero-sub { font-size: 15.5px; }
  .pl-section-title, .pl-transition-title { font-size: 23px; }
  .pl-customer-name { font-size: 25px; }
  .pl-customer-head { flex-direction: column; align-items: flex-start; }
  .pl-card, .st-key-pl_deal, .st-key-pl_sim { padding: 20px 18px; }
  .st-key-pl_results { padding: 14px 16px 8px; }
  .pl-legend-val { font-size: 21px; }
  .pl-kv-grid { grid-template-columns: 1fr; }
  .pl-compare { grid-template-columns: 1fr; gap: 10px; }
  .pl-compare-mid { flex-direction: row; }
  .pl-compare-arrow { transform: rotate(90deg); }
  .pl-insight { padding: 22px 20px; }
  .pl-insight-line { font-size: 20px; }
  .pl-insight-grid { grid-template-columns: 1fr; }
  .pl-score-num { font-size: 54px; }
  .pl-ccard-score span { font-size: 46px; }
  .pl-equation { flex-wrap: wrap; justify-content: center; }
}
@media (max-width: 420px) {
  .pl-metrics { grid-template-columns: 1fr 1fr; }
  .pl-metric-value { font-size: 16px; }
  .pl-legend { gap: 8px; }
  .pl-legend-key { font-size: 11.5px; }
}
"""


def stylesheet() -> str:
    return f"<style>{FONT_IMPORT}{CSS}</style>"
