"""Load CSV/JSON datasets and convert amounts to base currency (EUR)."""
from __future__ import annotations

import json
from datetime import date
from functools import lru_cache
from pathlib import Path

import pandas as pd

DATA_DIR = Path(__file__).resolve().parents[1] / "data"

DATE_COLS = {
    "cash_transactions.csv": ["date"],
    "ar_invoices.csv": ["issue_date", "due_date", "expected_payment_date", "payment_date"],
    "ap_invoices.csv": ["issue_date", "due_date", "expected_payment_date", "payment_date"],
    "fx_rates.csv": ["date"],
}


def _read(name: str) -> pd.DataFrame:
    path = DATA_DIR / name
    df = pd.read_csv(path)
    for col in DATE_COLS.get(name, []):
        df[col] = pd.to_datetime(df[col], errors="coerce").dt.date
    return df


@lru_cache(maxsize=1)
def load_assumptions() -> dict:
    with open(DATA_DIR / "assumptions.json") as f:
        return json.load(f)


@lru_cache(maxsize=1)
def load_fx() -> pd.DataFrame:
    return _read("fx_rates.csv")


@lru_cache(maxsize=1)
def load_bank_accounts() -> pd.DataFrame:
    return _read("bank_accounts.csv")


@lru_cache(maxsize=1)
def load_transactions() -> pd.DataFrame:
    df = _read("cash_transactions.csv")
    df = _attach_eur(df, "amount", "currency", "date")
    return df


@lru_cache(maxsize=1)
def load_ar() -> pd.DataFrame:
    df = _read("ar_invoices.csv")
    df = _attach_eur(df, "amount", "currency", "issue_date")
    return df


@lru_cache(maxsize=1)
def load_ap() -> pd.DataFrame:
    df = _read("ap_invoices.csv")
    df = _attach_eur(df, "amount", "currency", "issue_date")
    return df


def _attach_eur(df: pd.DataFrame, amt_col: str, ccy_col: str, date_col: str) -> pd.DataFrame:
    fx = load_fx().copy()
    fx["date"] = pd.to_datetime(fx["date"]).dt.date
    out = df.merge(fx, left_on=date_col, right_on="date", how="left", suffixes=("", "_fx"))
    # forward-fill missing fx (weekends, etc.)
    for c in ["EUR", "USD", "GBP"]:
        out[c] = out[c].ffill().bfill()
    rate = out.apply(lambda r: r[r[ccy_col]] if r[ccy_col] in ("EUR", "USD", "GBP") else 1.0, axis=1)
    out["amount_eur"] = out[amt_col] / rate
    drop = [c for c in ("EUR", "USD", "GBP", "date_fx") if c in out.columns]
    return out.drop(columns=drop)


def today() -> date:
    return date.fromisoformat(load_assumptions()["today"])
