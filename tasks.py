"""
All SQL for the project lives here, so the delivered .sql files and the Streamlit app
always run exactly the same queries.

build_tasks(tables, focus, dialect) -> list of task dicts:
    id, part, title, goal, sql, creates (True if it CREATEs a table), show (query to preview)
dialect is 'sqlite' (live playground) or 'mysql' (submission file).
"""

DISPLAY = {
    "bajaj_auto": "Bajaj Auto", "eicher_motors": "Eicher Motors", "hero_motocorp": "Hero Motocorp",
    "infosys": "Infosys", "tcs": "TCS", "tvs_motors": "TVS Motors",
}
SHORT = {  # master_table column names, in the order the guide asks for
    "bajaj_auto": "bajaj", "tcs": "tcs", "tvs_motors": "tvs",
    "infosys": "infosys", "eicher_motors": "eicher", "hero_motocorp": "hero",
}
MASTER_ORDER = ["bajaj_auto", "tcs", "tvs_motors", "infosys", "eicher_motors", "hero_motocorp"]

# Corporate actions found in task 12 (1:1 bonus issues -> price halves, nothing is lost)
EVENTS = {"tcs": "2018-05-31", "infosys": "2015-06-15"}
FACTOR = 2


def stack(tables, cols="date, close_price"):
    return "\n  UNION ALL\n  ".join(
        f"SELECT '{DISPLAY[t]}' AS stock, {cols} FROM {t}" for t in tables)


def signal_chain(src, col):
    """CTEs ma -> lagged -> sig (partitioned per stock). Unrounded averages."""
    return f"""ma AS (
  SELECT stock, date, {col} AS close_price,
    CASE WHEN ROW_NUMBER() OVER (PARTITION BY stock ORDER BY date) >= 20
         THEN AVG({col}) OVER (PARTITION BY stock ORDER BY date ROWS BETWEEN 19 PRECEDING AND CURRENT ROW) END AS ma20,
    CASE WHEN ROW_NUMBER() OVER (PARTITION BY stock ORDER BY date) >= 50
         THEN AVG({col}) OVER (PARTITION BY stock ORDER BY date ROWS BETWEEN 49 PRECEDING AND CURRENT ROW) END AS ma50
  FROM {src}
),
lagged AS (
  SELECT *,
    LAG(ma20) OVER (PARTITION BY stock ORDER BY date) AS prev_ma20,
    LAG(ma50) OVER (PARTITION BY stock ORDER BY date) AS prev_ma50
  FROM ma
),
sig AS (
  SELECT stock, date, close_price, ma20, ma50,
    CASE
      WHEN ma20 IS NULL OR ma50 IS NULL OR prev_ma20 IS NULL OR prev_ma50 IS NULL THEN 'Hold'
      WHEN ma20 > ma50 AND prev_ma20 <= prev_ma50 THEN 'Buy'
      WHEN ma20 < ma50 AND prev_ma20 >= prev_ma50 THEN 'Sell'
      ELSE 'Hold'
    END AS `signal`
  FROM lagged
)"""


