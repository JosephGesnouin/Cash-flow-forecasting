"""
Build a self-contained HTML preview of the dashboard.

Uses the same src/metrics.py and src/forecasting.py library as the Streamlit
app, so the numbers are identical. Plotly is loaded once from CDN; subsequent
charts are embedded as div fragments so the file works offline after first
load.

Run:  python tools/build_html_dashboard.py
Output: docs/dashboard.html
"""
from __future__ import annotations

import sys
from datetime import timedelta
from html import escape
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src import data_loader as dl  # noqa: E402
from src import forecasting as fc  # noqa: E402
from src import metrics as m  # noqa: E402

OUT = ROOT / "docs" / "dashboard.html"

# ---------------------------------------------------------------------------
# Build figures
# ---------------------------------------------------------------------------
def build_figures():
    today = dl.today()
    assumptions = dl.load_assumptions()
    banks = dl.load_bank_accounts()
    txns = dl.load_transactions()
    ar = dl.load_ar()
    ap = dl.load_ap()
    fx = dl.load_fx()

    cash = m.total_cash_eur(banks, txns, today)
    monthly_out = m.avg_monthly_outflow(txns, today, months=6)
    runway = m.liquidity_ratio(cash, monthly_out)
    dso_v = m.dso(ar, today)
    dpo_v = m.dpo(ap, today)
    open_ar = float(ar.loc[ar["status"] == "Open", "amount_eur"].sum())
    open_ap = float(ap.loc[ap["status"] == "Open", "amount_eur"].sum())
    rcf_drawn = assumptions["drivers"]["rcf_drawn_eur"]
    rcf_limit = assumptions["drivers"]["rcf_limit_eur"]
    min_buffer = assumptions["drivers"]["min_cash_buffer_eur"]

    kpis = {
        "cash": cash,
        "runway": runway,
        "rcf_avail": rcf_limit - rcf_drawn,
        "rcf_drawn": rcf_drawn,
        "wc_gap": open_ar - open_ap,
        "dso": dso_v,
        "dso_target": assumptions["drivers"]["dso_target_days"],
        "dpo": dpo_v,
        "dpo_target": assumptions["drivers"]["dpo_target_days"],
        "open_ar": open_ar,
        "open_ap": open_ap,
        "ar_count": int((ar["status"] == "Open").sum()),
        "ap_count": int((ap["status"] == "Open").sum()),
    }

    figs = {}

    # 90-day cash position
    series = m.daily_balance_series(banks, txns, today - timedelta(days=90), today)
    series.index = pd.to_datetime(series.index)
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=series.index, y=series.values, mode="lines", name="Cash position",
        line=dict(color="#0E4D92", width=2),
        fill="tozeroy", fillcolor="rgba(14,77,146,0.10)",
    ))
    fig.add_hline(y=min_buffer, line_dash="dash", line_color="#E63946",
                  annotation_text=f"Minimum buffer €{min_buffer/1e6:.1f}M",
                  annotation_position="top left")
    fig.update_layout(height=360, hovermode="x unified", yaxis_title="EUR",
                      margin=dict(l=20, r=20, t=10, b=20), showlegend=False)
    figs["cash_90d"] = fig

    # 13-week forecast trajectory (base scenario)
    end = today + timedelta(weeks=13)
    base = fc.ScenarioParams("base", **assumptions["scenarios"]["base"])
    f_base = fc.build_direct_forecast(ar, ap, txns, today + timedelta(days=1), end, base)
    bal_base = fc.project_balance(cash, f_base, today + timedelta(days=1), end)

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=pd.to_datetime(list(bal_base.index)), y=bal_base.values,
        mode="lines", name="Base", line=dict(color="#0E4D92", width=2.5),
        fill="tozeroy", fillcolor="rgba(14,77,146,0.08)",
    ))
    fig.add_hline(y=min_buffer, line_dash="dash", line_color="#E63946",
                  annotation_text="Minimum buffer", annotation_position="top left")
    fig.update_layout(height=360, hovermode="x unified", yaxis_title="EUR",
                      margin=dict(l=20, r=20, t=10, b=20), showlegend=False)
    figs["forecast_13w"] = fig

    # Inflow/outflow waterfall (weekly)
    agg = fc.aggregate_forecast(f_base, freq="W")
    agg["period_label"] = pd.to_datetime(agg["period"]).dt.strftime("%d %b")
    fig = go.Figure()
    fig.add_trace(go.Bar(x=agg["period_label"], y=agg["inflow"], name="Inflows",
                         marker_color="#2A9D8F"))
    fig.add_trace(go.Bar(x=agg["period_label"], y=agg["outflow"], name="Outflows",
                         marker_color="#E76F51"))
    fig.add_trace(go.Scatter(x=agg["period_label"], y=agg["net"], name="Net",
                             mode="lines+markers",
                             line=dict(color="#0E4D92", width=2)))
    fig.update_layout(barmode="relative", height=340, hovermode="x unified",
                      yaxis_title="EUR", margin=dict(l=20, r=20, t=10, b=20),
                      legend=dict(orientation="h", yanchor="bottom", y=1.02,
                                  xanchor="right", x=1))
    figs["weekly_bars"] = fig

    # Three scenarios
    scenarios = {
        "Base":       fc.ScenarioParams("base",       **assumptions["scenarios"]["base"]),
        "Optimistic": fc.ScenarioParams("optimistic", **assumptions["scenarios"]["optimistic"]),
        "Stress":     fc.ScenarioParams("stress",     **assumptions["scenarios"]["stress"]),
    }
    colors = {"Base": "#0E4D92", "Optimistic": "#2A9D8F", "Stress": "#E63946"}
    fig = go.Figure()
    sc_table = []
    for name, sc in scenarios.items():
        f = fc.build_direct_forecast(ar, ap, txns, today + timedelta(days=1), end, sc)
        bal = fc.project_balance(cash, f, today + timedelta(days=1), end)
        fig.add_trace(go.Scatter(
            x=pd.to_datetime(list(bal.index)), y=bal.values, mode="lines",
            name=name, line=dict(color=colors[name], width=2.4),
        ))
        sc_table.append({
            "Scenario": name,
            "Closing balance": f"€{bal.iloc[-1]/1e6:,.2f}M",
            "Min balance": f"€{bal.min()/1e6:,.2f}M",
            "Min date": str(bal.idxmin()),
            "Inflows": f"€{f.loc[f['amount_eur']>0,'amount_eur'].sum()/1e6:,.2f}M",
            "Outflows": f"€{f.loc[f['amount_eur']<0,'amount_eur'].sum()/1e6:,.2f}M",
            "Buffer breach": "Yes" if bal.min() < min_buffer else "No",
        })
    fig.add_hline(y=min_buffer, line_dash="dash", line_color="#999",
                  annotation_text="Minimum buffer", annotation_position="top left")
    fig.update_layout(height=380, hovermode="x unified", yaxis_title="EUR",
                      margin=dict(l=20, r=20, t=10, b=20),
                      legend=dict(orientation="h", yanchor="bottom", y=1.02,
                                  xanchor="right", x=1))
    figs["scenarios"] = fig

    # AR aging
    aging = m.aging_buckets(ar, today)
    fig = go.Figure(go.Bar(
        x=aging["bucket"], y=aging["amount_eur"],
        marker_color=["#2A9D8F", "#F4A261", "#E76F51", "#D62828", "#7F1D1D"],
        text=[f"€{v/1e3:,.0f}k" for v in aging["amount_eur"]],
        textposition="outside",
    ))
    fig.update_layout(height=320, yaxis_title="EUR",
                      margin=dict(l=20, r=20, t=10, b=20))
    figs["ar_aging"] = fig

    # Top customers
    open_ar_df = ar[ar["status"] == "Open"].copy()
    top = open_ar_df.groupby("customer")["amount_eur"].sum().sort_values(ascending=True).tail(8)
    fig = go.Figure(go.Bar(x=top.values, y=top.index, orientation="h",
                           marker_color="#0E4D92",
                           text=[f"€{v/1e3:,.0f}k" for v in top.values],
                           textposition="outside"))
    fig.update_layout(height=320, xaxis_title="EUR",
                      margin=dict(l=20, r=20, t=10, b=20))
    figs["top_customers"] = fig

    # Currency donut
    pos = m.cash_position_by_account(banks, txns, today)
    by_ccy = pos[pos["account_type"] != "RCF"].groupby("currency")["closing_balance_eur"].sum().reset_index()
    fig = px.pie(by_ccy, names="currency", values="closing_balance_eur", hole=0.55,
                 color_discrete_sequence=["#0E4D92", "#2A9D8F", "#F4A261"])
    fig.update_layout(height=320, margin=dict(l=20, r=20, t=10, b=20))
    figs["ccy_donut"] = fig

    # FX trend
    fx_long = fx.copy()
    fx_long["date"] = pd.to_datetime(fx_long["date"])
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=fx_long["date"], y=fx_long["USD"], name="EUR/USD",
                             line=dict(color="#2A9D8F", width=1.5)))
    fig.add_trace(go.Scatter(x=fx_long["date"], y=fx_long["GBP"], name="EUR/GBP",
                             yaxis="y2", line=dict(color="#E76F51", width=1.5)))
    fig.update_layout(
        height=300, hovermode="x unified",
        yaxis=dict(title="EUR/USD"),
        yaxis2=dict(title="EUR/GBP", overlaying="y", side="right"),
        margin=dict(l=20, r=20, t=10, b=20),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )
    figs["fx"] = fig

    return today, kpis, figs, sc_table


