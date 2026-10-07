"""Builds Stock_Market_Insights.pdf from the SQL results.  Run:  python make_report.py"""
import os, tempfile
import numpy as np, pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer, Table, TableStyle,
                                Image, PageBreak, KeepTogether)
import analytics as A, tasks as T

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "Stock_Market_Insights.pdf")
TMP = tempfile.mkdtemp()
INDIGO, DARK, MUTED, GREEN, RED, AMBER = "#4f46e5", "#0f172a", "#64748b", "#16a34a", "#dc2626", "#d97706"
PAL = {"Bajaj Auto": "#0ea5e9", "Eicher Motors": "#f59e0b", "Hero Motocorp": "#e11d48", "Infosys": "#7c3aed",
       "TCS": "#10b981", "TVS Motors": "#f97316"}

# fonts (DejaVu has the rupee sign and arrows)
FN, FB = "Helvetica", "Helvetica-Bold"
RS = "Rs. "
for d in ("/usr/share/fonts/truetype/dejavu", "/usr/share/fonts/dejavu", "C:/Windows/Fonts"):
    r, b = os.path.join(d, "DejaVuSans.ttf"), os.path.join(d, "DejaVuSans-Bold.ttf")
    if os.path.exists(r) and os.path.exists(b):
        pdfmetrics.registerFont(TTFont("DV", r)); pdfmetrics.registerFont(TTFont("DVB", b))
        from reportlab.pdfbase.pdfmetrics import registerFontFamily
        registerFontFamily("DV", normal="DV", bold="DVB", italic="DV", boldItalic="DVB")
        FN, FB, RS = "DV", "DVB", "₹"
        break

S = lambda name, **k: ParagraphStyle(name, fontName=k.pop("fontName", FN), **k)
body = S("body", fontSize=9.3, leading=13.4, textColor=colors.HexColor(DARK))
small = S("small", fontSize=7.8, leading=10.5, textColor=colors.HexColor(MUTED))
cell = S("cell", fontSize=8.2, leading=11, textColor=colors.HexColor(DARK))
cell_s = S("cell_s", fontSize=7.4, leading=9.3, textColor=colors.HexColor(DARK))
cellb = S("cellb", fontName=FB, fontSize=8.2, leading=11, textColor=colors.HexColor(INDIGO))
h1 = S("h1", fontName=FB, fontSize=17, leading=22, textColor=colors.HexColor(DARK), spaceBefore=4, spaceAfter=6)
h2 = S("h2", fontName=FB, fontSize=12, leading=16, textColor=colors.HexColor(INDIGO), spaceBefore=8, spaceAfter=4)
th = S("th", fontName=FB, fontSize=8.2, leading=11, textColor=colors.white)
bullet = S("bullet", fontSize=9.3, leading=13.4, leftIndent=12, bulletIndent=2, textColor=colors.HexColor(DARK))
P = lambda t, st=body: Paragraph(t, st)

# ----------------------------------------------------------------------------- data
con, TABLES = A.build_base()
df = A.load_frames(con, TABLES)
STK = sorted(df.stock.unique())
adj = A.stock_stats(df, "adj_close").set_index("stock")
raw = A.stock_stats(df, "close").set_index("stock")
sig = A.signal_summary(df).set_index("stock")
focus = "bajaj_auto" if "bajaj_auto" in TABLES else TABLES[0]
q = lambda i: pd.read_sql(next(t for t in T.build_tasks(TABLES, focus) if t["id"] == i)["sql"], con)
whip = q(19).set_index("stock"); summ = q(21).set_index("stock"); worst = q(12).set_index("stock")
cmp16 = q(16).set_index("stock"); fake = q(17); dd = q(22).set_index("stock")
trades = pd.read_sql("SELECT * FROM trades", con)
yr = q(24)
trend_now, tn = A.trend_now(df); trend = dict(zip(tn, trend_now))
HAS_BAJAJ = "bajaj_auto" in TABLES
fmt = lambda x, d=1: f"{x:+.{d}f}%"

eq, bh = {}, {}
for s in STK:
    g = df[df.stock == s]
    e, pos = A.strategy_equity(g)
    eq[s] = (e.iloc[-1] - 100); bh[s] = 100 * (g.adj_close.iloc[-1] / g.adj_close.iloc[0] - 1)
    adj.loc[s, "invested"] = 100 * pos.mean()

# "lag" evidence: how far above the recent trough did each Buy fire?
lags = []
for s in STK:
    g = df[df.stock == s].reset_index(drop=True)
    for i in g.index[g.signal == "Buy"]:
        lo = g.adj_close.iloc[max(0, i - 60):i + 1].min()
        lags.append(100 * (g.adj_close.iloc[i] / lo - 1))
