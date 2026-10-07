import inspect, os, re, sqlite3, time
from datetime import date

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from plotly.subplots import make_subplots

import analytics as A
import db
import tasks as T

import base64, glob, io
from PIL import Image as _PIL

# ---- logo: self-contained (no extra module). Looks in ./assets, next to app.py, and the parent folder ----
_HERE = os.path.dirname(os.path.abspath(__file__))
_NAMES = ["logo.png", "logo_256.png", "NSE_Logo.png", "nse_logo.png",
          "NSE Stock Market Analysis Badge.png", "NSE_Stock_Market_Analysis_Badge.png"]


@st.cache_resource(show_spinner=False)
def _logo_path():
    dirs = [os.path.join(_HERE, "assets"), _HERE, os.path.dirname(_HERE), os.getcwd()]
    for d in dirs:
        for n in _NAMES:
            if os.path.isfile(os.path.join(d, n)):
                return os.path.join(d, n)
    for d in dirs:
        for p in sorted(glob.glob(os.path.join(d, "*.png"))):
            if any(k in os.path.basename(p).lower() for k in ("logo", "badge")):
                return p
    return None


def logo_image(size=256):
    p = _logo_path()
    if not p:
        return None
    im = _PIL.open(p).convert("RGBA")
    im.thumbnail((size, size), _PIL.LANCZOS)
    return im


def logo_b64(size=256):
    im = logo_image(size)
    if im is None:
        return ""
    buf = io.BytesIO(); im.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode()


_icon = logo_image(64) or "📈"
st.set_page_config(page_title="NSE Stock Market Analysis", page_icon=_icon, layout="wide",
                   initial_sidebar_state="expanded")

# --------------------------------------------------------------------------- look & feel
COLORS = {"Bajaj Auto": "#38bdf8", "Eicher Motors": "#f59e0b", "Hero Motocorp": "#f43f5e",
          "Infosys": "#a78bfa", "TCS": "#34d399", "TVS Motors": "#fb923c"}
GREEN, RED, INDIGO = "#22c55e", "#ef4444", "#818cf8"
EVENT_BY_STOCK = {T.DISPLAY[t]: d for t, d in T.EVENTS.items()}
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

st.markdown("""
<style>
.block-container {padding-top: 1.4rem; max-width: 1400px;}
[data-testid="stSidebar"] {background: linear-gradient(180deg,#0f1630 0%,#0b1020 100%); border-right: 1px solid #1e2748;}
.hero {background: radial-gradient(1200px 400px at 0% 0%, rgba(99,102,241,.35), transparent 60%),
        radial-gradient(900px 300px at 100% 0%, rgba(34,197,94,.22), transparent 60%), #111936;
       border: 1px solid #243059; border-radius: 22px; padding: 28px 34px; margin-bottom: 18px;}
.hero {display: flex; align-items: center; gap: 26px;}
.hero-logo {width: 118px; height: 118px; filter: drop-shadow(0 6px 22px rgba(45,212,191,.35)); flex: none;}
.hero h1 {margin: 0; font-size: 2.1rem; font-weight: 800;
          background: linear-gradient(90deg,#c7d2fe,#86efac); -webkit-background-clip: text; -webkit-text-fill-color: transparent;}
.hero p {margin: 6px 0 0 0; color: #aab4d4; font-size: 1.0rem;}
.kpi {background: #121a33; border: 1px solid #222d55; border-left: 4px solid var(--accent); border-radius: 14px;
      padding: 14px 16px; height: 100%; transition: transform .15s ease, box-shadow .15s ease;}
.kpi:hover {transform: translateY(-3px); box-shadow: 0 10px 28px rgba(0,0,0,.35);}
.kpi-t {font-size: .78rem; color: #93a0c8; text-transform: uppercase; letter-spacing: .06em;}
.kpi-v {font-size: 1.65rem; font-weight: 800; margin: 2px 0; color: #f1f5ff;}
.kpi-s {font-size: .82rem; color: #9aa6cc;}
.pill {display:inline-block; padding: 2px 10px; border-radius: 999px; font-size: .75rem; font-weight: 700;}
.pill.buy {background: rgba(34,197,94,.18); color:#4ade80;} .pill.sell {background: rgba(239,68,68,.18); color:#f87171;}
.pill.up {background: rgba(34,197,94,.18); color:#4ade80;} .pill.down {background: rgba(239,68,68,.18); color:#f87171;}
.callout {background: #1a1530; border: 1px solid #4c3a8a; border-left: 4px solid #a78bfa; border-radius: 12px; padding: 14px 18px; margin: 10px 0;}
.callout.warn {background: #2a1a14; border-color: #7a3b1d; border-left-color: #fb923c;}
.callout.ok {background: #10261c; border-color: #1d6b43; border-left-color: #22c55e;}
.section {font-size: 1.15rem; font-weight: 700; margin: 18px 0 6px 0; color: #e0e7ff;}
textarea {font-family: 'JetBrains Mono','Fira Code',Consolas,monospace !important; font-size: 0.9rem !important;}
div[data-testid="stTabs"] button {font-weight: 600;}
</style>
""", unsafe_allow_html=True)

_ST_VER = tuple(int(x) for x in re.findall(r"\d+", st.__version__)[:2])
_STRETCH = [{"width": "stretch"}, {"use_container_width": True}] if _ST_VER >= (1, 50) \
    else [{"use_container_width": True}, {"width": "stretch"}]


def _wide(fn, *a, **k):
    """Full-width rendering that works across Streamlit versions."""
    for kw in _STRETCH:
        try:
            return fn(*a, **kw, **k)
        except (TypeError, st.errors.StreamlitAPIException):
            continue
    return fn(*a, **k)


