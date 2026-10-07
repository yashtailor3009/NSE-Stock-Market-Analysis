# NSE Stock Market Analysis in SQL

Moving averages, golden-cross signals and the data trap, for NSE stocks (Jan 2015 → Jul 2018).
Everything is computed in SQL; Streamlit is only the front end.

## Run it
```bash
pip install -r requirements.txt
streamlit run app.py
```

## What's inside
| File | Purpose |
|---|---|
| `app.py` | Streamlit dashboard (8 pages) incl. **live SQL playground** |
| `tasks.py` | **All SQL lives here** (24 tasks) – the .sql files and the app both come from it |
| `analytics.py`, `db.py` | pandas helpers / CSV → SQLite loader |
| `sql/stock_analysis.sql` | Submission #1 – SQLite version (runs top-to-bottom, re-runnable) |
| `sql/stock_analysis_mysql.sql` | Same analysis for MySQL 8 incl. CSV loader + `CREATE FUNCTION` (task 9) |
| `Stock_Market_Insights.pdf` | Submission #2 – insights report |
| `make_report.py`, `make_sql.py` | Regenerate the PDF / SQL files |
| `data/` | The CSVs |

## Dashboard pages
Overview · Stock Explorer (candlestick, MA20/50, Buy/Sell markers) · Compare Stocks · Signals & Backtest ·
The Data Trap (raw vs adjusted) · **SQL Playground** (editor, schema browser, presets for every task, CSV export, chart-this-result) ·
Task Walkthrough (runs each guide task and checks the guide's checkpoints) · Downloads.
The sidebar toggle switches the whole app between raw and bonus-adjusted prices.

## Bajaj Auto
`Bajaj_Auto.csv` was not in the supplied files. Drop it into `data/` (or upload it in the app sidebar), then:
```bash
python make_report.py   # regenerates the PDF with Bajaj included
```
The SQL files already cover all six stocks. Single-stock tasks (1, 5, 7, 8, 9) run on Eicher Motors until Bajaj is present.

## Key finding
Infosys (2015-06-15) and TCS (2018-05-31) had 1:1 bonus issues → fake −50% days. On raw prices TCS = −23.8%, Infosys = −30.9%;
adjusted they are +52.4% and +38.2%, and TCS's latest signal flips from Sell to Buy.