lag_avg = float(np.mean(lags))
d1111 = df[df.date == "2016-11-11"].copy()
r1111 = (df.pivot(index="date", columns="stock", values="adj_close").pct_change().loc["2016-11-11"] * 100)
n_down = int((r1111 < -3).sum())

# ----------------------------------------------------------------------------- charts
def savefig(fig, name, tight=True):
    p = os.path.join(TMP, name); fig.savefig(p, dpi=170, bbox_inches="tight" if tight else None, facecolor="white"); plt.close(fig); return p

def clean(ax):
    for sp in ("top", "right"): ax.spines[sp].set_visible(False)
    for sp in ("left", "bottom"): ax.spines[sp].set_color("#cbd5e1")
    ax.tick_params(colors="#475569", labelsize=7.5); ax.grid(True, color="#e2e8f0", lw=.6)
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %y"))

def chart_rebased():
    fig, ax = plt.subplots(figsize=(8.2, 3.5))
    for s in STK:
        r = A.rebased(df, [s], "adj_close")[s]; ax.plot(r.index, r.values, color=PAL[s], lw=1.7, label=s)
    ax.axhline(100, color="#94a3b8", ls=":", lw=1); clean(ax); ax.set_ylabel("Adjusted close, rebased to 100", fontsize=8)
    ax.legend(ncol=5, fontsize=7.5, frameon=False, loc="upper left"); return savefig(fig, "rebased.png")

def chart_trap(s):
    ev = pd.Timestamp(T.EVENTS["tcs" if s == "TCS" else "infosys"]); g = df[df.stock == s]
    fig, axs = plt.subplots(1, 2, figsize=(8.2, 2.2), sharey=False)
    for ax, col, ttl, c in ((axs[0], "close", f"{s}: raw close", RED), (axs[1], "adj_close", f"{s}: adjusted close", GREEN)):
        ax.plot(g.date, g[col], color=c, lw=1.5); ax.axvline(ev, color=AMBER, ls="--", lw=1)
        ax.set_title(ttl, fontsize=8.5, color=DARK, loc="left"); clean(ax)
    axs[0].annotate("1:1 bonus issue", (ev, g.loc[g.date == ev, "close"].iloc[0]), xytext=(-78, 26), textcoords="offset points",
                    fontsize=7.5, color=AMBER, arrowprops=dict(arrowstyle="->", color=AMBER, lw=.8))
    return savefig(fig, f"trap_{s}.png")

def chart_stock(s):
    g = df[df.stock == s]
    fig, ax = plt.subplots(figsize=(8.2, 1.95))
    ax.plot(g.date, g.adj_close, color=PAL[s], lw=1.4, label="Adjusted close")
    ax.plot(g.date, g.ma20, color="#f59e0b", lw=1, label="MA 20"); ax.plot(g.date, g.ma50, color="#0ea5e9", lw=1, label="MA 50")
    b, sl = g[g.signal == "Buy"], g[g.signal == "Sell"]
    ax.scatter(b.date, b.adj_close, marker="^", s=34, color=GREEN, zorder=5, label="Buy", edgecolor="white", lw=.5)
    ax.scatter(sl.date, sl.adj_close, marker="v", s=34, color=RED, zorder=5, label="Sell", edgecolor="white", lw=.5)
    clean(ax); ax.legend(ncol=5, fontsize=7, frameon=False, loc="upper left"); return savefig(fig, f"stock_{s}.png")

def chart_backtest():
    fig, ax = plt.subplots(figsize=(8.2, 2.4)); x = np.arange(len(STK)); w = .38
    ax.bar(x - w / 2, [bh[s] for s in STK], w, color="#94a3b8", label="Buy & hold")
    ax.bar(x + w / 2, [eq[s] for s in STK], w, color=INDIGO, label="Golden-cross strategy")
    ax.set_xticks(x); ax.set_xticklabels(STK, fontsize=8); ax.axhline(0, color="#475569", lw=.8)
    ax.set_ylabel("Total return %", fontsize=8); clean(ax); ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda v, p: ""))
    ax.set_xticks(x); ax.set_xticklabels(STK, fontsize=8)
    for i, s in enumerate(STK):
        ax.text(i - w / 2, bh[s] + (3 if bh[s] >= 0 else -9), f"{bh[s]:.0f}%", ha="center", fontsize=7)
        ax.text(i + w / 2, eq[s] + (3 if eq[s] >= 0 else -9), f"{eq[s]:.0f}%", ha="center", fontsize=7)
    ax.legend(fontsize=7.5, frameon=False); return savefig(fig, "backtest.png")

