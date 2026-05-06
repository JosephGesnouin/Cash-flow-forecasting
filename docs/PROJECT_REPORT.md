# Project report — Cash-Flow Forecasting application

> 🏦 Produced by **BNP Paribas Cash Management** as a treasurer-education
> demo. Built by Claude (Opus 4.7) under a "vibe-coding" prompt from a
> corporate-treasury angle.
>
> Branch: `claude/cash-flow-forecasting-app-3fl9v`
> Date: 2026-05-05

This document is the audit trail of the project: what the user asked for, the
design decisions taken in response, what was actually built, and how to
operate it. It is meant to stand on its own — a reader who has never seen the
chat conversation should be able to understand the entire delivery from this
single file.

---

## 1. The original request

The user prompt (paraphrased from French):

> *"Pretend you are a corporate treasurer. Vibe-code me a cash-flow
> forecasting application, with all the necessary documentation and simulated
> data."*

Then a follow-up:

> *"Write complete English documentation explaining the exchanges and what
> you did, plus an HTML of the page."*

There were no further constraints — no preferred stack, no specific KPIs, no
target company size. That's the spirit of "vibe coding": the developer (here,
Claude) is free to pick the right tool and bring domain judgement to fill the
blanks.

---

## 2. Decisions taken before writing any code

### 2.1 Persona — what does a real treasurer want?

A corporate treasurer's morning routine is roughly:

1. **Where is the cash?** Across all bank accounts, all currencies, all
   entities, *right now*.
2. **Where will the cash be?** Over the next 13 weeks (the industry-standard
   short-term horizon).
3. **What if things go wrong?** Stress tests on revenue, customer payment
   delays, capex.
4. **Who owes us / who do we owe?** AR/AP detail, with aging.
5. **Was last month's forecast any good?** Variance and recalibration.

These five questions structured the entire app — one page per question, plus
a summary dashboard.

### 2.2 The fictional company

To avoid generic dummy data, I designed a fictional issuer that gives the
numbers a realistic *texture*:

- **Helios Industries SA** — French mid-cap industrial group, EUR base
  currency, ~€80M annual revenue
- 12 customers across Energy / Aerospace / Public Sector / Defence /
  Construction etc., with realistic payment-terms (30–75 days) and a
  paying-behaviour spectrum (early / on-time / late / very late)
- 10 suppliers in raw materials, components, utilities, IT, professional
  services
- 8 bank accounts: 4 EUR (operating, payroll, tax & VAT, term deposit) at BNP
  Paribas + Deutsche Bank, 1 GBP at NatWest, 1 USD at Citibank, plus a €15M
  revolving credit facility at HSBC of which €1.5M drawn
- A €3M minimum cash-buffer policy (typical mid-cap covenant level)

The deterministic generator (`SEED = 42`) produces 24 months of history —
3,365 transactions, 2,340 AR invoices (482 currently open), 1,603 AP
invoices (291 open), and a daily FX rate series (EUR/USD around 1.08,
EUR/GBP around 0.85 with realistic random-walk volatility).

### 2.3 Stack choice — why Streamlit?

Three viable options were considered:

| Option         | Pros                                        | Cons                       |
|----------------|---------------------------------------------|----------------------------|
| **Streamlit**  | de-facto standard for finance dashboards; hot reload; rich plotly support; minimal boilerplate | Python-only; opinionated layout |
| Next.js + React | best-in-class polish; full control          | much heavier; weeks of work |
| Static HTML/JS | zero install                                | no interactivity; data baked in |

Streamlit was chosen because it gives a treasurer *exactly* the kind of
sliders / date-pickers / drill-downs that real workflows demand, with five
dependencies and a ~5-minute setup. A static HTML preview was added later
(see §6) so the project can also be shared without running Streamlit.

### 2.4 Forecasting methodology

A short-term cash forecast must be **direct** (line-by-line receipts and
payments), not derived from net income. The app implements:

1. **Direct method** as the primary forecast: combines (a) expected receipts
   from open AR invoices shifted by realised customer payment delay, (b)
   payments on open AP invoices, (c) recurring fixed items (payroll, social
   charges, VAT, debt service, rent, capex, FX hedging, taxes) projected
   from historical 6-month averages on canonical calendar dates.
2. **Statistical method** as a sanity check: trend + day-of-week +
   month-of-year decomposition, projected forward.
3. **Scenarios** as a 3-tuple of knobs over the same engine:
   `(sales_multiplier, collection_delay_days, capex_multiplier)`.
4. **Variance** using point-in-time data: the forecast as of N weeks ago is
   reconstructed from the data that *would have been visible* at that date
   — no future leakage — and compared against the actuals that have since
   posted.

This is the methodology section of `docs/METHODOLOGY.md`, summarised.

---

## 3. What was built

### 3.1 Repository layout