def show(fig, key=None):
    return _wide(st.plotly_chart, fig, key=key)


def table(df, **k):
    return _wide(st.dataframe, df, hide_index=True, **k)


def kpi(title, value, sub="", accent=INDIGO):
    return (f'<div class="kpi" style="--accent:{accent}"><div class="kpi-t">{title}</div>'
            f'<div class="kpi-v">{value}</div><div class="kpi-s">{sub}</div></div>')


def pill(text):
    cls = {"Buy": "buy", "Sell": "sell", "Uptrend": "up", "Downtrend": "down"}.get(text, "")
    return f'<span class="pill {cls}">{text}</span>'


def style(fig, h=520, legend=True):
    fig.update_layout(template="plotly_dark", height=h, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                      hovermode="x unified", margin=dict(l=10, r=10, t=40, b=10),
                      legend=dict(orientation="h", y=1.08, x=0) if legend else None, showlegend=legend,
                      font=dict(color="#cbd5ee"))
    fig.update_xaxes(gridcolor="rgba(148,163,184,.12)")
    fig.update_yaxes(gridcolor="rgba(148,163,184,.12)")
    return fig


# --------------------------------------------------------------------------- data (all built with SQL)
@st.cache_resource(show_spinner="Building the database with SQL …")
def get_base():
    return A.build_base()


@st.cache_data(show_spinner=False)
def get_df(_n):
    con, tables = get_base()
    return A.load_frames(con, tables)


@st.cache_data(show_spinner=False)
def task_df(_n, task_id):
    """Result of a project query, run on the shared base DB."""
    con, tables = get_base()
    t = next(x for x in T.build_tasks(tables, A_focus(tables)) if x["id"] == task_id)
    return pd.read_sql(t["sql"], con)


def A_focus(tables):
    return "bajaj_auto" if "bajaj_auto" in tables else tables[0]


def session_con():
    if "con" not in st.session_state:
        st.session_state.con = A.clone(get_base()[0])
    return st.session_state.con


# --------------------------------------------------------------------------- sidebar
base_con, TABLES = get_base()
N = len(TABLES)
df = get_df(N)
STOCKS = sorted(df.stock.unique())

with st.sidebar:
    if logo_image(256) is not None:
        st.image(logo_image(256), width=150)
    else:
        st.caption("⚠️ Logo not found. Put NSE_Logo.png in the same folder as app.py.")
    st.markdown("### NSE Stock Market Analysis")
    st.caption("Jan 2015 → Jul 2018 · 889 trading days")
    page = st.radio("Navigate", [
        "🏠 Overview", "🔎 Stock Explorer", "⚖️ Compare Stocks", "🚦 Signals & Backtest",
        "🪤 The Data Trap", "🧪 SQL Playground", "📚 Task Walkthrough", "📦 Downloads"],
        label_visibility="collapsed")
    st.divider()
    st.markdown("**Loaded tables**")
    st.markdown(" ".join(f"`{t}`" for t in TABLES))
    if "bajaj_auto" not in TABLES:
        st.warning("`Bajaj_Auto.csv` isn't in the data folder yet. Upload it to add the 6th stock.")
        up = st.file_uploader("Add Bajaj_Auto.csv", type="csv", key="bajaj_up")
        if up is not None:
            try:
                tmp = os.path.join(db.DATA_DIR, "_tmp.csv")
                with open(tmp, "wb") as f:
                    f.write(up.getvalue())
                db.read_csv(tmp)  # validates format
                os.replace(tmp, os.path.join(db.DATA_DIR, "Bajaj_Auto.csv"))
                st.cache_resource.clear(); st.cache_data.clear()
                st.session_state.pop("con", None)
                st.rerun()
            except Exception as e:
                st.error(f"Couldn't read that file: {e}")
    st.divider()
    adj_default = st.toggle("Use bonus-adjusted prices", value=True,
                            help="TCS (2018-05-31) and Infosys (2015-06-15) had 1:1 bonus issues. "
                                 "Raw prices show a fake ~50% crash on those days.")
    PC = "adj_close" if adj_default else "close"

stats = A.stock_stats(df, PC)