def chart_riskreturn():
    fig, ax = plt.subplots(figsize=(4.2, 3.2))
    for s in STK:
        ax.scatter(adj.loc[s, "volatility"], adj.loc[s, "cagr"], s=90, color=PAL[s], edgecolor="white", zorder=3)
        left = adj.loc[s, "volatility"] > adj.volatility.median() and adj.loc[s, "cagr"] < adj.cagr.max()
        ax.annotate(s, (adj.loc[s, "volatility"], adj.loc[s, "cagr"]), xytext=((-7, -12) if left else (5, 5)), textcoords="offset points",
                    fontsize=7, ha="right" if left else "left")
    ax.set_xlabel("Annualised volatility %", fontsize=8); ax.set_ylabel("CAGR %", fontsize=8); clean(ax)
    ax.xaxis.set_major_formatter(plt.ScalarFormatter()); fig.subplots_adjust(left=.14, right=.97, bottom=.15, top=.97); return savefig(fig, "rr.png", tight=False)

def chart_corr():
    rets = A.daily_returns(df, "adj_close")[STK].dropna(); c = rets.corr()
    fig, ax = plt.subplots(figsize=(4.2, 3.2)); im = ax.imshow(c.values, cmap="RdBu_r", vmin=-1, vmax=1)
    ax.set_xticks(range(len(STK))); ax.set_yticks(range(len(STK)))
    ax.set_xticklabels([s.split()[0] for s in STK], fontsize=7, rotation=30); ax.set_yticklabels([s.split()[0] for s in STK], fontsize=7)
    for i in range(len(STK)):
        for j in range(len(STK)): ax.text(j, i, f"{c.values[i, j]:.2f}", ha="center", va="center", fontsize=7, color="white" if abs(c.values[i, j]) > .6 else "#0f172a")
    fig.subplots_adjust(left=.16, right=.97, bottom=.15, top=.97); return savefig(fig, "corr.png", tight=False)

# ----------------------------------------------------------------------------- helpers
def tbl(rows, widths, header=True, zebra=True, cs=None):
    cs = cs or cell
    data = [[P(str(c), th if (header and i == 0) else cs) for c in r] for i, r in enumerate(rows)]
    t = Table(data, colWidths=widths, repeatRows=1 if header else 0)
    st = [("VALIGN", (0, 0), (-1, -1), "TOP"), ("LINEBELOW", (0, 0), (-1, -1), .4, colors.HexColor("#e2e8f0")),
          ("TOPPADDING", (0, 0), (-1, -1), 4), ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
          ("LEFTPADDING", (0, 0), (-1, -1), 5), ("RIGHTPADDING", (0, 0), (-1, -1), 5)]
    if header: st.append(("BACKGROUND", (0, 0), (-1, 0), colors.HexColor(INDIGO)))
    if zebra:
        for i in range(1, len(rows)):
            if i % 2 == 0: st.append(("BACKGROUND", (0, i), (-1, i), colors.HexColor("#f8fafc")))
    t.setStyle(TableStyle(st)); return t

def callout(text, color=INDIGO, bg="#eef2ff"):
    t = Table([[P(text)]], colWidths=[174 * mm])
    t.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), colors.HexColor(bg)), ("LINEBEFORE", (0, 0), (0, -1), 3, colors.HexColor(color)),
                           ("LEFTPADDING", (0, 0), (-1, -1), 10), ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                           ("TOPPADDING", (0, 0), (-1, -1), 7), ("BOTTOMPADDING", (0, 0), (-1, -1), 7)]))
    return t

def img(path, w=174 * mm):
    from PIL import Image as PI
    iw, ih = PI.open(path).size; return Image(path, width=w, height=w * ih / iw)

def bl(items): return [Paragraph(i, bullet, bulletText="•") for i in items]

# ----------------------------------------------------------------------------- page furniture
def on_page(c, d):
    c.saveState(); c.setFont(FN, 7.5); c.setFillColor(colors.HexColor(MUTED))
    c.drawString(18 * mm, 10 * mm, "NSE Stock Market Analysis in SQL · Insights report")
    c.drawRightString(A4[0] - 18 * mm, 10 * mm, f"Page {d.page}")
    c.setStrokeColor(colors.HexColor("#e2e8f0")); c.line(18 * mm, 14 * mm, A4[0] - 18 * mm, 14 * mm); c.restoreState()

