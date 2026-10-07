# NSE Stock Market Analysis

An end-to-end **NSE stock market analysis project** built with **SQL,
Python, SQLite/MySQL, Streamlit, and Machine Learning**.

The project analyzes six NSE stocks from **January 2015 to July 2018**,
covering price trends, moving averages, golden-cross trading signals,
bonus-issue adjustments, backtesting, drawdown, liquidity, delivery
percentage, calendar-year performance, and an additional ML experiment.

> **Note:** This project uses historical NSE stock data. It is an
> analytical/educational project and does not provide live market prices
> or financial advice.

## 📊 Stocks Covered

-   Bajaj Auto
-   Eicher Motors
-   Hero Motocorp
-   Infosys
-   TCS
-   TVS Motors

Each stock contains **889 trading days**, covering **2015-01-01 to
2018-07-31**.

## 🚀 Project Highlights

-   24 SQL analysis tasks
-   SQLite and MySQL-compatible SQL
-   Interactive Streamlit dashboard
-   Stock explorer with price trends and moving averages
-   20-day and 50-day moving-average analysis
-   Golden-cross Buy/Sell signals
-   Raw vs bonus-adjusted price analysis
-   Backtesting of completed Buy → Sell trades
-   Maximum drawdown analysis
-   Liquidity and delivery-percentage analysis
-   Calendar-year performance analysis
-   SQL Playground with query presets and result export
-   Task-by-task walkthrough with checkpoint validation
-   Machine-learning experiment with:
    -   Chronological train/validation/test split
    -   Time-series cross-validation
    -   Feature engineering
    -   Baseline comparison
    -   Hyperparameter tuning
    -   Feature importance
    -   Overfitting/underfitting diagnostics

## 🖥️ Streamlit Dashboard

The dashboard contains the following sections:

### 1. Overview

High-level summary of the six stocks, key metrics, and project findings.

### 2. Stock Explorer

Explore individual stocks using: - Historical price charts - MA20 and
MA50 - Buy/Sell signal markers - Raw or bonus-adjusted prices

### 3. Compare Stocks

Compare performance and important metrics across all six stocks.

### 4. Signals & Backtest

Analyze: - Golden-cross signals - Buy/Sell counts - Completed trades -
Trade returns - Win rate - Average return

### 5. Data Trap

Investigate the two major approximately -50% price movements caused by
bonus issues and compare raw prices with adjusted prices.

### 6. SQL Playground

Run SQL queries directly from the dashboard, browse the database schema,
use task presets, export query results, and visualize query output.

### 7. Task Walkthrough

Run the project tasks and compare important results with the expected
checkpoints from the project guide.

### 8. Downloads

Access project outputs and analysis files.

## 🧠 Important Data Insight

Two major price drops in the raw data were caused by **1:1 bonus
issues**, rather than genuine 50% economic losses:

-   **Infosys --- 2015-06-15**
-   **TCS --- 2018-05-31**

The project adjusts prices before these events by dividing the pre-event
prices by 2.

### Raw vs Adjusted Performance

  Stock       Raw Change   Adjusted Change
  --------- ------------ -----------------
  TCS             -23.8%            +52.4%
  Infosys         -30.9%            +38.2%

This demonstrates why corporate actions must be considered before
interpreting historical stock-price movements.

## 📈 Trading Signal Analysis

The project uses a **20-day / 50-day moving-average golden-cross
strategy**.

A Buy signal is generated when the short-term moving average crosses
above the long-term moving average. A Sell signal is generated when it
crosses below.

On raw prices:

-   **56 Buy signals**
-   **57 Sell signals**

On bonus-adjusted prices:

-   **57 Buy signals**
-   **57 Sell signals**

The adjustment changes some signals, particularly around the
corporate-action periods.

## 💰 Backtesting

The project pairs adjusted Buy and Sell signals into completed trades
and evaluates:

-   Number of trades
-   Winning trades
-   Win rate
-   Average trade return
-   Total trade return

A useful finding is that short-duration trades can be noisy: the
analysis found **11 trades completed within 30 trading days, and all 11
were loss-making**, with an average return of approximately **-5.0%**.

These results are historical and do not represent a guaranteed future
strategy.

## 🤖 Machine Learning Analysis

`ml_analysis.py` provides an additional predictive experiment without
replacing the SQL-based analysis.

### Features

The ML pipeline uses technical and market-derived features such as:

-   1-day return
-   5-day return
-   20-day return
-   SMA ratios
-   RSI
-   Volatility
-   High-low percentage
-   Close-open percentage
-   Volume change
-   Turnover change
-   Delivery percentage

The target is the **next trading day's price direction**.

### Methodology

The experiment uses a chronological:

-   **70% training set**
-   **15% validation set**
-   **15% test set**

It also includes time-series cross-validation and hyperparameter tuning.

### Final ML Result

The selected model in the final run was **Logistic Regression**.

The final test ROC-AUC was approximately **0.521**, indicating a weak
predictive signal. The experiment therefore does **not** demonstrate a
strong standalone trading edge.

The project also compares Logistic Regression, Random Forest, and
HistGradientBoosting and includes diagnostics for model complexity and
overfitting/underfitting.

ML outputs are stored in:

``` text
ml_results/
├── feature_importance.csv
├── hyperparameter_tuning.csv
├── model_comparison.csv
├── overfitting_diagnostics.csv
├── selected_model_metrics.csv
└── train_validation_test_split.csv
```

