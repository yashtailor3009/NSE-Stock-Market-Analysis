-- ==========================================================================
-- Stock Market Analysis in SQL — NSE, Jan 2015 → Jul 2018
-- Dialect: MySQL 8 (submission version)
-- Tables: bajaj_auto, eicher_motors, hero_motocorp, infosys, tcs, tvs_motors
-- Every created table starts with DROP TABLE IF EXISTS, so this file can be re-run.
-- ==========================================================================

-- SETUP: load the six CSVs (Appendix A of the guide). Run once.
-- SET GLOBAL local_infile = 1;  (and OPT_LOCAL_INFILE=1 in Workbench)

CREATE TABLE IF NOT EXISTS bajaj_auto (
  `date` DATE PRIMARY KEY,
  open_price DECIMAL(12,2), high_price DECIMAL(12,2), low_price DECIMAL(12,2),
  close_price DECIMAL(12,2), wap DECIMAL(16,4),
  no_of_shares BIGINT, no_of_trades BIGINT, total_turnover DECIMAL(20,2),
  deliverable_qty BIGINT, pct_deli_qty DECIMAL(6,2),
  spread_high_low DECIMAL(12,2), spread_close_open DECIMAL(12,2)
);
LOAD DATA LOCAL INFILE '/path/to/Bajaj_Auto.csv' INTO TABLE bajaj_auto
FIELDS TERMINATED BY ',' LINES TERMINATED BY '\n' IGNORE 1 LINES
(@d,@o,@h,@l,@c,@w,@s,@tr,@to,@dq,@pd,@shl,@sco)
SET `date` = STR_TO_DATE(@d, '%d-%M-%Y'),
  open_price = NULLIF(@o,''), high_price = NULLIF(@h,''), low_price = NULLIF(@l,''),
  close_price = NULLIF(@c,''), wap = NULLIF(@w,''), no_of_shares = NULLIF(@s,''),
  no_of_trades = NULLIF(@tr,''), total_turnover = NULLIF(@to,''),
  deliverable_qty = NULLIF(@dq,''), pct_deli_qty = NULLIF(@pd,''),
  spread_high_low = NULLIF(@shl,''), spread_close_open = NULLIF(TRIM(@sco),'');

CREATE TABLE IF NOT EXISTS eicher_motors (
  `date` DATE PRIMARY KEY,
  open_price DECIMAL(12,2), high_price DECIMAL(12,2), low_price DECIMAL(12,2),
  close_price DECIMAL(12,2), wap DECIMAL(16,4),
  no_of_shares BIGINT, no_of_trades BIGINT, total_turnover DECIMAL(20,2),
  deliverable_qty BIGINT, pct_deli_qty DECIMAL(6,2),
  spread_high_low DECIMAL(12,2), spread_close_open DECIMAL(12,2)
);
LOAD DATA LOCAL INFILE '/path/to/Eicher_Motors.csv' INTO TABLE eicher_motors
FIELDS TERMINATED BY ',' LINES TERMINATED BY '\n' IGNORE 1 LINES
(@d,@o,@h,@l,@c,@w,@s,@tr,@to,@dq,@pd,@shl,@sco)
SET `date` = STR_TO_DATE(@d, '%d-%M-%Y'),
  open_price = NULLIF(@o,''), high_price = NULLIF(@h,''), low_price = NULLIF(@l,''),
  close_price = NULLIF(@c,''), wap = NULLIF(@w,''), no_of_shares = NULLIF(@s,''),
  no_of_trades = NULLIF(@tr,''), total_turnover = NULLIF(@to,''),
  deliverable_qty = NULLIF(@dq,''), pct_deli_qty = NULLIF(@pd,''),
  spread_high_low = NULLIF(@shl,''), spread_close_open = NULLIF(TRIM(@sco),'');

