"""Data layer: loads the NSE CSV files into an in-memory SQLite database."""
import os, sqlite3
from datetime import datetime
import pandas as pd

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")

# table name -> (display name, csv file name)
STOCKS = {
    "bajaj_auto":    ("Bajaj Auto",    "Bajaj_Auto.csv"),
    "eicher_motors": ("Eicher Motors", "Eicher_Motors.csv"),
    "hero_motocorp": ("Hero Motocorp", "Hero_Motocorp.csv"),
    "infosys":       ("Infosys",       "Infosys.csv"),
    "tcs":           ("TCS",           "TCS.csv"),
    "tvs_motors":    ("TVS Motors",    "TVS_Motors.csv"),
}
COLS = ["date", "open_price", "high_price", "low_price", "close_price", "wap",
        "no_of_shares", "no_of_trades", "total_turnover", "deliverable_qty",
        "pct_deli_qty", "spread_high_low", "spread_close_open"]


def available_tables():
    """Tables whose CSV exists in /data (Bajaj Auto is skipped if file is absent)."""
    return {t: v for t, v in STOCKS.items()
            if os.path.exists(os.path.join(DATA_DIR, v[1]))}


def read_csv(path):
    df = pd.read_csv(path)
    df.columns = COLS
    # '31-July-2018' -> '2018-07-31' (ISO text sorts correctly, as the guide requires)
    df["date"] = [datetime.strptime(d.strip(), "%d-%B-%Y").strftime("%Y-%m-%d") for d in df["date"]]
    for c in COLS[1:]:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    return df.sort_values("date").reset_index(drop=True)


def build_connection():
    """Fresh in-memory SQLite DB with one table per stock."""
    con = sqlite3.connect(":memory:", check_same_thread=False)
    for table, (_, fname) in available_tables().items():
        read_csv(os.path.join(DATA_DIR, fname)).to_sql(table, con, index=False)
    return con


def run_script(con, script):
    """Run a multi-statement SQL script."""
    con.executescript(script)
    con.commit()
