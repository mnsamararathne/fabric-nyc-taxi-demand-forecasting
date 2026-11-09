#!/usr/bin/env python3
"""Offline alternative to Microsoft Fabric using DuckDB + scikit-learn.

After downloading NYC TLC source files:
  pip install -r requirements-local.txt
  python scripts/run_local.py

Produces reproducible locally calculated metrics, not Fabric Delta tables.
Do not claim model performance until you have executed this script.
"""
import json
from pathlib import Path
import duckdb
import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / 'data/raw/yellow_tripdata_2025-01.parquet'
LOOKUP = ROOT / 'data/reference/taxi_zone_lookup.csv'
OUT = ROOT / 'results/local_run'
OUT.mkdir(parents=True, exist_ok=True)
for p in (RAW, LOOKUP):
    if not p.exists():
        raise FileNotFoundError(f'Missing {p}. First run python scripts/download_data.py')

db = duckdb.connect(str(OUT / 'nyc_taxi.duckdb'))
db.execute("SET memory_limit='3GB'")
# Escaping literal paths for SQL statements.
raw_path = str(RAW).replace("'", "''")
lookup_path = str(LOOKUP).replace("'", "''")
db.execute(f"CREATE OR REPLACE VIEW bronze AS SELECT * FROM read_parquet('{raw_path}')")
db.execute(f"CREATE OR REPLACE VIEW zone_lookup AS SELECT * FROM read_csv_auto('{lookup_path}', HEADER=TRUE)")

db.execute('''CREATE OR REPLACE TABLE silver AS
SELECT b.*, z.Borough AS pickup_borough, z.Zone AS pickup_zone,
 z.service_zone AS pickup_service_zone,
 CASE WHEN PULocationID=264 THEN 'UNKNOWN' WHEN PULocationID=265 THEN 'OUTSIDE_NYC' ELSE 'VALID' END AS geographic_quality_flag,
 CASE WHEN tpep_pickup_datetime IS NULL THEN 'MISSING_TIMESTAMP'
      WHEN tpep_pickup_datetime < TIMESTAMP '2025-01-01' THEN 'BEFORE_PERIOD'
      WHEN tpep_pickup_datetime >= TIMESTAMP '2025-02-01' THEN 'AFTER_PERIOD'
      ELSE 'IN_PERIOD' END AS reporting_period_flag,
 CASE WHEN trip_distance IS NULL OR isnan(trip_distance) THEN 'MISSING_OR_NAN'
      WHEN trip_distance < 0 THEN 'NEGATIVE' WHEN trip_distance=0 THEN 'ZERO'
      WHEN trip_distance > 100 THEN 'EXTREME' ELSE 'NORMAL' END AS distance_quality_flag,
 date_diff('second',tpep_pickup_datetime,tpep_dropoff_datetime)/60.0 AS trip_duration_minutes,
 CASE WHEN tpep_pickup_datetime IS NULL OR tpep_dropoff_datetime IS NULL THEN 'MISSING'
      WHEN date_diff('second',tpep_pickup_datetime,tpep_dropoff_datetime)<0 THEN 'NEGATIVE'
      WHEN date_diff('second',tpep_pickup_datetime,tpep_dropoff_datetime)=0 THEN 'ZERO'
      WHEN date_diff('second',tpep_pickup_datetime,tpep_dropoff_datetime)>10800 THEN 'LONG'
      ELSE 'NORMAL' END AS duration_quality_flag,
 (PULocationID IS NOT NULL AND PULocationID NOT IN (264,265)
  AND tpep_pickup_datetime >= TIMESTAMP '2025-01-01'
  AND tpep_pickup_datetime < TIMESTAMP '2025-02-01') AS pickup_eligible_flag
FROM bronze b LEFT JOIN zone_lookup z ON b.PULocationID=z.LocationID
''')

db.execute('''CREATE OR REPLACE TABLE gold AS
WITH observed AS (
 SELECT PULocationID, date_trunc('hour',tpep_pickup_datetime) AS pickup_hour,
        count(*)::BIGINT AS pickup_count
 FROM silver WHERE pickup_eligible_flag GROUP BY 1,2
), zones AS (SELECT DISTINCT PULocationID FROM observed),
calendar AS (SELECT unnest(generate_series(TIMESTAMP '2025-01-01 00:00:00',TIMESTAMP '2025-01-31 23:00:00',INTERVAL 1 HOUR)) AS pickup_hour)
SELECT zones.PULocationID, calendar.pickup_hour, coalesce(observed.pickup_count,0)::BIGINT AS pickup_count
FROM zones CROSS JOIN calendar LEFT JOIN observed
ON zones.PULocationID=observed.PULocationID AND calendar.pickup_hour=observed.pickup_hour
''')

db.execute('''CREATE OR REPLACE TABLE features AS
WITH base AS (
SELECT *,
 extract('hour' FROM pickup_hour)::INTEGER AS hour_of_day,
 ((extract('isodow' FROM pickup_hour)::INTEGER+6)%7)::INTEGER AS day_of_week,
 extract('day' FROM pickup_hour)::INTEGER AS day_of_month,
 extract('month' FROM pickup_hour)::INTEGER AS month,
 (extract('isodow' FROM pickup_hour) IN (6,7))::INTEGER AS is_weekend,
 lag(pickup_count,1) OVER w AS lag_1,
 lag(pickup_count,2) OVER w AS lag_2,
 lag(pickup_count,24) OVER w AS lag_24,
 lag(pickup_count,168) OVER w AS lag_168,
 round(avg(pickup_count) OVER (PARTITION BY PULocationID ORDER BY pickup_hour ROWS BETWEEN 3 PRECEDING AND 1 PRECEDING),2) AS rolling_mean_3h,
 round(avg(pickup_count) OVER (PARTITION BY PULocationID ORDER BY pickup_hour ROWS BETWEEN 24 PRECEDING AND 1 PRECEDING),2) AS rolling_mean_24h
FROM gold WINDOW w AS (PARTITION BY PULocationID ORDER BY pickup_hour)
)
SELECT * FROM base
''')

counts = db.execute('''SELECT (SELECT count(*) FROM bronze) AS bronze_rows,
 (SELECT count(*) FROM silver) AS silver_rows,
 (SELECT count(*) FROM silver WHERE pickup_eligible_flag) AS eligible_rows,
 (SELECT count(*) FROM gold) AS gold_rows,
 (SELECT count(*) FROM gold WHERE pickup_count=0) AS zero_rows,
 (SELECT sum(pickup_count) FROM gold) AS aggregated_pickups,
 (SELECT count(*) FROM features WHERE lag_168 IS NOT NULL) AS model_rows''').df().iloc[0].to_dict()
print('Pipeline counts:',counts)
assert counts['bronze_rows']==counts['silver_rows']
assert counts['eligible_rows']==counts['aggregated_pickups']
assert counts['gold_rows']==192696, 'Unexpected zone count; NYC may revise source data'

# Read only the compact, historical-featured model panel into pandas.
# All models fit on the same chronological training interval; the test window
# is used only after selection from validation MAE.
import sys
sys.path.insert(0, str(ROOT))
from src.experiment import run_experiments

panel = db.execute('''SELECT * FROM features WHERE lag_168 IS NOT NULL ORDER BY PULocationID,pickup_hour''').df()
results = run_experiments(panel, OUT)
print('Selected by validation:', results['selected_by_validation_MAE'])
print('Validation weekly MAE:', round(results['validation_reference_weekly_MAE'],4))
print('Wrote verified ML results and charts to', OUT)
