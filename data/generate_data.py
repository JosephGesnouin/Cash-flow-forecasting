"""
Synthetic data generator for Helios Industries SA — a fictional mid-cap
industrial company used to demo the cash-flow forecasting application.

Generates ~24 months of treasury data ending today:
  - cash_transactions.csv : posted transactions across bank accounts
  - ar_invoices.csv       : customer invoices (open + paid)
  - ap_invoices.csv       : supplier invoices (open + paid)
  - bank_accounts.csv     : account master
  - fx_rates.csv          : daily ECB-like rates vs EUR
  - assumptions.json      : forecasting assumptions / drivers

Run:  python data/generate_data.py
"""
from __future__ import annotations

import json
import math
import random
from datetime import date, timedelta
from pathlib import Path

import numpy as np
import pandas as pd

DATA_DIR = Path(__file__).resolve().parent
SEED = 42
TODAY = date(2026, 5, 5)
HISTORY_MONTHS = 24
HORIZON_DAYS = 120  # forward window of open invoices

random.seed(SEED)
np.random.seed(SEED)


# ---------------------------------------------------------------------------
# Reference data
# ---------------------------------------------------------------------------
BANK_ACCOUNTS = [
    # iban, nickname, bank, currency, account_type, opening_balance
    ("FR7630006000011234567890189", "Operating EUR",   "BNP Paribas",     "EUR", "Operating",     8_500_000),
    ("FR7630006000011234567890245", "Payroll EUR",     "BNP Paribas",     "EUR", "Payroll",       1_200_000),
    ("FR7630006000011234567890366", "Tax & VAT EUR",   "BNP Paribas",     "EUR", "Tax",             750_000),
    ("DE89370400440532013000",      "Operating EUR DE","Deutsche Bank",   "EUR", "Operating",     2_400_000),
    ("GB29NWBK60161331926819",      "Operating GBP",   "NatWest",         "GBP", "Operating",       820_000),
    ("US64SVBKUS6S3300958879",      "Operating USD",   "Citibank NA",     "USD", "Operating",     1_650_000),
    ("FR7630006000011234567899001", "Term Deposit EUR","BNP Paribas",     "EUR", "Term Deposit",  5_000_000),
    ("FR7630006000011234567899115", "Revolving Facility","HSBC France",   "EUR", "RCF",          -1_500_000),
]

CUSTOMERS = [
    # name, country, currency, segment, payment_terms_days, monthly_volume_eur, paying_behaviour
    ("Atlas Energy Group",     "FR", "EUR", "Energy",        45,   880_000, "ontime"),
    ("Borealis Mobility",      "DE", "EUR", "Automotive",    60,   660_000, "late"),
    ("Caledonia Rail",         "GB", "GBP", "Rail",          30,   400_000, "ontime"),
    ("Delphi Aerospace",       "US", "USD", "Aerospace",     45,   940_000, "early"),
    ("Eos Pharma",             "CH", "EUR", "Pharma",        30,   270_000, "ontime"),
    ("Forge Manufacturing",    "IT", "EUR", "Industrial",    60,   540_000, "late"),
    ("Gaia Renewables",        "ES", "EUR", "Energy",        45,   320_000, "ontime"),
    ("Helios Public Transit",  "FR", "EUR", "Public Sector", 75,   770_000, "very_late"),
    ("Indus Logistics",        "NL", "EUR", "Logistics",     30,   240_000, "ontime"),
    ("Janus Defence",          "FR", "EUR", "Defence",       60,   700_000, "ontime"),
    ("Kepler Robotics",        "DE", "EUR", "Industrial",    45,   300_000, "late"),
    ("Luma Construction",      "BE", "EUR", "Construction",  60,   175_000, "very_late"),
]

SUPPLIERS = [
    # name, country, currency, category, payment_terms_days, monthly_spend_eur
    ("Steelworks Holding",      "DE", "EUR", "Raw Materials",     45,   720_000),
    ("Polymer Industries",      "BE", "EUR", "Raw Materials",     45,   380_000),
    ("Voltage Components Ltd",  "GB", "GBP", "Components",        30,   240_000),
    ("MicroChip US Inc.",       "US", "USD", "Components",        30,   480_000),
    ("Logistica Express",       "IT", "EUR", "Logistics",         30,   165_000),
    ("EnerGrid",                "FR", "EUR", "Utilities",         30,   115_000),
    ("CloudOps SAS",            "FR", "EUR", "IT Services",       30,    72_000),
    ("Atelier Maintenance",     "FR", "EUR", "Maintenance",       45,    95_000),
    ("Global Insurance Co",     "FR", "EUR", "Insurance",         60,    38_000),
    ("Audit & Co",              "FR", "EUR", "Professional Svcs", 45,    48_000),
]

