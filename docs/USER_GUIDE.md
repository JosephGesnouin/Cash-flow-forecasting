# User guide — a treasurer's walk-through

> 🏦 *A BNP Paribas Cash Management treasurer-education asset.*

This document mirrors the workflow of a real corporate treasurer using the
app on a typical Monday morning.

---

## 09:00 — open the dashboard

1. Run `streamlit run app.py`.
2. The **Home** page shows three things at a glance:
   - the current **cash on hand** (excluding RCF),
   - the **liquidity runway** in months,
   - the **RCF availability** with how much is currently drawn.

   Sanity-check: cash on hand should be roughly stable or trending in line
   with recent variance. A runway below 3 months on operating outflow alone
   warrants escalation to the CFO.

3. Below the headline KPIs, the **last-90-day cash position** chart should
   stay above the red "minimum buffer" line. If it dipped, click through
   to **Bank Accounts** and identify which entity drove the drop.

---

## 09:15 — review the 13-week forecast

Go to **Forecast**.

1. Default view is **Weekly**, **13 weeks**, with the statistical overlay on.
   - Direct vs statistical lines should not diverge by more than ±10% at the
     horizon. If they do, scroll to the **Forecast line items** table and
     look for missing recurring posts.
2. Look at the **closing balance KPI** — does it stay above the buffer?
   - If not: switch to the **Scenarios** page to see how much headroom the
     stress scenario erases.
3. Scan the **inflow/outflow waterfall**:
   - Outsized outflow weeks usually correspond to VAT (week of the 20th),
     payroll (last business week), or a quarterly tax instalment.
   - Outsized inflow weeks typically follow a public-sector customer payment
     window (Helios Public Transit pays around 75 days after issue).
4. Use the **sliders** to test: "what if our biggest customer pays 10 days
   late?" → set Collection delay to +10 and watch the closing balance.

---

## 09:30 — scenarios & stress test

Open **Scenarios**.

1. The **headline metrics table** ranks Base / Optimistic / Stress on
   closing balance, minimum balance and buffer breach.
2. The **sensitivity heat-map** answers the executive question: "at what
   combination of sales drop and collection delay do we breach our buffer?"
   - Cells turn red when projected closing balance < buffer.
   - Use this to calibrate the size of an RCF drawdown request.
3. If the stress closing balance is below buffer:
   - Plan a precautionary RCF drawdown (timing matters — drawing too early
     burns interest, too late burns relationships with the bank).
   - Consider tightening capex authorisation thresholds for the quarter.

---

## 09:45 — working capital

Go to **Receivables & Payables**, tab **Receivables (AR)**.

1. **Aging buckets** — anything over 60 days overdue requires escalation to
   the credit-control team.
2. **Top customers — open balance** — concentration risk: if one customer
   represents > 25% of open AR, it warrants a credit-insurance review.
3. **Customer concentration treemap** — by country. Sudden growth in a
   single country can flag macro risk.
4. **Open AR detail** (expander) — sortable table; export to share with
   credit control.

Switch to **Payables (AP)**:

1. **Due in 7 days** — the working list for this week's payment run.
2. **DPO vs target** — DPO above target means we're paying too slowly
   (working-capital benefit but supplier-relationship risk). Below target
   means we're paying too fast (cash burn for no benefit).
3. **Top suppliers** — concentration is less critical on the AP side, but
   strategic suppliers (single-source raw materials) should be paid on
   time regardless of the DPO target.

---

## 10:00 — bank accounts & FX

Open **Bank Accounts**.

1. The **account positions table** is the cash inventory. Cross-check
   against bank statements (in production this would reconcile against
   MT940/CAMT.053 imports).
2. **Cash by currency** — anything > 5% of total non-EUR is an exposure.
   Decide whether to hedge or keep as natural-hedge against future
   foreign-currency outflows.
3. **FX exposure trendline** — useful before triggering the next batch of
   forward contracts.
4. **Daily cash position by account (last 60 days)** — useful to detect
   which entity drove a group-level cash anomaly.

---

## 10:15 — close the loop with variance

Go to **Variance**.

1. Set **forecast vintage** to 4 weeks ago.
2. Compare actual vs forecast for those 4 weeks.
3. **MAPE under 10%** is excellent, **10–15%** is acceptable, **above 15%**
   means recalibration.
4. If MAPE is high, the typical causes are (in order of frequency):
   - paying-behaviour drift on a major customer (update `behaviour` in the
     master data),
   - a one-off (M&A, dividend, disposal) that wasn't entered as a manual
     line item,
   - a structural change in seasonality (e.g. the company entered a new
     market with different payment culture).

---

## Configuration tips

- `data/assumptions.json` is the single source for all guard-rail thresholds
  (minimum cash buffer, DSO/DPO targets, RCF size). Edit it and reload — no
  code change needed.
- `data/generate_data.py` is deterministic; bump `SEED` to get a different
  fictional company personality (lateness patterns, FX volatility, capex
  cadence).
- All currency conversions happen at load time. To add a new currency, add
  it to the FX generator and to `_attach_eur` in `src/data_loader.py`.