```
.
├── app.py                          # Streamlit entrypoint (Dashboard)
├── pages/
│   ├── 1_Forecast.py               # 13-week direct forecast
│   ├── 2_Scenarios.py              # Base/Optimistic/Stress + heat-map
│   ├── 3_Receivables_Payables.py   # AR/AP drill-down
│   ├── 4_Bank_Accounts.py          # Multi-currency liquidity view
│   ├── 5_Variance.py               # Forecast-vs-actuals MAPE
│   └── 6_Methodology.py            # Renders the methodology doc
├── src/                            # Pure library (no Streamlit)
│   ├── data_loader.py              # CSV/JSON loading + FX→EUR conversion
│   ├── metrics.py                  # KPIs (cash, DSO, DPO, aging…)
│   └── forecasting.py              # Direct & statistical engines, variance
├── data/
│   ├── generate_data.py            # Deterministic synthetic-data generator
│   ├── cash_transactions.csv       # 3,365 rows
│   ├── ar_invoices.csv             # 2,340 rows
│   ├── ap_invoices.csv             # 1,603 rows
│   ├── bank_accounts.csv           # 8 rows
│   ├── fx_rates.csv                # 855 rows
│   └── assumptions.json            # Drivers + scenario knobs
├── docs/
│   ├── PROJECT_REPORT.md           # ← this file
│   ├── METHODOLOGY.md              # Forecasting math
│   ├── DATA_MODEL.md               # Schema field-by-field
│   ├── USER_GUIDE.md               # Treasurer's walk-through
│   └── dashboard.html              # Static HTML preview (built by tools/)
├── tools/
│   └── build_html_dashboard.py     # Generates docs/dashboard.html
├── requirements.txt
├── .streamlit/config.toml          # Light theme, primary color #0E4D92
└── .gitignore
```

### 3.2 Key numbers produced

After `python data/generate_data.py` and on the reference date 2026-05-05:

| Metric                          | Value             |
|---------------------------------|-------------------|
| Cash on hand (excl. RCF)        | €18.28M           |
| Liquidity runway                | 2.8 months        |
| Open AR                         | €38.30M           |
| Open AP                         | €13.37M           |
| Working-capital gap (AR − AP)   | €24.92M           |
| DSO                             | 55.0 days (target 52) |
| DPO                             | 43.0 days (target 41) |
| RCF available                   | €13.5M (€15M limit, €1.5M drawn) |
| 13-week base closing balance    | €19.49M           |
| 13-week stress closing balance  | €14.34M           |
| 13-week minimum (any scenario)  | €12.89M (above €3M buffer) |

These are deliberately calibrated so that:
- The base case shows mild positive cash generation,
- The stress scenario erodes ~€5M of headroom but does **not** breach the
  buffer — making the dashboard useful as a teaching tool rather than
  alarmist.

### 3.3 Per-page summary

| Page | Anchors | Charts | Interactions |
|------|---------|--------|--------------|
| Dashboard | 8 KPIs (cash, runway, RCF, WC gap, DSO, DPO, AR, AP) | 90-day cash position vs buffer | None |
| Forecast | 4 KPIs (inflows, outflows, closing, min balance) | Projected balance curve, weekly waterfall, category breakdown | Horizon slider, freq selector, sales/delay/capex sliders |
| Scenarios | KPI table for 3 scenarios | Combined trajectory chart, sensitivity heat-map | Horizon slider |
| AR/AP | 4 KPIs per tab | Aging buckets, top counterparties, country/category treemap | Tab switcher |
| Bank Accounts | 3 KPIs | Account table, ccy donut, type bar, FX trend, per-account daily series | None |
| Variance | 4 KPIs | Forecast vs actual bars + variance line | Vintage slider, horizon slider, freq selector |
| Methodology | — | — | Static |

---

## 4. The design conversation, exchange by exchange

### Exchange 1 — initial brief

**User**: vibe-code a cash-flow forecasting app with documentation and
simulated data, treasurer hat on.

**Assistant** (this is what happened internally):

1. Surveyed an empty repo. Confirmed the development branch
   (`claude/cash-flow-forecasting-app-3fl9v`) was already checked out.
2. Drafted the structure: Streamlit + pandas + plotly, with a `data/`
   generator, an `src/` library, a `pages/` Streamlit tree, and a `docs/`
   folder.
3. Wrote, in order: `requirements.txt`, `.gitignore`, `.streamlit/config.toml`,
   the data generator, the three library modules (loader / metrics /
   forecasting), the seven Streamlit pages, then the documentation.
