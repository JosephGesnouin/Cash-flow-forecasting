# Helios Industries SA — Cash-Flow Forecasting

> 🏦 **A treasurer-education demo by BNP Paribas Cash Management.**
> Built to train junior treasurers and product owners on how a modern
> short-term cash-flow forecasting tool works, what assumptions sit
> underneath it, and how to specify the next features. The fictional
> client *Helios Industries SA* mirrors the profile of a typical BNP
> Paribas Cash Management mid-cap industrial customer.

> **You're the Product Owner.** You opened this repo because someone is
> going to ask you, in the next few weeks, *"what should we build into our
> treasury cash-flow tool?"*. This README is written to put you in the
> driving seat: what the app already does, what the numbers mean, what
> assumptions sit underneath, and where the obvious next features are.
>
> By the end of it you should be able to walk into a 30-minute call with
> IT and say *"here's our backlog, here's our priority, here's the
> acceptance test for feature #1"*.

---

## 1. The 3-minute tour

Imagine you walked into the treasury department of a fictional industrial
group called **Helios Industries SA** on the morning of 5 May 2026. The
app is open on your laptop. You see seven tabs. Here's what each one
answers:

| Tab | The treasurer's question it answers in one sentence |
|-----|------------------------------------------------------|
| 🏠 **Home / Dashboard** | *"How much cash do I have right now, in how many places, and how long does it last me?"* |
| 📈 **Forecast** | *"What does my cash position look like over the next 13 weeks if nothing surprising happens?"* |
| 🎯 **Scenarios** | *"What if sales drop 15% and our customers pay 12 days later? Do I breach my minimum buffer? Do I need to draw on my RCF?"* |
| 📒 **Receivables & Payables** | *"Who owes me money, how late are they, and which 3 customers do I really need to keep happy?"* |
| 🏦 **Bank Accounts** | *"What's my liquidity per entity, per currency, and what's my FX exposure trending like?"* |
| 🔍 **Variance** | *"Was last month's forecast any good? Where did I miss?"* |
| 📘 **Methodology** | *"How exactly is the forecast computed? (For when audit asks.)"* |

That's the **product as it exists today**. Everything else in this README
either explains what's underneath, or puts you in a position to challenge
it.

---

## 2. Meet your client — Helios Industries SA (fictional)

To make the numbers feel real, the app tells the story of a believable
mid-cap industrial group. None of the names are real, but the *shape* is
typical of what you'd find on the books of a French ETI in the BNP
Paribas Cash Management book:

- **Sector**: industrial manufacturing, EUR base currency.
- **Annual revenue**: ~€80M, growing ~4.5% YoY.
- **Gross margin target**: 32%.
- **Customer book**: 12 active accounts across Energy, Aerospace, Defence,
  Public Sector, Industrial, Construction. Payment terms range from 30 to
  75 days. Some pay on time, some are systematically late (looking at you,
  Helios Public Transit at 75 days + ~20 days of drift).
- **Supplier book**: 10 strategic suppliers (steel, polymers, components,
  utilities, IT, professional services).
- **8 bank accounts** at 5 banks: 4 EUR (operating, payroll, tax & VAT,
  term deposit), 1 GBP (NatWest), 1 USD (Citibank), and a €15M revolving
  credit facility at HSBC of which €1.5M is currently drawn.

That's your "client" for the rest of the doc.

---

## 3. What the app shows you, today

Headline numbers as of 2026-05-05 (refresh the data and they shift):

| KPI | Value | Reading |
|-----|-------|---------|
| Cash on hand (excl. RCF) | **€18.28M** | comfortably above the €3M minimum buffer |
| Liquidity runway | **2.8 months** | (cash ÷ trailing-6m average outflow) |
| RCF available | **€13.50M** of €15M | only €1.5M drawn — plenty of dry powder |
| Open AR | **€38.30M** (482 invoices) | the working-capital lifeblood |
| Open AP | **€13.37M** (291 invoices) | what we owe |
| Working-capital gap | **+€24.92M** | AR > AP — we're financing our customers |
| DSO | **55.0 d** | vs target 52d → +3d drift, modest but worth tracking |
| DPO | **43.0 d** | vs target 41d → +2d, fine |
| 13-week base closing | **€19.49M** | mild positive cash generation forecast |
| 13-week stress closing | **€14.34M** | stress scenario erodes ~€5M, no breach |