CREATE TABLE IF NOT EXISTS hero_motocorp (
  `date` DATE PRIMARY KEY,
  open_price DECIMAL(12,2), high_price DECIMAL(12,2), low_price DECIMAL(12,2),
  close_price DECIMAL(12,2), wap DECIMAL(16,4),
  no_of_shares BIGINT, no_of_trades BIGINT, total_turnover DECIMAL(20,2),
  deliverable_qty BIGINT, pct_deli_qty DECIMAL(6,2),
  spread_high_low DECIMAL(12,2), spread_close_open DECIMAL(12,2)
);
LOAD DATA LOCAL INFILE '/path/to/Hero_Motocorp.csv' INTO TABLE hero_motocorp
FIELDS TERMINATED BY ',' LINES TERMINATED BY '\n' IGNORE 1 LINES
(@d,@o,@h,@l,@c,@w,@s,@tr,@to,@dq,@pd,@shl,@sco)
SET `date` = STR_TO_DATE(@d, '%d-%M-%Y'),
  open_price = NULLIF(@o,''), high_price = NULLIF(@h,''), low_price = NULLIF(@l,''),
  close_price = NULLIF(@c,''), wap = NULLIF(@w,''), no_of_shares = NULLIF(@s,''),
  no_of_trades = NULLIF(@tr,''), total_turnover = NULLIF(@to,''),
  deliverable_qty = NULLIF(@dq,''), pct_deli_qty = NULLIF(@pd,''),
  spread_high_low = NULLIF(@shl,''), spread_close_open = NULLIF(TRIM(@sco),'');

CREATE TABLE IF NOT EXISTS infosys (
  `date` DATE PRIMARY KEY,
  open_price DECIMAL(12,2), high_price DECIMAL(12,2), low_price DECIMAL(12,2),
  close_price DECIMAL(12,2), wap DECIMAL(16,4),
  no_of_shares BIGINT, no_of_trades BIGINT, total_turnover DECIMAL(20,2),
  deliverable_qty BIGINT, pct_deli_qty DECIMAL(6,2),
  spread_high_low DECIMAL(12,2), spread_close_open DECIMAL(12,2)
);
LOAD DATA LOCAL INFILE '/path/to/Infosys.csv' INTO TABLE infosys
FIELDS TERMINATED BY ',' LINES TERMINATED BY '\n' IGNORE 1 LINES
(@d,@o,@h,@l,@c,@w,@s,@tr,@to,@dq,@pd,@shl,@sco)
SET `date` = STR_TO_DATE(@d, '%d-%M-%Y'),
  open_price = NULLIF(@o,''), high_price = NULLIF(@h,''), low_price = NULLIF(@l,''),
  close_price = NULLIF(@c,''), wap = NULLIF(@w,''), no_of_shares = NULLIF(@s,''),
  no_of_trades = NULLIF(@tr,''), total_turnover = NULLIF(@to,''),
  deliverable_qty = NULLIF(@dq,''), pct_deli_qty = NULLIF(@pd,''),
  spread_high_low = NULLIF(@shl,''), spread_close_open = NULLIF(TRIM(@sco),'');

CREATE TABLE IF NOT EXISTS tcs (
  `date` DATE PRIMARY KEY,
  open_price DECIMAL(12,2), high_price DECIMAL(12,2), low_price DECIMAL(12,2),
  close_price DECIMAL(12,2), wap DECIMAL(16,4),
  no_of_shares BIGINT, no_of_trades BIGINT, total_turnover DECIMAL(20,2),
  deliverable_qty BIGINT, pct_deli_qty DECIMAL(6,2),
  spread_high_low DECIMAL(12,2), spread_close_open DECIMAL(12,2)
);
LOAD DATA LOCAL INFILE '/path/to/TCS.csv' INTO TABLE tcs
FIELDS TERMINATED BY ',' LINES TERMINATED BY '\n' IGNORE 1 LINES
(@d,@o,@h,@l,@c,@w,@s,@tr,@to,@dq,@pd,@shl,@sco)
SET `date` = STR_TO_DATE(@d, '%d-%M-%Y'),
  open_price = NULLIF(@o,''), high_price = NULLIF(@h,''), low_price = NULLIF(@l,''),
  close_price = NULLIF(@c,''), wap = NULLIF(@w,''), no_of_shares = NULLIF(@s,''),
  no_of_trades = NULLIF(@tr,''), total_turnover = NULLIF(@to,''),
  deliverable_qty = NULLIF(@dq,''), pct_deli_qty = NULLIF(@pd,''),
  spread_high_low = NULLIF(@shl,''), spread_close_open = NULLIF(TRIM(@sco),'');