CATEGORIES_INFLOW = [
    "Customer Receipts",
    "Tax Refund",
    "Interest Income",
    "Asset Disposal",
    "Intercompany Funding",
]
CATEGORIES_OUTFLOW = [
    "Supplier Payments",
    "Payroll",
    "Social Charges",
    "VAT",
    "Corporate Tax",
    "Rent",
    "Debt Service",
    "Capex",
    "FX Hedging",
    "Bank Fees",
]


# ---------------------------------------------------------------------------
# FX rates (random walk around plausible levels)
# ---------------------------------------------------------------------------
def generate_fx_rates(start: date, end: date) -> pd.DataFrame:
    days = pd.date_range(start, end, freq="D")
    n = len(days)
    eur_usd = 1.08 + np.cumsum(np.random.normal(0, 0.0025, n))
    eur_gbp = 0.85 + np.cumsum(np.random.normal(0, 0.0015, n))
    eur_usd = np.clip(eur_usd, 1.00, 1.20)
    eur_gbp = np.clip(eur_gbp, 0.78, 0.92)
    return pd.DataFrame({
        "date": days.date,
        "EUR": 1.0,
        "USD": eur_usd,
        "GBP": eur_gbp,
    })


def to_eur(amount: float, ccy: str, fx: pd.DataFrame, on: date) -> float:
    if ccy == "EUR":
        return amount
    row = fx.loc[fx["date"] == on]
    if row.empty:
        row = fx.iloc[[-1]]
    rate = float(row[ccy].iloc[0])
    # rate is units of CCY per 1 EUR -> EUR amount = ccy_amount / rate
    return amount / rate


# ---------------------------------------------------------------------------
# Invoice generation
# ---------------------------------------------------------------------------
def _seasonality(d: date) -> float:
    """Annual sine + summer dip + Q4 peak."""
    doy = d.timetuple().tm_yday
    base = 1.0 + 0.08 * math.sin(2 * math.pi * (doy - 80) / 365)
    if d.month == 8:
        base *= 0.78
    if d.month in (11, 12):
        base *= 1.12
    return base


def _payment_delay(behaviour: str) -> int:
    if behaviour == "early":
        return int(np.clip(np.random.normal(-3, 2), -10, 0))
    if behaviour == "ontime":
        return int(np.clip(np.random.normal(1, 3), -3, 10))
    if behaviour == "late":
        return int(np.clip(np.random.normal(8, 6), 0, 30))
    if behaviour == "very_late":
        return int(np.clip(np.random.normal(20, 10), 5, 60))
    return 0


def generate_ar_invoices(start: date, end: date) -> pd.DataFrame:
    rows = []
    inv_id = 10_000
    for cust_name, country, ccy, segment, terms, mvol_eur, behaviour in CUSTOMERS:
        cur = start
        while cur <= end:
            month_start = cur.replace(day=1)
            # 4–10 invoices/month per customer
            n_inv = np.random.randint(4, 11)
            seas = _seasonality(month_start)
            trend = 1.0 + 0.0035 * ((month_start.year - start.year) * 12 + (month_start.month - start.month))
            target_eur = mvol_eur * seas * trend
            weights = np.random.dirichlet(np.ones(n_inv) * 2)
            for w in weights:
                day_offset = np.random.randint(0, 28)
                issue = month_start + timedelta(days=int(day_offset))
                if issue > end:
                    break
                amt_eur = float(target_eur * w)
                # convert to invoice currency
                if ccy == "EUR":
                    amt_ccy = amt_eur
                elif ccy == "USD":
                    amt_ccy = amt_eur * 1.08
                else:
                    amt_ccy = amt_eur * 0.85
                amt_ccy = round(amt_ccy, 2)
                due = issue + timedelta(days=terms)
                delay = _payment_delay(behaviour)
                expected_pay = due + timedelta(days=delay)
                # paid only if expected payment date already past today
                if expected_pay <= TODAY:
                    paid_date = expected_pay
                    status = "Paid"
                else:
                    paid_date = None
                    status = "Open"
                rows.append({
                    "invoice_id": f"AR-{inv_id}",
                    "customer": cust_name,
                    "country": country,
                    "segment": segment,
                    "currency": ccy,
                    "amount": amt_ccy,
                    "issue_date": issue,
                    "due_date": due,
                    "expected_payment_date": expected_pay,
                    "payment_date": paid_date,
                    "status": status,
                    "payment_terms_days": terms,
                    "behaviour": behaviour,
                })
                inv_id += 1
            # advance to next month
            if cur.month == 12:
                cur = date(cur.year + 1, 1, 1)
            else:
                cur = date(cur.year, cur.month + 1, 1)
    return pd.DataFrame(rows)