If those numbers stop being plausible (e.g. cash on hand goes negative),
either the data was regenerated with different assumptions or something
broke. They are the canary.

---

## 4. What's simulated, what's plausible, what's invented

This is the section a junior PO is most often asked to explain. Be
precise: the *texture* of the data is realistic, but the *content* is
fictional.

### What's invented (do not believe it for a second)

- Every customer name, supplier name, bank account IBAN, transaction.
- Every euro amount.
- The capex calendar, the M&A history (none), the precise FX rates.

### What's *modelled to be plausible* (the data behaves like real data)

- **Customer payment behaviour**: each customer has a paying personality
  (`early`, `ontime`, `late`, `very_late`). Paid invoices show a payment
  date drawn from a normal distribution around their due date with the
  characteristic offset. So if you compute DSO bucket-by-customer, you
  get realistic dispersion — not a single number on every line.
- **Seasonality**: revenue has a sine-shaped annual cycle plus a summer
  dip in August (-22%) and a Q4 peak in Nov-Dec (+12%). The forecast
  picks this up via the historical-average mechanism.
- **Recurring outflows**: payroll on the last business day, social
  charges 5 days later, VAT on the 20th, debt service on the 15th, rent
  on the 1st, quarterly corporate tax on the 15th of the following
  quarter end, term-deposit interest on the 28th of each quarter end.
  These are real treasury calendars.
- **Multi-currency exposure**: ~€1.65M held in USD, ~€820k in GBP at the
  reference date. EUR/USD does a random walk around 1.08, EUR/GBP around
  0.85, with realistic daily volatility.
- **Aging profile**: AR aging buckets show a long-tail of small overdue
  balances dominated by Public Sector (75-day terms + 20-day drift),
  matching what you'd see on a real balance.

### What's not modelled (and that's OK for now — but it's PO backlog material)

- **Real bank reconciliation**: there's no MT940 / CAMT.053 import. The
  cash position is computed by walking transactions, not by reading bank
  statements.
- **Intercompany flows**: cash pooling, sweep accounts, intercompany
  funding — only stylised at best.
- **Hedging logic**: FX exposure is shown, but no optimal-hedge
  recommendation. Hedge premiums are flat.
- **Credit risk**: customers don't default. Open AR is always recoverable.
- **Project-level capex**: the capex outflow is a 6-month historical
  average, not a project-by-project tracker.
- **Authentication, audit trail, multi-user**: zero. This is a
  single-user demo.

A junior PO's first job: **decide which of these absences matters most**
to your real treasury team, and pitch it as feature #1.

---

## 5. The cash-management policy assumptions (the rules of the game)

These live in `data/assumptions.json` and are the levers a PO can pull.
Every chart in the app references at least one of them.

```jsonc
{
  "company": "Helios Industries SA",
  "base_currency": "EUR",
  "today": "2026-05-05",
  "drivers": {
    "revenue_growth_yoy": 0.045,        // +4.5% YoY trend baked into history
    "gross_margin": 0.32,               // 32% gross margin
    "dso_target_days": 52,              // any drift > 5d → escalate
    "dpo_target_days": 41,              // we don't pay early; we don't pay too late
    "min_cash_buffer_eur": 3000000,     // the red line on every chart
    "rcf_limit_eur": 15000000,          // total committed facility
    "rcf_drawn_eur": 1500000            // currently drawn portion
  },
  "scenarios": {
    "base":       { "sales_multiplier": 1.00, "collection_delay_days":  0,  "capex_multiplier": 1.00 },
    "optimistic": { "sales_multiplier": 1.08, "collection_delay_days": -3,  "capex_multiplier": 1.10 },
    "stress":     { "sales_multiplier": 0.85, "collection_delay_days": 12,  "capex_multiplier": 0.60 }
  }
}
```

**Treasurer's reading of each driver**:

- `min_cash_buffer_eur` is your **floor**. If the forecast crosses it, you
  trigger a treasury action (usually: draw RCF, defer capex, accelerate
  collections). On every chart it's the dashed red line.
- `dso_target_days` / `dpo_target_days` are your **steering wheel**.
  Variance vs target is shown on the dashboard with a delta indicator.
- `rcf_limit_eur` minus `rcf_drawn_eur` is your **dry powder**. The
  dashboard shows availability. A real treasurer also tracks the bank
  covenants attached — out of scope here.
- The three **scenarios** are calibrated against historical mid-cycle
  industrial downturns (the stress = 2009-style demand shock + 2020-style
  collection delay). You can edit the JSON to add `extreme_stress` or
  `cyber_event` — no code change needed.