def render_kpi_card(label: str, value: str, sub: str = "", color: str = "#0E4D92") -> str:
    sub_html = f'<div class="kpi-sub">{escape(sub)}</div>' if sub else ""
    return f"""
    <div class="kpi-card">
      <div class="kpi-label">{escape(label)}</div>
      <div class="kpi-value" style="color:{color}">{escape(value)}</div>
      {sub_html}
    </div>
    """


def render_table(rows: list[dict]) -> str:
    if not rows:
        return ""
    cols = list(rows[0].keys())
    head = "".join(f"<th>{escape(c)}</th>" for c in cols)
    body = ""
    for r in rows:
        cells = "".join(f"<td>{escape(str(r[c]))}</td>" for c in cols)
        body += f"<tr>{cells}</tr>"
    return f'<table class="report"><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table>'


def fig_to_div(fig: go.Figure, include_plotly: bool) -> str:
    return fig.to_html(
        full_html=False,
        include_plotlyjs="cdn" if include_plotly else False,
        config={"displayModeBar": False, "responsive": True},
    )


def main() -> None:
    today, kpis, figs, sc_table = build_figures()

    # KPI cards
    cash_color = "#0E4D92"
    runway_color = "#2A9D8F" if kpis["runway"] >= 2 else ("#F4A261" if kpis["runway"] >= 1 else "#E63946")

    kpi_html = "\n".join([
        render_kpi_card("Cash on hand (excl. RCF)", f"€{kpis['cash']/1e6:,.2f}M", "across 7 accounts", cash_color),
        render_kpi_card("Liquidity runway", f"{kpis['runway']:,.1f} mo",
                        "vs trailing 6m outflow", runway_color),
        render_kpi_card("RCF available",  f"€{kpis['rcf_avail']/1e6:,.2f}M",
                        f"{kpis['rcf_drawn']/1e6:,.2f}M drawn"),
        render_kpi_card("Working-capital gap", f"€{kpis['wc_gap']/1e6:,.2f}M",
                        "open AR − open AP"),
        render_kpi_card("DSO",  f"{kpis['dso']:,.1f} d",
                        f"target {kpis['dso_target']}d  ·  Δ {kpis['dso']-kpis['dso_target']:+.1f}"),
        render_kpi_card("DPO",  f"{kpis['dpo']:,.1f} d",
                        f"target {kpis['dpo_target']}d  ·  Δ {kpis['dpo']-kpis['dpo_target']:+.1f}"),
        render_kpi_card("Open AR", f"€{kpis['open_ar']/1e6:,.2f}M",
                        f"{kpis['ar_count']} invoices"),
        render_kpi_card("Open AP", f"€{kpis['open_ap']/1e6:,.2f}M",
                        f"{kpis['ap_count']} invoices"),
    ])

    chart_cash_90d   = fig_to_div(figs["cash_90d"], include_plotly=True)
    chart_forecast   = fig_to_div(figs["forecast_13w"], include_plotly=False)
    chart_weekly     = fig_to_div(figs["weekly_bars"], include_plotly=False)
    chart_scenarios  = fig_to_div(figs["scenarios"], include_plotly=False)
    chart_aging      = fig_to_div(figs["ar_aging"], include_plotly=False)
    chart_top_cust   = fig_to_div(figs["top_customers"], include_plotly=False)
    chart_ccy        = fig_to_div(figs["ccy_donut"], include_plotly=False)
    chart_fx         = fig_to_div(figs["fx"], include_plotly=False)

    sc_table_html = render_table(sc_table)

    html = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Helios Industries SA — Treasury Cash-Flow Dashboard</title>
  <style>
    :root {{
      --primary: #0E4D92;
      --green:   #2A9D8F;
      --orange:  #F4A261;
      --red:     #E63946;
      --bg:      #F4F6FA;
      --text:    #1F2937;
      --muted:   #6B7280;
      --card:    #FFFFFF;
      --border:  #E5E7EB;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
      margin: 0; padding: 0; background: var(--bg); color: var(--text);
      -webkit-font-smoothing: antialiased;
    }}
    .container {{ max-width: 1280px; margin: 0 auto; padding: 28px 32px 64px; }}
    header {{
      border-bottom: 2px solid var(--primary);
      padding-bottom: 18px; margin-bottom: 28px;
      display: flex; justify-content: space-between; align-items: flex-end;
      flex-wrap: wrap; gap: 16px;
    }}
    h1 {{ margin: 0; font-size: 26px; color: var(--primary); letter-spacing: -0.01em; }}
    h2 {{ margin: 36px 0 14px; font-size: 18px; color: var(--text); border-left: 3px solid var(--primary); padding-left: 10px; }}
    .subtitle {{ color: var(--muted); font-size: 14px; margin-top: 4px; }}
    .meta {{ font-size: 13px; color: var(--muted); text-align: right; line-height: 1.4; }}
    .meta strong {{ color: var(--text); }}

    .kpi-grid {{
      display: grid; gap: 14px;
      grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
      margin-bottom: 8px;
    }}
    .kpi-card {{
      background: var(--card); border: 1px solid var(--border); border-radius: 10px;
      padding: 14px 16px; box-shadow: 0 1px 2px rgba(0,0,0,0.03);
    }}
    .kpi-label {{ color: var(--muted); font-size: 12px; text-transform: uppercase; letter-spacing: 0.04em; }}
    .kpi-value {{ font-size: 22px; font-weight: 700; margin-top: 4px; letter-spacing: -0.01em; }}
    .kpi-sub   {{ color: var(--muted); font-size: 12px; margin-top: 2px; }}

    .grid-2 {{ display: grid; gap: 18px; grid-template-columns: 1fr 1fr; }}
    @media (max-width: 880px) {{ .grid-2 {{ grid-template-columns: 1fr; }} }}

    .card {{
      background: var(--card); border: 1px solid var(--border); border-radius: 10px;
      padding: 18px 20px; box-shadow: 0 1px 2px rgba(0,0,0,0.03); margin-bottom: 18px;
    }}
    .card h3 {{ margin: 0 0 10px; font-size: 15px; font-weight: 600; color: var(--text); }}

    table.report {{ width: 100%; border-collapse: collapse; font-size: 13.5px; }}
    table.report th, table.report td {{
      text-align: left; padding: 9px 12px;
      border-bottom: 1px solid var(--border);
    }}
    table.report thead th {{
      background: var(--bg); color: var(--muted);
      text-transform: uppercase; font-size: 11.5px; letter-spacing: 0.04em;
      font-weight: 600;
    }}
    table.report tbody tr:hover {{ background: rgba(14, 77, 146, 0.03); }}

    .nav-strip {{
      display: flex; flex-wrap: wrap; gap: 8px; margin: 18px 0 12px;
      font-size: 13px;
    }}
    .nav-strip a {{
      padding: 6px 12px; border-radius: 999px; background: var(--card);
      border: 1px solid var(--border); color: var(--text);
      text-decoration: none;
    }}
    .nav-strip a:hover {{ background: var(--primary); color: white; border-color: var(--primary); }}

    footer {{
      margin-top: 48px; padding-top: 18px; border-top: 1px solid var(--border);
      color: var(--muted); font-size: 12.5px; line-height: 1.6;
    }}
    footer code {{
      background: var(--bg); padding: 1px 6px; border-radius: 4px;
      font-family: "SFMono-Regular", Menlo, Consolas, monospace; font-size: 12px;
    }}
  </style>
