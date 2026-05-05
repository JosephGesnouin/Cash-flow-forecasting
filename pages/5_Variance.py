"""
Variance analysis: actuals vs the forecast that was produced N weeks ago.

We rebuild a "frozen" forecast as of (today - lookback) using only data that
would have been known at that point, then compare to what actually happened.
"""
from __future__ import annotations

from datetime import timedelta

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from src import data_loader as dl
from src import forecasting as fc

st.set_page_config(page_title="Variance", page_icon="🔍", layout="wide")
st.title("🔍 Forecast vs Actuals — Variance Analysis")

txns = dl.load_transactions()
ar = dl.load_ar()
ap = dl.load_ap()
today = dl.today()

with st.sidebar:
    lookback_weeks = st.slider("Forecast vintage (weeks ago)", 2, 12, 4)
    horizon_weeks = st.slider("Compared horizon (weeks)", 2, 12, 4)
    freq_label = st.selectbox("Aggregation", ["Weekly", "Daily", "Monthly"])

freq = {"Daily": "D", "Weekly": "W", "Monthly": "ME"}[freq_label]
forecast_date = today - timedelta(weeks=lookback_weeks)
period_start = forecast_date + timedelta(days=1)
period_end = min(today, forecast_date + timedelta(weeks=horizon_weeks))

# Re-create the forecast as it would have been at forecast_date
ar_then = ar[ar["issue_date"] <= forecast_date].copy()
# An invoice that has since been paid was "Open" back then if expected payment > forecast_date
ar_then["status"] = ar_then.apply(
    lambda r: "Open" if (pd.isna(r["payment_date"]) or r["payment_date"] > forecast_date) else "Paid",
    axis=1,
)
ap_then = ap[ap["issue_date"] <= forecast_date].copy()
ap_then["status"] = ap_then.apply(
    lambda r: "Open" if (pd.isna(r["payment_date"]) or r["payment_date"] > forecast_date) else "Paid",
    axis=1,
)
txns_then = txns[txns["date"] <= forecast_date].copy()

scenario = fc.ScenarioParams("base")
forecast_lines = fc.build_direct_forecast(
    ar_then, ap_then, txns_then, period_start, period_end, scenario
)
actuals = txns[(txns["date"] >= period_start) & (txns["date"] <= period_end)][
    ["date", "amount_eur"]
].copy()

variance = fc.variance_table(actuals, forecast_lines, freq=freq)

# KPIs
total_actual = actuals["amount_eur"].sum()
total_forecast = forecast_lines["amount_eur"].sum() if not forecast_lines.empty else 0
abs_var = total_actual - total_forecast
pct_var = abs_var / abs(total_forecast) * 100 if total_forecast else 0
mape = variance["variance"].abs().sum() / variance["forecast"].abs().sum() * 100 \
    if variance["forecast"].abs().sum() else 0

c1, c2, c3, c4 = st.columns(4)
c1.metric("Forecast vintage", forecast_date.isoformat())
c2.metric("Actual net (€M)", f"€{total_actual/1e6:,.2f}M")
c3.metric("Forecast net (€M)", f"€{total_forecast/1e6:,.2f}M",
          delta=f"{abs_var/1e6:+,.2f}M ({pct_var:+,.1f}%)")
c4.metric("Aggregated MAPE", f"{mape:,.1f}%",
          help="Mean absolute percentage error across periods.")

st.divider()
st.subheader(f"{freq_label} comparison")
fig = go.Figure()
fig.add_trace(go.Bar(x=variance["period"], y=variance["forecast"],
                     name="Forecast", marker_color="#5C677D"))
fig.add_trace(go.Bar(x=variance["period"], y=variance["actual"],
                     name="Actual", marker_color="#0E4D92"))
fig.add_trace(go.Scatter(x=variance["period"], y=variance["variance"],
                         name="Variance", mode="lines+markers",
                         line=dict(color="#E63946", width=2)))
fig.update_layout(barmode="group", height=400, hovermode="x unified",
                  yaxis_title="EUR", margin=dict(l=20, r=20, t=10, b=20))
st.plotly_chart(fig, use_container_width=True)

st.dataframe(
    variance.assign(
        actual=variance["actual"].round(0),
        forecast=variance["forecast"].round(0),
        variance=variance["variance"].round(0),
        variance_pct=variance["variance_pct"].round(1),
    ),
    use_container_width=True, hide_index=True,
)

st.caption(
    "Reading guide: positive variance = actual cash inflow exceeded forecast (favourable). "
    "MAPE above 15% suggests forecast assumptions need recalibration — typically a sign "
    "that DSO has drifted from target or a one-off item was missed."
)
