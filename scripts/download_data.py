#!/usr/bin/env python3
"""Download official NYC TLC January 2025 data directly from NYC's public hosting.

Usage: python scripts/download_data.py
"""
from pathlib import Path
from urllib.request import urlretrieve

ROOT = Path(__file__).resolve().parents[1]
FILES = {
    ROOT / 'data/raw/yellow_tripdata_2025-01.parquet': 'https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2025-01.parquet',
    ROOT / 'data/reference/taxi_zone_lookup.csv': 'https://d37ci6vzurychx.cloudfront.net/misc/taxi_zone_lookup.csv',
}

for destination, url in FILES.items():
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.is_file() and destination.stat().st_size:
        print(f'Already present: {destination}')
        continue
    print(f'Downloading {url} -> {destination}')
    try:
        urlretrieve(url, destination)
    except Exception:
        destination.unlink(missing_ok=True)
        raise
    print(f'Saved {destination.stat().st_size:,} bytes')
print('Source download finished. Data attribution: NYC TLC.')
