"""
04_eda_graphs.py
----------------
Step 4: Generate 7 EDA visualizations.

Graphs saved to outputs/graphs/:
  1. aqi_trend.png          - Daily AQI trend over time
  2. monthly_avg.png        - Monthly average AQI bar chart
  3. hourly_pattern.png     - AQI by hour of day
  4. season_comparison.png  - Season-wise AQI distribution (boxplot)
  5. worst_days.png         - Top 10 worst AQI days
  6. pollutants_heatmap.png - Monthly pollutant levels heatmap
  7. aqi_distribution.png   - AQI category pie chart
"""

import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
import os

matplotlib.use("Agg")

BASE_DIR   = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROC_DIR   = os.path.join(BASE_DIR, "data", "processed")
GRAPHS_DIR = os.path.join(BASE_DIR, "outputs", "graphs")
os.makedirs(GRAPHS_DIR, exist_ok=True)

plt.rcParams.update({
    "figure.facecolor":  "white", "axes.facecolor":    "white",
    "axes.spines.top":   False,   "axes.spines.right":  False,
    "font.family":       "DejaVu Sans",
    "axes.titlesize":    13,      "axes.labelsize":     11,
})

AQI_COLORS = {
    "Good":      "#2ecc71",
    "Fair":      "#f1c40f",
    "Moderate":  "#e67e22",
    "Poor":      "#e74c3c",
    "Very Poor": "#8e44ad",
}


def save(fig, name):
    path = os.path.join(GRAPHS_DIR, name)
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved: {name}")


def plot_aqi_trend(daily):
    fig, ax = plt.subplots(figsize=(12, 4))
    ax.fill_between(daily["date"], daily["aqi_mean"], alpha=0.3, color="#e74c3c")
    ax.plot(daily["date"], daily["aqi_mean"],     color="#e74c3c", linewidth=0.8, label="Daily AQI")
    ax.plot(daily["date"], daily["aqi_7day_avg"], color="#2c3e50", linewidth=1.5, label="7-day avg")
    ax.axhline(3, color="#e67e22", linestyle="--", linewidth=0.8, alpha=0.7, label="Moderate threshold")
    ax.axhline(4, color="#8e44ad", linestyle="--", linewidth=0.8, alpha=0.7, label="Poor threshold")
    ax.set_title("Lahore Daily AQI Trend")
    ax.set_ylabel("AQI Index (1=Good, 5=Very Poor)")
    ax.set_ylim(0, 5.5)
    ax.legend(fontsize=8)
    fig.tight_layout()
    save(fig, "aqi_trend.png")


def plot_monthly_avg(monthly):
    fig, ax = plt.subplots(figsize=(9, 4))
    colors = ["#2ecc71" if v <= 2 else "#e67e22" if v <= 3 else "#e74c3c"
              for v in monthly["aqi_mean"]]
    bars = ax.bar(monthly["month_name"], monthly["aqi_mean"], color=colors)
    ax.bar_label(bars, fmt="%.1f", padding=3, fontsize=9)
    ax.set_title("Monthly Average AQI — Lahore")
    ax.set_ylabel("Average AQI")
    ax.set_ylim(0, 5.5)
    ax.axhline(3, color="#e67e22", linestyle="--", linewidth=0.8, alpha=0.6)
    fig.tight_layout()
    save(fig, "monthly_avg.png")


def plot_hourly_pattern(hourly):
    fig, ax = plt.subplots(figsize=(9, 4))
    ax.fill_between(hourly["hour"], hourly["aqi_mean"], alpha=0.4, color="#3498db")
    ax.plot(hourly["hour"], hourly["aqi_mean"], color="#2980b9", linewidth=2,
            marker="o", markersize=4)
    ax.set_title("Average AQI by Hour of Day")
    ax.set_xlabel("Hour (0 = Midnight, 12 = Noon)")
    ax.set_ylabel("Average AQI")
    ax.set_xticks(range(0, 24, 2))
    ax.set_ylim(0, 5.5)
    fig.tight_layout()
    save(fig, "hourly_pattern.png")


