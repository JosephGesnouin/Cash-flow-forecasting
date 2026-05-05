"""AR/AP working-capital drill-down."""
from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from src import data_loader as dl
from src import metrics as m

st.set_page_config(page_title="Receivables & Payables", page_icon="📒", layout="wide")
st.title("📒 Receivables & Payables")

ar = dl.load_ar()
ap = dl.load_ap()
today = dl.today()
assumptions = dl.load_assumptions()

tab_ar, tab_ap = st.tabs(["Receivables (AR)", "Payables (AP)"])

with tab_ar:
    open_ar = ar[ar["status"] == "Open"].copy()
    open_total = open_ar["amount_eur"].sum()
    overdue = open_ar[open_ar["due_date"] < today]["amount_eur"].sum()
    dso_v = m.dso(ar, today)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Open AR", f"€{open_total/1e6:,.2f}M", f"{len(open_ar)} invoices")
    c2.metric("Overdue", f"€{overdue/1e6:,.2f}M",
              f"{(open_ar['due_date'] < today).sum()} invoices",
              delta_color="inverse")
    c3.metric("DSO", f"{dso_v:,.1f} d",
              delta=f"{dso_v - assumptions['drivers']['dso_target_days']:+.1f} vs target")
    c4.metric("Avg invoice (open)", f"€{open_total/max(len(open_ar),1)/1e3:,.1f}k")

    st.divider()
    aging = m.aging_buckets(ar, today)
    col_a, col_b = st.columns([1, 1])
    with col_a:
        st.subheader("Aging buckets")
        fig = go.Figure(go.Bar(
            x=aging["bucket"], y=aging["amount_eur"],
            marker_color=["#2A9D8F", "#F4A261", "#E76F51", "#D62828", "#7F1D1D"],
            text=[f"€{v/1e3:,.0f}k" for v in aging["amount_eur"]],
            textposition="outside",
        ))
        fig.update_layout(height=340, yaxis_title="EUR",
                          margin=dict(l=20, r=20, t=10, b=20))
        st.plotly_chart(fig, use_container_width=True)
    with col_b:
        st.subheader("Top customers — open balance")
        top = open_ar.groupby("customer")["amount_eur"].sum().sort_values(ascending=True).tail(10)
        fig = go.Figure(go.Bar(x=top.values, y=top.index, orientation="h",
                               marker_color="#0E4D92"))
        fig.update_layout(height=340, xaxis_title="EUR",
                          margin=dict(l=20, r=20, t=10, b=20))
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("Customer concentration")
    by_cust = open_ar.groupby(["customer", "country", "currency"])["amount_eur"].sum().reset_index()
    fig = px.treemap(by_cust, path=["country", "customer"], values="amount_eur",
                     color="amount_eur", color_continuous_scale="Blues")
    fig.update_layout(height=420, margin=dict(l=10, r=10, t=10, b=10))
    st.plotly_chart(fig, use_container_width=True)

    with st.expander("Open AR detail", expanded=False):
        show = open_ar.copy().sort_values("due_date")
        show["days_overdue"] = (today - show["due_date"]).apply(lambda d: d.days)
        st.dataframe(show, use_container_width=True, height=380)

with tab_ap:
    open_ap = ap[ap["status"] == "Open"].copy()
    open_total = open_ap["amount_eur"].sum()
    due_7d = open_ap[open_ap["expected_payment_date"] <= today + pd.Timedelta(days=7)]["amount_eur"].sum()
    dpo_v = m.dpo(ap, today)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Open AP", f"€{open_total/1e6:,.2f}M", f"{len(open_ap)} invoices")
    c2.metric("Due in 7 days", f"€{due_7d/1e6:,.2f}M")
    c3.metric("DPO", f"{dpo_v:,.1f} d",
              delta=f"{dpo_v - assumptions['drivers']['dpo_target_days']:+.1f} vs target")
    c4.metric("Avg invoice (open)", f"€{open_total/max(len(open_ap),1)/1e3:,.1f}k")

    st.divider()
    aging = m.aging_buckets(ap, today)
    col_a, col_b = st.columns([1, 1])
    with col_a:
        st.subheader("Aging buckets")
        fig = go.Figure(go.Bar(
            x=aging["bucket"], y=aging["amount_eur"],
            marker_color=["#2A9D8F", "#F4A261", "#E76F51", "#D62828", "#7F1D1D"],
            text=[f"€{v/1e3:,.0f}k" for v in aging["amount_eur"]],
            textposition="outside",
        ))
        fig.update_layout(height=340, yaxis_title="EUR",
                          margin=dict(l=20, r=20, t=10, b=20))
        st.plotly_chart(fig, use_container_width=True)
    with col_b:
        st.subheader("Top suppliers — open balance")
        top = open_ap.groupby("supplier")["amount_eur"].sum().sort_values(ascending=True).tail(10)
        fig = go.Figure(go.Bar(x=top.values, y=top.index, orientation="h",
                               marker_color="#5C677D"))
        fig.update_layout(height=340, xaxis_title="EUR",
                          margin=dict(l=20, r=20, t=10, b=20))
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("Supplier spend by category")
    by_cat = open_ap.groupby(["category", "supplier"])["amount_eur"].sum().reset_index()
    fig = px.treemap(by_cat, path=["category", "supplier"], values="amount_eur",
                     color="amount_eur", color_continuous_scale="Reds")
    fig.update_layout(height=420, margin=dict(l=10, r=10, t=10, b=10))
    st.plotly_chart(fig, use_container_width=True)

    with st.expander("Open AP detail", expanded=False):
        show = open_ap.copy().sort_values("expected_payment_date")
        st.dataframe(show, use_container_width=True, height=380)
