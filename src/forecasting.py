"""
Forecasting engine.

Two complementary methods are exposed:

1. **Direct method (bottom-up).** Combines:
   - Receipts from open AR invoices, shifted by realized customer payment delay
   - Payments on open AP invoices, shifted by realized supplier payment delay
   - Recurring fixed items (payroll, rent, debt service, taxes) projected from
     historical patterns
   - Discretionary items (capex, FX hedging) modelled as monthly averages

2. **Indirect / statistical method.** Decomposes the historical daily net cash
   flow into trend + seasonality (DOW, day-of-month, month-of-year) and
   projects forward. Useful as a sanity check against the direct forecast.

Scenario knobs (sales multiplier, collection delay, capex multiplier) modulate
the direct forecast.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
from typing import Iterable

import numpy as np
import pandas as pd


@dataclass
class ScenarioParams:
    name: str
    sales_multiplier: float = 1.0
    collection_delay_days: int = 0
    capex_multiplier: float = 1.0


# ---------------------------------------------------------------------------
# Direct method
# ---------------------------------------------------------------------------
def forecast_ar_receipts(
    ar: pd.DataFrame, start: date, end: date, scenario: ScenarioParams
) -> pd.DataFrame:
    """Project receipts from open invoices + new sales pipeline."""
    open_ar = ar[ar["status"] == "Open"].copy()
    open_ar["expected_payment_date"] = open_ar["expected_payment_date"].apply(
        lambda d: d + timedelta(days=int(scenario.collection_delay_days))
    )
    open_ar = open_ar[
        (open_ar["expected_payment_date"] >= start)
        & (open_ar["expected_payment_date"] <= end)
    ]
    if open_ar.empty:
        return pd.DataFrame(columns=["date", "amount_eur", "category"])
    rec = (
        open_ar.groupby("expected_payment_date")["amount_eur"].sum()
        .rename("amount_eur").reset_index()
        .rename(columns={"expected_payment_date": "date"})
    )
    rec["amount_eur"] *= scenario.sales_multiplier
    rec["category"] = "Customer Receipts (forecast)"
    return rec


def forecast_ap_payments(
    ap: pd.DataFrame, start: date, end: date, scenario: ScenarioParams
) -> pd.DataFrame:
    open_ap = ap[ap["status"] == "Open"].copy()
    open_ap = open_ap[
        (open_ap["expected_payment_date"] >= start)
        & (open_ap["expected_payment_date"] <= end)
    ]
    if open_ap.empty:
        return pd.DataFrame(columns=["date", "amount_eur", "category"])
    pay = (
        open_ap.groupby("expected_payment_date")["amount_eur"].sum()
        .rename("amount_eur").reset_index()
        .rename(columns={"expected_payment_date": "date"})
    )
    pay["amount_eur"] = -pay["amount_eur"]
    pay["category"] = "Supplier Payments (forecast)"
    return pay


def _last_business_day(year: int, month: int) -> date:
    if month == 12:
        nxt = date(year + 1, 1, 1)
    else:
        nxt = date(year, month + 1, 1)
    eom = nxt - timedelta(days=1)
    while eom.weekday() >= 5:
        eom -= timedelta(days=1)
    return eom


def forecast_recurring(
    txns: pd.DataFrame, start: date, end: date, scenario: ScenarioParams
) -> pd.DataFrame:
    """Project recurring items from historical averages by category."""
    rows: list[dict] = []
    # average monthly amounts per category over last 6 months
    lookback = 180
    hist_start = start - timedelta(days=lookback)
    hist = txns[(txns["date"] >= hist_start) & (txns["date"] < start)].copy()
    if hist.empty:
        return pd.DataFrame(columns=["date", "amount_eur", "category"])
    hist["month"] = pd.to_datetime(hist["date"]).dt.to_period("M")
    avg_by_cat = hist.groupby("category")["amount_eur"].sum() / 6.0

    cur = date(start.year, start.month, 1)
    while cur <= end:
        last = _last_business_day(cur.year, cur.month)
        # Payroll: last business day
        if "Payroll" in avg_by_cat.index and start <= last <= end:
            rows.append({"date": last, "amount_eur": avg_by_cat["Payroll"], "category": "Payroll (forecast)"})
        # Social charges: 5 days after payroll
        if "Social Charges" in avg_by_cat.index:
            d = last + timedelta(days=5)
            if start <= d <= end:
                rows.append({"date": d, "amount_eur": avg_by_cat["Social Charges"], "category": "Social Charges (forecast)"})
        # Rent: 1st
        if "Rent" in avg_by_cat.index and start <= cur <= end:
            rows.append({"date": cur, "amount_eur": avg_by_cat["Rent"], "category": "Rent (forecast)"})
        # Debt service: 15th
        if "Debt Service" in avg_by_cat.index:
            d = cur.replace(day=15)
            if start <= d <= end:
                rows.append({"date": d, "amount_eur": avg_by_cat["Debt Service"], "category": "Debt Service (forecast)"})
        # VAT: 20th of next month — billing for current month falls 20th of following month
        # Practically, post a VAT outflow on 20th of current month
        if "VAT" in avg_by_cat.index:
            d = cur.replace(day=20)
            if start <= d <= end:
                rows.append({"date": d, "amount_eur": avg_by_cat["VAT"], "category": "VAT (forecast)"})
        # Bank fees: end of month
        if "Bank Fees" in avg_by_cat.index and start <= last <= end:
            rows.append({"date": last, "amount_eur": avg_by_cat["Bank Fees"], "category": "Bank Fees (forecast)"})
        # Capex: monthly average, posted on 20th, scaled by scenario
        if "Capex" in avg_by_cat.index:
            d = cur.replace(day=20)
            if start <= d <= end:
                rows.append({
                    "date": d,
                    "amount_eur": avg_by_cat["Capex"] * scenario.capex_multiplier,
                    "category": "Capex (forecast)",
                })
        # FX hedging: 10th
        if "FX Hedging" in avg_by_cat.index:
            d = cur.replace(day=10)
            if start <= d <= end:
                rows.append({"date": d, "amount_eur": avg_by_cat["FX Hedging"], "category": "FX Hedging (forecast)"})
        # Quarterly corporate tax
        if cur.month in (3, 6, 9, 12) and "Corporate Tax" in avg_by_cat.index:
            d = cur.replace(day=15)
            if start <= d <= end:
                rows.append({"date": d, "amount_eur": avg_by_cat["Corporate Tax"] * 3, "category": "Corporate Tax (forecast)"})
        # Interest income: end of quarter
        if cur.month in (3, 6, 9, 12) and "Interest Income" in avg_by_cat.index:
            d = cur.replace(day=28)
            if start <= d <= end:
                rows.append({"date": d, "amount_eur": avg_by_cat["Interest Income"] * 3, "category": "Interest Income (forecast)"})
        if cur.month == 12:
            cur = date(cur.year + 1, 1, 1)
        else:
            cur = date(cur.year, cur.month + 1, 1)
    return pd.DataFrame(rows)


def build_direct_forecast(
    ar: pd.DataFrame,
    ap: pd.DataFrame,
    txns: pd.DataFrame,
    start: date,
    end: date,
    scenario: ScenarioParams,
) -> pd.DataFrame:
    parts = [
        forecast_ar_receipts(ar, start, end, scenario),
        forecast_ap_payments(ap, start, end, scenario),
        forecast_recurring(txns, start, end, scenario),
    ]
    out = pd.concat([p for p in parts if not p.empty], ignore_index=True)
    out["date"] = pd.to_datetime(out["date"]).dt.date
    return out.sort_values("date").reset_index(drop=True)


def aggregate_forecast(forecast_lines: pd.DataFrame, freq: str = "W") -> pd.DataFrame:
    """Aggregate per period (D/W/M)."""
    if forecast_lines.empty:
        return pd.DataFrame(columns=["period", "inflow", "outflow", "net"])
    df = forecast_lines.copy()
    df["date"] = pd.to_datetime(df["date"])
    df["inflow"] = df["amount_eur"].clip(lower=0)
    df["outflow"] = df["amount_eur"].clip(upper=0)
    g = df.set_index("date").groupby(pd.Grouper(freq=freq))[["inflow", "outflow"]].sum()
    g["net"] = g["inflow"] + g["outflow"]
    g = g.reset_index().rename(columns={"date": "period"})
    return g


def project_balance(
    opening_eur: float, forecast_lines: pd.DataFrame, start: date, end: date
) -> pd.Series:
    days = pd.date_range(start, end, freq="D").date
    daily = forecast_lines.groupby("date")["amount_eur"].sum() if not forecast_lines.empty else pd.Series(dtype=float)
    s = pd.Series(0.0, index=days)
    s.update(daily)
    return opening_eur + s.cumsum()


# ---------------------------------------------------------------------------
# Indirect / statistical method
# ---------------------------------------------------------------------------
def statistical_forecast(
    txns: pd.DataFrame, start: date, end: date, lookback_days: int = 540
) -> pd.Series:
    """
    Decompose historical net daily flow into:
      - trend (rolling 30d mean)
      - day-of-week seasonality
      - month-of-year seasonality
    Project each component forward.
    """
    hist_start = start - timedelta(days=lookback_days)
    hist = txns[(txns["date"] >= hist_start) & (txns["date"] < start)].copy()
    if hist.empty:
        return pd.Series(0.0, index=pd.date_range(start, end, freq="D").date)
    hist["date"] = pd.to_datetime(hist["date"])
    daily = hist.groupby("date")["amount_eur"].sum()
    daily = daily.reindex(pd.date_range(daily.index.min(), daily.index.max(), freq="D"), fill_value=0)
    trend = daily.rolling(30, min_periods=5).mean().bfill()
    detrended = daily - trend
    dow_season = detrended.groupby(detrended.index.dayofweek).mean()
    moy_season = detrended.groupby(detrended.index.month).mean()
    overall_trend = float(trend.iloc[-30:].mean())

    fut_index = pd.date_range(start, end, freq="D")
    proj = pd.Series(
        [overall_trend + dow_season.get(d.dayofweek, 0) + moy_season.get(d.month, 0) for d in fut_index],
        index=fut_index,
    )
    proj.index = proj.index.date
    return proj


# ---------------------------------------------------------------------------
# Variance — actuals vs an earlier forecast
# ---------------------------------------------------------------------------
def variance_table(actual: pd.DataFrame, forecast: pd.DataFrame, freq: str = "W") -> pd.DataFrame:
    """Compare aggregated actual vs forecast over a period."""
    a = actual.copy()
    a["date"] = pd.to_datetime(a["date"])
    a = a.set_index("date").groupby(pd.Grouper(freq=freq))["amount_eur"].sum().rename("actual")
    f = forecast.copy()
    f["date"] = pd.to_datetime(f["date"])
    f = f.set_index("date").groupby(pd.Grouper(freq=freq))["amount_eur"].sum().rename("forecast")
    out = pd.concat([a, f], axis=1).fillna(0).reset_index().rename(columns={"date": "period"})
    out["variance"] = out["actual"] - out["forecast"]
    out["variance_pct"] = np.where(
        out["forecast"].abs() > 1e-6,
        out["variance"] / out["forecast"].abs() * 100.0,
        np.nan,
    )
    return out
