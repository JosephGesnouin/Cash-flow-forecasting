"""13-week direct cash-flow forecast with weekly aggregation."""
from __future__ import annotations

from datetime import timedelta

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from src import data_loader as dl
from src import forecasting as fc
from src import metrics as m

st.set_page_config(page_title="Forecast", page_icon="📈", layout="wide")
st.title("📈 Direct Cash-Flow Forecast")

assumptions = dl.load_assumptions()
banks = dl.load_bank_accounts()
txns = dl.load_transactions()
ar = dl.load_ar()
ap = dl.load_ap()
today = dl.today()

with st.sidebar:
    st.header("Forecast settings")
    horizon_weeks = st.slider("Horizon (weeks)", 4, 26, 13)
    freq_label = st.selectbox("Aggregation", ["Weekly", "Daily", "Monthly"])
    show_stat = st.checkbox("Overlay statistical projection", value=True,
                            help="Indirect method using trend + DOW/MOY seasonality.")
    sales_mult = st.slider("Sales multiplier", 0.5, 1.5, 1.00, 0.01)
    coll_delay = st.slider("Collection delay (days)", -10, 30, 0)
    capex_mult = st.slider("Capex multiplier", 0.0, 2.0, 1.00, 0.05)

freq = {"Daily": "D", "Weekly": "W", "Monthly": "ME"}[freq_label]
end = today + timedelta(weeks=horizon_weeks)
scenario = fc.ScenarioParams("custom", sales_mult, coll_delay, capex_mult)

forecast = fc.build_direct_forecast(ar, ap, txns, today + timedelta(days=1), end, scenario)
agg = fc.aggregate_forecast(forecast, freq=freq)

opening = m.total_cash_eur(banks, txns, today)
balance = fc.project_balance(opening, forecast, today + timedelta(days=1), end)

# --- KPIs ---
total_in = float(agg["inflow"].sum())
total_out = float(agg["outflow"].sum())
end_balance = float(balance.iloc[-1])
min_balance = float(balance.min())
min_balance_date = balance.idxmin()

c1, c2, c3, c4 = st.columns(4)
c1.metric("Forecast inflows", f"€{total_in/1e6:,.2f}M")
c2.metric("Forecast outflows", f"€{total_out/1e6:,.2f}M")
c3.metric(f"Closing balance ({end:%d %b %Y})", f"€{end_balance/1e6:,.2f}M",
          delta=f"{(end_balance-opening)/1e6:+,.2f}M vs today")
c4.metric("Min balance in horizon", f"€{min_balance/1e6:,.2f}M",
          delta=f"on {min_balance_date}",
          delta_color="inverse" if min_balance < assumptions["drivers"]["min_cash_buffer_eur"] else "normal")

st.divider()

# --- Cash bridge chart ---
st.subheader("Projected cash position")
fig = go.Figure()
fig.add_trace(go.Scatter(
    x=pd.to_datetime(list(balance.index)), y=balance.values,
    mode="lines", name="Direct projection",
    line=dict(color="#0E4D92", width=2),
    fill="tozeroy", fillcolor="rgba(14,77,146,0.08)",
))
if show_stat:
    stat = fc.statistical_forecast(txns, today + timedelta(days=1), end)
    stat_balance = opening + stat.cumsum()
    fig.add_trace(go.Scatter(
        x=pd.to_datetime(list(stat_balance.index)), y=stat_balance.values,
        mode="lines", name="Statistical (sanity check)",
        line=dict(color="#7F8FA6", width=1.5, dash="dot"),
    ))
fig.add_hline(y=assumptions["drivers"]["min_cash_buffer_eur"], line_dash="dash",
              line_color="#E63946", annotation_text="Minimum buffer", annotation_position="top left")
fig.update_layout(height=380, hovermode="x unified",
                  yaxis_title="EUR", margin=dict(l=20, r=20, t=10, b=20))
st.plotly_chart(fig, use_container_width=True)

# --- Inflow / outflow waterfall ---
st.subheader(f"{freq_label} inflows / outflows")
agg_disp = agg.copy()
agg_disp["period_label"] = pd.to_datetime(agg_disp["period"]).dt.strftime("%d %b")
fig2 = go.Figure()
fig2.add_trace(go.Bar(x=agg_disp["period_label"], y=agg_disp["inflow"],
                      name="Inflows", marker_color="#2A9D8F"))
fig2.add_trace(go.Bar(x=agg_disp["period_label"], y=agg_disp["outflow"],
                      name="Outflows", marker_color="#E76F51"))
fig2.add_trace(go.Scatter(x=agg_disp["period_label"], y=agg_disp["net"],
                          name="Net", mode="lines+markers",
                          line=dict(color="#0E4D92", width=2)))
fig2.update_layout(barmode="relative", height=360, hovermode="x unified",
                   yaxis_title="EUR", margin=dict(l=20, r=20, t=10, b=20))
st.plotly_chart(fig2, use_container_width=True)

# --- Forecast lines table ---
with st.expander("Forecast line items", expanded=False):
    show = forecast.copy()
    show["amount_eur"] = show["amount_eur"].round(0)
    st.dataframe(show, use_container_width=True, height=420)

# --- Category breakdown ---
st.subheader("Forecast by category")
cat = forecast.groupby("category")["amount_eur"].sum().reset_index().sort_values("amount_eur")
fig3 = go.Figure(go.Bar(
    x=cat["amount_eur"], y=cat["category"], orientation="h",
    marker_color=["#2A9D8F" if v > 0 else "#E76F51" for v in cat["amount_eur"]],
))
fig3.update_layout(height=380, xaxis_title="EUR", margin=dict(l=20, r=20, t=10, b=20))
st.plotly_chart(fig3, use_container_width=True)