</head>
<body>
  <div class="container">

    <header>
      <div>
        <h1>Helios Industries SA — Treasury Command Center</h1>
        <div class="subtitle">Group cash-flow forecasting · base currency EUR · static preview</div>
      </div>
      <div class="meta">
        <strong>Data refreshed</strong>: {today.isoformat()}<br>
        <strong>Horizon</strong>: 13 weeks · 3 scenarios<br>
        <strong>Mode</strong>: read-only HTML · for interactivity, run <code>streamlit run app.py</code>
      </div>
    </header>

    <div class="nav-strip">
      <a href="#kpis">Headline KPIs</a>
      <a href="#cash">Cash position</a>
      <a href="#forecast">13-week forecast</a>
      <a href="#scenarios">Scenarios</a>
      <a href="#ar">Receivables</a>
      <a href="#liquidity">Liquidity & FX</a>
    </div>

    <h2 id="kpis">Headline KPIs</h2>
    <div class="kpi-grid">
      {kpi_html}
    </div>

    <h2 id="cash">Cash position — last 90 days</h2>
    <div class="card">{chart_cash_90d}</div>

    <h2 id="forecast">13-week direct cash-flow forecast (base scenario)</h2>
    <div class="card"><h3>Projected balance trajectory</h3>{chart_forecast}</div>
    <div class="card"><h3>Weekly inflows / outflows / net</h3>{chart_weekly}</div>

    <h2 id="scenarios">Scenario comparison</h2>
    <div class="card"><h3>Projected cash trajectory by scenario</h3>{chart_scenarios}</div>
    <div class="card"><h3>Headline metrics</h3>{sc_table_html}</div>

    <h2 id="ar">Receivables drill-down</h2>
    <div class="grid-2">
      <div class="card"><h3>AR aging buckets</h3>{chart_aging}</div>
      <div class="card"><h3>Top 8 customers — open balance</h3>{chart_top_cust}</div>
    </div>

    <h2 id="liquidity">Liquidity & FX</h2>
    <div class="grid-2">
      <div class="card"><h3>Cash by currency (€-equivalent)</h3>{chart_ccy}</div>
      <div class="card"><h3>FX exposure — last 24 months</h3>{chart_fx}</div>
    </div>

    <footer>
      Generated by <code>tools/build_html_dashboard.py</code> from the
      synthetic dataset in <code>data/</code>. All numbers, customers,
      suppliers and bank IBANs are fictional. For interactive exploration
      (sliders, scenario knobs, variance, drill-down tables) run
      <code>streamlit run app.py</code> from the repo root.
    </footer>

  </div>
</body>
</html>
"""

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(html, encoding="utf-8")
    # Mirror to index.html so the repo is GitHub-Pages-ready out of the box
    # (Settings → Pages → branch / docs).
    INDEX = OUT.parent / "index.html"
    INDEX.write_text(html, encoding="utf-8")
    print(f"Wrote {OUT.relative_to(ROOT)}  ({OUT.stat().st_size/1024:,.1f} KB)")
    print(f"Wrote {INDEX.relative_to(ROOT)}  (mirror, GitHub-Pages landing page)")


if __name__ == "__main__":
    main()