# --------------------------------------------------------------------------- pages
def page_overview():
    _logo = logo_b64(256)
    _img = f'<img src="data:image/png;base64,{_logo}" class="hero-logo">' if _logo else ""
    st.markdown(f"""<div class="hero">{_img}<div><h1>NSE Stock Market Analysis</h1>
    <p>{len(STOCKS)} stocks · moving-average golden-cross signals · everything computed in <b>SQL</b>,
    then explored interactively. {'Prices are bonus-adjusted.' if adj_default else '⚠️ Showing RAW prices (TCS & Infosys distorted).'}</p></div></div>""",
                unsafe_allow_html=True)
    sig = A.signal_summary(df).set_index("stock")
    trend, names = A.trend_now(df)
    tr = dict(zip(names, trend))
    cols = st.columns(len(STOCKS))
    for c, s in zip(cols, STOCKS):
        r = stats[stats.stock == s].iloc[0]
        c.markdown(kpi(s, f"{r.total_return:+.1f}%",
                       f"{pill(tr[s])} {pill(sig.loc[s, 'last_signal'])}<br>since Jan-2015",
                       COLORS.get(s, INDIGO)), unsafe_allow_html=True)

    st.markdown('<div class="section">Growth of 100 — who actually made money?</div>', unsafe_allow_html=True)
    c1, c2 = st.columns([3, 1])
    pick = c1.multiselect("Stocks", STOCKS, default=STOCKS, key="ov_pick")
    dmin, dmax = df.date.min().date(), df.date.max().date()
    rng = c2.slider("Period", dmin, dmax, (dmin, dmax), key="ov_rng")
    d = df[(df.date.dt.date >= rng[0]) & (df.date.dt.date <= rng[1])]
    if pick:
        rb = A.rebased(d, pick, PC)
        fig = go.Figure()
        for s in pick:
            fig.add_trace(go.Scatter(x=rb.index, y=rb[s], name=s, mode="lines", line=dict(color=COLORS.get(s), width=2.4),
                                     hovertemplate="%{y:.1f}"))
        fig.add_hline(y=100, line_dash="dot", line_color="#64748b")
        show(style(fig, 470))
    else:
        st.info("Pick at least one stock.")

    left, right = st.columns([3, 2])
    with left:
        st.markdown('<div class="section">Leaderboard</div>', unsafe_allow_html=True)
        lb = stats.sort_values("total_return", ascending=False)[
            ["stock", "total_return", "cagr", "volatility", "max_drawdown", "return_per_risk"]]
        lb.columns = ["Stock", "Total return %", "CAGR %", "Volatility %", "Max drawdown %", "Return / risk"]
        table(lb.round(2), column_config={
            "Total return %": st.column_config.ProgressColumn(format="%.1f", min_value=-40, max_value=100),
            "Return / risk": st.column_config.NumberColumn(format="%.2f")})
    with right:
        st.markdown('<div class="section">Latest golden-cross signal</div>', unsafe_allow_html=True)
        s2 = sig.reset_index().rename(columns={"stock": "Stock", "last_signal": "Last signal",
                                               "last_signal_date": "Date"})
        table(s2[["Stock", "Buy", "Sell", "Last signal", "Date"]])

    st.markdown('<div class="section">Key insights</div>', unsafe_allow_html=True)
    best = stats.sort_values("total_return").iloc[-1]; worst = stats.sort_values("total_return").iloc[0]
    st.markdown(f"""<div class="callout ok"><b>Best performer:</b> {best.stock} ({best.total_return:+.1f}%) &nbsp;|&nbsp;
    <b>Weakest:</b> {worst.stock} ({worst.total_return:+.1f}%) &nbsp;|&nbsp;
    <b>Highest return per unit of risk:</b> {stats.sort_values('return_per_risk').iloc[-1].stock}</div>""",
                unsafe_allow_html=True)
    if all(t in TABLES for t in T.EVENTS):
        raw = A.stock_stats(df, "close").set_index("stock")
        st.markdown(f"""<div class="callout warn"><b>🪤 Data trap:</b> on raw prices TCS looks like
        <b>{raw.loc['TCS','total_return']:+.1f}%</b> and Infosys <b>{raw.loc['Infosys','total_return']:+.1f}%</b>.
        After adjusting for the 1:1 bonus issues they are <b>+{stats.set_index('stock').loc['TCS','total_return']:.1f}%</b>
        and <b>+{stats.set_index('stock').loc['Infosys','total_return']:.1f}%</b>. Open <i>The Data Trap</i> to see why.</div>""",
                    unsafe_allow_html=True)


