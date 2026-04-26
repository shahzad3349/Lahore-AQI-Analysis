"""
05_forecasting.py
-----------------
Step 5: Forecast the AQI for the next 7 days.

Methods:
  1. Moving Average (simple, interpretable)
  2. ARIMA (time series forecasting)

Best forecast saved to: outputs/models/forecast.csv
Forecast plot saved to: outputs/graphs/forecast.png
"""

import pandas as pd
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import os
import warnings
warnings.filterwarnings("ignore")

matplotlib.use("Agg")

BASE_DIR   = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROC_DIR   = os.path.join(BASE_DIR, "data", "processed")
MODELS_DIR = os.path.join(BASE_DIR, "outputs", "models")
GRAPHS_DIR = os.path.join(BASE_DIR, "outputs", "graphs")
IN_FILE    = os.path.join(PROC_DIR, "03_daily.csv")
os.makedirs(MODELS_DIR, exist_ok=True)

plt.rcParams.update({
    "figure.facecolor": "white", "axes.facecolor":   "white",
    "axes.spines.top":  False,   "axes.spines.right": False,
    "font.family":      "DejaVu Sans",
})

FORECAST_DAYS = 7
AQI_LABELS = {1: "Good", 2: "Fair", 3: "Moderate", 4: "Poor", 5: "Very Poor"}


def moving_average_forecast(series: pd.Series, days: int = 7) -> np.ndarray:
    """Simple moving average forecast using last 14 days."""
    window = min(14, len(series))
    avg    = series.iloc[-window:].mean()
    return np.full(days, round(avg, 3))


def arima_forecast(series: pd.Series, days: int = 7) -> np.ndarray:
    """ARIMA(1,1,1) forecast."""
    try:
        from statsmodels.tsa.arima.model import ARIMA
        model  = ARIMA(series, order=(1, 1, 1))
        result = model.fit()
        fc     = result.forecast(steps=days)
        return np.clip(fc.values, 1, 5).round(3)
    except Exception as e:
        print(f"  ARIMA failed ({e}), falling back to Moving Average")
        return moving_average_forecast(series, days)


def plot_forecast(daily, forecast_df, method_name):
    fig, ax = plt.subplots(figsize=(12, 4))

    # Last 60 days actual
    recent = daily.tail(60)
    ax.plot(recent["date"], recent["aqi_mean"],
            color="#2c3e50", linewidth=1.5, label="Actual AQI")
    ax.fill_between(recent["date"], recent["aqi_mean"], alpha=0.2, color="#2c3e50")

    # Forecast
    ax.plot(forecast_df["date"], forecast_df["aqi_forecast"],
            color="#e74c3c", linewidth=2, linestyle="--",
            marker="o", markersize=6, label=f"Forecast ({method_name})")
    ax.fill_between(forecast_df["date"],
                    forecast_df["aqi_forecast"] - 0.3,
                    forecast_df["aqi_forecast"] + 0.3,
                    alpha=0.2, color="#e74c3c")

    ax.axhline(3, color="#e67e22", linestyle=":", linewidth=0.8, alpha=0.6)
    ax.axhline(4, color="#8e44ad", linestyle=":", linewidth=0.8, alpha=0.6)
    ax.set_title(f"Lahore AQI — Last 60 Days + {FORECAST_DAYS}-Day Forecast")
    ax.set_ylabel("AQI Index (1=Good, 5=Very Poor)")
    ax.set_ylim(0, 5.5)
    ax.legend(fontsize=9)

    path = os.path.join(GRAPHS_DIR, "forecast.png")
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved: forecast.png")


def main():
    print("=" * 55)
    print("LAHORE AQI DASHBOARD — Forecasting")
    print("=" * 55)

    daily = pd.read_csv(IN_FILE, parse_dates=["date"])
    daily = daily.sort_values("date")
    series = daily["aqi_mean"].dropna()

    print(f"Training data: {len(series)} days")
    print(f"Forecasting next {FORECAST_DAYS} days...\n")

    # Try ARIMA first, fallback to MA
    print("Method 1: Moving Average")
    ma_fc = moving_average_forecast(series, FORECAST_DAYS)

    print("Method 2: ARIMA")
    arima_fc = arima_forecast(series, FORECAST_DAYS)

    # Build forecast dates
    last_date      = daily["date"].max()
    forecast_dates = pd.date_range(last_date + pd.Timedelta(days=1), periods=FORECAST_DAYS)

    # Use ARIMA if available, else MA
    final_fc = arima_fc

    forecast_df = pd.DataFrame({
        "date":           forecast_dates,
        "aqi_forecast":   np.clip(final_fc, 1, 5).round(2),
        "ma_forecast":    np.clip(ma_fc, 1, 5).round(2),
    })

    forecast_df["aqi_label"] = forecast_df["aqi_forecast"].round().astype(int).clip(1,5).map(AQI_LABELS)

    print(f"\n7-Day AQI Forecast for Lahore:")
    print(forecast_df[["date", "aqi_forecast", "aqi_label"]].to_string(index=False))

    # Save
    out = os.path.join(MODELS_DIR, "forecast.csv")
    forecast_df.to_csv(out, index=False)
    plot_forecast(daily, forecast_df, "ARIMA")

    print(f"\n✔  Forecast saved to {out}")


if __name__ == "__main__":
    main()