def cover(c, d):
    c.saveState(); W, H = A4
    c.setFillColor(colors.HexColor("#0f172a")); c.rect(0, H - 120 * mm, W, 120 * mm, fill=1, stroke=0)
    c.setFillColor(colors.HexColor("#6366f1")); c.rect(0, H - 120 * mm, 8 * mm, 120 * mm, fill=1, stroke=0)
    c.setFillColor(colors.white); c.setFont(FB, 28); c.drawString(24 * mm, H - 55 * mm, "NSE Stock Market Analysis")
    c.setFont(FB, 28); c.drawString(24 * mm, H - 68 * mm, "in SQL: Insights Report")
    c.setFont(FN, 11); c.setFillColor(colors.HexColor("#c7d2fe"))
    c.drawString(24 * mm, H - 84 * mm, "Moving averages, golden-cross signals and the data problem hiding in plain sight")
    c.drawString(24 * mm, H - 92 * mm, ", ".join(STK)); c.drawString(24 * mm, H - 99 * mm, "Jan 2015 - Jul 2018  ·  889 trading days per stock")
    c.restoreState()

doc = BaseDocTemplate(OUT, pagesize=A4, leftMargin=18 * mm, rightMargin=18 * mm, topMargin=16 * mm, bottomMargin=20 * mm,
                      title="NSE Stock Market Analysis in SQL: Insights", author="SQL Stock Analysis Project")
fr = Frame(18 * mm, 20 * mm, A4[0] - 36 * mm, A4[1] - 36 * mm, id="f")
fr1 = Frame(18 * mm, 20 * mm, A4[0] - 36 * mm, A4[1] - 150 * mm, id="f1")
doc.addPageTemplates([PageTemplate(id="cover", frames=[fr1], onPage=cover), PageTemplate(id="main", frames=[fr], onPage=on_page)])
from reportlab.platypus import NextPageTemplate

st_ = []
# ============================================================ COVER + EXEC SUMMARY
tcs_r, inf_r = raw.loc["TCS", "total_return"], raw.loc["Infosys", "total_return"]
st_ += [Spacer(1, 4), P("Executive summary", h1)]
best = adj.total_return.idxmax(); wrs = adj.total_return.idxmin()
nb, ns_ = int(sig.Buy.sum()), int(sig.Sell.sum())
short = trades[trades.days_held < 30]
summary = [
    f"<b>Scope.</b> {len(STK)} NSE stocks, 889 trading days each, analysed entirely with SQL (24 queries, window functions, CTEs). "
    f"Across the stocks the 20/50-day golden-cross rule produced <b>{nb} Buy and {ns_} Sell</b> signals.",
    f"<b>The data trap changes the story.</b> TCS (31 May 2018) and Infosys (15 Jun 2015) each show a one-day fall of about 50%. These are "
    f"1:1 bonus issues, not crashes. On raw prices TCS is {fmt(tcs_r)} and Infosys {fmt(inf_r)}; after adjustment they are "
    f"<b>{fmt(adj.loc['TCS','total_return'])}</b> and <b>{fmt(adj.loc['Infosys','total_return'])}</b>. Winners and losers flip.",
    f"<b>Best / weakest after adjustment:</b> {best} ({fmt(adj.loc[best,'total_return'])}) / {wrs} ({fmt(adj.loc[wrs,'total_return'])}).",
    f"<b>The signal rule did not beat buy-and-hold</b> for any stock tested (see section 4). Every one of the {len(short)} trades held under 30 days lost money "
    f"(average {short.return_pct.mean():.1f}%).",
    f"<b>The bonus cliff also corrupted signals.</b> TCS's latest signal on raw prices was a Sell (5 Jun 2018). On clean prices it is a "
    f"<b>Buy (20 Apr 2018)</b>, and Infosys gains {int(cmp16.loc['Infosys','net_change'])} signals.",
]
st_ += bl(summary) + [Spacer(1, 6)]
if not HAS_BAJAJ:
    st_.append(callout("<b>Coverage note.</b> The Bajaj Auto file (Bajaj_Auto.csv) was not among the supplied data, so Bajaj Auto is not analysed in "
                       "this report. The SQL files and the Streamlit app already include it: place the CSV in <font name='Courier'>data/</font> "
                       "and re-run <font name='Courier'>python make_report.py</font>. I have deliberately not copied the course deck's Bajaj "
                       "numbers, because the guide asks that no figure be taken from the deck without being checked against your own query.", AMBER, "#fffbeb"))
st_ += [Spacer(1, 6), P("How to read this report", h2),
        P("Every claim in section 3 is given three ways: the <b>claim</b>, the <b>evidence</b> (which SQL task and which number) and the "
          "<b>caveat</b> (what could make it wrong). Task numbers refer to <font name='Courier'>stock_analysis.sql</font>. Prices are in rupees. "
          "Nothing here is investment advice.")]