def page_explorer():
    st.markdown('<div class="section">Stock Explorer — price, moving averages & golden-cross signals</div>',
                unsafe_allow_html=True)
    c = st.columns([2, 2, 3])
    s = c[0].selectbox("Stock", STOCKS)
    style_pick = c[1].radio("Chart", ["Line", "Candlestick"], horizontal=True)
    dmin, dmax = df.date.min().date(), df.date.max().date()
    rng = c[2].slider("Period", dmin, dmax, (dmin, dmax), key="ex_rng")
    o = st.columns(4)
    show20 = o[0].checkbox("MA 20", True); show50 = o[1].checkbox("MA 50", True)
    showsig = o[2].checkbox("Buy / Sell markers", True); showvol = o[3].checkbox("Volume", True)

    g = df[(df.stock == s) & (df.date.dt.date >= rng[0]) & (df.date.dt.date <= rng[1])]
    pre = "adj_" if adj_default else ""
    rows = 2 if showvol else 1
    fig = make_subplots(rows=rows, cols=1, shared_xaxes=True, vertical_spacing=0.03,
                        row_heights=[0.75, 0.25] if showvol else [1])
    if style_pick == "Candlestick":
        fig.add_trace(go.Candlestick(x=g.date, open=g[f"{pre}open"], high=g[f"{pre}high"], low=g[f"{pre}low"],
                                     close=g[PC], name="Price", increasing_line_color=GREEN,
                                     decreasing_line_color=RED), row=1, col=1)
    else:
        fig.add_trace(go.Scatter(x=g.date, y=g[PC], name="Close", mode="lines",
                                 line=dict(color=COLORS.get(s, INDIGO), width=2.2)), row=1, col=1)
    # the MAs/signals in the DB were computed on adjusted prices; for raw view recompute from raw
    if adj_default:
        m20, m50, sg = g.ma20, g.ma50, g.signal
    else:
        full = df[df.stock == s].sort_values("date")
        r20 = full.close.rolling(20).mean(); r50 = full.close.rolling(50).mean()
        m20 = r20.loc[g.index]; m50 = r50.loc[g.index]; sg = g.signal
    if show20:
        fig.add_trace(go.Scatter(x=g.date, y=m20, name="MA 20", line=dict(color="#f8fafc", width=1.5, dash="dot")), row=1, col=1)
    if show50:
        fig.add_trace(go.Scatter(x=g.date, y=m50, name="MA 50", line=dict(color="#e879f9", width=1.8)), row=1, col=1)
    if showsig:
        b = g[sg == "Buy"]; sl = g[sg == "Sell"]
        fig.add_trace(go.Scatter(x=b.date, y=b[PC], mode="markers", name="Buy",
                                 marker=dict(symbol="triangle-up", size=14, color=GREEN, line=dict(width=1, color="white")),
                                 hovertemplate="BUY %{x|%d %b %Y}<br>₹%{y:,.2f}<extra></extra>"), row=1, col=1)
        fig.add_trace(go.Scatter(x=sl.date, y=sl[PC], mode="markers", name="Sell",
                                 marker=dict(symbol="triangle-down", size=14, color=RED, line=dict(width=1, color="white")),
                                 hovertemplate="SELL %{x|%d %b %Y}<br>₹%{y:,.2f}<extra></extra>"), row=1, col=1)
    if showvol:
        fig.add_trace(go.Bar(x=g.date, y=g.volume, name="Volume", marker_color="rgba(129,140,248,.55)"), row=2, col=1)
    if not adj_default and s in EVENT_BY_STOCK:
        ev = EVENT_BY_STOCK[s]
        fig.add_shape(type="line", x0=ev, x1=ev, y0=0, y1=1, xref="x", yref="paper",
                      line=dict(color="#fb923c", dash="dash", width=1.5))
        fig.add_annotation(x=ev, y=1, xref="x", yref="paper", text="1:1 bonus issue", showarrow=False,
                           yanchor="bottom", font=dict(color="#fb923c"))
    fig.update_xaxes(rangeslider_visible=False)
    lo, hi = float(g[PC].min()), float(g[PC].max())
    if style_pick == "Candlestick":
        lo, hi = float(g[f"{pre}low"].min()), float(g[f"{pre}high"].max())
    pad = (hi - lo) * 0.06
    fig.update_yaxes(range=[lo - pad, hi + pad], row=1, col=1)
    if showvol:
        fig.update_yaxes(range=[0, float(g.volume.quantile(0.99)) * 1.25], row=2, col=1)
    show(style(fig, 640))
    if showvol:
        st.caption("Volume axis is capped near the 99th percentile so normal days stay visible; rare spikes run off the top.")

    last = g.iloc[-1]; first = g.iloc[0]
    m = st.columns(5)
    m[0].markdown(kpi("Last close", f"₹{last[PC]:,.2f}", f"{last.date:%d %b %Y}", COLORS.get(s)), unsafe_allow_html=True)
    m[1].markdown(kpi("Period return", f"{100 * (last[PC] / first[PC] - 1):+.1f}%", "selected range", COLORS.get(s)), unsafe_allow_html=True)
    m[2].markdown(kpi("Highest close", f"₹{g[PC].max():,.2f}", f"{g.loc[g[PC].idxmax(), 'date']:%d %b %Y}", COLORS.get(s)), unsafe_allow_html=True)
    m[3].markdown(kpi("Lowest close", f"₹{g[PC].min():,.2f}", f"{g.loc[g[PC].idxmin(), 'date']:%d %b %Y}", COLORS.get(s)), unsafe_allow_html=True)
    m[4].markdown(kpi("Signals shown", f"{(sg == 'Buy').sum()} Buy / {(sg == 'Sell').sum()} Sell", "golden crosses", COLORS.get(s)), unsafe_allow_html=True)
    if not adj_default:
        st.caption("Raw view: signals shown are those calculated on adjusted prices (the DB table), the MA lines are recomputed on raw prices.")
    with st.expander("📋 Signal log"):
        log = g[g.signal != "Hold"][["date", "signal", "adj_close", "ma20", "ma50"]].copy()
        log["date"] = log.date.dt.date
        table(log.round(2))


def page_compare():
    st.markdown('<div class="section">Compare stocks — returns, risk and co-movement</div>', unsafe_allow_html=True)
    pick = st.multiselect("Stocks", STOCKS, default=STOCKS, key="cmp_pick")
    if len(pick) < 2:
        st.info("Pick two or more stocks."); return
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**Risk vs return** (bubble size = avg daily turnover)")
        st_ = stats[stats.stock.isin(pick)]
        fig = px.scatter(st_, x="volatility", y="cagr", size="avg_turnover_cr", color="stock", text="stock",
                         color_discrete_map=COLORS, size_max=55,
                         labels={"volatility": "Annualised volatility %", "cagr": "CAGR %"})
        fig.update_traces(textposition="top center")
        fig.update_layout(hovermode="closest")
        show(style(fig, 430, legend=False))
    with c2:
        st.markdown("**Correlation of daily returns**")
        rets = A.daily_returns(df, PC)[pick].dropna()
        corr = rets.corr()
        fig = px.imshow(corr, text_auto=".2f", color_continuous_scale="RdBu_r", zmin=-1, zmax=1, aspect="auto")
        fig.update_layout(hovermode="closest")
        show(style(fig, 430, legend=False))
    st.markdown("**Calendar-year returns** (2015 from 1-Jan, 2018 only to 31-Jul)")
    y = df[df.stock.isin(pick)].copy(); y["year"] = y.date.dt.year
    yr = y.sort_values("date").groupby(["stock", "year"])[PC].agg(["first", "last"]).reset_index()
    yr["ret"] = 100 * (yr["last"] / yr["first"] - 1)
    fig = px.bar(yr, x="year", y="ret", color="stock", barmode="group", color_discrete_map=COLORS,
                 labels={"ret": "Return in year %", "year": ""})
    fig.update_layout(hovermode="closest")
    show(style(fig, 400))
    st.markdown("**Underwater chart** — how far below its previous peak each stock was")
    fig = go.Figure()
    for s in pick:
        p = df[df.stock == s].set_index("date")[PC]
        fig.add_trace(go.Scatter(x=p.index, y=100 * (p / p.cummax() - 1), name=s, line=dict(color=COLORS.get(s), width=1.8)))
    fig.update_yaxes(title="Drawdown %")
    show(style(fig, 380))
    st.markdown("**Full statistics**")
    ss = stats[stats.stock.isin(pick)].round(2).rename(columns={
        "total_return": "Total %", "cagr": "CAGR %", "volatility": "Vol %", "max_drawdown": "Max DD %",
        "best_day": "Best day %", "worst_day": "Worst day %", "avg_turnover_cr": "Turnover ₹cr/day",
        "avg_delivery": "Delivery %", "return_per_risk": "Return/risk", "first": "First ₹", "last": "Last ₹"})
    table(ss)


