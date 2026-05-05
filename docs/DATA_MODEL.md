# Data model

All files live in `data/` and are produced by `data/generate_data.py`. The
generator is deterministic (`SEED = 42`).

Reference date used by the demo: **2026-05-05** (configurable via `TODAY`
in the generator).

---

## `cash_transactions.csv`

Posted (i.e. settled) cash movements across all bank accounts. The forecast
**does not** read this file for forward-looking lines — it uses open AR/AP
plus recurring averages — but it is the source of truth for everything
historical (cash position, KPIs, statistical projection, variance actuals).

| Column          | Type   | Notes                                                           |
|-----------------|--------|-----------------------------------------------------------------|
| `txn_id`        | str    | Primary key, e.g. `TX-100123`                                   |
| `date`          | date   | Settlement date                                                 |
| `account_iban`  | str    | FK → `bank_accounts.iban`                                       |
| `currency`      | str    | EUR / USD / GBP                                                 |
| `amount`        | float  | Native currency, sign convention: + inflow / − outflow          |
| `category`      | str    | One of the categories listed in §Categories below               |
| `counterparty`  | str    | Customer / supplier / authority name                            |
| `description`   | str    | Free text                                                       |
| `status`        | str    | Always `Posted` in this dataset                                 |
| `amount_eur`    | float  | Added at load time (`data_loader._attach_eur`)                  |

### Categories

Inflows: `Customer Receipts`, `Tax Refund`, `Interest Income`, `Asset Disposal`,
`Intercompany Funding`.

Outflows: `Supplier Payments`, `Payroll`, `Social Charges`, `VAT`,
`Corporate Tax`, `Rent`, `Debt Service`, `Capex`, `FX Hedging`, `Bank Fees`.

---

## `ar_invoices.csv`

Customer invoices, both open and historically paid.

| Column                  | Type | Notes                                                           |
|-------------------------|------|-----------------------------------------------------------------|
| `invoice_id`            | str  | Primary key, e.g. `AR-10123`                                    |
| `customer`              | str  |                                                                 |
| `country`               | str  | ISO 3166-1 alpha-2                                              |
| `segment`               | str  | Customer industry (Energy, Aerospace, Public Sector, …)         |
| `currency`              | str  | EUR / USD / GBP                                                 |
| `amount`                | float| Native currency, always positive                                |
| `issue_date`            | date | Invoice creation                                                |
| `due_date`              | date | `issue_date + payment_terms_days`                               |
| `expected_payment_date` | date | `due_date + behaviour_offset` (the **forecast** payment date)   |
| `payment_date`          | date | NULL while `status=Open`; equals `expected_payment_date` when paid |
| `status`                | str  | `Open` or `Paid`                                                |
| `payment_terms_days`    | int  | 30 / 45 / 60 / 75                                               |
| `behaviour`             | str  | `early` / `ontime` / `late` / `very_late`                       |
| `amount_eur`            | float| Added at load time                                              |

`paying_behaviour` parameters used by the generator and by the forecast:

| Behaviour    | Mean offset (d) | Std (d) |
|--------------|-----------------|---------|
| `early`      | −3              | 2       |
| `ontime`     | +1              | 3       |
| `late`       | +8              | 6       |
| `very_late`  | +20             | 10      |

---

## `ap_invoices.csv`

Same shape as `ar_invoices.csv`, with `customer→supplier`, `segment→category`
and no `behaviour` column (we model own-payment delay as a centred normal
around due date).

---

## `bank_accounts.csv`

| Column             | Type   | Notes                                       |
|--------------------|--------|---------------------------------------------|
| `iban`             | str    | Primary key                                 |
| `nickname`         | str    | Human-readable name                         |
| `bank`             | str    | Bank counterparty                           |
| `currency`         | str    | EUR / USD / GBP                             |
| `account_type`     | str    | Operating / Payroll / Tax / Term Deposit / RCF |
| `opening_balance`  | float  | Native currency, balance at history start   |

The dataset includes 8 accounts: 4 EUR operating/specialised, 1 GBP, 1 USD,
1 EUR term deposit, 1 EUR revolving credit facility.

---

## `fx_rates.csv`

Daily FX rates expressed as **units of foreign currency per 1 EUR** (ECB
convention). Rate column for `EUR` is constant 1.0.

| Column | Type  | Notes                          |
|--------|-------|--------------------------------|
| `date` | date  |                                |
| `EUR`  | float | always 1.0                     |
| `USD`  | float | mean ≈ 1.08, σ ≈ 0.0025/day    |
| `GBP`  | float | mean ≈ 0.85, σ ≈ 0.0015/day    |

Conversion rule used by `_attach_eur`:

```
amount_eur = amount / fx_rate_on(date, currency)
```

If the transaction date falls on a weekend / missing FX day, the rate is
forward-filled (then back-filled for the very first date).

---

## `assumptions.json`

```jsonc
{
  "company": "Helios Industries SA",
  "base_currency": "EUR",
  "today": "2026-05-05",
  "history_start": "2024-05-01",
  "horizon_days": 120,
  "drivers": {
    "revenue_growth_yoy": 0.045,
    "gross_margin": 0.32,
    "dso_target_days": 52,
    "dpo_target_days": 41,
    "min_cash_buffer_eur": 3000000,
    "rcf_limit_eur": 15000000,
    "rcf_drawn_eur": 1500000
  },
  "scenarios": {
    "base":       { "sales_multiplier": 1.00, "collection_delay_days":  0,  "capex_multiplier": 1.00 },
    "optimistic": { "sales_multiplier": 1.08, "collection_delay_days": -3,  "capex_multiplier": 1.10 },
    "stress":     { "sales_multiplier": 0.85, "collection_delay_days": 12,  "capex_multiplier": 0.60 }
  }
}
```

`drivers` are surfaced on the dashboard and used as targets for DSO/DPO and
liquidity-buffer guard-rails. `scenarios` are consumed by `pages/2_Scenarios.py`.