4. **First data generation produced unrealistic numbers**: a negative cash
   position of −€34M after 24 months, because monthly customer revenue
   (~€3.4M) was below total monthly outflows (~€5.5M). I diagnosed this by
   reading the smoke-test output, then re-balanced the model:
   - Customer monthly volumes scaled ~1.85x to ~€6.2M/month total,
   - Supplier monthly spend scaled to ~€2.35M/month (preserving a
     32% gross-margin shape),
   - Opening bank balances bumped to ~€19.8M total (excl. RCF) so the
     simulated company is a *healthy* mid-cap, not a distressed one.
5. Re-ran the generator. The numbers came out at €18.28M cash, 2.8 months
   runway, with the stress scenario staying above the €3M buffer — these
   are the headline metrics the dashboard shows today.
6. Smoke-tested every page's logic path (forecast at 3 frequencies,
   statistical projection, sensitivity grid 7×6, AR/AP aging, variance
   reconstruction) without errors.
7. Booted Streamlit headlessly to confirm the homepage returns HTTP 200.
8. Committed the 25 files in one root commit and pushed.

**Why this worked first try after the rebalance**: the synthetic generator
is deterministic (seeded). Once the unit-economic levers (revenue, COGS,
opex) were sized, every downstream page reflected the change without any
Streamlit-level edits. That's the point of separating `src/` (library) from
`pages/` (presentation): rebalance once, ship everywhere.

### Exchange 2 — this report + HTML

**User**: write complete English documentation explaining the exchanges and
what you did, plus an HTML of the page.

**Assistant**: building two artefacts:

- `docs/PROJECT_REPORT.md` (this file) — narrative report, in English,
  covering the user prompts, the decisions, and the deliverable.
- `docs/dashboard.html` — a self-contained HTML preview of the dashboard
  (Plotly charts inlined), generated by `tools/build_html_dashboard.py`.
  Useful for sharing the project with someone who doesn't have Python /
  Streamlit installed.

---

## 5. How to operate

### 5.1 First-time install

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python data/generate_data.py
streamlit run app.py
```

### 5.2 Refresh the static HTML preview

```bash
python tools/build_html_dashboard.py        # writes docs/dashboard.html
open docs/dashboard.html                    # macOS; xdg-open on Linux
```

### 5.3 Tweak the simulated company

Open `data/generate_data.py` and edit:

- `TODAY` — reference date for the snapshot
- `HISTORY_MONTHS` — depth of history
- `CUSTOMERS` / `SUPPLIERS` rosters and monthly volumes
- `BANK_ACCOUNTS` opening balances
- `SEED` — change personality entirely

After editing, rerun `python data/generate_data.py` and refresh the
Streamlit page (Ctrl+R in the browser).

### 5.4 Tweak the policy thresholds

Edit `data/assumptions.json`:

- `drivers.min_cash_buffer_eur` — the red guard-rail line on charts
- `drivers.dso_target_days` / `drivers.dpo_target_days` — KPI deltas
- `scenarios.*` — knobs of the three scenarios

No code changes needed.

---

## 6. Static HTML preview — what it is and isn't

`docs/dashboard.html` is generated by `tools/build_html_dashboard.py`. It
uses the same `src/metrics.py` and `src/forecasting.py` library used by the
Streamlit app, so the numbers are identical. The Plotly charts are embedded
inline (CDN), so the file works offline once loaded.

What it includes:

- The 8 headline KPIs from the Dashboard
- 90-day cash position chart with minimum-buffer line
- 13-week base-case forecast trajectory
- Three-scenario comparison
- AR aging and top customers
- Currency split donut

What it deliberately omits compared to the Streamlit app:

- Sliders / interactive parameter changes
- Variance analysis (depends on point-in-time reconstruction tied to
  user-selected vintage)
- Drill-down tables (the static page targets executive-summary readability)

For full interactivity, run the Streamlit app.

---

## 7. Limitations and natural next steps

The app is a credible demo, not a production treasury system. To move it
toward production, the natural items to address — in priority order — are:

1. **Real bank-statement ingestion**: replace the synthetic
   `cash_transactions.csv` with MT940 / CAMT.053 imports. The data model
   already matches what those formats produce.
2. **Per-customer paying-behaviour learning**: today, behaviour is a label
   (`early` / `late` / …). A Gamma fit on
   `payment_date − due_date` per customer would yield calibrated
   distributions and confidence intervals on the forecast.
3. **FX hedging integration**: the app reports FX exposure but doesn't
   optimise hedge sizing. A simple linear-program would close that loop.
4. **ERP-aware capex pipeline**: replace the historical-average capex
   projection with the capex-committee tracker.
5. **Authentication and audit**: any production treasury tool needs SSO and
   a write-audit log; not in scope here.

---

## 8. Provenance and license

All data is synthetic. *Helios Industries SA* and every customer / supplier
/ counterparty mentioned in the dataset are fictional. The IBANs are
formatted plausibly but are not real account numbers. Nothing in this
repository should be used to make real treasury decisions.

The code is intended for demo / educational use.