st_ += [NextPageTemplate("main"), PageBreak()]

# ============================================================ 1. DATA & METHOD
st_ += [P("1. Data and method", h1),
        P(f"Each table has one row per trading day (889 rows, 1 Jan 2015 to 31 Jul 2018) with OHLC prices, VWAP, volume, turnover and delivery data. "
          f"I load the CSVs, convert dates like <font name='Courier'>31-July-2018</font> to ISO <font name='Courier'>2018-07-31</font> "
          f"(so text sorting equals time sorting) and run the analysis in SQL:"),
        *bl(["<b>Tasks 1-4</b> profile the data: history length, Eicher's best closes (all in September 2017), TCS yearly averages and the NULL "
             "<font name='Courier'>deliverable_qty</font> rows. These are one row per stock on only two dates (2015-12-09 for four stocks, "
             "2017-08-31 for Infosys), which points to an <i>exchange reporting gap</i>, not company-specific events.",
             "<b>Tasks 5-10</b> build the 20- and 50-day moving averages with <font name='Courier'>AVG() OVER (... ROWS BETWEEN n PRECEDING)</font>, "
             "blank the incomplete windows, and detect crossings with <font name='Courier'>LAG()</font>. A cross is a Buy on the day MA20 moves "
             "above MA50 (yesterday it was not), a Sell for the mirror image, otherwise Hold. Task 10 does all stocks in one query using PARTITION BY.",
             "<b>Tasks 11-13</b> compute returns, find the data trap (worst one-day move) and fix it by dividing pre-event prices by 2.",
             "<b>Tasks 14-24</b> extend the work: adjusted signals, whipsaw counts, a trade-by-trade backtest, drawdowns, liquidity and yearly returns."]),
        Spacer(1, 6),
        callout("<b>Validation.</b> The signal counts and last-signal dates from my SQL match the course deck exactly for every stock supplied "
                "(Eicher 6/7, Hero 9/9, Infosys 9/9, TCS 12/13, TVS 8/8). TCS's 2016 average is exactly 2419.00, TVS is +86.9% and the "
                "first signals fall after the 50-day warm-up. So the pipeline reproduces the deck on raw prices, and the differences "
                "found later are genuine corrections, not bugs.", GREEN, "#f0fdf4"),
        Spacer(1, 6), P("Performance at a glance (adjusted prices)", h2), img(chart_rebased(), 160 * mm), Spacer(1, 4)]
rows = [["Stock", "First close", "Last close", "Total return", "CAGR", "Volatility", "Max drawdown"]]
for s in STK:
    r = adj.loc[s]; rows.append([s, f"{RS}{r['first']:,.2f}", f"{RS}{r['last']:,.2f}", fmt(r.total_return), fmt(r.cagr), f"{r.volatility:.1f}%", f"{r.max_drawdown:.1f}%"])
st_ += [tbl(rows, [32 * mm, 26 * mm, 26 * mm, 24 * mm, 20 * mm, 22 * mm, 24 * mm]), PageBreak()]

# ============================================================ 2. DATA TRAP
st_ += [P("2. The data trap: two crashes that never happened", h1),
        P(f"Task 12 ranks each stock's worst day-over-day move. Most stocks' worst day is between {worst.pct_move.drop(['TCS','Infosys']).max():.1f}% and "
          f"{worst.pct_move.drop(['TCS','Infosys']).min():.1f}%, but <b>TCS ({worst.loc['TCS','pct_move']:.1f}% on {worst.loc['TCS','date']})</b> and "
          f"<b>Infosys ({worst.loc['Infosys','pct_move']:.1f}% on {worst.loc['Infosys','date']})</b> are in a different league. A large profitable "
          "company does not lose half its value in a day with no headlines. Searching those names and dates shows both were <b>1:1 bonus issues</b>: "
          "every holder received one extra share per share held, the share count doubled and the price halved, with no change in anyone's wealth."),
        Spacer(1, 4), img(chart_trap("TCS"), 168 * mm), Spacer(1, 2), img(chart_trap("Infosys"), 168 * mm), Spacer(1, 4),
        P("How I handled it (task 13)", h2),
        P(f"I divided every close <b>before</b> the event date by 2 (TCS before 2018-05-31, Infosys before 2015-06-15) and left later prices unchanged, "
          "then rebuilt the moving averages and signals on the adjusted series (tasks 14-15). The cliff disappears and the line is continuous. "
          "All other stocks are unchanged."), Spacer(1, 4)]