def build_tasks(tables, focus=None, dialect="sqlite"):
    """tables: list of table names that exist. focus: table used for the single-stock tasks."""
    mysql = dialect == "mysql"
    focus = focus or ("bajaj_auto" if "bajaj_auto" in tables else tables[0])
    prefix = {"bajaj_auto": "bajaj"}.get(focus, focus)
    F, F1, F2 = focus, f"{prefix}1", f"{prefix}2"
    name = DISPLAY[focus]
    year = "YEAR(date)" if mysql else "strftime('%Y', date)"
    days_between = (lambda a, b: f"DATEDIFF({a}, {b})") if mysql else \
                   (lambda a, b: f"CAST(julianday({a}) - julianday({b}) AS INTEGER)")
    prices = stack(tables)
    T = []

    def add(id, part, title, goal, sql, creates=False, show=None):
        T.append(dict(id=id, part=part, title=title, goal=goal, sql=sql.strip() + "\n",
                      creates=creates, show=show))

    # ------------------------------------------------------------------ Part 1
    add(1, "Part 1 · Get to know the data", f"How much history do we have? ({name})",
        f"Number of trading days, first date and last date for {name}.",
        f"""
SELECT COUNT(*)  AS trading_days,
       MIN(date) AS first_day,
       MAX(date) AS last_day
FROM {F};""")

    add(2, "Part 1 · Get to know the data", "Eicher's five best closes",
        "Date and close price of Eicher Motors' five highest closing prices.",
        """
SELECT date, close_price
FROM eicher_motors
ORDER BY close_price DESC
LIMIT 5;""")

    add(3, "Part 1 · Get to know the data", "TCS, year by year",
        "Average TCS close per calendar year, rounded to 2 decimals (raw, unadjusted prices).",
        f"""
SELECT {year} AS year,
       ROUND(AVG(close_price), 2) AS avg_close
FROM tcs
GROUP BY {year}
ORDER BY {year};""")

    nulls = "\nUNION ALL\n".join(
        f"SELECT '{t}' AS stock, date FROM {t} WHERE deliverable_qty IS NULL" for t in tables)
    add(4, "Part 1 · Get to know the data", "Find the holes (NULL deliverable_qty)",
        "Every row across all tables where deliverable_qty is NULL.",
        f"""
{nulls}
ORDER BY date, stock;""")

    # ------------------------------------------------------------------ Part 2
    add(5, "Part 2 · The assignment", f"Moving averages → {F1}",
        f"20- and 50-day moving averages of close price for {name}; NULL until a full window exists.",
        f"""
DROP TABLE IF EXISTS {F1};
CREATE TABLE {F1} AS
SELECT
  date,
  close_price,
  CASE WHEN ROW_NUMBER() OVER (ORDER BY date) >= 20
       THEN ROUND(AVG(close_price) OVER (ORDER BY date ROWS BETWEEN 19 PRECEDING AND CURRENT ROW), 2)
  END AS ma20,
  CASE WHEN ROW_NUMBER() OVER (ORDER BY date) >= 50
       THEN ROUND(AVG(close_price) OVER (ORDER BY date ROWS BETWEEN 49 PRECEDING AND CURRENT ROW), 2)
  END AS ma50
FROM {F};""", creates=True, show=f"SELECT * FROM {F1} ORDER BY date")

    order = [t for t in MASTER_ORDER if t in tables]
    base = order[0]
    # simple unique aliases
    alias = {t: f"s_{SHORT[t]}" for t in order}
    sel = [f"{alias[base]}.date"] + [f"{alias[t]}.close_price AS {SHORT[t]}" for t in order]
    jn = "\n".join(f"JOIN {t} {alias[t]} ON {alias[t]}.date = {alias[base]}.date" for t in order if t != base)
    add(6, "Part 2 · The assignment", "Master table",
        "One row per date with every stock's close price side by side.",
        f"""
DROP TABLE IF EXISTS master_table;
CREATE TABLE master_table AS
SELECT {(","+chr(10)+"       ").join(sel)}
FROM {base} {alias[base]}
{jn};""", creates=True, show="SELECT * FROM master_table ORDER BY date")

    add(7, "Part 2 · The assignment", f"Golden-cross signals → {F2}",
        "Buy on the day ma20 crosses above ma50, Sell when it crosses below, Hold otherwise.",
        f"""
DROP TABLE IF EXISTS {F2};
CREATE TABLE {F2} AS
WITH t AS (
  SELECT date, close_price, ma20, ma50,
         LAG(ma20) OVER (ORDER BY date) AS prev_ma20,
         LAG(ma50) OVER (ORDER BY date) AS prev_ma50
  FROM {F1}
)
SELECT date, close_price,
  CASE
    WHEN ma20 IS NULL OR ma50 IS NULL OR prev_ma20 IS NULL OR prev_ma50 IS NULL THEN 'Hold'
    WHEN ma20 > ma50 AND prev_ma20 <= prev_ma50 THEN 'Buy'
    WHEN ma20 < ma50 AND prev_ma20 >= prev_ma50 THEN 'Sell'
    ELSE 'Hold'
  END AS `signal`
FROM t;""", creates=True, show=f"SELECT * FROM {F2} WHERE `signal` <> 'Hold' ORDER BY date")

    add(8, "Part 2 · The assignment", "How often did it trigger?",
        f"Number of days carrying each signal for {name}.",
        f"""
SELECT `signal`, COUNT(*) AS days
FROM {F2}
GROUP BY `signal`
ORDER BY `signal`;""")

    sig_q = f"SELECT `signal`\nFROM {F2}\nWHERE date = '2018-06-21';"
    if mysql:
        sig_q += f"""

-- MySQL: reusable function (Appendix B of the guide)
DROP FUNCTION IF EXISTS {prefix}_signal;
DELIMITER $$
CREATE FUNCTION {prefix}_signal(d DATE)
RETURNS VARCHAR(4) DETERMINISTIC READS SQL DATA
BEGIN
  DECLARE s VARCHAR(4);
  SELECT `signal` INTO s FROM {F2} WHERE date = d;
  RETURN s;
END $$
DELIMITER ;

SELECT {prefix}_signal('2018-06-21') AS `signal`;"""
    add(9, "Part 2 · The assignment", "Signal on a given day (2018-06-21)",
        f"The {name} signal on 2018-06-21. (In MySQL this becomes a function.)", sig_q)

    add(10, "Part 2 · The assignment", "All stocks in one query",
        "Buys, sells and latest signal for every stock — no per-stock tables needed.",
        f"""
WITH prices AS (
  {prices}
),
{signal_chain('prices', 'close_price')},
latest AS (
  SELECT stock, date, `signal`,
         ROW_NUMBER() OVER (PARTITION BY stock ORDER BY date DESC) AS rn
  FROM sig
  WHERE `signal` <> 'Hold'
)
SELECT s.stock,
       SUM(s.`signal` = 'Buy')  AS buys,
       SUM(s.`signal` = 'Sell') AS sells,
       MAX(l.date)              AS last_signal_date,
       MAX(l.`signal`)          AS last_signal
FROM sig s
JOIN latest l ON l.stock = s.stock AND l.rn = 1
GROUP BY s.stock
ORDER BY s.stock;""")

    # ------------------------------------------------------------------ Part 3
    add(11, "Part 3 · Question the result", "Who went up? (raw prices)",
        "First close, last close and % change per stock — computed on RAW prices (before the fix).",
        f"""
WITH prices AS (
  {prices}
),
ends AS (
  SELECT stock, MIN(date) AS first_day, MAX(date) AS last_day
  FROM prices GROUP BY stock
)
SELECT e.stock,
       f.close_price AS first_close,
       l.close_price AS last_close,
       ROUND(100.0 * (l.close_price - f.close_price) / f.close_price, 1) AS pct_change
FROM ends e
JOIN prices f ON f.stock = e.stock AND f.date = e.first_day
JOIN prices l ON l.stock = e.stock AND l.date = e.last_day
ORDER BY pct_change DESC;""")

    add(12, "Part 3 · Question the result", "The data trap — worst day per stock",
        "Each stock's single worst day-over-day move. Two rows are ~-50%: those are bonus issues, not crashes.",
        f"""
WITH prices AS (
  {prices}
),
moves AS (
  SELECT stock, date, close_price,
         100.0 * (close_price / LAG(close_price) OVER (PARTITION BY stock ORDER BY date) - 1) AS pct_move
  FROM prices
),
ranked AS (
  SELECT *, ROW_NUMBER() OVER (PARTITION BY stock ORDER BY pct_move ASC) AS rn
  FROM moves
  WHERE pct_move IS NOT NULL
)
SELECT stock, date, close_price, ROUND(pct_move, 1) AS pct_move
FROM ranked
WHERE rn = 1
ORDER BY pct_move;""")

    ev = [t for t in EVENTS if t in tables]
    adj_parts = []
    for t in tables:
        if t in EVENTS:
            adj_parts.append(f"SELECT '{DISPLAY[t]}' AS stock, date, close_price,\n         CASE WHEN date < '{EVENTS[t]}' THEN close_price / {FACTOR} ELSE close_price END AS adj_close\n  FROM {t}")
        else:
            adj_parts.append(f"SELECT '{DISPLAY[t]}' AS stock, date, close_price, close_price AS adj_close FROM {t}")
    adj_union = "\n  UNION ALL\n  ".join(adj_parts)

    add(13, "Part 3 · Question the result", "Fix it — adjust TCS & Infosys for the 1:1 bonus issues",
        "Divide pre-event prices by 2 (TCS before 2018-05-31, Infosys before 2015-06-15) and recompute % change.",
        f"""
WITH adjusted AS (
  SELECT 'TCS' AS stock, date,
         CASE WHEN date < '{EVENTS['tcs']}' THEN close_price / {FACTOR} ELSE close_price END AS adj_close
  FROM tcs
  UNION ALL
  SELECT 'Infosys' AS stock, date,
         CASE WHEN date < '{EVENTS['infosys']}' THEN close_price / {FACTOR} ELSE close_price END AS adj_close
  FROM infosys
)
SELECT stock,
       ROUND(100.0 * (MAX(CASE WHEN date = '2018-07-31' THEN adj_close END) /
                      MAX(CASE WHEN date = '2015-01-01' THEN adj_close END) - 1), 1) AS adjusted_pct_change
FROM adjusted
GROUP BY stock
ORDER BY stock;""" if all(t in tables for t in EVENTS) else "SELECT 'TCS/Infosys files not loaded' AS note;")

    # ------------------------------------------------------------------ Part 4 (extensions)
    add(14, "Part 4 · Extensions for the insights report", "adj_prices — the clean price table",
        "Adjusted close for all stocks (only TCS and Infosys actually change).",
        f"""
DROP TABLE IF EXISTS adj_prices;
CREATE TABLE adj_prices AS
  {adj_union};""", creates=True, show="SELECT * FROM adj_prices ORDER BY stock, date")

    add(15, "Part 4 · Extensions for the insights report", "adj_signals — signals on adjusted prices",
        "Moving averages and Buy/Sell/Hold for every stock using adjusted prices.",
        f"""
DROP TABLE IF EXISTS adj_signals;
CREATE TABLE adj_signals AS
WITH {signal_chain('adj_prices', 'adj_close')}
SELECT * FROM sig;""", creates=True,
        show="SELECT * FROM adj_signals WHERE `signal` <> 'Hold' ORDER BY stock, date")

    add(16, "Part 4 · Extensions for the insights report", "Signal counts: raw vs adjusted",
        "How many signals did the price cliff create or destroy? (Stretch challenge)",
        f"""
WITH raw AS (
  {prices}
),
{signal_chain('raw', 'close_price')},
raw_sig AS (SELECT stock, SUM(`signal`='Buy') AS raw_buys, SUM(`signal`='Sell') AS raw_sells FROM sig GROUP BY stock),
adj_sig AS (SELECT stock, SUM(`signal`='Buy') AS adj_buys, SUM(`signal`='Sell') AS adj_sells FROM adj_signals GROUP BY stock)
SELECT r.stock, raw_buys, adj_buys, raw_sells, adj_sells,
       (adj_buys + adj_sells) - (raw_buys + raw_sells) AS net_change
FROM raw_sig r JOIN adj_sig a ON a.stock = r.stock
ORDER BY r.stock;""")

    add(17, "Part 4 · Extensions for the insights report", "Stretch: which TCS & Infosys signals were fake?",
        "Signals that exist on raw prices but not on adjusted prices (or vice-versa), by date.",
        f"""
WITH raw AS (
  {prices}
),
{signal_chain('raw', 'close_price')}
SELECT r.stock, r.date, r.`signal` AS raw_signal, a.`signal` AS adjusted_signal
FROM sig r
JOIN adj_signals a ON a.stock = r.stock AND a.date = r.date
WHERE r.`signal` <> a.`signal`
ORDER BY r.stock, r.date;""")

    add(18, "Part 4 · Extensions for the insights report", "Adjusted % change (all stocks)",
        "First vs last adjusted close for all stocks — the corrected version of task 11.",
        f"""
WITH ends AS (
  SELECT stock, MIN(date) AS first_day, MAX(date) AS last_day FROM adj_prices GROUP BY stock
)
SELECT e.stock,
       ROUND(f.adj_close, 2) AS first_adj_close,
       ROUND(l.adj_close, 2) AS last_adj_close,
       ROUND(100.0 * (l.adj_close - f.adj_close) / f.adj_close, 1) AS adj_pct_change
FROM ends e
JOIN adj_prices f ON f.stock = e.stock AND f.date = e.first_day
JOIN adj_prices l ON l.stock = e.stock AND l.date = e.last_day
ORDER BY adj_pct_change DESC;""")

    add(19, "Part 4 · Extensions for the insights report", "Whipsaws — signals that flipped within 30 days",
        "For each stock: how many consecutive signals came less than 30 days apart (adjusted prices).",
        f"""
WITH flips AS (
  SELECT stock, date, `signal`, close_price,
         LEAD(date)   OVER (PARTITION BY stock ORDER BY date) AS next_date,
         LEAD(`signal`) OVER (PARTITION BY stock ORDER BY date) AS next_signal
  FROM adj_signals
  WHERE `signal` <> 'Hold'
)
SELECT stock,
       COUNT(next_date) AS signal_pairs,
       SUM({days_between('next_date', 'date')} < 30) AS whipsaws_under_30d,
       ROUND(100.0 * SUM({days_between('next_date', 'date')} < 30) / COUNT(next_date), 1) AS whipsaw_pct,
       MIN({days_between('next_date', 'date')}) AS shortest_gap_days
FROM flips
WHERE next_date IS NOT NULL
GROUP BY stock
ORDER BY whipsaw_pct DESC;""")

    add(20, "Part 4 · Extensions for the insights report", "Backtest: every completed Buy → Sell trade",
        "Buy at each Buy signal's close, sell at the next Sell signal's close (adjusted prices).",
        f"""
DROP TABLE IF EXISTS trades;
CREATE TABLE trades AS
WITH s AS (
  SELECT stock, date, `signal`, close_price,
         LEAD(date)         OVER (PARTITION BY stock ORDER BY date) AS next_date,
         LEAD(`signal`)     OVER (PARTITION BY stock ORDER BY date) AS next_signal,
         LEAD(close_price)  OVER (PARTITION BY stock ORDER BY date) AS next_price
  FROM adj_signals
  WHERE `signal` <> 'Hold'
)
SELECT stock,
       date        AS buy_date,
       next_date   AS sell_date,
       ROUND(close_price, 2) AS buy_price,
       ROUND(next_price, 2)  AS sell_price,
       ROUND(100.0 * (next_price - close_price) / close_price, 2) AS return_pct,
       {days_between('next_date', 'date')} AS days_held
FROM s
WHERE `signal` = 'Buy' AND next_signal = 'Sell';""", creates=True,
        show="SELECT * FROM trades ORDER BY stock, buy_date")

    add(21, "Part 4 · Extensions for the insights report", "Backtest summary vs buy-and-hold",
        "Per stock: number of trades, win rate, average return and average holding period.",
        """
SELECT stock,
       COUNT(*)                                   AS trades,
       SUM(return_pct > 0)                        AS winners,
       ROUND(100.0 * SUM(return_pct > 0) / COUNT(*), 1) AS win_rate_pct,
       ROUND(AVG(return_pct), 2)                  AS avg_return_pct,
       ROUND(SUM(return_pct), 2)                  AS sum_return_pct,
       ROUND(AVG(days_held), 0)                   AS avg_days_held
FROM trades
GROUP BY stock
ORDER BY sum_return_pct DESC;""")

    add(22, "Part 4 · Extensions for the insights report", "Maximum drawdown (adjusted prices)",
        "Worst peak-to-trough fall in each stock's history.",
        """
WITH dd AS (
  SELECT stock, date, adj_close,
         MAX(adj_close) OVER (PARTITION BY stock ORDER BY date ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS peak
  FROM adj_prices
),
d AS (
  SELECT stock, date, 100.0 * (adj_close - peak) / peak AS drawdown_pct,
         ROW_NUMBER() OVER (PARTITION BY stock ORDER BY (adj_close - peak) / peak ASC) AS rn
  FROM dd
)
SELECT stock, date AS trough_date, ROUND(drawdown_pct, 1) AS max_drawdown_pct
FROM d
WHERE rn = 1
ORDER BY max_drawdown_pct;""")

    add(23, "Part 4 · Extensions for the insights report", "Liquidity & conviction: turnover and delivery %",
        "Average daily turnover (₹ crore) and average % of shares actually delivered.",
        "SELECT stock, ROUND(AVG(turnover_cr), 2) AS avg_daily_turnover_cr, ROUND(AVG(deli), 1) AS avg_delivery_pct\nFROM (\n  "
        + "\n  UNION ALL\n  ".join(
            f"SELECT '{DISPLAY[t]}' AS stock, total_turnover / 10000000.0 AS turnover_cr, pct_deli_qty AS deli FROM {t}"
            for t in tables)
        + "\n) x\nGROUP BY stock\nORDER BY avg_daily_turnover_cr DESC;")

    add(24, "Part 4 · Extensions for the insights report", "Best and worst calendar year per stock (adjusted)",
        "Year-over-year change of the last close of each year (2015 starts Jan-1; 2018 ends Jul-31).",
        f"""
WITH yr AS (
  SELECT stock, {year} AS year, MIN(date) AS first_day, MAX(date) AS last_day
  FROM adj_prices GROUP BY stock, {year}
)
SELECT y.stock, y.year,
       ROUND(100.0 * (l.adj_close - f.adj_close) / f.adj_close, 1) AS return_in_year_pct
FROM yr y
JOIN adj_prices f ON f.stock = y.stock AND f.date = y.first_day
JOIN adj_prices l ON l.stock = y.stock AND l.date = y.last_day
ORDER BY y.stock, y.year;""")

    return T


