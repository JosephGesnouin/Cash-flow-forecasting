"""Treasury KPIs: cash position, DSO/DPO, AR/AP aging, liquidity ratio."""
from __future__ import annotations

from datetime import date, timedelta

import numpy as np
import pandas as pd


def opening_balance_total(banks: pd.DataFrame) -> float:
    return float(banks["opening_balance"].sum())


def cash_position_by_account(
    banks: pd.DataFrame, txns: pd.DataFrame, as_of: date
) -> pd.DataFrame:
    """Closing balance per account in account ccy AND in EUR."""
    tx = txns[txns["date"] <= as_of].copy()
    movements = tx.groupby("account_iban")["amount"].sum().rename("net_movement")
    movements_eur = tx.groupby("account_iban")["amount_eur"].sum().rename("net_movement_eur")
    out = banks.merge(movements, left_on="iban", right_index=True, how="left") \
               .merge(movements_eur, left_on="iban", right_index=True, how="left")
    out["net_movement"] = out["net_movement"].fillna(0)
    out["net_movement_eur"] = out["net_movement_eur"].fillna(0)
    out["closing_balance"] = out["opening_balance"] + out["net_movement"]
    # opening balance is in account ccy already; need eur equivalent for total
    # use latest fx rate handled upstream — simple approximation: assume opening posted in EUR equivalent
    out["closing_balance_eur"] = out["opening_balance"] + out["net_movement_eur"]
    return out


def total_cash_eur(banks: pd.DataFrame, txns: pd.DataFrame, as_of: date) -> float:
    pos = cash_position_by_account(banks, txns, as_of)
    # exclude RCF (it's a credit line) when reporting "cash on hand"
    return float(pos.loc[pos["account_type"] != "RCF", "closing_balance_eur"].sum())


def daily_balance_series(
    banks: pd.DataFrame, txns: pd.DataFrame, start: date, end: date
) -> pd.Series:
    """Aggregated EUR cash position by day across all non-RCF accounts."""
    days = pd.date_range(start, end, freq="D").date
    opening = float(banks.loc[banks["account_type"] != "RCF", "opening_balance"].sum())
    tx = txns[(txns["date"] >= start) & (txns["date"] <= end)].copy()
    # exclude RCF account movements from "cash" view
    rcf_ibans = banks.loc[banks["account_type"] == "RCF", "iban"].tolist()
    tx = tx[~tx["account_iban"].isin(rcf_ibans)]
    daily = tx.groupby("date")["amount_eur"].sum()
    s = pd.Series(0.0, index=days)
    s.update(daily)
    return opening + s.cumsum()


def dso(ar: pd.DataFrame, as_of: date, lookback_days: int = 90) -> float:
    """DSO = (AR open / credit sales over period) * period."""
    period_start = as_of - timedelta(days=lookback_days)
    sales = ar[(ar["issue_date"] >= period_start) & (ar["issue_date"] <= as_of)]["amount_eur"].sum()
    open_ar = ar[(ar["status"] == "Open") & (ar["issue_date"] <= as_of)]["amount_eur"].sum()
    if sales <= 0:
        return float("nan")
    return float(open_ar / sales * lookback_days)


def dpo(ap: pd.DataFrame, as_of: date, lookback_days: int = 90) -> float:
    period_start = as_of - timedelta(days=lookback_days)
    purchases = ap[(ap["issue_date"] >= period_start) & (ap["issue_date"] <= as_of)]["amount_eur"].sum()
    open_ap = ap[(ap["status"] == "Open") & (ap["issue_date"] <= as_of)]["amount_eur"].sum()
    if purchases <= 0:
        return float("nan")
    return float(open_ap / purchases * lookback_days)


def aging_buckets(invoices: pd.DataFrame, as_of: date) -> pd.DataFrame:
    """AR/AP aging in EUR. Buckets: not_due, 1-30, 31-60, 61-90, 90+."""
    open_inv = invoices[invoices["status"] == "Open"].copy()
    if open_inv.empty:
        return pd.DataFrame({"bucket": [], "amount_eur": []})
    open_inv["days_overdue"] = open_inv["due_date"].apply(lambda d: (as_of - d).days)

    def _bucket(d: int) -> str:
        if d < 0:
            return "Not due"
        if d <= 30:
            return "1-30"
        if d <= 60:
            return "31-60"
        if d <= 90:
            return "61-90"
        return "90+"

    open_inv["bucket"] = open_inv["days_overdue"].apply(_bucket)
    order = ["Not due", "1-30", "31-60", "61-90", "90+"]
    agg = open_inv.groupby("bucket")["amount_eur"].sum().reindex(order, fill_value=0).reset_index()
    return agg


def liquidity_ratio(cash_eur: float, monthly_outflow_eur: float) -> float:
    """Cash / average monthly operating outflow → months of runway."""
    if monthly_outflow_eur <= 0:
        return float("inf")
    return cash_eur / monthly_outflow_eur


def avg_monthly_outflow(txns: pd.DataFrame, as_of: date, months: int = 6) -> float:
    start = as_of - timedelta(days=30 * months)
    out = txns[(txns["date"] >= start) & (txns["date"] <= as_of) & (txns["amount_eur"] < 0)]
    if out.empty:
        return 0.0
    return float(-out["amount_eur"].sum() / months)


def category_summary(txns: pd.DataFrame, start: date, end: date) -> pd.DataFrame:
    sub = txns[(txns["date"] >= start) & (txns["date"] <= end)].copy()
    g = sub.groupby("category")["amount_eur"].agg(["sum", "count"]).reset_index()
    g = g.rename(columns={"sum": "amount_eur", "count": "n_transactions"})
    return g.sort_values("amount_eur")
