# Methodology

> How the cash-flow forecast is built, written down so anyone (treasurer, FP&A,
> auditor) can reproduce it from the source data.

## 1. Why a direct, 13-week cash forecast

Two cash-forecasting families exist:

- **Indirect** — start from P&L net income, add/remove non-cash items
  (depreciation, working-capital change). Useful for the **annual budget** and
  for understanding the *quality* of earnings, useless for short-term
  liquidity because the granularity is monthly at best.
- **Direct** — list every expected receipt and payment on its expected date,
  then sum. The right tool for **short-term (≤90-day) cash management**. A
  rolling 13-week horizon is the de-facto industry standard: long enough to
  see a quarterly tax payment coming, short enough to be informed by actual
  invoice positions.

This application is **direct + rolling 13-week**, with a **statistical
overlay** for sanity-checking.

## 2. Components of the direct forecast

For a horizon `[t+1, t+H]` the forecast net flow on day `d` is:

```
flow(d) = AR_receipts(d) + AP_payments(d) + Recurring(d) + Discretionary(d)
```

Each component:

### 2.1 AR receipts — `forecast_ar_receipts`

For every **open** customer invoice we already have on the books:

```
expected_payment_date = due_date + realised_payment_delay(customer)
```

`realised_payment_delay` is observed from history — `paying_behaviour` is one
of `early`, `ontime`, `late`, `very_late` and produces a sampled offset (in
days) around the customer's typical pattern. The amount lands on
`expected_payment_date`, in EUR (converted at issue-date FX).

The scenario knob `collection_delay_days` shifts every expected payment.

### 2.2 AP payments — `forecast_ap_payments`

Same mechanic, applied to supplier invoices. Outflows are negative.

### 2.3 Recurring fixed items — `forecast_recurring`

Six month average per category (over `[t-180, t-1]`), placed on the canonical
calendar date for that category:

| Category         | Posting date convention      |
|------------------|------------------------------|
| Payroll          | last business day of month   |
| Social charges   | payroll + 5 days             |
| Rent             | 1st of month                 |
| Debt service     | 15th of month                |
| VAT              | 20th of month                |
| Bank fees        | last business day of month   |
| Capex            | 20th of month (× scenario)   |
| FX hedging       | 10th of month                |
| Corporate tax    | 15th of {Mar, Jun, Sep, Dec} |
| Interest income  | 28th of {Mar, Jun, Sep, Dec} |

### 2.4 Discretionary

Captured inside the recurring engine via `Capex (× capex_multiplier)`. Other
discretionary items (M&A, dividends) are not modelled by default and would be
added as one-off line items in the forecast lines table.

## 3. Statistical (indirect) overlay — `statistical_forecast`

A simple decomposition of the historical daily net flow series:

1. trend — 30-day rolling mean of historical net daily flow
2. day-of-week seasonality — mean of detrended series by `dayofweek`
3. month-of-year seasonality — mean of detrended series by `month`

Projection on day `d`:

```
flow_stat(d) = trend_30d_mean + dow_seasonality(d.weekday) + moy_seasonality(d.month)
```

This is **not** a primary forecast — it's a sanity check. If the direct and
the statistical projections diverge by more than ±10% at the 13-week horizon,
something is off (typically a structural break the direct method captured
correctly, or a missing recurring item).

## 4. Cash position projection

The opening EUR-equivalent balance (today, all non-RCF accounts) is plus the
running cumulative sum of the forecast lines:

```
balance(d) = opening_eur + Σ_{k≤d} flow(k)
```

The minimum-cash buffer (default €3M, configurable in
`assumptions.json → drivers.min_cash_buffer_eur`) is rendered as a red
horizontal line on every projection chart. Breaches are flagged in the
scenarios table.

## 5. Scenarios

A scenario is a 3-tuple of knobs:

| Knob                       | Meaning                                                 |
|----------------------------|---------------------------------------------------------|
| `sales_multiplier`         | scales AR receipts (lost / gained sales)               |
| `collection_delay_days`    | adds a constant offset to every customer payment date  |
| `capex_multiplier`         | scales discretionary capex outflow                     |

The three default scenarios live in `assumptions.json → scenarios`:

- **Base** — knobs at neutral.
- **Optimistic** — +8% sales, customers pay 3 days earlier, capex +10%.
- **Stress** — −15% sales, +12 days collection delay, capex cut to 60%.

The stress shock is calibrated against historical mid-cycle industrial
downturns (2009, 2015, 2020 averaged).

## 6. KPIs

| KPI                | Formula                                                                                  |
|--------------------|------------------------------------------------------------------------------------------|
| Cash on hand       | Σ closing EUR-equivalent balances of operating, payroll, tax, term-deposit accounts      |
| RCF available      | facility limit − drawn                                                                  |
| Liquidity runway   | cash on hand / trailing-6m average monthly outflow                                       |
| Working-capital gap| open AR (€) − open AP (€)                                                                |
| DSO                | open AR (€) / credit sales over lookback (€) × lookback (days). Lookback = 90 days.      |
| DPO                | open AP (€) / purchases over lookback (€) × lookback (days). Lookback = 90 days.         |
| Aging buckets      | Open invoices grouped by `today − due_date` into Not due / 1-30 / 31-60 / 61-90 / 90+    |

## 7. Variance analysis

Given a forecast vintage `t₀ = today − N weeks`:

1. Reconstruct the dataset *as it was* at `t₀` by treating any invoice with
   `payment_date > t₀` (or `null`) as Open at that date.
2. Run the **base** forecast from `t₀+1` to `min(today, t₀ + horizon)`.
3. Aggregate forecast and actuals on the same period grid (D / W / M).
4. `variance = actual − forecast`,
   `MAPE = Σ|variance| / Σ|forecast|`.

A MAPE above ~15% is the threshold at which we recalibrate assumptions
(typically: customer paying-behaviour parameters, recurring-item averages,
DSO/DPO targets in the assumptions file).

## 8. Limitations

- Customer / supplier paying behaviour is a **sampled offset**, not a learned
  model. Fitting a per-customer Gamma distribution on `payment_date − due_date`
  would be a natural upgrade.
- FX is treated as a price-taker — there is no FX-hedging optimisation.
- Intercompany funding flows are stylised, not driven by per-entity cash
  pooling rules.
- Capex pipeline is not project-aware; in production we would source it from
  the capex committee tracker rather than averaging history.