def page_signals():
    st.markdown('<div class="section">Golden-cross signals — how many, how reliable, and would they have paid?</div>',
                unsafe_allow_html=True)
    sig = A.signal_summary(df)
    c1, c2 = st.columns([2, 3])
    with c1:
        long = sig.melt(id_vars="stock", value_vars=["Buy", "Sell"], var_name="Signal", value_name="Count")
        fig = px.bar(long, x="stock", y="Count", color="Signal", barmode="group",
                     color_discrete_map={"Buy": GREEN, "Sell": RED}, text="Count")
        fig.update_layout(hovermode="closest")
        show(style(fig, 360))
    with c2:
        wh = task_df(N, 19)
        wh.columns = ["Stock", "Signal pairs", "Whipsaws <30d", "Whipsaw %", "Shortest gap (days)"]
        st.markdown("**Whipsaws** — consecutive signals fewer than 30 days apart (SQL task 19)")
        table(wh, column_config={"Whipsaw %": st.column_config.ProgressColumn(format="%.1f", min_value=0, max_value=100)})

    st.markdown('<div class="section">Backtest: follow every signal vs just holding</div>', unsafe_allow_html=True)
    s = st.selectbox("Stock", STOCKS, key="bt_stock")
    g = df[df.stock == s]
    eq, pos = A.strategy_equity(g)
    bh = 100 * g.set_index("date")["adj_close"] / g["adj_close"].iloc[0]
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=bh.index, y=bh.values, name="Buy & hold", line=dict(color="#94a3b8", width=2)))
    fig.add_trace(go.Scatter(x=eq.index, y=eq.values, name="Golden-cross strategy", line=dict(color=COLORS.get(s), width=2.6)))
    # shade the periods we're invested
    inv = pd.Series(pos, index=g.date.values)
    start = None
    for d, v in inv.items():
        if v == 1 and start is None:
            start = d
        if v == 0 and start is not None:
            fig.add_vrect(x0=start, x1=d, fillcolor="rgba(34,197,94,.07)", line_width=0); start = None
    if start is not None:
        fig.add_vrect(x0=start, x1=inv.index[-1], fillcolor="rgba(34,197,94,.07)", line_width=0)
    show(style(fig, 440))
    st.caption("Green shading = periods the strategy was invested. Trades execute on the day AFTER the signal (no look-ahead). "
               "No brokerage, taxes or dividends.")
    m = st.columns(3)
    m[0].markdown(kpi("Strategy", f"{eq.iloc[-1] - 100:+.1f}%", "total return", COLORS.get(s)), unsafe_allow_html=True)
    m[1].markdown(kpi("Buy & hold", f"{bh.iloc[-1] - 100:+.1f}%", "total return", "#94a3b8"), unsafe_allow_html=True)
    m[2].markdown(kpi("Time invested", f"{100 * np.mean(pos):.0f}%", "of trading days", INDIGO), unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    summ = task_df(N, 21)
    with c1:
        st.markdown("**Backtest summary** (SQL task 21)")
        table(summ)
    with c2:
        trades = pd.read_sql("SELECT * FROM trades WHERE stock = ? ORDER BY buy_date", get_base()[0], params=(s,))
        st.markdown(f"**{s}: every completed trade** (SQL task 20)")
        if len(trades):
            trades["result"] = np.where(trades["return_pct"] > 0, "Win", "Loss")
            fig = px.bar(trades, x="buy_date", y="return_pct", color="result",
                         color_discrete_map={"Win": GREEN, "Loss": RED}, labels={"return_pct": "Return %", "buy_date": "Buy date"})
            fig.update_layout(showlegend=False, hovermode="closest")
            show(style(fig, 260, legend=False))
    if len(trades):
        table(trades)


def page_trap():
    st.markdown('<div class="section">🪤 The data trap — two "crashes" that never happened</div>', unsafe_allow_html=True)
    if not all(t in TABLES for t in T.EVENTS):
        st.warning("TCS and Infosys files are needed for this page."); return
    st.markdown("""<div class="callout warn">A <b>1:1 bonus issue</b> gives every shareholder one extra share for each they own.
    The number of shares doubles so the price <b>halves overnight</b> — but nobody lost anything.
    Treat the raw prices naïvely and you get a fake −50% day, a wrong total return, and fake Buy/Sell signals.</div>""",
                unsafe_allow_html=True)
    st.markdown("**Step 1 — spot it: worst day per stock (SQL task 12)**")
    w = task_df(N, 12); table(w)
    s = st.radio("Inspect", ["TCS", "Infosys"], horizontal=True)
    ev = EVENT_BY_STOCK[s]
    g = df[df.stock == s]
    c1, c2 = st.columns(2)
    for col, ttl, y, color in ((c1, f"{s} — raw close", "close", RED), (c2, f"{s} — adjusted close", "adj_close", GREEN)):
        fig = go.Figure(go.Scatter(x=g.date, y=g[y], line=dict(color=color, width=2), name=ttl))
        fig.add_shape(type="line", x0=ev, x1=ev, y0=0, y1=1, xref="x", yref="paper", line=dict(color="#fb923c", dash="dash"))
        fig.add_annotation(x=ev, y=1, xref="x", yref="paper", text=f"Bonus {ev}", showarrow=False, yanchor="bottom",
                           font=dict(color="#fb923c"))
        fig.update_layout(title=ttl)
        with col:
            show(style(fig, 360, legend=False))
    st.markdown("**Step 2 — the damage on returns (raw → fixed)**")
    raw = task_df(N, 11).set_index("stock"); adj = task_df(N, 18).set_index("stock")
    cmp_ = pd.DataFrame({"Raw %": raw["pct_change"], "Adjusted %": adj["adj_pct_change"]}).reset_index()
    cmp_["Changed?"] = np.where((cmp_["Raw %"] - cmp_["Adjusted %"]).abs() > 0.05, "⚠️ distorted", "✓ fine")
    lc, rc = st.columns([2, 3])
    with lc:
        table(cmp_.rename(columns={"stock": "Stock"}))
    with rc:
        mm = cmp_.melt(id_vars="stock", value_vars=["Raw %", "Adjusted %"], var_name="Version", value_name="pct")
        fig = px.bar(mm, x="stock", y="pct", color="Version", barmode="group",
                     color_discrete_map={"Raw %": RED, "Adjusted %": GREEN})
        fig.update_layout(hovermode="closest")
        show(style(fig, 330))
    st.markdown("**Step 3 — the damage on signals (SQL tasks 16 & 17)**")
    c1, c2 = st.columns([3, 2])
    with c1:
        table(task_df(N, 16))
    with c2:
        table(task_df(N, 17))
    st.markdown("""<div class="callout ok"><b>Lesson:</b> always scan for impossible one-day moves before computing returns or
    indicators. Moving averages <i>smear</i> a price cliff across 20–50 days, so even signals far from the event date can be wrong.</div>""",
                unsafe_allow_html=True)

    st.markdown("**What the course deck got right and wrong**")
    deck = pd.DataFrame([
        ("Eicher Motors", "+82.5%", "+82.6%", "Rounding (82.57 → 82.6)"),
        ("TVS Motors", "+86.9%", "+86.9%", "✓ matches"),
        ("Hero Motocorp", "+6%", "+6.0%", "✓ matches"),
        ("TCS", "−23.8%", "+52.4%", "Raw price cliff. Deck also lists a start price (2454.1) that is Bajaj's, not TCS's (2548.20 raw / 1274.10 adjusted)"),
        ("Infosys", "−3%", "+38.2%", "Raw price cliff; raw figure is actually −30.9%, so the deck's '−3%' is also a typo"),
        ("TCS trend", "Down (Sell, 05-Jun-2018)", "Up (Buy, 20-Apr-2018)", "The Sell was created by the bonus cliff"),
        ("TCS signals", "12 Buy / 13 Sell", "12 Buy / 12 Sell", "One fake Sell removed"),
        ("Infosys signals", "9 Buy / 9 Sell", "10 Buy / 10 Sell", "Cliff hid real crossings"),
    ], columns=["Item", "Course deck", "Verified (adjusted)", "Why"])
    table(deck)


# ---- SQL playground ------------------------------------------------------------------------
BLOCKED = re.compile(r"\b(attach|detach|pragma|load_extension|vacuum)\b", re.I)
MAXROWS = 5000


def split_statements(sql):
    out, buf = [], ""
    for part in sql.split(";"):
        buf += part + ";"
        if sqlite3.complete_statement(buf):
            if buf.replace(";", "").strip():
                out.append(buf)
            buf = ""
    return out


def run_sql(con, sql):
    """Run a multi-statement script; return (df of last result set or None, message)."""
    if BLOCKED.search(sql):
        raise ValueError("ATTACH / DETACH / PRAGMA / VACUUM / load_extension are disabled in the playground.")
    stmts = split_statements(sql)
    if not stmts:
        raise ValueError("Nothing to run — write a query first.")
    result, n_changed = None, 0
    for stmt in stmts:
        cur = con.execute(stmt)
        if cur.description:
            rows = cur.fetchmany(MAXROWS + 1)
            result = pd.DataFrame(rows[:MAXROWS], columns=[d[0] for d in cur.description])
            result.attrs["truncated"] = len(rows) > MAXROWS
        else:
            n_changed += 1
    con.commit()
    msg = f"{len(stmts)} statement(s) executed" + (f" · {n_changed} changed the database" if n_changed else "")
    return result, msg


def _presets(tables):
    p = {"✏️ Blank": "SELECT * FROM tcs LIMIT 10;"}
    for t in T.build_tasks(tables, A_focus(tables)):
        p[f"Task {t['id']:>2} · {t['title']}"] = t["sql"]
    p["⭐ Daily returns (TCS, adjusted)"] = (
        "SELECT date, adj_close,\n       ROUND(100.0 * (adj_close / LAG(adj_close) OVER (ORDER BY date) - 1), 2) AS daily_return_pct\n"
        "FROM adj_prices WHERE stock = 'TCS'\nORDER BY date DESC\nLIMIT 30;")
    p["⭐ Rolling 20-day high (Infosys)"] = (
        "SELECT date, adj_close,\n       MAX(adj_close) OVER (ORDER BY date ROWS BETWEEN 19 PRECEDING AND CURRENT ROW) AS high_20d\n"
        "FROM adj_prices WHERE stock = 'Infosys'\nORDER BY date;")
    p["⭐ Every Buy/Sell signal (adjusted)"] = (
        "SELECT stock, date, `signal`, ROUND(close_price, 2) AS price\nFROM adj_signals\nWHERE `signal` <> 'Hold'\nORDER BY stock, date;")
    return p


def page_playground():
    st.markdown('<div class="section">🧪 Live SQL playground — a real SQLite database in your session</div>',
                unsafe_allow_html=True)
    con = session_con()
    presets = _presets(TABLES)
    if "sql_text" not in st.session_state:
        st.session_state.sql_text = presets["⭐ Every Buy/Sell signal (adjusted)"]

    def load_preset():
        st.session_state.sql_text = presets[st.session_state.preset_pick]

    left, right = st.columns([3, 1.4])
    with right:
        st.selectbox("Load a query", list(presets), key="preset_pick", on_change=load_preset,
                     help="Every task from the guide plus a few starters.")
        with st.expander("🗂️ Schema", expanded=True):
            names = [r[0] for r in con.execute(
                "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name").fetchall()]
            t_sel = st.selectbox("Table", names, key="schema_tbl")
            info = con.execute(f'PRAGMA table_info("{t_sel}")').fetchall()
            table(pd.DataFrame([(r[1], r[2]) for r in info], columns=["column", "type"]))
            n = con.execute(f'SELECT COUNT(*) FROM "{t_sel}"').fetchone()[0]
            st.caption(f"{n:,} rows")
        st.caption("Dates are ISO text (YYYY-MM-DD). `signal` needs backticks. Window functions are supported.")
        if st.button("↺ Reset database"):
            st.session_state.con = A.clone(get_base()[0]); st.session_state.pop("last", None); st.rerun()
    with left:
        st.text_area("SQL", key="sql_text", height=330, label_visibility="collapsed",
                     help="Multiple statements allowed — the last SELECT is displayed.")
        b1, b2 = st.columns([1, 5])
        run = b1.button("▶ Run", type="primary")
        b2.caption("Tip: click outside the editor (or press Ctrl+Enter) to commit your text, then Run.")
        if run:
            t0 = time.time()
            try:
                res, msg = run_sql(con, st.session_state.sql_text)
                st.session_state.last = dict(df=res, msg=msg, secs=time.time() - t0, err=None)
                st.session_state.setdefault("history", []).insert(0, st.session_state.sql_text)
            except Exception as e:
                st.session_state.last = dict(df=None, msg="", secs=0, err=str(e))
        last = st.session_state.get("last")
        if last:
            if last["err"]:
                st.error(f"SQL error: {last['err']}")
            else:
                res = last["df"]
                st.success(f"{last['msg']} · {last['secs'] * 1000:.0f} ms" + (f" · {len(res):,} rows × {res.shape[1]} cols" if res is not None else ""))
                if res is not None:
                    if res.attrs.get("truncated"):
                        st.warning(f"Showing the first {MAXROWS:,} rows.")
                    table(res)
                    st.download_button("⬇ Download result (CSV)", res.to_csv(index=False).encode(), "query_result.csv", "text/csv")
                    with st.expander("📊 Chart this result"):
                        num = res.select_dtypes("number").columns.tolist()
                        if not num:
                            st.info("No numeric columns to plot.")
                        else:
                            cc = st.columns(4)
                            kind = cc[0].selectbox("Type", ["Line", "Bar", "Scatter"])
                            xcol = cc[1].selectbox("X", res.columns.tolist())
                            ycols = cc[2].multiselect("Y", num, default=num[:1])
                            cat = cc[3].selectbox("Colour by", ["—"] + [c for c in res.columns if c not in num])
                            if ycols:
                                kw = dict(x=xcol, y=ycols if len(ycols) > 1 else ycols[0])
                                if cat != "—":
                                    kw["color"] = cat
                                fn = {"Line": px.line, "Bar": px.bar, "Scatter": px.scatter}[kind]
                                fig = fn(res, **kw)
                                fig.update_layout(hovermode="closest")
                                show(style(fig, 420))
        if st.session_state.get("history"):
            with st.expander(f"🕘 History ({len(st.session_state.history)})"):
                for i, q in enumerate(st.session_state.history[:8]):
                    st.code(q, language="sql")


# ---- Task walkthrough ----------------------------------------------------------------------
DECK = {"Eicher Motors": (6, 7), "Bajaj Auto": (12, 11), "TCS": (12, 13), "TVS Motors": (8, 8),
        "Hero Motocorp": (9, 9), "Infosys": (9, 9)}


def check_task(tid, res, focus):
    """Checkpoints from the student guide, verified against our own output."""
    out = []
    ok = lambda c, t: out.append(("✅ " if c else "❌ ") + t)
    try:
        if tid == 1:
            ok(res.iloc[0, 0] == 889, "889 trading days"); ok(res.iloc[0, 1] == "2015-01-01" and res.iloc[0, 2] == "2018-07-31", "2015-01-01 → 2018-07-31")
        elif tid == 2:
            ok(len(res) == 5 and res.close_price.max() > 32000, "5 rows, top close above ₹32,000"); ok(res.date.str[:7].nunique() == 1, "all five in the same month (Sept 2017)")
        elif tid == 3:
            ok(len(res) == 4, "4 rows (2015-2018)"); ok(float(res.loc[res.year == "2016", "avg_close"].iloc[0]) == 2419.00, "2016 average is exactly 2419.00")
        elif tid == 4:
            ok(len(res) == len(TABLES), f"{len(TABLES)} rows — one per stock"); ok(res.date.nunique() == 2, "only 2 distinct dates (exchange reporting gap, not the companies)")
        elif tid == 8:
            ok(res.days.sum() == 889, "counts add up to 889")
            d = dict(zip(res.signal, res.days)); ok(abs(d.get("Buy", 0) - d.get("Sell", 0)) <= 1, "Buy and Sell differ by at most one")
            if focus == "bajaj_auto":
                ok((d.get("Buy"), d.get("Sell")) == DECK["Bajaj Auto"], "matches the deck: 12 Buy / 11 Sell")
        elif tid == 10:
            good = all(DECK[r.stock] == (r.buys, r.sells) for r in res.itertuples())
            ok(good, "buy/sell counts match the course deck for every stock")
            if len(res) == 6:
                ok(res.buys.sum() == 56 and res.sells.sum() == 57, "56 Buys and 57 Sells in total")
        elif tid == 11:
            ok(res.iloc[0]["stock"] == "TVS Motors" and res.iloc[0]["pct_change"] == 86.9, "TVS Motors tops the list at 86.9%")
            ok((res["pct_change"] < 0).sum() == 2, "two stocks come out negative (TCS & Infosys — the trap!)")
        elif tid == 12:
            ok(int((res.pct_move < -40).sum()) == 2, "two rows are wildly worse than the rest (≈ −50%)")
        elif tid == 13:
            ok(len(res) == 2 and (res.adjusted_pct_change > 0).all(), "both stocks are actually UP after adjustment")
    except Exception as e:
        out.append(f"⚠️ check could not run: {e}")
    return out


def page_tasks():
    st.markdown('<div class="section">📚 Task walkthrough — every query from the guide, live</div>', unsafe_allow_html=True)
    focus = A_focus(TABLES)
    if focus != "bajaj_auto":
        st.warning(f"Bajaj Auto isn't loaded, so single-stock tasks (1, 5, 7, 8, 9) run on **{T.DISPLAY[focus]}** instead. "
                   "Upload Bajaj_Auto.csv in the sidebar to switch.")
    tasks = T.build_tasks(TABLES, focus)
    parts = list(dict.fromkeys(t["part"] for t in tasks))
    c = st.columns([1, 3])
    part = c[0].selectbox("Part", parts)
    sub = [t for t in tasks if t["part"] == part]
    label = c[1].selectbox("Task", [f"{t['id']}. {t['title']}" for t in sub])
    t = next(x for x in sub if f"{x['id']}. {x['title']}" == label)
    st.markdown(f"**Goal.** {t['goal']}")
    st.code(t["sql"], language="sql")
    if st.button("▶ Run this task", type="primary", key=f"run_{t['id']}"):
        con = session_con()
        try:
            res, msg = run_sql(con, t["sql"])
            if t["creates"]:
                st.success(msg + " — table created; preview below")
                res = pd.read_sql(t["show"], con)
            else:
                st.success(msg)
            st.caption(f"{len(res):,} rows × {res.shape[1]} columns")
            table(res.head(500))
            if not t["creates"]:
                st.markdown("**Check yourself**")
                for line in check_task(t["id"], res, focus):
                    st.markdown(line)
            else:
                chk = []
                if t["id"] == 5 and focus == "bajaj_auto":
                    r = res[res.ma20.notna()].iloc[0]
                    chk.append(("First MA20 on 2015-01-29 = 2415.53", (r.date, r.ma20) == ("2015-01-29", 2415.53)))
                    r = res[res.ma50.notna()].iloc[0]
                    chk.append(("First MA50 on 2015-03-13 = 2283.80", (r.date, r.ma50) == ("2015-03-13", 2283.80)))
                if t["id"] == 6:
                    chk.append((f"{len(res)} rows, no NULLs", len(res) == 889 and res.isna().sum().sum() == 0))
                if t["id"] == 7 and focus == "bajaj_auto":
                    ch = res[res.signal != "Hold"]
                    chk.append(("First Buy 2015-05-18, first Sell 2015-08-24",
                                (ch[ch.signal == "Buy"].date.iloc[0], ch[ch.signal == "Sell"].date.iloc[0]) == ("2015-05-18", "2015-08-24")))
                if chk:
                    st.markdown("**Check yourself**")
                    for txt, good in chk:
                        st.markdown(("✅ " if good else "❌ ") + txt)
        except Exception as e:
            st.error(f"SQL error: {e}")
    st.info("Want to tweak it? Pick the same task in the **SQL Playground** and edit away.")


def page_downloads():
    st.markdown('<div class="section">📦 Deliverables</div>', unsafe_allow_html=True)
    files = [("SQL analysis (SQLite — runs in the playground)", "sql/stock_analysis.sql", "text/plain"),
             ("SQL analysis (MySQL 8 — submission version)", "sql/stock_analysis_mysql.sql", "text/plain"),
             ("Insights report (PDF)", "Stock_Market_Insights.pdf", "application/pdf")]
    cols = st.columns(3)
    for c, (label, path, mime) in zip(cols, files):
        full = os.path.join(BASE_DIR, path)
        with c:
            st.markdown(kpi(label, os.path.basename(path), "", INDIGO), unsafe_allow_html=True)
            if os.path.exists(full):
                with open(full, "rb") as f:
                    st.download_button("⬇ Download", f.read(), os.path.basename(path), mime, key=f"dl_{path}")
            else:
                st.caption("Not generated yet — run `python make_report.py`.")
    st.markdown("""<div class="callout">The video walkthrough is the third submission item — record your screen while you click through
    <b>Overview → Stock Explorer → Signals & Backtest → The Data Trap → SQL Playground</b> and explain each SQL step.</div>""",
                unsafe_allow_html=True)


{"🏠 Overview": page_overview, "🔎 Stock Explorer": page_explorer, "⚖️ Compare Stocks": page_compare,
 "🚦 Signals & Backtest": page_signals, "🪤 The Data Trap": page_trap, "🧪 SQL Playground": page_playground,
 "📚 Task Walkthrough": page_tasks, "📦 Downloads": page_downloads}[page]()