CREATE TABLE IF NOT EXISTS tvs_motors (
  `date` DATE PRIMARY KEY,
  open_price DECIMAL(12,2), high_price DECIMAL(12,2), low_price DECIMAL(12,2),
  close_price DECIMAL(12,2), wap DECIMAL(16,4),
  no_of_shares BIGINT, no_of_trades BIGINT, total_turnover DECIMAL(20,2),
  deliverable_qty BIGINT, pct_deli_qty DECIMAL(6,2),
  spread_high_low DECIMAL(12,2), spread_close_open DECIMAL(12,2)
);
LOAD DATA LOCAL INFILE '/path/to/TVS_Motors.csv' INTO TABLE tvs_motors
FIELDS TERMINATED BY ',' LINES TERMINATED BY '\n' IGNORE 1 LINES
(@d,@o,@h,@l,@c,@w,@s,@tr,@to,@dq,@pd,@shl,@sco)
SET `date` = STR_TO_DATE(@d, '%d-%M-%Y'),
  open_price = NULLIF(@o,''), high_price = NULLIF(@h,''), low_price = NULLIF(@l,''),
  close_price = NULLIF(@c,''), wap = NULLIF(@w,''), no_of_shares = NULLIF(@s,''),
  no_of_trades = NULLIF(@tr,''), total_turnover = NULLIF(@to,''),
  deliverable_qty = NULLIF(@dq,''), pct_deli_qty = NULLIF(@pd,''),
  spread_high_low = NULLIF(@shl,''), spread_close_open = NULLIF(TRIM(@sco),'');


-- ------------------------------------------------------------------------
-- Part 1 · Get to know the data
-- TASK 1: How much history do we have? (Bajaj Auto)
-- Number of trading days, first date and last date for Bajaj Auto.
-- ------------------------------------------------------------------------
SELECT COUNT(*)  AS trading_days,
       MIN(date) AS first_day,
       MAX(date) AS last_day
FROM bajaj_auto;

-- ------------------------------------------------------------------------
-- Part 1 · Get to know the data
-- TASK 2: Eicher's five best closes
-- Date and close price of Eicher Motors' five highest closing prices.
-- ------------------------------------------------------------------------
SELECT date, close_price
FROM eicher_motors
ORDER BY close_price DESC
LIMIT 5;

-- ------------------------------------------------------------------------
-- Part 1 · Get to know the data
-- TASK 3: TCS, year by year
-- Average TCS close per calendar year, rounded to 2 decimals (raw, unadjusted prices).
-- ------------------------------------------------------------------------
SELECT YEAR(date) AS year,
       ROUND(AVG(close_price), 2) AS avg_close
FROM tcs
GROUP BY YEAR(date)
ORDER BY YEAR(date);

-- ------------------------------------------------------------------------
-- Part 1 · Get to know the data
-- TASK 4: Find the holes (NULL deliverable_qty)
-- Every row across all tables where deliverable_qty is NULL.
-- ------------------------------------------------------------------------
SELECT 'bajaj_auto' AS stock, date FROM bajaj_auto WHERE deliverable_qty IS NULL
UNION ALL
SELECT 'eicher_motors' AS stock, date FROM eicher_motors WHERE deliverable_qty IS NULL
UNION ALL
SELECT 'hero_motocorp' AS stock, date FROM hero_motocorp WHERE deliverable_qty IS NULL
UNION ALL
SELECT 'infosys' AS stock, date FROM infosys WHERE deliverable_qty IS NULL
UNION ALL
SELECT 'tcs' AS stock, date FROM tcs WHERE deliverable_qty IS NULL
UNION ALL
SELECT 'tvs_motors' AS stock, date FROM tvs_motors WHERE deliverable_qty IS NULL
ORDER BY date, stock;