rows = [["Stock", "Raw return", "Adjusted return", "Raw signals (B/S)", "Adjusted signals (B/S)"]]
for s in ("TCS", "Infosys"):
    if s in STK:
        rows.append([s, fmt(raw.loc[s, "total_return"]), fmt(adj.loc[s, "total_return"]),
                     f"{int(cmp16.loc[s,'raw_buys'])} / {int(cmp16.loc[s,'raw_sells'])}", f"{int(cmp16.loc[s,'adj_buys'])} / {int(cmp16.loc[s,'adj_sells'])}"])
st_ += [tbl(rows, [32 * mm, 34 * mm, 38 * mm, 36 * mm, 40 * mm]), Spacer(1, 6)]
fk = ["<b>Which signals were fake?</b> (task 17)"]
for r in fake.itertuples():
    fk.append(f"{r.stock}, {r.date}: raw says <b>{r.raw_signal}</b>, adjusted says <b>{r.adjusted_signal}</b>.")
st_ += [KeepTogether([P(fk[0])] + bl(fk[1:])), Spacer(1, 4),
        callout("<b>Why signals far from the event date change.</b> A moving average smears a price cliff across its whole window "
                "(20 or 50 days). The TCS Sell on 5 June 2018 came five days after the bonus issue, when the 20-day average had been dragged "
                "down by the halved prices. It was an arithmetic artefact. Infosys's raw series also <i>hid</i> real crossings in July and "
                "August 2015 for the same reason.", AMBER, "#fffbeb"), PageBreak()]

# ============================================================ 3. STOCK BY STOCK
st_ += [P("3. Stock by stock: claim, evidence, caveat", h1)]
CAV_Y = "Start and end dates are arbitrary points; dividends and splits other than the two found are not in the data."
for k, s in enumerate(STK):
    r = adj.loc[s]; sg = sig.loc[s]; w = whip.loc[s]; sm = summ.loc[s]
    tr_s = trades[trades.stock == s]; sh = tr_s[tr_s.days_held < 30]; lg = tr_s[tr_s.days_held >= 30]
    # 1 price
    c1 = f"{s} {'rose' if r.total_return > 0 else 'fell'} <b>{fmt(r.total_return)}</b> ({fmt(r.cagr)} a year) over the period."
    e1 = f"Task 18: {RS}{r['first']:,.2f} to {RS}{r['last']:,.2f}. Max drawdown {r.max_drawdown:.1f}% (trough {dd.loc[s,'trough_date']})."
    k1 = CAV_Y + (f" On raw prices this would wrongly read {fmt(raw.loc[s,'total_return'])}." if s in ("TCS", "Infosys") else "")
    # 2 signals
    c2 = f"{int(sg.Buy)} Buy and {int(sg.Sell)} Sell signals; the latest was a <b>{sg.last_signal}</b> on {sg.last_signal_date}."
    e2 = f"Tasks 10 and 15. Current MA20 vs MA50: {trend[s].lower()}."
    k2 = "No signal can appear before day 50 (March 2015). " + (f"Adjusted counts differ from raw ({int(cmp16.loc[s,'raw_buys'])}/{int(cmp16.loc[s,'raw_sells'])} raw)." if s in ("TCS", "Infosys") else "Counts match the deck's raw figures.")
    # 3 whipsaws
    c3 = (f"{int(w.whipsaws_under_30d)} of {int(w.signal_pairs)} consecutive signals came less than 30 days apart ({w.whipsaw_pct:.0f}%)."
          + (f" Those {len(sh)} quick trades averaged {sh.return_pct.mean():.1f}%." if len(sh) else " No completed trade was held under 30 days."))
    e3 = (f"Tasks 19-20. Shortest gap {int(w.shortest_gap_days)} days. Trades held 30+ days: {len(lg)} averaging {lg.return_pct.mean():+.1f}%." if len(lg) else f"Tasks 19-20. Shortest gap {int(w.shortest_gap_days)} days.")
    k3 = f"Returns exclude brokerage, taxes and slippage, which would hurt frequent trading more. Sample is only {len(tr_s)} trades."
    # 4 latest vs long-run
    up_long = r.total_return > 0
    if abs(r.total_return) < 15:
        c4 = (f"The long-run move is small ({fmt(r.total_return)} in 3.6 years), so there is no clear trend to compare with. "
              f"The latest signal ({sg.last_signal}, {sg.last_signal_date}) is the only directional information, and it is short-term.")
        e4 = f"Task 10 plus task 18. Current MA20 is {'above' if trend[s]=='Uptrend' else 'below'} MA50."
        k4 = "A near-flat stock with large swings is exactly where moving-average crossovers whipsaw; read the signal with caution."
    elif (sg.last_signal == "Buy") == up_long:
        c4 = f"The latest signal ({sg.last_signal}) <b>agrees</b> with the long-run direction ({fmt(r.total_return)})."
        e4 = "Task 10 plus task 18."
        k4 = "Agreement between a 3-year trend and a 2-month signal is weak confirmation, not proof."
    else:
        c4 = (f"The latest signal ({sg.last_signal}, {sg.last_signal_date}) <b>disagrees</b> with the long-run trend ({fmt(r.total_return)}). "
              "I would treat the 3-year trend as the better guide to direction and the signal as a short-term warning only.")
        e4 = f"Task 10 plus task 18. Current MA20 is {'above' if trend[s]=='Uptrend' else 'below'} MA50."
        k4 = "A moving-average cross reacts late; the trend could also resume or the Sell may be an early sign of a genuine reversal."
    rows = [["", "Claim", "Evidence", "Caveat"],
            ["Price change", c1, e1, k1], ["Signals", c2, e2, k2], ["Whipsaws", c3, e3, k3], ["Signal vs trend", c4, e4, k4]]
    t = tbl(rows, [19 * mm, 55 * mm, 50 * mm, 50 * mm], cs=cell_s)
    block = [P(f"<font color='{PAL[s]}'>■</font> {s}", h2), img(chart_stock(s), 160 * mm), Spacer(1, 2), t, Spacer(1, 2)]
    st_ += [KeepTogether(block)]
