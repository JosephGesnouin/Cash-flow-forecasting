"""
Helios Industries SA — Treasury Cash-Flow Forecasting App
Entrypoint. Run with:  streamlit run app.py
"""
from __future__ import annotations

from datetime import timedelta

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from src import data_loader as dl
from src import metrics as m

st.set_page_config(
    page_title="Helios Treasury — Cash-Flow Forecasting",
    page_icon="💶",
    layout="wide",
    initial_sidebar_state="expanded",
)


def _kpi(label: str, value: str, delta: str | None = None, help: str | None = None) -> None:
    st.metric(label, value, delta=delta, help=help)


def main() -> None:
    st.title("Helios Industries SA — Treasury Command Center")
    st.caption(
        "Group cash-flow forecasting · base currency EUR · "
        "data refreshed " + dl.today().isoformat()
    )

    assumptions = dl.load_assumptions()
    banks = dl.load_bank_accounts()
    txns = dl.load_transactions()
    ar = dl.load_ar()
    ap = dl.load_ap()
    today = dl.today()

    cash = m.total_cash_eur(banks, txns, today)
    monthly_out = m.avg_monthly_outflow(txns, today, months=6)
    runway = m.liquidity_ratio(cash, monthly_out)
    dso_v = m.dso(ar, today)
    dpo_v = m.dpo(ap, today)
    open_ar = ar.loc[ar["status"] == "Open", "amount_eur"].sum()
    open_ap = ap.loc[ap["status"] == "Open", "amount_eur"].sum()
    rcf_drawn = assumptions["drivers"]["rcf_drawn_eur"]
    rcf_limit = assumptions["drivers"]["rcf_limit_eur"]
    rcf_avail = rcf_limit - rcf_drawn

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        _kpi("Cash on hand (EUR)", f"€{cash/1e6:,.2f}M",
             help="Sum of EUR-equivalent closing balances across operating, payroll, tax and term-deposit accounts. RCF excluded.")
    with c2:
        _kpi("Liquidity runway", f"{runway:,.1f} months",
             help="Cash on hand divided by trailing 6-month average monthly outflow.")
    with c3:
        _kpi("RCF available", f"€{rcf_avail/1e6:,.2f}M",
             delta=f"{rcf_drawn/1e6:,.2f}M drawn",
             help="Undrawn portion of the EUR 15M revolving credit facility.")
    with c4:
        _kpi("Working capital gap", f"€{(open_ar - open_ap)/1e6:,.2f}M",
             help="Open AR minus open AP, EUR-equivalent.")

    c5, c6, c7, c8 = st.columns(4)
    with c5:
        _kpi("DSO", f"{dso_v:,.1f} d",
             delta=f"{dso_v - assumptions['drivers']['dso_target_days']:+.1f} vs target")
    with c6:
        _kpi("DPO", f"{dpo_v:,.1f} d",
             delta=f"{dpo_v - assumptions['drivers']['dpo_target_days']:+.1f} vs target")
    with c7:
        _kpi("Open AR", f"€{open_ar/1e6:,.2f}M",
             delta=f"{(ar['status']=='Open').sum()} invoices")
    with c8:
        _kpi("Open AP", f"€{open_ap/1e6:,.2f}M",
             delta=f"{(ap['status']=='Open').sum()} invoices")

    st.divider()

    # -- 90-day cash position chart --
    st.subheader("Cash position — last 90 days")
    start = today - timedelta(days=90)
    series = m.daily_balance_series(banks, txns, start, today)
    series.index = pd.to_datetime(series.index)
    min_buffer = assumptions["drivers"]["min_cash_buffer_eur"]
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=series.index, y=series.values, mode="lines",
                             name="Cash position", line=dict(color="#0E4D92", width=2),
                             fill="tozeroy", fillcolor="rgba(14,77,146,0.08)"))
    fig.add_hline(y=min_buffer, line_dash="dash", line_color="#E63946",
                  annotation_text=f"Minimum buffer €{min_buffer/1e6:.1f}M", annotation_position="top left")
    fig.update_layout(height=380, hovermode="x unified",
                      yaxis_title="EUR", xaxis_title="", showlegend=False,
                      margin=dict(l=20, r=20, t=10, b=20))
    st.plotly_chart(fig, use_container_width=True)

    st.info(
        "Use the sidebar to navigate: **Forecast** for the 13-week direct projection, "
        "**Scenarios** for sensitivity analysis, **Receivables / Payables** for working-capital "
        "drill-down, **Bank Accounts** for liquidity by entity & currency, and **Variance** to "
        "compare last month's forecast against actuals."
    )


if __name__ == "__main__":
    main()
