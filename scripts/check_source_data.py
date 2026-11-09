"""Checks official source data location; never generates or substitutes records."""
from pathlib import Path
root=Path(__file__).resolve().parents[1]
required=[root/'data/raw/yellow_tripdata_2025-01.parquet',root/'data/reference/taxi_zone_lookup.csv']
for file in required:
    print(f'{"OK" if file.exists() and file.stat().st_size>0 else "MISSING"}: {file}')
if not all(f.exists() and f.stat().st_size>0 for f in required):
    raise SystemExit('Download TLC source data with python scripts/download_data.py')