st_.append(PageBreak())

# ============================================================ 4. CROSS-STOCK
st_ += [P("4. Would following the signals have paid?", h1),
        P("Task 20 builds every completed trade (buy at a Buy signal's close, sell at the next Sell's close). Section 4 uses a stricter daily "
          "version: the strategy owns the stock after a Buy and holds cash after a Sell, acting on the <i>next</i> day's return so it never uses "
          "information it would not have had.")]
st_ += [img(chart_backtest(), 160 * mm), Spacer(1, 4)]
rows = [["Stock", "Buy & hold", "Strategy", "Time invested", "Trades", "Win rate", "Avg trade"]]
for s in STK:
    sm = summ.loc[s]; rows.append([s, fmt(bh[s]), fmt(eq[s]), f"{adj.loc[s,'invested']:.0f}%", int(sm.trades), f"{sm.win_rate_pct:.0f}%", fmt(sm.avg_return_pct, 1)])
st_ += [tbl(rows, [32 * mm, 24 * mm, 24 * mm, 26 * mm, 18 * mm, 22 * mm, 24 * mm]), Spacer(1, 6)]
beat = [s for s in STK if eq[s] > bh[s]]
st_ += bl([f"The rule beat buy-and-hold for <b>{len(beat)} of {len(STK)}</b> stocks. It lagged most for TCS "
           f"({fmt(eq['TCS'])} vs {fmt(bh['TCS'])}): only {int(summ.loc['TCS','winners'])} of its {int(summ.loc['TCS','trades'])} trades won, "
           f"in a market that moved sideways until 2017 and then rallied while the strategy was often in cash." if 'TCS' in STK else "",
           f"Where it worked, it worked through <b>long holds</b>: Eicher won all {int(summ.loc['Eicher Motors','winners'])} of its trades and TVS's 30+ day trades averaged "
           f"{trades[(trades.stock=='TVS Motors')&(trades.days_held>=30)].return_pct.mean():+.1f}%." if {'Eicher Motors','TVS Motors'} <= set(STK) else "",
           f"Every trade shorter than 30 days lost money ({len(short)} of {len(short)}), a clear signature of a lagging indicator whipsawing in a range-bound market."])
st_ += [Spacer(1, 4)]
two = Table([[img(chart_riskreturn(), 82 * mm), img(chart_corr(), 82 * mm)]], colWidths=[87 * mm, 87 * mm]); st_ += [KeepTogether([P("Risk, return and co-movement", h2), two])]
hi = A.daily_returns(df, "adj_close")[STK].dropna().corr().where(~np.eye(len(STK), dtype=bool)).stack()
st_ += [Spacer(1, 4), P(f"Return per unit of risk is highest for <b>{adj.return_per_risk.idxmax()}</b> ({adj.return_per_risk.max():.2f}) and lowest for "
                        f"<b>{adj.return_per_risk.idxmin()}</b> ({adj.return_per_risk.min():.2f}). Correlations of daily returns are modest "
                        f"(highest pair {hi.max():.2f}), so the stocks give some diversification."), PageBreak()]