-- ------------------------------------------------------------------------
-- Part 2 · The assignment
-- TASK 5: Moving averages → bajaj1
-- 20- and 50-day moving averages of close price for Bajaj Auto; NULL until a full window exists.
-- ------------------------------------------------------------------------
DROP TABLE IF EXISTS bajaj1;
CREATE TABLE bajaj1 AS
SELECT
  date,
  close_price,
  CASE WHEN ROW_NUMBER() OVER (ORDER BY date) >= 20
       THEN ROUND(AVG(close_price) OVER (ORDER BY date ROWS BETWEEN 19 PRECEDING AND CURRENT ROW), 2)
  END AS ma20,
  CASE WHEN ROW_NUMBER() OVER (ORDER BY date) >= 50
       THEN ROUND(AVG(close_price) OVER (ORDER BY date ROWS BETWEEN 49 PRECEDING AND CURRENT ROW), 2)
  END AS ma50
FROM bajaj_auto;

-- ------------------------------------------------------------------------
-- Part 2 · The assignment
-- TASK 6: Master table
-- One row per date with every stock's close price side by side.
-- ------------------------------------------------------------------------
DROP TABLE IF EXISTS master_table;
CREATE TABLE master_table AS
SELECT s_bajaj.date,
       s_bajaj.close_price AS bajaj,
       s_tcs.close_price AS tcs,
       s_tvs.close_price AS tvs,
       s_infosys.close_price AS infosys,
       s_eicher.close_price AS eicher,
       s_hero.close_price AS hero
FROM bajaj_auto s_bajaj
JOIN tcs s_tcs ON s_tcs.date = s_bajaj.date
JOIN tvs_motors s_tvs ON s_tvs.date = s_bajaj.date
JOIN infosys s_infosys ON s_infosys.date = s_bajaj.date
JOIN eicher_motors s_eicher ON s_eicher.date = s_bajaj.date
JOIN hero_motocorp s_hero ON s_hero.date = s_bajaj.date;

-- ------------------------------------------------------------------------
-- Part 2 · The assignment
-- TASK 7: Golden-cross signals → bajaj2
-- Buy on the day ma20 crosses above ma50, Sell when it crosses below, Hold otherwise.
-- ------------------------------------------------------------------------
DROP TABLE IF EXISTS bajaj2;
CREATE TABLE bajaj2 AS
WITH t AS (
  SELECT date, close_price, ma20, ma50,
         LAG(ma20) OVER (ORDER BY date) AS prev_ma20,
         LAG(ma50) OVER (ORDER BY date) AS prev_ma50
  FROM bajaj1
)
SELECT date, close_price,
  CASE
    WHEN ma20 IS NULL OR ma50 IS NULL OR prev_ma20 IS NULL OR prev_ma50 IS NULL THEN 'Hold'
    WHEN ma20 > ma50 AND prev_ma20 <= prev_ma50 THEN 'Buy'
    WHEN ma20 < ma50 AND prev_ma20 >= prev_ma50 THEN 'Sell'
    ELSE 'Hold'
  END AS `signal`
FROM t;

-- ------------------------------------------------------------------------
-- Part 2 · The assignment
-- TASK 8: How often did it trigger?
-- Number of days carrying each signal for Bajaj Auto.
-- ------------------------------------------------------------------------
SELECT `signal`, COUNT(*) AS days
FROM bajaj2
GROUP BY `signal`
ORDER BY `signal`;

-- ------------------------------------------------------------------------
-- Part 2 · The assignment
-- TASK 9: Signal on a given day (2018-06-21)
-- The Bajaj Auto signal on 2018-06-21. (In MySQL this becomes a function.)
-- ------------------------------------------------------------------------
SELECT `signal`
FROM bajaj2
WHERE date = '2018-06-21';

-- MySQL: reusable function (Appendix B of the guide)
DROP FUNCTION IF EXISTS bajaj_signal;
DELIMITER $$
CREATE FUNCTION bajaj_signal(d DATE)
RETURNS VARCHAR(4) DETERMINISTIC READS SQL DATA
BEGIN
  DECLARE s VARCHAR(4);
  SELECT `signal` INTO s FROM bajaj2 WHERE date = d;
  RETURN s;