## 🗂️ Project Structure

``` text
stock_project/
│
├── app.py
├── analytics.py
├── db.py
├── tasks.py
├── ml_analysis.py
├── report.py
├── make_report.py
├── make_sql.py
│
├── requirements.txt
├── README.md
├── FINAL_SUBMISSION.md
├── NSE_Logo.png
│
├── data/
│   ├── Bajaj_Auto.csv
│   ├── Eicher_Motors.csv
│   ├── Hero_Motocorp.csv
│   ├── Infosys.csv
│   ├── TCS.csv
│   └── TVS_Motors.csv
│
├── sql/
│   ├── stock_analysis.sql
│   └── stock_analysis_mysql.sql
│
├── ml_results/
│   ├── feature_importance.csv
│   ├── hyperparameter_tuning.csv
│   ├── model_comparison.csv
│   ├── overfitting_diagnostics.csv
│   ├── selected_model_metrics.csv
│   └── train_validation_test_split.csv
│
└── Stock_Market_Insights_Final.pdf
```

## ⚙️ Installation

### 1. Clone the repository

``` bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd stock_project
```

### 2. Create a virtual environment

``` bash
python -m venv venv
```

Activate it on macOS/Linux:

``` bash
source venv/bin/activate
```

On Windows:

``` bash
venv\Scripts\activate
```

### 3. Install dependencies

``` bash
pip install -r requirements.txt
```

## ▶️ Run the Streamlit Dashboard

Run:

``` bash
python -m streamlit run app.py
```

The application will open in your browser, normally at:

``` text
http://localhost:8501
```

## 🧪 Run the SQL Analysis

Generate the SQL files:

``` bash
python make_sql.py
```

The generated SQL files are available in:

``` text
sql/stock_analysis.sql
sql/stock_analysis_mysql.sql
```

The SQL analysis covers Tasks 1--24 from the project guide.

## 📄 Generate the PDF Report

Run:

``` bash
python report.py
```

The report is generated as:

``` text
Stock_Market_Insights.pdf
```

The final submission report is:

``` text
Stock_Market_Insights_Final.pdf
```

## 🤖 Run the ML Analysis

Run:

``` bash
python ml_analysis.py
```

The generated ML results are saved inside:

``` text
ml_results/
```

## ☁️ Deploy on Streamlit Community Cloud

This project can be deployed using **Streamlit Community Cloud**.

### Step 1 --- Push the project to GitHub

Make sure the repository contains:

``` text
app.py
requirements.txt
data/
analytics.py
db.py
tasks.py
```

along with the other project files.

### Step 2 --- Open Streamlit Community Cloud

Go to:

**https://share.streamlit.io/**

Sign in with GitHub and choose **Deploy an app**.

### Step 3 --- Select the repository

Choose your GitHub repository and set:

``` text
Main file path: app.py
```

Then click **Deploy**.

### Step 4 --- Wait for the build

Streamlit will install the packages from:

``` text
requirements.txt
```

and start the application.

### Important deployment note

The dashboard uses the CSV files from the project's `data/` directory.
Therefore, make sure all six CSV files are committed to GitHub and the
paths remain unchanged.

## 🗄️ SQL Database

The application uses SQLite for the interactive dashboard and SQL
Playground.

The database is built from the CSV files and contains stock-specific
tables for:

-   Bajaj Auto
-   Eicher Motors
-   Hero Motocorp
-   Infosys
-   TCS
-   TVS Motors

A MySQL-compatible SQL version is also included for database execution
outside the Streamlit application.

## 🛠️ Technologies Used

  Technology     Purpose
  -------------- ---------------------------------------
  Python         Data processing, analytics and ML
  SQL            Stock-market analysis
  SQLite         Dashboard database
  MySQL          SQL submission/database compatibility
  Pandas         Data manipulation
  NumPy          Numerical analysis
  Streamlit      Interactive dashboard
  Plotly         Interactive visualizations
  Scikit-learn   Machine learning
  ReportLab      PDF report generation
  Git & GitHub   Version control and deployment

## 📌 Key Project Findings

-   TVS Motors had the highest raw and adjusted full-period price growth
    at approximately **86.9%**.
-   Eicher Motors returned approximately **82.6%** over the full period
    after adjustment.
-   TCS and Infosys initially appeared to have large losses because of
    unadjusted bonus-issue price changes.
-   Eicher Motors had the strongest backtest profile, with all 6
    completed trades profitable in the final adjusted analysis.
-   TCS had the weakest backtest profile among the six stocks, with an
    18.2% trade win rate and approximately -36.9% total trade return.
-   TVS Motors had the highest maximum drawdown at approximately
    **-34.6%**.
-   Infosys had the highest average daily turnover among the six stocks.
-   The ML experiment produced only a weak predictive signal,
    highlighting the limitations of using technical features alone.

## ⚠️ Limitations

This project is designed for educational and analytical purposes.

The analysis does not fully model:

-   Brokerage and transaction costs
-   Slippage
-   Taxes
-   Dividends
-   Corporate announcements/news
-   Market-wide conditions
-   Sector-level effects
-   Real-time market data

Therefore, the backtest and ML results should not be interpreted as
investment advice or guaranteed future performance.

## 👨‍💻 Author

**Yash Tailor**

Computer Science & Engineering

Interested in **Software Development, Data Analytics, SQL, Python, and
Machine Learning**.

------------------------------------------------------------------------

⭐ If you find this project useful, consider giving the repository a
star.