def plot_season_comparison(daily):
    season_order  = ["Winter", "Spring", "Summer", "Autumn"]
    season_colors = {"Winter": "#3498db", "Spring": "#2ecc71",
                     "Summer": "#e74c3c", "Autumn": "#e67e22"}
    fig, ax = plt.subplots(figsize=(8, 4))
    data   = [daily[daily["season"] == s]["aqi_mean"].dropna().values
              for s in season_order if s in daily["season"].values]
    labels = [s for s in season_order if s in daily["season"].values]
    colors = [season_colors[s] for s in labels]
    bp = ax.boxplot(data, labels=labels, patch_artist=True)
    for patch, color in zip(bp["boxes"], colors):
        patch.set_facecolor(color)
        patch.set_alpha(0.7)
    ax.set_title("AQI Distribution by Season — Lahore")
    ax.set_ylabel("AQI Index")
    fig.tight_layout()
    save(fig, "season_comparison.png")


def plot_worst_days(daily):
    worst = daily.nlargest(10, "aqi_mean")[["date", "aqi_mean", "season"]].copy()
    worst["date_str"] = worst["date"].astype(str)
    fig, ax = plt.subplots(figsize=(9, 5))
    colors = [AQI_COLORS.get("Very Poor") if v >= 4.5 else AQI_COLORS.get("Poor")
              for v in worst["aqi_mean"]]
    bars = ax.barh(worst["date_str"], worst["aqi_mean"], color=colors)
    ax.bar_label(bars, fmt="%.2f", padding=3, fontsize=9)
    ax.set_title("Top 10 Worst AQI Days — Lahore")
    ax.set_xlabel("Average AQI")
    ax.set_xlim(0, 5.5)
    ax.invert_yaxis()
    fig.tight_layout()
    save(fig, "worst_days.png")


def plot_pollutants_heatmap(daily):
    monthly_poll = daily.groupby("month_name").agg(
        PM2_5 = ("pm2_5_mean", "mean"),
        PM10  = ("pm10_mean",  "mean"),
        NO2   = ("no2_mean",   "mean"),
        O3    = ("o3_mean",    "mean"),
    ).round(2)
    month_order  = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                    "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    monthly_poll = monthly_poll.reindex(
        [m for m in month_order if m in monthly_poll.index]
    )
    fig, ax = plt.subplots(figsize=(10, 5))
    sns.heatmap(monthly_poll.T, annot=True, fmt=".1f", cmap="YlOrRd",
                ax=ax, linewidths=0.5, annot_kws={"size": 8})
    ax.set_title("Monthly Pollutant Levels — Lahore (µg/m³)")
    fig.tight_layout()
    save(fig, "pollutants_heatmap.png")


def plot_aqi_distribution(daily):
    counts = daily["aqi_category"].value_counts()
    order  = ["Good", "Fair", "Moderate", "Poor", "Very Poor"]
    counts = counts.reindex([o for o in order if o in counts.index])
    colors = [AQI_COLORS.get(k, "#999") for k in counts.index]
    fig, ax = plt.subplots(figsize=(6, 6))
    ax.pie(counts.values, labels=counts.index, colors=colors,
           autopct="%1.1f%%", startangle=140, pctdistance=0.8)
    ax.set_title("AQI Category Distribution — Lahore")
    fig.tight_layout()
    save(fig, "aqi_distribution.png")


def main():
    print("=" * 55)
    print("LAHORE AQI DASHBOARD — EDA Graphs")
    print("=" * 55)

    daily   = pd.read_csv(os.path.join(PROC_DIR, "03_daily.csv"),   parse_dates=["date"])
    hourly  = pd.read_csv(os.path.join(PROC_DIR, "03_hourly.csv"))
    monthly = pd.read_csv(os.path.join(PROC_DIR, "03_monthly.csv"))

    print("Generating 7 graphs...")
    plot_aqi_trend(daily)
    plot_monthly_avg(monthly)
    plot_hourly_pattern(hourly)
    plot_season_comparison(daily)
    plot_worst_days(daily)
    plot_pollutants_heatmap(daily)
    plot_aqi_distribution(daily)

    print(f"\n✔  All graphs saved to {GRAPHS_DIR}")


if __name__ == "__main__":
    main()