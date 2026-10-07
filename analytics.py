"""Pandas helpers on top of the SQL-built tables (no UI code here, so it is unit-testable)."""
import sqlite3
import numpy as np
import pandas as pd
import db, tasks

TRADING_DAYS = 248  # ~NSE trading days per year


def build_base():
    """In-memory DB: raw tables + every table created by the project's SQL (tasks 5-7, 14, 15, 20)."""
    con = db.build_connection()
    tables = list(db.available_tables())
    con.executescript(tasks.build_script(tables))
    con.commit()
    return con, tables


def clone(con):
    """Private copy of the DB for one user session (so playground edits never leak)."""
    new = sqlite3.connect(":memory:", check_same_thread=False)
    con.backup(new)
    return new


def load_frames(con, tables):
    """One tidy long DataFrame with raw + adjusted prices, MAs, signals and volume info."""
    raw = " UNION ALL ".join(
        f"SELECT '{tasks.DISPLAY[t]}' AS stock, date, open_price AS open, high_price AS high, low_price AS low, "
        f"close_price AS close, no_of_shares AS volume, total_turnover AS turnover, pct_deli_qty AS delivery_pct FROM {t}"
        for t in tables)
    df = pd.read_sql(f"""
        SELECT r.*, a.adj_close, s.ma20, s.ma50, s.`signal`
        FROM ({raw}) r
        JOIN adj_prices a  ON a.stock = r.stock AND a.date = r.date
        JOIN adj_signals s ON s.stock = r.stock AND s.date = r.date
        ORDER BY r.stock, r.date""", con)
    df["date"] = pd.to_datetime(df["date"])
    # adjusted OHLC (same factor as adj_close/close) so candlesticks stay continuous
    f = (df["adj_close"] / df["close"]).fillna(1.0)
    for c in ("open", "high", "low"):
        df[f"adj_{c}"] = df[c] * f
    return df


def rebased(df, stocks, col="adj_close"):
    out = {}
    for s in stocks:
        x = df[df.stock == s].set_index("date")[col]
        out[s] = 100 * x / x.iloc[0]
    return pd.DataFrame(out)


def daily_returns(df, col="adj_close"):
    p = df.pivot(index="date", columns="stock", values=col)
    return p.pct_change().dropna(how="all")


def stock_stats(df, col="adj_close"):
    rows = []
    for s, g in df.groupby("stock"):
        p = g.set_index("date")[col]
        r = p.pct_change().dropna()
        years = (p.index[-1] - p.index[0]).days / 365.25
        dd = (p / p.cummax() - 1)
        rows.append(dict(
            stock=s, first=p.iloc[0], last=p.iloc[-1],
            total_return=100 * (p.iloc[-1] / p.iloc[0] - 1),
            cagr=100 * ((p.iloc[-1] / p.iloc[0]) ** (1 / years) - 1),
            volatility=100 * r.std() * np.sqrt(TRADING_DAYS),
            max_drawdown=100 * dd.min(), best_day=100 * r.max(), worst_day=100 * r.min(),
            avg_turnover_cr=g["turnover"].mean() / 1e7, avg_delivery=g["delivery_pct"].mean(),
        ))
    out = pd.DataFrame(rows)
    out["return_per_risk"] = out["cagr"] / out["volatility"]
    return out


def strategy_equity(g, col="adj_close"):
    """Long-only golden-cross strategy: in the stock after a Buy, in cash after a Sell. Starts at 100."""
    g = g.sort_values("date").reset_index(drop=True)
    pos = pd.Series(np.nan, index=g.index)
    pos[g["signal"] == "Buy"] = 1.0
    pos[g["signal"] == "Sell"] = 0.0
    pos = pos.ffill().fillna(0.0).shift(1).fillna(0.0)   # act on the NEXT day's return (no look-ahead)
    ret = g[col].pct_change().fillna(0.0) * pos
    return pd.Series(100 * (1 + ret).cumprod().values, index=g["date"]), pos.values


def signal_summary(df):
    s = df[df.signal != "Hold"]
    out = s.groupby(["stock", "signal"]).size().unstack(fill_value=0)
    for c in ("Buy", "Sell"):
        if c not in out:
            out[c] = 0
    last = s.sort_values("date").groupby("stock").tail(1).set_index("stock")
    out["last_signal"] = last["signal"]
    out["last_signal_date"] = last["date"].dt.date
    return out[["Buy", "Sell", "last_signal", "last_signal_date"]].reset_index()


def trend_now(df):
    """Latest ma20 vs ma50 per stock -> 'up' / 'down'."""
    last = df.sort_values("date").groupby("stock").tail(1).set_index("stock")
    return np.where(last["ma20"] > last["ma50"], "Uptrend", "Downtrend"), last.index.tolist()
