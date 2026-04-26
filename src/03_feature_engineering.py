"""
03_feature_engineering.py
--------------------------
Step 3: Extract meaningful features from hourly data.

Creates:
  - Daily averages  (date-level dataset)
  - Rolling 7-day and 30-day averages
  - Hourly AQI patterns (average by hour of day)
  - Monthly aggregates
  - Pollution severity flags (bad day indicator)
"""

import pandas as pd
import numpy as np
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROC_DIR = os.path.join(BASE_DIR, "data", "processed")
IN_FILE  = os.path.join(PROC_DIR, "02_cleaned.csv")
os.makedirs(PROC_DIR, exist_ok=True)


def build_daily(df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate hourly records to daily level."""
    daily = df.groupby("date").agg(
        aqi_mean   = ("aqi",   "mean"),
        aqi_max    = ("aqi",   "max"),
        aqi_min    = ("aqi",   "min"),
        pm2_5_mean = ("pm2_5", "mean"),
        pm10_mean  = ("pm10",  "mean"),
        no2_mean   = ("no2",   "mean"),
        o3_mean    = ("o3",    "mean"),
        co_mean    = ("co",    "mean"),
        so2_mean   = ("so2",   "mean"),
        month      = ("month", "first"),
        month_name = ("month_name", "first"),
        season     = ("season", "first"),
    ).reset_index()

    daily["date"] = pd.to_datetime(daily["date"])
    daily = daily.sort_values("date")

    # Rolling averages
    daily["aqi_7day_avg"]  = daily["aqi_mean"].rolling(7,  min_periods=1).mean().round(2)
    daily["aqi_30day_avg"] = daily["aqi_mean"].rolling(30, min_periods=1).mean().round(2)

    # Flag days where AQI is Poor or worse
    daily["is_bad_day"] = (daily["aqi_mean"] >= 4).astype(int)

    # Categorize daily mean AQI
    def categorize(val):
        if val <= 1.5:   return "Good"
        elif val <= 2.5: return "Fair"
        elif val <= 3.5: return "Moderate"
        elif val <= 4.5: return "Poor"
        else:            return "Very Poor"

    daily["aqi_category"] = daily["aqi_mean"].apply(categorize)
    return daily


def build_hourly_pattern(df: pd.DataFrame) -> pd.DataFrame:
    """Compute average AQI by hour of day across all records."""
    return df.groupby("hour").agg(
        aqi_mean   = ("aqi",   "mean"),
        pm2_5_mean = ("pm2_5", "mean"),
    ).reset_index().round(3)


def build_monthly(daily: pd.DataFrame) -> pd.DataFrame:
    """Compute monthly summary statistics."""
    return daily.groupby(["month", "month_name"]).agg(
        aqi_mean   = ("aqi_mean",  "mean"),
        aqi_max    = ("aqi_max",   "max"),
        bad_days   = ("is_bad_day","sum"),
        total_days = ("date",      "count"),
    ).reset_index().sort_values("month").round(3)


def main():
    print("=" * 55)
    print("LAHORE AQI DASHBOARD — Feature Engineering")
    print("=" * 55)

    df = pd.read_csv(IN_FILE)
    df["datetime"] = pd.to_datetime(df["datetime"])

    print(f"Hourly records: {len(df):,}")

    # Build all datasets
    daily   = build_daily(df)
    hourly  = build_hourly_pattern(df)
    monthly = build_monthly(daily)

    # Save outputs
    daily.to_csv(  os.path.join(PROC_DIR, "03_daily.csv"),   index=False)
    hourly.to_csv( os.path.join(PROC_DIR, "03_hourly.csv"),  index=False)
    monthly.to_csv(os.path.join(PROC_DIR, "03_monthly.csv"), index=False)

    print(f"\nDaily records   : {len(daily)}")
    print(f"Hourly patterns : {len(hourly)}")
    print(f"Monthly summary : {len(monthly)}")
    print(f"\nWorst days (AQI >= 4):")
    print(daily[daily["is_bad_day"] == 1][["date", "aqi_mean", "season"]].tail(5))
    print(f"\n✔  All files saved to {PROC_DIR}")


if __name__ == "__main__":
    main()