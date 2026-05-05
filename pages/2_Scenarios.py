"""Side-by-side comparison of base / optimistic / stress scenarios."""
from __future__ import annotations

from datetime import timedelta

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from src import data_loader as dl
from src import forecasting as fc
from src import metrics as m

st.set_page_config(page_title="Scenarios", page_icon="🎯", layout="wide")
st.title("🎯 Scenario Analysis")
st.caption(
    "Compare projected cash trajectory under three scenarios. "
    "Stress assumes a 15% sales drop combined with 12 days of additional collection delay — "
    "a typical mid-cycle downturn shock used in our internal liquidity stress testing."
)

assumptions = dl.load_assumptions()
banks = dl.load_bank_accounts()
txns = dl.load_transactions()
ar = dl.load_ar()
ap = dl.load_ap()
today = dl.today()

with st.sidebar:
    horizon_weeks = st.slider("Horizon (weeks)", 4, 26, 13)
end = today + timedelta(weeks=horizon_weeks)
opening = m.total_cash_eur(banks, txns, today)

scenarios = {
    "Base": fc.ScenarioParams("base", **assumptions["scenarios"]["base"]),
    "Optimistic": fc.ScenarioParams("optimistic", **assumptions["scenarios"]["optimistic"]),
    "Stress": fc.ScenarioParams("stress", **assumptions["scenarios"]["stress"]),
}
colors = {"Base": "#0E4D92", "Optimistic": "#2A9D8F", "Stress": "#E63946"}

results = {}
for name, sc in scenarios.items():
    f = fc.build_direct_forecast(ar, ap, txns, today + timedelta(days=1), end, sc)
    bal = fc.project_balance(opening, f, today + timedelta(days=1), end)
    results[name] = {"forecast": f, "balance": bal}

# KPI table
st.subheader("Headline metrics")
kpi_rows = []
for name, r in results.items():
    bal = r["balance"]
    f = r["forecast"]
    kpi_rows.append({
        "Scenario": name,
        "Closing balance (€M)": round(bal.iloc[-1] / 1e6, 2),
        "Min balance (€M)": round(bal.min() / 1e6, 2),
        "Min balance date": str(bal.idxmin()),
        "Inflows (€M)": round(f.loc[f["amount_eur"] > 0, "amount_eur"].sum() / 1e6, 2),
        "Outflows (€M)": round(f.loc[f["amount_eur"] < 0, "amount_eur"].sum() / 1e6, 2),
        "Buffer breach?": "⚠️ Yes" if bal.min() < assumptions["drivers"]["min_cash_buffer_eur"] else "OK",
    })
st.dataframe(pd.DataFrame(kpi_rows), use_container_width=True, hide_index=True)

# Combined chart
st.subheader("Projected cash trajectory")
fig = go.Figure()
for name, r in results.items():
    bal = r["balance"]
    fig.add_trace(go.Scatter(
        x=pd.to_datetime(list(bal.index)), y=bal.values, mode="lines", name=name,
        line=dict(color=colors[name], width=2.4),
    ))
fig.add_hline(y=assumptions["drivers"]["min_cash_buffer_eur"], line_dash="dash",
              line_color="#999", annotation_text="Minimum buffer")
fig.update_layout(height=420, hovermode="x unified", yaxis_title="EUR",
                  margin=dict(l=20, r=20, t=10, b=20))
st.plotly_chart(fig, use_container_width=True)

# Sensitivity grid — sweep sales multiplier x collection delay
st.subheader("Sensitivity: closing balance under sales × collection-delay shock")
sales_grid = [0.80, 0.85, 0.90, 0.95, 1.00, 1.05, 1.10]
delay_grid = [-5, 0, 5, 10, 15, 20]
matrix = []
for s in sales_grid:
    row = []
    for d in delay_grid:
        sc = fc.ScenarioParams("grid", sales_multiplier=s, collection_delay_days=d, capex_multiplier=1.0)
        f = fc.build_direct_forecast(ar, ap, txns, today + timedelta(days=1), end, sc)
        bal = fc.project_balance(opening, f, today + timedelta(days=1), end)
        row.append(round(bal.iloc[-1] / 1e6, 2))
    matrix.append(row)
heat = go.Figure(go.Heatmap(
    z=matrix,
    x=[f"{d:+d}d" for d in delay_grid],
    y=[f"{int(s*100)}%" for s in sales_grid],
    colorscale="RdYlGn",
    text=[[f"€{v:,.1f}M" for v in row] for row in matrix],
    texttemplate="%{text}",
    colorbar=dict(title="€M"),
))
heat.update_layout(height=380, xaxis_title="Collection delay shock",
                   yaxis_title="Sales multiplier",
                   margin=dict(l=20, r=20, t=10, b=20))
st.plotly_chart(heat, use_container_width=True)

with st.expander("Scenario assumptions", expanded=False):
    st.json(assumptions["scenarios"])
