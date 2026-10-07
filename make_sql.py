"""Writes sql/stock_analysis.sql (SQLite) and sql/stock_analysis_mysql.sql (MySQL 8) for all six stocks."""
import os, tasks
tasks.write_sql_files(list(tasks.DISPLAY), os.path.join(os.path.dirname(os.path.abspath(__file__)), "sql"))