def build_script(tables, focus=None):
    """Only the table-creating statements (what the app runs at start-up)."""
    return "\n".join(t["sql"] for t in build_tasks(tables, focus) if t["creates"])


def mysql_loader(tables):
    from db import STOCKS
    out = []
    for t in tables:
        out.append(f"""CREATE TABLE IF NOT EXISTS {t} (
  `date` DATE PRIMARY KEY,
  open_price DECIMAL(12,2), high_price DECIMAL(12,2), low_price DECIMAL(12,2),
  close_price DECIMAL(12,2), wap DECIMAL(16,4),
  no_of_shares BIGINT, no_of_trades BIGINT, total_turnover DECIMAL(20,2),
  deliverable_qty BIGINT, pct_deli_qty DECIMAL(6,2),
  spread_high_low DECIMAL(12,2), spread_close_open DECIMAL(12,2)
);
LOAD DATA LOCAL INFILE '/path/to/{STOCKS[t][1]}' INTO TABLE {t}
FIELDS TERMINATED BY ',' LINES TERMINATED BY '\\n' IGNORE 1 LINES
(@d,@o,@h,@l,@c,@w,@s,@tr,@to,@dq,@pd,@shl,@sco)
SET `date` = STR_TO_DATE(@d, '%d-%M-%Y'),
  open_price = NULLIF(@o,''), high_price = NULLIF(@h,''), low_price = NULLIF(@l,''),
  close_price = NULLIF(@c,''), wap = NULLIF(@w,''), no_of_shares = NULLIF(@s,''),
  no_of_trades = NULLIF(@tr,''), total_turnover = NULLIF(@to,''),
  deliverable_qty = NULLIF(@dq,''), pct_deli_qty = NULLIF(@pd,''),
  spread_high_low = NULLIF(@shl,''), spread_close_open = NULLIF(TRIM(@sco),'');
""")
    return "\n".join(out)