def generate_ap_invoices(start: date, end: date) -> pd.DataFrame:
    rows = []
    inv_id = 50_000
    for sup_name, country, ccy, category, terms, mspend_eur in SUPPLIERS:
        cur = start
        while cur <= end:
            month_start = cur.replace(day=1)
            n_inv = np.random.randint(3, 9)
            seas = _seasonality(month_start)
            trend = 1.0 + 0.0030 * ((month_start.year - start.year) * 12 + (month_start.month - start.month))
            target_eur = mspend_eur * seas * trend
            weights = np.random.dirichlet(np.ones(n_inv) * 2)
            for w in weights:
                day_offset = np.random.randint(0, 28)
                issue = month_start + timedelta(days=int(day_offset))
                if issue > end:
                    break
                amt_eur = float(target_eur * w)
                if ccy == "EUR":
                    amt_ccy = amt_eur
                elif ccy == "USD":
                    amt_ccy = amt_eur * 1.08
                else:
                    amt_ccy = amt_eur * 0.85
                amt_ccy = round(amt_ccy, 2)
                due = issue + timedelta(days=terms)
                # we pay close to due, occasionally a bit late
                delay = int(np.clip(np.random.normal(2, 3), -5, 12))
                expected_pay = due + timedelta(days=delay)
                if expected_pay <= TODAY:
                    paid_date = expected_pay
                    status = "Paid"
                else:
                    paid_date = None
                    status = "Open"
                rows.append({
                    "invoice_id": f"AP-{inv_id}",
                    "supplier": sup_name,
                    "country": country,
                    "category": category,
                    "currency": ccy,
                    "amount": amt_ccy,
                    "issue_date": issue,
                    "due_date": due,
                    "expected_payment_date": expected_pay,
                    "payment_date": paid_date,
                    "status": status,
                    "payment_terms_days": terms,
                })
                inv_id += 1
            if cur.month == 12:
                cur = date(cur.year + 1, 1, 1)
            else:
                cur = date(cur.year, cur.month + 1, 1)
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# Posted cash transactions (derived from invoices + recurring items)
# ---------------------------------------------------------------------------
def generate_recurring(start: date, end: date) -> list[dict]:
    """Recurring cash items: payroll, social charges, VAT, taxes, rent, debt, capex."""
    rows = []
    cur = start.replace(day=1)
    txn_id = 700_000
    while cur <= end:
        month_label = cur.strftime("%Y-%m")
        seas = _seasonality(cur)
        # Payroll — last business day of month
        payroll_day = (cur.replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(days=1)
        if payroll_day <= end:
            base_payroll = 1_850_000 * (1 + 0.004 * ((cur.year - start.year) * 12 + cur.month - start.month))
            rows.append({
                "txn_id": f"TX-{txn_id}", "date": payroll_day, "account_iban": BANK_ACCOUNTS[1][0],
                "currency": "EUR", "amount": -round(base_payroll, 2),
                "category": "Payroll", "counterparty": "Employees",
                "description": f"Monthly payroll {month_label}", "status": "Posted",
            })
            txn_id += 1
            # social charges 5 days later
            sc_day = payroll_day + timedelta(days=5)
            if sc_day <= end:
                rows.append({
                    "txn_id": f"TX-{txn_id}", "date": sc_day, "account_iban": BANK_ACCOUNTS[2][0],
                    "currency": "EUR", "amount": -round(base_payroll * 0.42, 2),
                    "category": "Social Charges", "counterparty": "URSSAF",
                    "description": f"Social charges {month_label}", "status": "Posted",
                })
                txn_id += 1
        # VAT — 20th of next month
        vat_day = (cur + timedelta(days=32)).replace(day=20)
        if vat_day <= end:
            vat_amount = 380_000 * seas * (1 + np.random.normal(0, 0.05))
            rows.append({
                "txn_id": f"TX-{txn_id}", "date": vat_day, "account_iban": BANK_ACCOUNTS[2][0],
                "currency": "EUR", "amount": -round(vat_amount, 2),
                "category": "VAT", "counterparty": "DGFiP",
                "description": f"VAT {month_label}", "status": "Posted",
            })
            txn_id += 1
        # Rent — 1st of month
        if cur <= end:
            rows.append({
                "txn_id": f"TX-{txn_id}", "date": cur, "account_iban": BANK_ACCOUNTS[0][0],
                "currency": "EUR", "amount": -185_000.0,
                "category": "Rent", "counterparty": "SCI Helios Properties",
                "description": f"Office & plant rent {month_label}", "status": "Posted",
            })
            txn_id += 1
        # Debt service — 15th of each month
        debt_day = cur.replace(day=15)
        if debt_day <= end:
            rows.append({
                "txn_id": f"TX-{txn_id}", "date": debt_day, "account_iban": BANK_ACCOUNTS[0][0],
                "currency": "EUR", "amount": -125_000.0,
                "category": "Debt Service", "counterparty": "Bond Trustee",
                "description": "Senior notes coupon + amortization", "status": "Posted",
            })
            txn_id += 1
        # Bank fees — end of month
        eom = (cur.replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(days=1)
        if eom <= end:
            rows.append({
                "txn_id": f"TX-{txn_id}", "date": eom, "account_iban": BANK_ACCOUNTS[0][0],
                "currency": "EUR", "amount": -round(np.random.uniform(3500, 6500), 2),
                "category": "Bank Fees", "counterparty": "BNP Paribas",
                "description": f"Banking fees {month_label}", "status": "Posted",
            })
            txn_id += 1
        # Quarterly corporate tax
        if cur.month in (3, 6, 9, 12) and cur.day == 1:
            tax_day = cur.replace(day=15)
            if tax_day <= end:
                rows.append({
                    "txn_id": f"TX-{txn_id}", "date": tax_day, "account_iban": BANK_ACCOUNTS[2][0],
                    "currency": "EUR", "amount": -round(np.random.uniform(420_000, 680_000), 2),
                    "category": "Corporate Tax", "counterparty": "DGFiP",
                    "description": f"IS quarterly instalment {month_label}", "status": "Posted",
                })
                txn_id += 1
        # Capex — irregular, ~3-4 hits/year
        if np.random.rand() < 0.30:
            day = cur + timedelta(days=int(np.random.randint(2, 26)))
            if day <= end:
                rows.append({
                    "txn_id": f"TX-{txn_id}", "date": day, "account_iban": BANK_ACCOUNTS[0][0],
                    "currency": "EUR", "amount": -round(np.random.uniform(80_000, 600_000), 2),
                    "category": "Capex", "counterparty": "Various Equipment Vendors",
                    "description": "Plant capex", "status": "Posted",
                })
                txn_id += 1
        if cur.month == 12:
            cur = date(cur.year + 1, 1, 1)
        else:
            cur = date(cur.year, cur.month + 1, 1)
    return rows


def _account_for_currency(ccy: str) -> str:
    for iban, _, _, c, t, _ in BANK_ACCOUNTS:
        if c == ccy and t == "Operating":
            return iban
    return BANK_ACCOUNTS[0][0]


def transactions_from_invoices(ar: pd.DataFrame, ap: pd.DataFrame) -> list[dict]:
    rows = []
    txn_id = 100_000
    for _, inv in ar[ar["status"] == "Paid"].iterrows():
        rows.append({
            "txn_id": f"TX-{txn_id}", "date": inv["payment_date"],
            "account_iban": _account_for_currency(inv["currency"]),
            "currency": inv["currency"], "amount": float(inv["amount"]),
            "category": "Customer Receipts", "counterparty": inv["customer"],
            "description": f"Receipt {inv['invoice_id']}", "status": "Posted",
        })
        txn_id += 1
    for _, inv in ap[ap["status"] == "Paid"].iterrows():
        rows.append({
            "txn_id": f"TX-{txn_id}", "date": inv["payment_date"],
            "account_iban": _account_for_currency(inv["currency"]),
            "currency": inv["currency"], "amount": -float(inv["amount"]),
            "category": "Supplier Payments", "counterparty": inv["supplier"],
            "description": f"Payment {inv['invoice_id']}", "status": "Posted",
        })
        txn_id += 1
    return rows


def generate_misc_transactions(start: date, end: date) -> list[dict]:
    """Tax refunds, interest income, intercompany, FX hedging, asset disposals."""
    rows = []
    txn_id = 900_000
    cur = start
    while cur <= end:
        # interest income on term deposit, end of quarter
        if cur.month in (3, 6, 9, 12):
            day = cur.replace(day=28)
            if day <= end:
                rows.append({
                    "txn_id": f"TX-{txn_id}", "date": day, "account_iban": BANK_ACCOUNTS[6][0],
                    "currency": "EUR", "amount": round(2_000_000 * 0.0325 / 4, 2),
                    "category": "Interest Income", "counterparty": "BNP Paribas",
                    "description": "Term deposit interest", "status": "Posted",
                })
                txn_id += 1
        # FX hedging premium, monthly
        fx_day = cur.replace(day=10)
        if fx_day <= end:
            rows.append({
                "txn_id": f"TX-{txn_id}", "date": fx_day, "account_iban": BANK_ACCOUNTS[0][0],
                "currency": "EUR", "amount": -round(np.random.uniform(8_000, 18_000), 2),
                "category": "FX Hedging", "counterparty": "HSBC FX Desk",
                "description": "FX forward premium", "status": "Posted",
            })
            txn_id += 1
        if cur.month == 12:
            cur = date(cur.year + 1, 1, 1)
        else:
            cur = date(cur.year, cur.month + 1, 1)
    # one tax refund
    rows.append({
        "txn_id": f"TX-{txn_id}", "date": date(2025, 4, 28),
        "account_iban": BANK_ACCOUNTS[2][0], "currency": "EUR", "amount": 215_400.00,
        "category": "Tax Refund", "counterparty": "DGFiP",
        "description": "CIR tax credit refund FY2024", "status": "Posted",
    })
    txn_id += 1
    # one asset disposal
    rows.append({
        "txn_id": f"TX-{txn_id}", "date": date(2025, 9, 17),
        "account_iban": BANK_ACCOUNTS[0][0], "currency": "EUR", "amount": 480_000.00,
        "category": "Asset Disposal", "counterparty": "Industrial Buyers Ltd",
        "description": "Sale of legacy press line", "status": "Posted",
    })
    return rows


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main() -> None:
    start = date(TODAY.year - 2, TODAY.month, 1)
    end_history = TODAY
    end_invoices = TODAY + timedelta(days=HORIZON_DAYS)

    print(f"Generating data from {start} to {end_invoices} (today = {TODAY})")

    fx = generate_fx_rates(start, end_invoices)
    ar = generate_ar_invoices(start, end_invoices)
    ap = generate_ap_invoices(start, end_invoices)

    txns = []
    txns += transactions_from_invoices(ar, ap)
    txns += generate_recurring(start, end_history)
    txns += generate_misc_transactions(start, end_history)
    df_tx = pd.DataFrame(txns)
    df_tx = df_tx.sort_values("date").reset_index(drop=True)

    bank_df = pd.DataFrame(BANK_ACCOUNTS, columns=[
        "iban", "nickname", "bank", "currency", "account_type", "opening_balance"
    ])

    # output
    DATA_DIR.mkdir(exist_ok=True, parents=True)
    df_tx.to_csv(DATA_DIR / "cash_transactions.csv", index=False)
    ar.to_csv(DATA_DIR / "ar_invoices.csv", index=False)
    ap.to_csv(DATA_DIR / "ap_invoices.csv", index=False)
    bank_df.to_csv(DATA_DIR / "bank_accounts.csv", index=False)
    fx.to_csv(DATA_DIR / "fx_rates.csv", index=False)

    assumptions = {
        "company": "Helios Industries SA",
        "base_currency": "EUR",
        "today": TODAY.isoformat(),
        "history_start": start.isoformat(),
        "horizon_days": HORIZON_DAYS,
        "drivers": {
            "revenue_growth_yoy": 0.045,
            "gross_margin": 0.32,
            "dso_target_days": 52,
            "dpo_target_days": 41,
            "min_cash_buffer_eur": 3_000_000,
            "rcf_limit_eur": 15_000_000,
            "rcf_drawn_eur": 1_500_000,
        },
        "scenarios": {
            "base": {"sales_multiplier": 1.00, "collection_delay_days": 0,  "capex_multiplier": 1.00},
            "optimistic": {"sales_multiplier": 1.08, "collection_delay_days": -3, "capex_multiplier": 1.10},
            "stress": {"sales_multiplier": 0.85, "collection_delay_days": 12, "capex_multiplier": 0.60},
        },
    }
    with open(DATA_DIR / "assumptions.json", "w") as f:
        json.dump(assumptions, f, indent=2)

    print(f"  cash_transactions: {len(df_tx):>6,} rows")
    print(f"  ar_invoices      : {len(ar):>6,} rows ({(ar['status']=='Open').sum()} open)")
    print(f"  ap_invoices      : {len(ap):>6,} rows ({(ap['status']=='Open').sum()} open)")
    print(f"  bank_accounts    : {len(bank_df):>6,} rows")
    print(f"  fx_rates         : {len(fx):>6,} rows")
    print("Done.")


if __name__ == "__main__":
    main()