Editing this file is the **fastest way to PO a new policy**. Want to
test a more conservative buffer at €5M? Edit one number, refresh the
page, every chart updates. That's the kind of immediate-feedback
prototyping a real treasury committee can do live in a meeting.

---

## 6. How the forecast actually works (in treasurer language)

Skip this section if you only care about the numbers. Read it if you'll
defend the forecast in front of audit or a CFO.

The app uses the **direct method** as its primary forecast — meaning:
list every expected receipt and every expected payment on its expected
date, sum them. We do **not** project net cash from P&L. (That would be
the *indirect* method; it's good for the annual budget, useless for
short-term liquidity.)

For each day in the next 13 weeks, the forecast computes:

```
day_flow = AR_receipts(day) + AP_payments(day) + recurring(day)

  AR_receipts: from open customer invoices,
               shifted by their realised payment delay
               (early/ontime/late/very_late personality)

  AP_payments: from open supplier invoices,
               shifted by our own typical payment timing

  recurring:   payroll, social charges, VAT, rent, debt service,
               capex, FX hedging, quarterly corporate tax,
               quarterly interest income on term deposit
               — all projected from a 6-month historical average,
               placed on the canonical calendar date
```

A second projection runs in parallel — a **statistical** one — that
decomposes the historical daily flow into trend + day-of-week +
month-of-year seasonality and projects forward. We display it as a dotted
overlay on the Forecast page. **It's a sanity check**: if direct and
statistical disagree by more than ±10% at the horizon, something is off
(usually a missed recurring item, or a structural break the direct method
caught correctly).

For the variance page, we don't compare the *current* forecast against
*current* actuals (that would be cheating). We rebuild the forecast as it
*would have been* N weeks ago, using only the data available at that
date — same code, same engine, point-in-time inputs. Then we compare to
what's posted since.

Full math is in [`docs/METHODOLOGY.md`](docs/METHODOLOGY.md).

---

## 7. The KPIs reference card (keep this open during reviews)

| KPI | Formula in plain words | Why it matters |
|-----|------------------------|----------------|
| **Cash on hand (€)** | Sum of EUR-equivalent closing balances on operating / payroll / tax / term-deposit accounts. RCF excluded. | The number you can spend tomorrow without negotiating anything. |
| **Liquidity runway (months)** | Cash on hand ÷ trailing 6-month average monthly outflow. | "If revenue dried up tomorrow, how long do I last?" |
| **Working-capital gap (€)** | Open AR (in EUR) − Open AP (in EUR). | Positive = we're financing our customers' delays. Negative = our suppliers are financing us. |
| **DSO (days)** | Open AR ÷ trailing 90-day credit sales × 90. | How long, on average, between an invoice and its cash. |
| **DPO (days)** | Open AP ÷ trailing 90-day purchases × 90. | Symmetric, on the supplier side. |
| **AR overdue %** | Share of open AR with `due_date < today`, in EUR. | Pain index of the credit-control team. |
| **Aging buckets** | Open invoices grouped by `today − due_date` into Not due / 1-30 / 31-60 / 61-90 / 90+. | The *shape* of the AR risk, not just the size. |
| **MAPE (variance)** | Mean Absolute Percentage Error of forecast vs actual, weekly. | Recalibrate when above 15%. |

---

## 8. Your PO backlog — what to prioritise next

Below is a ready-made backlog grouped by theme. Treat it as a starting
point. Reorder it based on what your real treasury team would benefit
from most, then turn the top two into proper issues (next section).

Effort tags: **S** = under an hour for someone who knows the codebase ·
**M** = half a day · **L** = full sprint or more.

### 8.1 — Data integration (connecting to real life)

| # | Feature | User story | Effort |
|---|---------|-----------|--------|
| 1 | **Bank statement ingestion** | *As a treasurer I want to import my bank's MT940/CAMT.053 files so the cash position reflects today's actual balances, not synthetic data.* | L |
| 2 | **ERP invoice sync** | *As a treasurer I want open AR/AP to refresh automatically from our ERP (SAP/Oracle/Sage) so I never key invoices twice.* | L |
| 3 | **TMS / payment platform connector** | *As a treasurer I want to push outgoing payment runs to our payment platform (Kyriba / SWIFT GPI) without manual export.* | L |
| 4 | **FX rates from a real source** | *As a treasury controller I want EUR/USD and EUR/GBP to come from ECB or Bloomberg, not a synthetic random walk.* | S |

