# Helios Industries SA — Cash-Flow Forecasting

A treasury-grade **cash-flow forecasting application** built as a multi-page
Streamlit app, with a fully synthetic but realistic dataset (24 months of
transactions, AR/AP, multi-currency bank accounts, FX rates) for a fictional
mid-cap industrial company called **Helios Industries SA**.

This is what a corporate treasurer would actually want to see every morning:

- a **command-center dashboard** with cash position, runway, RCF availability,
  DSO/DPO and working-capital gap
- a **13-week direct cash-flow forecast** (the industry-standard rolling
  short-term cash plan), with weekly aggregation and a statistical sanity-check
  overlay
- **scenario analysis** (base / optimistic / stress) with a sensitivity
  heat-map across sales × collection-delay shocks
- **AR/AP drill-down** with aging buckets, top-counterparty concentration and
  treemaps by country / category
- **multi-bank, multi-currency liquidity view** with FX exposure trendline
- **variance analysis** comparing a frozen forecast vintage against actuals,
  with MAPE

> The numbers are simulated. The structure, ratios, drivers and forecast
> mechanics are exactly what we use in real life.

---

## Quick start

```bash
# 1. install
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# 2. generate synthetic data (writes CSV/JSON into ./data)
python data/generate_data.py

# 3. launch the app
streamlit run app.py
```

Then open http://localhost:8501 .

### Static HTML preview (no Streamlit needed)

```bash
python tools/build_html_dashboard.py     # writes docs/dashboard.html (+ index.html mirror)
```

A self-contained HTML file with the same KPIs and Plotly charts as the
Streamlit dashboard, suitable for sharing with stakeholders who don't have
Python installed. The same content is also written as `docs/index.html` so
the repo can be served directly via **GitHub Pages**:

> Repository → Settings → Pages → Source: branch
> `claude/cash-flow-forecasting-app-3fl9v`, folder `/docs` → Save.
> The demo will be live at
> `https://<owner>.github.io/<repo>/dashboard.html` (or just the root URL,
> which serves `index.html`).

See [`docs/PROJECT_REPORT.md`](docs/PROJECT_REPORT.md) for the full project
narrative in English.

The app pages are auto-discovered from `pages/` and appear in the sidebar:

| # | Page | What it answers |
|---|------|-----------------|
| 🏠 | **Home / Dashboard** | "How much cash do we have, where, and how long does it last?" |
| 📈 | **Forecast** | "What does the next 13 weeks look like?" |
| 🎯 | **Scenarios** | "What if sales drop 15% and customers pay 12 days later?" |
| 📒 | **Receivables & Payables** | "Who owes us, who do we owe, and is anything overdue?" |
| 🏦 | **Bank Accounts** | "What's our liquidity by entity / currency / account type?" |
| 🔍 | **Variance** | "Was last month's forecast any good?" |
| 📘 | **Methodology** | The forecasting model, written down. |

---

## Project layout

```
.
├── app.py                       # Streamlit entrypoint (dashboard)
├── pages/                       # Auto-discovered Streamlit pages
│   ├── 1_Forecast.py
│   ├── 2_Scenarios.py
│   ├── 3_Receivables_Payables.py
│   ├── 4_Bank_Accounts.py
│   ├── 5_Variance.py
│   └── 6_Methodology.py
├── src/                         # Pure-Python library (no Streamlit deps)
│   ├── data_loader.py           # CSV/JSON loading + EUR conversion
│   ├── metrics.py               # KPIs (cash position, DSO, DPO, aging…)
│   └── forecasting.py           # Direct & statistical forecasts, variance
├── data/
│   ├── generate_data.py         # Synthetic-data generator
│   ├── cash_transactions.csv    # Output: posted transactions
│   ├── ar_invoices.csv          # Output: customer invoices
│   ├── ap_invoices.csv          # Output: supplier invoices
│   ├── bank_accounts.csv        # Output: account master
│   ├── fx_rates.csv             # Output: daily FX vs EUR
│   └── assumptions.json         # Output: drivers + scenario knobs
├── docs/
│   ├── PROJECT_REPORT.md        # English narrative of conversation + delivery
│   ├── WORKSHOP.md              # 45-min vibe-coding session plan (FR)
│   ├── METHODOLOGY.md           # Forecasting math
│   ├── DATA_MODEL.md            # Field-by-field schema
│   ├── USER_GUIDE.md            # Treasurer's walk-through
│   ├── dashboard.html           # Static preview (built by tools/)
│   └── index.html               # Mirror for GitHub Pages
├── tools/
│   └── build_html_dashboard.py  # Renders docs/dashboard.html
└── requirements.txt
```

---

## Key design choices

- **EUR is the base currency.** Every amount is stored in its native currency
  *and* converted to EUR using the daily FX rate at transaction date. The
  `data_loader` performs the conversion once on load.
- **The forecast is direct, bottom-up.** We don't try to project net cash from
  P&L (the indirect method) — short-term cash forecasts demand line-by-line
  receipts/payments visibility. We additionally surface a statistical
  trend+seasonality projection as a sanity check.
- **Scenarios are knobs, not separate spreadsheets.** A scenario is a tuple
  `(sales_multiplier, collection_delay_days, capex_multiplier)`; the same
  engine produces the projection.
- **Variance uses point-in-time data.** When you look at "the forecast as of
  4 weeks ago", we re-derive it from invoices/transactions that existed at
  that date — nothing is leaked from the future.
- **No external services.** The whole thing runs offline with five
  dependencies: streamlit, pandas, numpy, plotly, python-dateutil.

See [`docs/METHODOLOGY.md`](docs/METHODOLOGY.md) for the math and
[`docs/DATA_MODEL.md`](docs/DATA_MODEL.md) for the schema.

---

## Regenerating data

`data/generate_data.py` is deterministic (`SEED = 42`). Edit the constants at
the top of the file (today's date, history length, customer/supplier rosters,
FX volatility, recurring-item amounts) and re-run. All downstream pages will
pick up the new data on next refresh.

---

## License

Demo / educational. No real bank, customer or supplier data. The fictional
"Helios Industries SA" and all counterparty names are invented for the purpose
of this demo.
