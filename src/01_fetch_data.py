"""
01_fetch_data.py
----------------
Step 1: Fetch Lahore AQI data from OpenWeatherMap API.

API used: Air Pollution API (free tier)
Saves raw data to: data/raw/lahore_aqi_raw.csv
"""

import requests
import pandas as pd
import os
import sys
from datetime import datetime, timedelta
import time

# ── Paths ─────────────────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_DIR  = os.path.join(BASE_DIR, "data", "raw")
os.makedirs(RAW_DIR, exist_ok=True)

# ── Config ────────────────────────────────────────────────────────────────────
sys.path.insert(0, BASE_DIR)
from config import API_KEY, LAT, LON, CITY

# OpenWeatherMap Air Pollution History API
BASE_URL = "http://api.openweathermap.org/data/2.5/air_pollution/history"

# AQI index meaning
AQI_LABELS = {1: "Good", 2: "Fair", 3: "Moderate", 4: "Poor", 5: "Very Poor"}


def fetch_aqi_history(start_dt: datetime, end_dt: datetime) -> list:
    """Fetch hourly AQI data between two datetime objects."""
    start_unix = int(start_dt.timestamp())
    end_unix   = int(end_dt.timestamp())

    params = {
        "lat":   LAT,
        "lon":   LON,
        "start": start_unix,
        "end":   end_unix,
        "appid": API_KEY,
    }

    response = requests.get(BASE_URL, params=params, timeout=15)

    if response.status_code != 200:
        print(f"  API Error {response.status_code}: {response.text}")
        return []

    data = response.json()
    return data.get("list", [])


def parse_records(raw_list: list) -> list:
    """Parse raw API response into flat records."""
    records = []
    for entry in raw_list:
        dt   = datetime.fromtimestamp(entry["dt"])
        aqi  = entry["main"]["aqi"]
        comp = entry.get("components", {})
        records.append({
            "datetime":  dt,
            "date":      dt.date(),
            "hour":      dt.hour,
            "aqi":       aqi,
            "aqi_label": AQI_LABELS.get(aqi, "Unknown"),
            "co":        comp.get("co",    None),  # Carbon Monoxide
            "no2":       comp.get("no2",   None),  # Nitrogen Dioxide
            "o3":        comp.get("o3",    None),  # Ozone
            "pm2_5":     comp.get("pm2_5", None),  # Fine particles
            "pm10":      comp.get("pm10",  None),  # Coarse particles
            "so2":       comp.get("so2",   None),  # Sulphur Dioxide
        })
    return records


def main():
    print("=" * 55)
    print("LAHORE AQI DASHBOARD — Data Fetching")
    print("=" * 55)
    print(f"City : {CITY}")
    print(f"Lat  : {LAT}, Lon: {LON}")

    # Fetch last 12 months in monthly chunks (API limit)
    end_dt   = datetime.now()
    start_dt = end_dt - timedelta(days=365)

    all_records = []
    chunk_start = start_dt

    print(f"\nFetching data from {start_dt.date()} to {end_dt.date()}...")

    while chunk_start < end_dt:
        chunk_end = min(chunk_start + timedelta(days=30), end_dt)
        print(f"  Fetching: {chunk_start.date()} → {chunk_end.date()}")

        raw     = fetch_aqi_history(chunk_start, chunk_end)
        records = parse_records(raw)
        all_records.extend(records)
        print(f"  Got {len(records)} records")

        chunk_start = chunk_end
        time.sleep(0.5)  # Avoid hitting API rate limits

    if not all_records:
        print("\nERROR: No data fetched. Check your API key in config.py")
        sys.exit(1)

    df = pd.DataFrame(all_records)
    df = df.sort_values("datetime").reset_index(drop=True)

    out = os.path.join(RAW_DIR, "lahore_aqi_raw.csv")
    df.to_csv(out, index=False)

    print(f"\nTotal records fetched : {len(df):,}")
    print(f"Date range            : {df['date'].min()} → {df['date'].max()}")
    print(f"AQI range             : {df['aqi'].min()} – {df['aqi'].max()}")
    print(f"\nAQI distribution:")
    print(df["aqi_label"].value_counts())
    print(f"\n✔  Saved to {out}")


if __name__ == "__main__":
    main()