### 8.2 — Forecast quality (better numbers)

| # | Feature | User story | Effort |
|---|---------|-----------|--------|
| 5 | **Per-customer payment-delay learning** | *As a treasurer I want each customer's expected payment date to come from a fitted distribution on their own payment history, not a generic label.* | M |
| 6 | **Confidence interval on the forecast** | *As a treasurer I want a P10 / P50 / P90 cone on the 13-week forecast so I see the uncertainty, not just a point estimate.* | M |
| 7 | **Forecast accuracy by category leaderboard** | *As a treasurer I want a MAPE leaderboard per category over the last 6 vintages so I know which assumptions are drifting.* | M |
| 8 | **Manual override line items** | *As a treasurer I want to add ad-hoc one-off lines (M&A, dividend, settlement) without editing JSON files.* | S |

### 8.3 — Risk management

| # | Feature | User story | Effort |
|---|---------|-----------|--------|
| 9 | **Customer concentration risk score** | *As a treasurer I want a Herfindahl index + top-3 share on open AR with a red-flag threshold so I monitor concentration risk.* | S |
| 10 | **Counterparty credit-risk overlay** | *As a credit-control lead I want each customer flagged with a credit rating (e.g. Coface / Altares) so overdue AR on a downgraded counterparty is escalated.* | L |
| 11 | **FX hedge sizing recommender** | *As a treasurer I want a recommendation on how much USD/GBP forward to buy to keep my net exposure within a tolerance band.* | L |
| 12 | **Stress-scenario library** | *As a treasurer I want a curated library of historical shock scenarios (2008, 2020, energy 2022) I can apply with one click.* | M |

### 8.4 — Workflow & alerts

| # | Feature | User story | Effort |
|---|---------|-----------|--------|
| 13 | **DSO drift alert** | *As a credit-control lead I want a banner alert when DSO exceeds target by 5 days so I can escalate before it becomes a runway issue.* | S |
| 14 | **AR collection worklist** | *As a credit-control lead I want a per-customer "next action" column on the Receivables page so my team has a daily worklist.* | M |
| 15 | **Bank-fee anomaly detector** | *As a treasury controller I want any bank fee > 1.5x the trailing 12-month rolling average to be flagged automatically.* | S |
| 16 | **Slack / Teams notification** | *As a treasurer I want a daily summary posted to my team channel: cash position, runway, top-3 events of the next 5 days.* | S |

### 8.5 — Reporting & operations

| # | Feature | User story | Effort |
|---|---------|-----------|--------|
| 17 | **PDF / Excel export for the CFO** | *As a treasurer I want a one-click "monthly board pack" PDF with the headline KPIs, the 13-week forecast chart and the scenarios summary.* | M |
| 18 | **Cash pooling simulation** | *As a group treasurer I want to see the consolidated cash position under a notional cash pool across the four EUR accounts.* | M |
| 19 | **Real-time intraday view** | *As a treasurer I want same-day movements (received / pending / outgoing) so I can decide whether to draw RCF before the 4pm cut-off.* | L |
| 20 | **Authentication & audit log** | *As a treasury controller I want every action tied to a named user and timestamped, with a downloadable audit trail.* | L |

### 8.6 — Acceptance-test template (use this for any feature you pick)

```
GIVEN   <starting state of the app — which page, which data>
WHEN    <the action the user takes — opens, clicks, configures>
THEN    <the observable result — a value shown, a chart updated,
         a file downloaded, an alert triggered>
AND     <a measurable, falsifiable secondary check>
```

Worked example for #13 (DSO drift alert):

> **GIVEN** the Dashboard is open with `assumptions.json → drivers.dso_target_days = 52`
> **WHEN** the computed DSO is ≥ 57 days (target + 5)
> **THEN** a red banner appears at the top of the Dashboard
> **AND** the banner text shows the current DSO and the absolute drift in days
> **AND** the banner disappears immediately when DSO drops back below 57

That's a unit-test specification. A developer (or the AI you prompt) can
ship it without ambiguity. This is also exactly what you paste into the
"Acceptance criteria" field of the GitHub issue (next section).

---

## 9. Propose an update — file a GitHub issue

Once you've picked a feature (or spotted a bug, or found a number that
doesn't match your reference), the right next step is to **open an
issue** on this repository. Issues are the unit of conversation between
treasury (you) and engineering (or the AI you prompt). A well-written
issue can be picked up and shipped without a single follow-up question;
a bad one bounces back and forth for days.