END $$
DELIMITER ;

SELECT bajaj_signal('2018-06-21') AS `signal`;

-- ------------------------------------------------------------------------
-- Part 2 · The assignment
-- TASK 10: All stocks in one query
-- Buys, sells and latest signal for every stock — no per-stock tables needed.
-- ------------------------------------------------------------------------
WITH prices AS (
  SELECT 'Bajaj Auto' AS stock, date, close_price FROM bajaj_auto
  UNION ALL
  SELECT 'Eicher Motors' AS stock, date, close_price FROM eicher_motors
  UNION ALL
  SELECT 'Hero Motocorp' AS stock, date, close_price FROM hero_motocorp
  UNION ALL
  SELECT 'Infosys' AS stock, date, close_price FROM infosys
  UNION ALL
  SELECT 'TCS' AS stock, date, close_price FROM tcs
  UNION ALL
  SELECT 'TVS Motors' AS stock, date, close_price FROM tvs_motors
),
ma AS (
  SELECT stock, date, close_price AS close_price,
    CASE WHEN ROW_NUMBER() OVER (PARTITION BY stock ORDER BY date) >= 20
         THEN AVG(close_price) OVER (PARTITION BY stock ORDER BY date ROWS BETWEEN 19 PRECEDING AND CURRENT ROW) END AS ma20,
    CASE WHEN ROW_NUMBER() OVER (PARTITION BY stock ORDER BY date) >= 50
         THEN AVG(close_price) OVER (PARTITION BY stock ORDER BY date ROWS BETWEEN 49 PRECEDING AND CURRENT ROW) END AS ma50
  FROM prices
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
),
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
ORDER BY s.stock;