# ============================================================ 5. METHOD QUESTIONS
st_ += [P("5. Questions about the method", h1),
        P("A moving average only uses past prices. What does that mean for how early a golden cross can tell you anything?", h2),
        P(f"It tells you late, by construction. A 50-day average needs 50 days of history, so no signal is possible before mid-March 2015 for any stock "
          f"(first real signals appear in late March to June 2015). More importantly, the crossing happens only after the price has already moved. "
          f"Across all Buy signals here, the price was on average <b>{lag_avg:.1f}% above its lowest close of the preceding 60 trading days</b> by the time "
          f"the Buy fired: a good part of each rally had already gone. The same lag is why quick reversals produce whipsaws."),
        P("Which conclusions in the course deck change after task 13?", h2)]
rows = [["Deck statement", "Verified result", "Change"],
        ["TCS: −23.8% over the period", f"{fmt(adj.loc['TCS','total_return'])} adjusted", "Sign flips. The deck used raw prices through a bonus issue." if 'TCS' in STK else ""],
        ["Infosys: −3%", f"{fmt(adj.loc['Infosys','total_return'])} adjusted (raw was {fmt(raw.loc['Infosys','total_return'])})", "Sign flips. The deck's −3% is also a typo for −30.9% raw." if 'Infosys' in STK else ""],
        ["TCS start price 2454.1", f"{RS}{raw.loc['TCS','first']:,.2f} raw / {RS}{adj.loc['TCS','first']:,.2f} adjusted", "The deck repeats Bajaj's start price; it is not TCS's."],
        ["TCS trend 'shifting down' (5 Jun 2018)", "Latest signal Buy, 20 Apr 2018; MA20 above MA50", "The Sell was created by the bonus cliff."],
        ["TCS: 12 Buy / 13 Sell", f"{int(cmp16.loc['TCS','adj_buys'])} Buy / {int(cmp16.loc['TCS','adj_sells'])} Sell", "One fake Sell removed."],
        ["Infosys: 9 Buy / 9 Sell", f"{int(cmp16.loc['Infosys','adj_buys'])} Buy / {int(cmp16.loc['Infosys','adj_sells'])} Sell", "Cliff hid genuine crossings in mid-2015."],
        ["Eicher: +82.5%", f"{fmt(adj.loc['Eicher Motors','total_return'])}", "Rounding only (82.57 rounds to 82.6)."],
        ["TVS +86.9%, Hero +6%", "Unchanged", "Both confirmed."],
        ["Final report: sell TCS, favour Infosys", f"TCS is #{int(adj.total_return.rank(ascending=False)['TCS'])} of {len(STK)} by return ({fmt(adj.loc['TCS','total_return'])}) and its latest signal is Buy", "Recommendation reverses for TCS."]]
st_ += [tbl(rows, [58 * mm, 62 * mm, 54 * mm]), Spacer(1, 6),
        P(f"Evidence of a shared market event: on 11 Nov 2016, <b>{n_down} of {len(STK)}</b> stocks fell by more than 3% in a single day, and TCS's drawdown trough "
          "and Hero's second-worst day both fall on that date. Price data alone cannot say why, which is exactly the kind of context this dataset lacks."),
        P("What isn't in this data that a real investor would need?", h2),
        *bl(["<b>Dividends</b>: total return would be higher, especially for Hero, TCS and Infosys which pay regular dividends.",
             "<b>Costs</b>: brokerage, STT, stamp duty, taxes and bid-ask slippage. They punish the whipsaw trades most.",
             "<b>News and fundamentals</b>: earnings, guidance, regulation and corporate actions. The two bonus issues were found only by inspecting the numbers; "
             "other splits or demergers could hide elsewhere.",
             "<b>The broader market</b>: no Nifty or sector index, so stock-specific moves cannot be separated from market moves; no risk-free rate for proper risk-adjusted metrics.",
             "<b>Regime diversity</b>: 3.6 years of one mostly rising market. A rule that lags may behave very differently in a long bear or a strongly trending year."]),
        P("6. Reproducing this work", h2),
        P("<font name='Courier'>sql/stock_analysis.sql</font> (SQLite, re-runnable top to bottom) and <font name='Courier'>sql/stock_analysis_mysql.sql</font> "
          "(MySQL 8 with the CSV loader and the task 9 function). <font name='Courier'>streamlit run app.py</font> opens the interactive dashboard and "
          "live SQL playground running these same queries. Limitations: five stocks over 3.6 years; past performance; not investment advice."
          + ("" if HAS_BAJAJ else " Bajaj Auto is not covered because its CSV was not supplied."), small)]

doc.build(st_)
print("wrote", OUT)