def write_sql_files(tables, out_dir):
    """Write the two submission files."""
    import os
    os.makedirs(out_dir, exist_ok=True)
    for dialect in ("sqlite", "mysql"):
        head = ["-- " + "=" * 74,
                "-- Stock Market Analysis in SQL — NSE, Jan 2015 → Jul 2018",
                f"-- Dialect: {'SQLite (runs in the Streamlit playground)' if dialect == 'sqlite' else 'MySQL 8 (submission version)'}",
                "-- Tables: " + ", ".join(tables),
                "-- Every created table starts with DROP TABLE IF EXISTS, so this file can be re-run.",
                "-- " + "=" * 74, ""]
        if dialect == "mysql":
            head += ["-- SETUP: load the six CSVs (Appendix A of the guide). Run once.",
                     "-- SET GLOBAL local_infile = 1;  (and OPT_LOCAL_INFILE=1 in Workbench)",
                     "", mysql_loader(tables), ""]
        body = []
        for t in build_tasks(tables, dialect=dialect):
            body.append(f"-- {'-' * 72}\n-- {t['part']}\n-- TASK {t['id']}: {t['title']}\n-- {t['goal']}\n-- {'-' * 72}\n{t['sql']}")
        path = os.path.join(out_dir, "stock_analysis_mysql.sql" if dialect == "mysql" else "stock_analysis.sql")
        with open(path, "w") as f:
            f.write("\n".join(head) + "\n" + "\n".join(body))
        print("wrote", path)