### 9.1 — The three templates available

This repository ships three issue templates in
[`.github/ISSUE_TEMPLATE/`](.github/ISSUE_TEMPLATE). When you click
*New issue* on GitHub, you will be offered a choice:

| Template | Use it when… |
|----------|--------------|
| 🟢 **Feature request (treasury PO)** | You want a new KPI, page, slider, alert, export — anything that adds capability. |
| 🔴 **Bug report** | A number, a chart, or a behaviour is wrong, missing, or crashes. |
| 🟡 **Data question** | A number is technically computed correctly but doesn't match what *you* would have computed from the underlying data. Often the methodology answer, sometimes a real bug in disguise. |

If your need doesn't fit any of these three, file a **feature request**
and tag it with whatever extra context you have. Don't write a free-form
issue — the templates exist to keep treasurers from forgetting the
acceptance criteria.

### 9.2 — Step-by-step: how to file an issue (5 minutes)

1. **Go to the repo on GitHub** → `Issues` tab → green button `New issue`.
2. **Pick the template** that matches your case (above).
3. **Fill in the template top-to-bottom**. Don't skip the acceptance
   criteria — it's the most important part. If you don't have one, you
   don't have a feature, you have a wish.
4. **Attach a screenshot** if you're talking about something visible.
   Drag-and-drop into the issue body — GitHub uploads it for you.
5. **Pick labels**. Templates pre-apply `enhancement`, `bug`, or
   `question`. Add `treasury-priority/high|medium|low` if you've agreed
   with your team on prioritisation, and `area/dashboard|forecast|ar-ap|…`
   to flag the surface.
6. **Submit**. The issue appears in the project board. Either a
   developer picks it up, or you (or your facilitator) drop the issue
   text into Claude Code as a prompt and ship it yourself.

### 9.3 — Worked example (filled-in feature request)

Here's what backlog item #13 (DSO drift alert) looks like as a finished
GitHub issue. This is exactly the level of detail you want to aim for.

```markdown
**Title**: [Feature] DSO drift alert on Dashboard

### What treasury question are you trying to answer?
We currently spot DSO drift only when the monthly board pack is built —
~2 weeks of lag. We need a same-day signal so credit-control can
escalate before runway is impacted.

### Acceptance criteria
GIVEN the Dashboard is open with `assumptions.json → drivers.dso_target_days = 52`
WHEN the computed DSO is ≥ 57 days (target + 5)
THEN a red banner appears at the top of the Dashboard
AND the banner text shows the current DSO and the absolute drift in days
AND the banner disappears immediately when DSO drops back below 57

### Where in the app?
- [x] Dashboard
- [ ] Forecast
- [ ] Scenarios
- [ ] Receivables / Payables
- [ ] Bank Accounts
- [ ] Variance
- [ ] New page

### Data needed
- `data/ar_invoices.csv` (already loaded by `src/data_loader.load_ar()`)
- `data/assumptions.json → drivers.dso_target_days`
- DSO already computed by `src/metrics.dso(ar, today)`

### Effort estimate
- [x] S — under an hour for someone who knows the codebase
- [ ] M — half a day
- [ ] L — full sprint

### Why now?
Q2 review showed our DSO drifted 3 days vs target without anyone
noticing for 6 weeks. The cost in working capital was ~€450k. A
real-time alert would have caught it in the first 5 days.

### References
- `docs/METHODOLOGY.md` §6 (DSO formula)
- `docs/USER_GUIDE.md` §09:00 (the dashboard reading routine)
```

Notice: the issue could be implemented from this content alone, with
zero follow-up questions. That is the bar.

### 9.4 — What makes a good issue (the 5 do's)

1. **Specific title.** *"DSO drift alert on Dashboard"* not *"improve
   alerts"*.
2. **Acceptance criteria, not description.** A spec that's testable,
   not a paragraph of intent.
3. **Reference the data.** Name the file, the column, the existing
   function. *"Use `src.metrics.dso`"* saves the developer 20 minutes.
4. **Justify the priority.** Quantify the cost of *not* doing it (lost
   working capital, missed buffer breach, audit finding). One sentence
   is enough.
5. **One issue, one feature.** *"Add DSO alert and rebuild the
   variance page"* is two issues. Split them.

### 9.5 — What makes a bad issue (the 4 don'ts)

