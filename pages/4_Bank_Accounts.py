"""Liquidity by bank, currency and entity."""
from __future__ import annotations

from datetime import timedelta

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from src import data_loader as dl
from src import metrics as m

st.set_page_config(page_title="Bank Accounts", page_icon="🏦", layout="wide")
st.title("🏦 Bank Accounts & Liquidity")

banks = dl.load_bank_accounts()
txns = dl.load_transactions()
fx = dl.load_fx()
today = dl.today()
assumptions = dl.load_assumptions()

pos = m.cash_position_by_account(banks, txns, today)

c1, c2, c3 = st.columns(3)
c1.metric("Total cash (excl. RCF)", f"€{m.total_cash_eur(banks, txns, today)/1e6:,.2f}M")
c2.metric("Number of accounts", f"{len(banks)}")
c3.metric("Currencies", ", ".join(sorted(banks['currency'].unique())))

st.divider()
st.subheader("Account positions")
disp = pos[["nickname", "bank", "currency", "account_type",
            "opening_balance", "net_movement", "closing_balance",
            "closing_balance_eur"]].copy()
disp = disp.rename(columns={
    "nickname": "Account",
    "bank": "Bank",
    "currency": "Ccy",
    "account_type": "Type",
    "opening_balance": "Opening",
    "net_movement": "Net mvt (ccy)",
    "closing_balance": "Closing (ccy)",
    "closing_balance_eur": "Closing (€)",
})
for c in ["Opening", "Net mvt (ccy)", "Closing (ccy)", "Closing (€)"]:
    disp[c] = disp[c].round(0)
st.dataframe(disp, use_container_width=True, hide_index=True)

col_a, col_b = st.columns(2)
with col_a:
    st.subheader("Cash by currency (€-equivalent)")
    by_ccy = pos[pos["account_type"] != "RCF"].groupby("currency")["closing_balance_eur"].sum().reset_index()
    fig = px.pie(by_ccy, names="currency", values="closing_balance_eur", hole=0.55,
                 color_discrete_sequence=px.colors.sequential.Blues_r)
    fig.update_layout(height=340, margin=dict(l=20, r=20, t=10, b=20))
    st.plotly_chart(fig, use_container_width=True)

with col_b:
    st.subheader("Cash by account type (€-equivalent)")
    by_type = pos[pos["account_type"] != "RCF"].groupby("account_type")["closing_balance_eur"].sum().reset_index()
    fig = go.Figure(go.Bar(x=by_type["account_type"], y=by_type["closing_balance_eur"],
                           marker_color="#0E4D92"))
    fig.update_layout(height=340, yaxis_title="EUR",
                      margin=dict(l=20, r=20, t=10, b=20))
    st.plotly_chart(fig, use_container_width=True)

st.divider()
st.subheader("FX exposure — last 24 months")
fx_long = fx.copy()
fx_long["date"] = pd.to_datetime(fx_long["date"])
fig = go.Figure()
fig.add_trace(go.Scatter(x=fx_long["date"], y=fx_long["USD"], name="EUR/USD",
                         line=dict(color="#2A9D8F", width=1.5)))
fig.add_trace(go.Scatter(x=fx_long["date"], y=fx_long["GBP"], name="EUR/GBP",
                         yaxis="y2", line=dict(color="#E76F51", width=1.5)))
fig.update_layout(
    height=320, hovermode="x unified",
    yaxis=dict(title="EUR/USD"),
    yaxis2=dict(title="EUR/GBP", overlaying="y", side="right"),
    margin=dict(l=20, r=20, t=10, b=20),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
)
st.plotly_chart(fig, use_container_width=True)

st.subheader("Daily cash position by account — last 60 days")
start = today - timedelta(days=60)
days = pd.date_range(start, today, freq="D").date
op_acc = banks.set_index("iban")
fig = go.Figure()
for iban, row in op_acc.iterrows():
    if row["account_type"] == "RCF":
        continue
    sub = txns[(txns["account_iban"] == iban) & (txns["date"] >= start) & (txns["date"] <= today)]
    daily = sub.groupby("date")["amount_eur"].sum()
    s = pd.Series(0.0, index=days)
    s.update(daily)
    # opening for period: closing as of start-1
    earlier = txns[(txns["account_iban"] == iban) & (txns["date"] < start)]["amount_eur"].sum()
    period_open = row["opening_balance"] + earlier
    bal = period_open + s.cumsum()
    fig.add_trace(go.Scatter(x=pd.to_datetime(list(bal.index)), y=bal.values,
                             mode="lines", name=row["nickname"]))
fig.update_layout(height=380, hovermode="x unified", yaxis_title="EUR",
                  margin=dict(l=20, r=20, t=10, b=20),
                  legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0))
st.plotly_chart(fig, use_container_width=True)
