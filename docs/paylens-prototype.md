# PayLens

**Know the payment risk before you sign the deal.**

PayLens helps a small business decide whether it can afford to take on a large B2B customer. It shows how the customer has paid other suppliers, then works out how exposed *your* business would be under the proposed contract, and lets you restructure the deal to see the exposure drop.

> Customer risk ≠ Contract risk. The same customer can be a small risk for one business and a serious one for another.

This is the **frontend prototype**. All customer data and the payment-delay model are **mocks** behind a clean service interface. The contract exposure engine is real and deterministic.

---

## Run it

Deployed demo: http://10.12.247.232:8502

```bash
pip install -r requirements.txt      # streamlit (+ pytest for tests)
streamlit run app.py
```

For a local run, open http://localhost:8502. The deployed demo above is already running and does not require local installation.

External URL: http://128.250.0.200:8502

Python 3.9+ and Streamlit 1.41 or newer.

## Standalone website (no install)

`web/index.html` is a single-file version of the same product: double-click it and it opens in any browser. It needs no Python or Streamlit and doesn't need to be online (Inter loads from Google Fonts when available, otherwise the system font is used). The scoring engine in `web/src/engine.js` is a line-for-line port of the Python modules; 864 input combinations were cross-checked and match exactly. Rebuild after editing `web/src/*` with `python tools/build_web.py`.

## Demo path (about 60 seconds)

1. Click **Demo Logistics Group** (or type "demo" and press Enter).
2. Go through the payment profile: 31 / 49 / 20 split, a worsening trend, **HIGH** payment-delay risk (76%).
3. Keep the default deal ($120k contract, $45k cash, $25k/month costs, 60 days, 0% upfront) and click **Analyse My Deal**. You get **CRITICAL, 79 / 100**.
4. In **Make this deal safer**, drag upfront to 30% and pick 30-day terms. Exposure moves to **MODERATE, 54**, and the page says *"Same customer. Different deal structure. Lower exposure."*
5. Or click **Apply suggestion** to jump to the smallest upfront % that reaches Moderate.
6. Click **New analysis** to start again.

Other demo customers cover the other states: *Sample Corporate Services* (low risk), *Example Infrastructure Ltd* (critical risk) and *Sample Manufacturing Co* (missing industry, history and peer data).

## Project structure

```
app.py                  page composition + Streamlit callbacks
src/services.py         the ONLY data/model entry point the UI uses (facade)
src/mock_services.py    demo companies + mock payment-delay "model"
src/risk_engine.py      deterministic contract exposure engine (+ min-upfront finder)
src/recommendations.py  plain-English next steps
src/state.py            journey state machine (plain dict–testable)
src/formatting.py       currency parsing / display helpers
src/ui/components.py    pure HTML builders (no business data)
src/ui/styles.py        stylesheet (our classes + scoped widget overrides)
src/ui/compat.py        Streamlit version feature-detection
.streamlit/config.toml  theme colours, hides chrome and error details
tests/                  unit tests + full journey test
tools/preview.py        renders static previews/screenshots of every state
```

## Plugging in real data and ML

The UI only calls `src/services.py`. To go live:

1. Create `src/real_services.py` that implements the same functions and returns the same shapes:

```python
def search_company(query: str) -> list            # [{company_id, name, abn, industry, size_band, is_demo}]
def get_company_features(company_id: str) -> dict # {pct_within_30, pct_31_60, pct_over_60, trend, trend_delta_days,
                                                  #  peer_slower_than_pct, peer_group, industry, abn, name, data_as_of, …}
def get_company_history(company_id: str)          # [{period, avg_days_to_pay}] (a DataFrame also works)
def predict_payment_risk(features: dict) -> dict  # {probability 0-1, level, factors[{text, tone}], confidence, model}
```

2. Run with `PAYLENS_BACKEND=src.real_services streamlit run app.py`, or change the default in `src/services.py`.

The facade takes care of edge cases: backend errors turn into empty states rather than stack traces, a percentage probability is converted to 0–1, and plain-string factors are accepted.

## Contract exposure methodology (prototype heuristic)

```
analyse_contract(payment_probability, contract_value, cash_reserve,
                 monthly_cost, upfront_pct=0.0, payment_terms_days=30) -> dict
```

| Component | Max pts | Formula |
|---|---|---|
| Customer delay risk | 20 | `p × materiality` |
| Exposure vs cash | 25 | `1 − exp(−ratio / 2.5)` |
| Timing vs runway | 35 | `(1 − exp(−pressure)) × materiality` |
| Upfront protection gap | 20 | `(1 − upfront) × materiality` |

- `net_exposure = contract × (1 − upfront)`, `ratio = net_exposure / cash`
- `materiality = min(1, ratio / 2)`: the share of your cash that is at stake
- `pressure = (terms + p × 30 days) / 30 ÷ ((cash + upfront received) / monthly costs)`
- Bands: 0–30 LOW, 31–55 MODERATE, 56–75 HIGH, 76–100 CRITICAL

Every constant lives in `ScoringConfig` in `src/risk_engine.py`. Zero cash, zero costs, a zero contract, 100% upfront and garbage inputs are all handled without crashing. **This is decision support. It is not a validated credit score.**

## Tests

```bash
python -m pytest            # or: python -m unittest discover -s tests -t .
```

The tests cover: score bounds across a large input grid, band boundaries, zero cash / costs / contract, 100% upfront, 90-day terms, very large and very small contracts, monotonicity (more upfront or shorter terms never increase exposure), mock services, the reset flow, recommendations, and a full journey through `app.py`. When Streamlit is installed, the journey test uses Streamlit's `AppTest`. When it isn't, it uses a strict stand-in in `tests/streamlit_stub.py`.

`python tools/preview.py` writes HTML previews and Playwright screenshots of every journey state (initial, search, no results, customer, analysed, simulated, applied, missing data) at desktop and mobile widths.