-- ------------------------------------------------------------------------
-- Part 3 · Question the result
-- TASK 11: Who went up? (raw prices)
-- First close, last close and % change per stock — computed on RAW prices (before the fix).
-- ------------------------------------------------------------------------
WITH prices AS (
  SELECT 'Bajaj Auto' AS stock, date, close_price FROM bajaj_auto
  UNION ALL
  SELECT 'Eicher Motors' AS stock, date, close_price FROM eicher_motors
  UNION ALL
  SELECT 'Hero Motocorp' AS stock, date, close_price FROM hero_motocorp
  UNION ALL
  SELECT 'Infosys' AS stock, date, close_price FROM infosys
  UNION ALL
  SELECT 'TCS' AS stock, date, close_price FROM tcs
  UNION ALL
  SELECT 'TVS Motors' AS stock, date, close_price FROM tvs_motors
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
ORDER BY pct_change DESC;

-- ------------------------------------------------------------------------
-- Part 3 · Question the result
-- TASK 12: The data trap — worst day per stock
-- Each stock's single worst day-over-day move. Two rows are ~-50%: those are bonus issues, not crashes.
-- ------------------------------------------------------------------------
WITH prices AS (
  SELECT 'Bajaj Auto' AS stock, date, close_price FROM bajaj_auto
  UNION ALL
  SELECT 'Eicher Motors' AS stock, date, close_price FROM eicher_motors
  UNION ALL
  SELECT 'Hero Motocorp' AS stock, date, close_price FROM hero_motocorp
  UNION ALL
  SELECT 'Infosys' AS stock, date, close_price FROM infosys
  UNION ALL
  SELECT 'TCS' AS stock, date, close_price FROM tcs
  UNION ALL
  SELECT 'TVS Motors' AS stock, date, close_price FROM tvs_motors
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
ORDER BY pct_move;

-- ------------------------------------------------------------------------
-- Part 3 · Question the result
-- TASK 13: Fix it — adjust TCS & Infosys for the 1:1 bonus issues
-- Divide pre-event prices by 2 (TCS before 2018-05-31, Infosys before 2015-06-15) and recompute % change.
-- ------------------------------------------------------------------------
WITH adjusted AS (
  SELECT 'TCS' AS stock, date,
         CASE WHEN date < '2018-05-31' THEN close_price / 2 ELSE close_price END AS adj_close
  FROM tcs
  UNION ALL
  SELECT 'Infosys' AS stock, date,
         CASE WHEN date < '2015-06-15' THEN close_price / 2 ELSE close_price END AS adj_close
  FROM infosys
)
SELECT stock,
       ROUND(100.0 * (MAX(CASE WHEN date = '2018-07-31' THEN adj_close END) /
                      MAX(CASE WHEN date = '2015-01-01' THEN adj_close END) - 1), 1) AS adjusted_pct_change
FROM adjusted
GROUP BY stock
ORDER BY stock;

-- ------------------------------------------------------------------------
-- Part 4 · Extensions for the insights report
-- TASK 14: adj_prices — the clean price table
-- Adjusted close for all stocks (only TCS and Infosys actually change).
-- ------------------------------------------------------------------------
DROP TABLE IF EXISTS adj_prices;
CREATE TABLE adj_prices AS
  SELECT 'Bajaj Auto' AS stock, date, close_price, close_price AS adj_close FROM bajaj_auto
  UNION ALL
  SELECT 'Eicher Motors' AS stock, date, close_price, close_price AS adj_close FROM eicher_motors
  UNION ALL
  SELECT 'Hero Motocorp' AS stock, date, close_price, close_price AS adj_close FROM hero_motocorp
  UNION ALL
  SELECT 'Infosys' AS stock, date, close_price,
         CASE WHEN date < '2015-06-15' THEN close_price / 2 ELSE close_price END AS adj_close
  FROM infosys
  UNION ALL
  SELECT 'TCS' AS stock, date, close_price,
         CASE WHEN date < '2018-05-31' THEN close_price / 2 ELSE close_price END AS adj_close
  FROM tcs
  UNION ALL
  SELECT 'TVS Motors' AS stock, date, close_price, close_price AS adj_close FROM tvs_motors;

-- ------------------------------------------------------------------------
-- Part 4 · Extensions for the insights report
-- TASK 15: adj_signals — signals on adjusted prices
-- Moving averages and Buy/Sell/Hold for every stock using adjusted prices.
-- ------------------------------------------------------------------------
DROP TABLE IF EXISTS adj_signals;
CREATE TABLE adj_signals AS
WITH ma AS (
  SELECT stock, date, adj_close AS close_price,
    CASE WHEN ROW_NUMBER() OVER (PARTITION BY stock ORDER BY date) >= 20
         THEN AVG(adj_close) OVER (PARTITION BY stock ORDER BY date ROWS BETWEEN 19 PRECEDING AND CURRENT ROW) END AS ma20,
    CASE WHEN ROW_NUMBER() OVER (PARTITION BY stock ORDER BY date) >= 50
         THEN AVG(adj_close) OVER (PARTITION BY stock ORDER BY date ROWS BETWEEN 49 PRECEDING AND CURRENT ROW) END AS ma50
  FROM adj_prices
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
)
SELECT * FROM sig;

-- ------------------------------------------------------------------------
-- Part 4 · Extensions for the insights report
-- TASK 16: Signal counts: raw vs adjusted
-- How many signals did the price cliff create or destroy? (Stretch challenge)
-- ------------------------------------------------------------------------
WITH raw AS (
  SELECT 'Bajaj Auto' AS stock, date, close_price FROM bajaj_auto
  UNION ALL
  SELECT 'Eicher Motors' AS stock, date, close_price FROM eicher_motors
  UNION ALL
  SELECT 'Hero Motocorp' AS stock, date, close_price FROM hero_motocorp
  UNION ALL
  SELECT 'Infosys' AS stock, date, close_price FROM infosys
  UNION ALL
  SELECT 'TCS' AS stock, date, close_price FROM tcs
  UNION ALL
  SELECT 'TVS Motors' AS stock, date, close_price FROM tvs_motors
),
ma AS (
  SELECT stock, date, close_price AS close_price,
    CASE WHEN ROW_NUMBER() OVER (PARTITION BY stock ORDER BY date) >= 20
         THEN AVG(close_price) OVER (PARTITION BY stock ORDER BY date ROWS BETWEEN 19 PRECEDING AND CURRENT ROW) END AS ma20,
    CASE WHEN ROW_NUMBER() OVER (PARTITION BY stock ORDER BY date) >= 50
         THEN AVG(close_price) OVER (PARTITION BY stock ORDER BY date ROWS BETWEEN 49 PRECEDING AND CURRENT ROW) END AS ma50
  FROM raw
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
),
raw_sig AS (SELECT stock, SUM(`signal`='Buy') AS raw_buys, SUM(`signal`='Sell') AS raw_sells FROM sig GROUP BY stock),
adj_sig AS (SELECT stock, SUM(`signal`='Buy') AS adj_buys, SUM(`signal`='Sell') AS adj_sells FROM adj_signals GROUP BY stock)
SELECT r.stock, raw_buys, adj_buys, raw_sells, adj_sells,
       (adj_buys + adj_sells) - (raw_buys + raw_sells) AS net_change
FROM raw_sig r JOIN adj_sig a ON a.stock = r.stock
ORDER BY r.stock;

-- ------------------------------------------------------------------------
-- Part 4 · Extensions for the insights report
-- TASK 17: Stretch: which TCS & Infosys signals were fake?
-- Signals that exist on raw prices but not on adjusted prices (or vice-versa), by date.
-- ------------------------------------------------------------------------
WITH raw AS (
  SELECT 'Bajaj Auto' AS stock, date, close_price FROM bajaj_auto
  UNION ALL
  SELECT 'Eicher Motors' AS stock, date, close_price FROM eicher_motors
  UNION ALL
  SELECT 'Hero Motocorp' AS stock, date, close_price FROM hero_motocorp
  UNION ALL
  SELECT 'Infosys' AS stock, date, close_price FROM infosys
  UNION ALL
  SELECT 'TCS' AS stock, date, close_price FROM tcs
  UNION ALL
  SELECT 'TVS Motors' AS stock, date, close_price FROM tvs_motors
),
ma AS (
  SELECT stock, date, close_price AS close_price,
    CASE WHEN ROW_NUMBER() OVER (PARTITION BY stock ORDER BY date) >= 20
         THEN AVG(close_price) OVER (PARTITION BY stock ORDER BY date ROWS BETWEEN 19 PRECEDING AND CURRENT ROW) END AS ma20,
    CASE WHEN ROW_NUMBER() OVER (PARTITION BY stock ORDER BY date) >= 50
         THEN AVG(close_price) OVER (PARTITION BY stock ORDER BY date ROWS BETWEEN 49 PRECEDING AND CURRENT ROW) END AS ma50
  FROM raw
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
)
SELECT r.stock, r.date, r.`signal` AS raw_signal, a.`signal` AS adjusted_signal
FROM sig r
JOIN adj_signals a ON a.stock = r.stock AND a.date = r.date
WHERE r.`signal` <> a.`signal`
ORDER BY r.stock, r.date;

-- ------------------------------------------------------------------------
-- Part 4 · Extensions for the insights report
-- TASK 18: Adjusted % change (all stocks)
-- First vs last adjusted close for all stocks — the corrected version of task 11.
-- ------------------------------------------------------------------------
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
ORDER BY adj_pct_change DESC;

-- ------------------------------------------------------------------------
-- Part 4 · Extensions for the insights report
-- TASK 19: Whipsaws — signals that flipped within 30 days
-- For each stock: how many consecutive signals came less than 30 days apart (adjusted prices).
-- ------------------------------------------------------------------------
WITH flips AS (
  SELECT stock, date, `signal`, close_price,
         LEAD(date)   OVER (PARTITION BY stock ORDER BY date) AS next_date,
         LEAD(`signal`) OVER (PARTITION BY stock ORDER BY date) AS next_signal
  FROM adj_signals
  WHERE `signal` <> 'Hold'
)
SELECT stock,
       COUNT(next_date) AS signal_pairs,
       SUM(DATEDIFF(next_date, date) < 30) AS whipsaws_under_30d,
       ROUND(100.0 * SUM(DATEDIFF(next_date, date) < 30) / COUNT(next_date), 1) AS whipsaw_pct,
       MIN(DATEDIFF(next_date, date)) AS shortest_gap_days
FROM flips
WHERE next_date IS NOT NULL
GROUP BY stock
ORDER BY whipsaw_pct DESC;

-- ------------------------------------------------------------------------
-- Part 4 · Extensions for the insights report
-- TASK 20: Backtest: every completed Buy → Sell trade
-- Buy at each Buy signal's close, sell at the next Sell signal's close (adjusted prices).
-- ------------------------------------------------------------------------
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
       DATEDIFF(next_date, date) AS days_held
FROM s
WHERE `signal` = 'Buy' AND next_signal = 'Sell';

-- ------------------------------------------------------------------------
-- Part 4 · Extensions for the insights report
-- TASK 21: Backtest summary vs buy-and-hold
-- Per stock: number of trades, win rate, average return and average holding period.
-- ------------------------------------------------------------------------
SELECT stock,
       COUNT(*)                                   AS trades,
       SUM(return_pct > 0)                        AS winners,
       ROUND(100.0 * SUM(return_pct > 0) / COUNT(*), 1) AS win_rate_pct,
       ROUND(AVG(return_pct), 2)                  AS avg_return_pct,
       ROUND(SUM(return_pct), 2)                  AS sum_return_pct,
       ROUND(AVG(days_held), 0)                   AS avg_days_held
FROM trades
GROUP BY stock
ORDER BY sum_return_pct DESC;

-- ------------------------------------------------------------------------
-- Part 4 · Extensions for the insights report
-- TASK 22: Maximum drawdown (adjusted prices)
-- Worst peak-to-trough fall in each stock's history.
-- ------------------------------------------------------------------------
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
ORDER BY max_drawdown_pct;

-- ------------------------------------------------------------------------
-- Part 4 · Extensions for the insights report
-- TASK 23: Liquidity & conviction: turnover and delivery %
-- Average daily turnover (₹ crore) and average % of shares actually delivered.
-- ------------------------------------------------------------------------
SELECT stock, ROUND(AVG(turnover_cr), 2) AS avg_daily_turnover_cr, ROUND(AVG(deli), 1) AS avg_delivery_pct
FROM (
  SELECT 'Bajaj Auto' AS stock, total_turnover / 10000000.0 AS turnover_cr, pct_deli_qty AS deli FROM bajaj_auto
  UNION ALL
  SELECT 'Eicher Motors' AS stock, total_turnover / 10000000.0 AS turnover_cr, pct_deli_qty AS deli FROM eicher_motors
  UNION ALL
  SELECT 'Hero Motocorp' AS stock, total_turnover / 10000000.0 AS turnover_cr, pct_deli_qty AS deli FROM hero_motocorp
  UNION ALL
  SELECT 'Infosys' AS stock, total_turnover / 10000000.0 AS turnover_cr, pct_deli_qty AS deli FROM infosys
  UNION ALL
  SELECT 'TCS' AS stock, total_turnover / 10000000.0 AS turnover_cr, pct_deli_qty AS deli FROM tcs
  UNION ALL
  SELECT 'TVS Motors' AS stock, total_turnover / 10000000.0 AS turnover_cr, pct_deli_qty AS deli FROM tvs_motors
) x
GROUP BY stock
ORDER BY avg_daily_turnover_cr DESC;

-- ------------------------------------------------------------------------
-- Part 4 · Extensions for the insights report
-- TASK 24: Best and worst calendar year per stock (adjusted)
-- Year-over-year change of the last close of each year (2015 starts Jan-1; 2018 ends Jul-31).
-- ------------------------------------------------------------------------
WITH yr AS (
  SELECT stock, YEAR(date) AS year, MIN(date) AS first_day, MAX(date) AS last_day
  FROM adj_prices GROUP BY stock, YEAR(date)
)
SELECT y.stock, y.year,
       ROUND(100.0 * (l.adj_close - f.adj_close) / f.adj_close, 1) AS return_in_year_pct
FROM yr y
JOIN adj_prices f ON f.stock = y.stock AND f.date = y.first_day
JOIN adj_prices l ON l.stock = y.stock AND l.date = y.last_day
ORDER BY y.stock, y.year;
