"""
02_data_cleaning.py
-------------------
Step 2: Clean the raw AQI dataset.

Operations:
  - Remove duplicate records
  - Handle missing values
  - Fix data types
  - Check for outliers
  - Add useful time-based columns
"""

import pandas as pd
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROC_DIR = os.path.join(BASE_DIR, "data", "processed")
IN_FILE  = os.path.join(BASE_DIR, "data", "raw", "lahore_aqi_raw.csv")
OUT_FILE = os.path.join(PROC_DIR, "02_cleaned.csv")
os.makedirs(PROC_DIR, exist_ok=True)


def clean(df: pd.DataFrame) -> pd.DataFrame:
    print(f"Input shape: {df.shape}")

    # 1. Parse datetime columns
    df["datetime"] = pd.to_datetime(df["datetime"])
    df["date"]     = pd.to_datetime(df["date"])

    # 2. Remove duplicate rows
    before = len(df)
    df = df.drop_duplicates(subset=["datetime"])
    print(f"Duplicates removed: {before - len(df)}")

    # 3. Sort chronologically
    df = df.sort_values("datetime").reset_index(drop=True)

    # 4. Fill missing pollutant values using forward fill then backward fill
    pollutant_cols = ["co", "no2", "o3", "pm2_5", "pm10", "so2"]
    for col in pollutant_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")
        df[col] = df[col].ffill().bfill()

    # 5. Keep only valid AQI values (1 to 5)
    df = df[df["aqi"].between(1, 5)].copy()

    # 6. Add useful time-based columns
    df["month"]       = df["datetime"].dt.month
    df["month_name"]  = df["datetime"].dt.strftime("%b")
    df["day_of_week"] = df["datetime"].dt.day_name()
    df["season"]      = df["month"].map({
        12: "Winter", 1: "Winter",  2: "Winter",
        3:  "Spring", 4: "Spring",  5: "Spring",
        6:  "Summer", 7: "Summer",  8: "Summer",
        9:  "Autumn", 10: "Autumn", 11: "Autumn",
    })

    print(f"Cleaned shape: {df.shape}")
    print(f"\nMissing values:\n{df.isnull().sum()[df.isnull().sum() > 0]}")
    return df


def main():
    print("=" * 55)
    print("LAHORE AQI DASHBOARD — Data Cleaning")
    print("=" * 55)

    df       = pd.read_csv(IN_FILE)
    df_clean = clean(df)

    print(f"\nAQI Label distribution:")
    print(df_clean["aqi_label"].value_counts())

    df_clean.to_csv(OUT_FILE, index=False)
    print(f"\n✔  Saved to {OUT_FILE}")


if __name__ == "__main__":
    main()