1. **"Improve the dashboard"** — no scope, no test. Closed in 24h.
2. **"Add ML"** — buzzword, no problem statement.
3. **"This is wrong"** — without saying what was expected.
4. **A 2-page novel** — a developer reads the first 5 lines. Lead
   with the acceptance criteria.

### 9.6 — Triage flow (what happens after you submit)

| Stage | Label | What it means |
|-------|-------|----------------|
| Just filed | `needs-triage` | Awaiting review by the maintainer / treasury committee. |
| Validated | `accepted` | Will be picked up; priority assigned. |
| In progress | `in-progress` | Someone is working on it. Branch usually linked. |
| Ready for PO review | `awaiting-po-review` | Implementation done, **you** validate the acceptance criteria. |
| Shipped | `closed` | Merged + deployed. Linked PR in the comments. |
| Won't ship | `wont-fix` | Out of scope or duplicate. Maintainer explains why. |

Your job as PO doesn't end at filing the issue: when it reaches
`awaiting-po-review`, you **open the app, run the acceptance test from
your own issue, and either approve or reopen with comments**. That
closing of the loop is what makes the next ten issues you file faster.

---

## 10. How to run it (you do not need to be a developer)

```bash
# install (one-time)
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# generate fresh synthetic data
python data/generate_data.py

# launch the interactive app
streamlit run app.py
```

Then open http://localhost:8501 .

If you only need a **screenshot for a deck**, skip Streamlit entirely:

```bash
python tools/build_html_dashboard.py     # writes docs/dashboard.html
```

That single file (~145 KB, all charts inlined) opens in any browser. The
same file is also written as `docs/index.html` so the repo is
**GitHub-Pages-ready** (Repository → Settings → Pages → Source: branch /
folder `/docs` → Save → public URL).

To **change the policy**, edit `data/assumptions.json` and refresh the
browser. No code change.

To **change the company shape** (different customers, different scale,
different FX volatility), edit the constants at the top of
`data/generate_data.py` and re-run `python data/generate_data.py`. The
seed is deterministic (`SEED = 42`); change it for a fresh personality.

---

## 11. Where to go next in this repo

Once you've internalised this README, the deeper docs are:

- [`docs/USER_GUIDE.md`](docs/USER_GUIDE.md) — a treasurer's morning
  walk-through, page by page, 9:00 to 10:15. Read this on day one.
- [`docs/METHODOLOGY.md`](docs/METHODOLOGY.md) — the math of the
  forecast and the KPIs. Read this before defending numbers in front
  of audit.
- [`docs/DATA_MODEL.md`](docs/DATA_MODEL.md) — every column, every file.
  Read this before requesting a new data field.
- [`docs/PROJECT_REPORT.md`](docs/PROJECT_REPORT.md) — how this app was
  actually built (with an AI). Read this to understand what's possible
  in a 2-hour build.
- [`docs/WORKSHOP.md`](docs/WORKSHOP.md) — 45-min "vibe coding"
  workshop plan. Read this if you'll be on stage running the live demo.

---

## 12. Project layout (one screen)

```
.
├── app.py                       # Dashboard (entry point)
├── pages/                       # 6 Streamlit pages, one per question
├── src/                         # Library: loader, metrics, forecasting
├── data/                        # Synthetic CSV + assumptions.json
├── docs/                        # All the docs you'd want as a PO
├── tools/                       # Build scripts (HTML preview)
├── .github/ISSUE_TEMPLATE/      # Templates for filing issues (PO-friendly)
└── requirements.txt
```

If you only ever edit two files: it'll be `data/assumptions.json` (to
change policy) and `data/generate_data.py` (to change the company shape).

---

## 13. Caveats & provenance

This is a **demo / educational** project produced by **BNP Paribas Cash
Management** for treasurer-education sessions. Helios Industries SA,
every customer, every supplier, every IBAN, every euro amount is
fictional. Do not use this app to run real treasury decisions. Do use
it to prototype, to teach, to onboard juniors, and — most usefully —
to write specifications for the real tool you'll commission next.

The numbers above (cash €18.28M, runway 2.8 months, DSO 55, etc.) are
pinned to the reference date 2026-05-05 and the deterministic seed. They
will shift if you regenerate.

> The app deliberately shows a multi-bank setup (BNP Paribas, Deutsche
> Bank, NatWest, Citibank, HSBC). Real corporate treasuries are
> multi-banked and a credible demo has to reflect that.
