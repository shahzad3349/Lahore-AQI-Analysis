"""
app.py — Lahore Air Quality Dashboard (Streamlit)
Run: streamlit run app.py
"""

import streamlit as st
import pandas as pd
import numpy as np
import os
import sys
from datetime import datetime, timedelta

st.set_page_config(
    page_title="Lahore AQI Dashboard",
    page_icon="🌫️",
    layout="wide",
)

BASE_DIR   = os.path.dirname(os.path.abspath(__file__))
PROC_DIR   = os.path.join(BASE_DIR, "data", "processed")
GRAPHS_DIR = os.path.join(BASE_DIR, "outputs", "graphs")
MODELS_DIR = os.path.join(BASE_DIR, "outputs", "models")

AQI_COLORS = {
    "Good":      "#2ecc71",
    "Fair":      "#f1c40f",
    "Moderate":  "#e67e22",
    "Poor":      "#e74c3c",
    "Very Poor": "#8e44ad",
}
AQI_LABELS = {1: "Good", 2: "Fair", 3: "Moderate", 4: "Poor", 5: "Very Poor"}


@st.cache_data
def load_daily():
    path = os.path.join(PROC_DIR, "03_daily.csv")
    if not os.path.exists(path):
        return None
    df = pd.read_csv(path, parse_dates=["date"])
    return df.sort_values("date")


@st.cache_data
def load_hourly():
    path = os.path.join(PROC_DIR, "03_hourly.csv")
    return pd.read_csv(path) if os.path.exists(path) else None


@st.cache_data
def load_monthly():
    path = os.path.join(PROC_DIR, "03_monthly.csv")
    return pd.read_csv(path) if os.path.exists(path) else None


@st.cache_data
def load_forecast():
    path = os.path.join(MODELS_DIR, "forecast.csv")
    if not os.path.exists(path):
        return None
    df = pd.read_csv(path, parse_dates=["date"])
    return df


def aqi_badge(label):
    color = AQI_COLORS.get(label, "#999")
    return f"<span style='background:{color};color:white;padding:3px 10px;border-radius:12px;font-weight:500;font-size:13px'>{label}</span>"


# ── Header ────────────────────────────────────────────────────────────────────
st.title("🌫️ Lahore Air Quality Dashboard")
st.caption("Real-time AQI analytics powered by OpenWeatherMap API")

daily = load_daily()

if daily is None:
    st.error("⚠️ Run the pipeline first: python src/01_fetch_data.py → ... → src/05_forecasting.py")
    st.stop()

# ── Top KPI Cards ──────────────────────────────────────────────────────────────
latest       = daily.iloc[-1]
latest_aqi   = round(latest["aqi_mean"], 1)
latest_label = latest["aqi_category"]
worst_day    = daily.loc[daily["aqi_mean"].idxmax()]
best_day     = daily.loc[daily["aqi_mean"].idxmin()]
bad_days     = int(daily["is_bad_day"].sum())

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("📅 Latest AQI", f"{latest_aqi}", help=f"Date: {latest['date'].date()}")
    st.markdown(aqi_badge(latest_label), unsafe_allow_html=True)
with col2:
    st.metric("😷 Worst Day AQI", f"{worst_day['aqi_mean']:.1f}")
    st.caption(f"{worst_day['date'].date()}")
with col3:
    st.metric("🌿 Best Day AQI", f"{best_day['aqi_mean']:.1f}")
    st.caption(f"{best_day['date'].date()}")
with col4:
    st.metric("⚠️ Bad Air Days", bad_days, help="Days with AQI ≥ 4 (Poor or worse)")

st.markdown("---")

# ── Tabs ──────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs(["📈 Trends", "🕐 Patterns", "🔮 Forecast", "📊 All Graphs"])

# ── Tab 1: Trends ─────────────────────────────────────────────────────────────
with tab1:
    st.subheader("AQI Trend Over Time")

    # Date filter
    col_a, col_b = st.columns(2)
    with col_a:
        start_date = st.date_input("From", value=daily["date"].min().date())
    with col_b:
        end_date = st.date_input("To", value=daily["date"].max().date())

    filtered = daily[(daily["date"].dt.date >= start_date) &
                     (daily["date"].dt.date <= end_date)]

    if len(filtered) == 0:
        st.warning("No data in selected range.")
    else:
        st.line_chart(filtered.set_index("date")[["aqi_mean", "aqi_7day_avg"]],
                      use_container_width=True)

        # AQI trend image
        img = os.path.join(GRAPHS_DIR, "aqi_trend.png")
        if os.path.exists(img):
            st.image(img, use_container_width=True)

    st.subheader("Monthly Average AQI")
    img = os.path.join(GRAPHS_DIR, "monthly_avg.png")
    if os.path.exists(img):
        st.image(img, use_container_width=True)

    # Monthly table
    monthly = load_monthly()
    if monthly is not None:
        st.dataframe(monthly.rename(columns={
            "month_name": "Month", "aqi_mean": "Avg AQI",
            "aqi_max": "Max AQI", "bad_days": "Bad Days",
            "total_days": "Total Days",
        })[["Month", "Avg AQI", "Max AQI", "Bad Days", "Total Days"]],
        use_container_width=True)


# ── Tab 2: Patterns ────────────────────────────────────────────────────────────
with tab2:
    st.subheader("AQI by Hour of Day")
    img = os.path.join(GRAPHS_DIR, "hourly_pattern.png")
    if os.path.exists(img):
        st.image(img, use_container_width=True)
    st.caption("Pollution is typically highest during morning rush hours and late night.")

    st.subheader("Season Comparison")
    img = os.path.join(GRAPHS_DIR, "season_comparison.png")
    if os.path.exists(img):
        st.image(img, use_container_width=True)

    st.subheader("Top 10 Worst Days")
    img = os.path.join(GRAPHS_DIR, "worst_days.png")
    if os.path.exists(img):
        st.image(img, use_container_width=True)

    worst_table = daily.nlargest(10, "aqi_mean")[["date", "aqi_mean", "aqi_category", "season"]]
    worst_table["date"] = worst_table["date"].dt.date
    st.dataframe(worst_table.rename(columns={
        "date": "Date", "aqi_mean": "Avg AQI",
        "aqi_category": "Category", "season": "Season"
    }), use_container_width=True)


# ── Tab 3: Forecast ────────────────────────────────────────────────────────────
with tab3:
    st.subheader("7-Day AQI Forecast — Lahore")
    forecast = load_forecast()

    if forecast is None:
        st.info("Run src/05_forecasting.py to generate forecast.")
    else:
        img = os.path.join(GRAPHS_DIR, "forecast.png")
        if os.path.exists(img):
            st.image(img, use_container_width=True)

        st.markdown("**Forecast Table:**")
        cols = st.columns(len(forecast))
        for i, (_, row) in enumerate(forecast.iterrows()):
            label = str(row.get("aqi_label", ""))
            color = AQI_COLORS.get(label, "#999")
            with cols[i]:
                st.markdown(
                    f"<div style='text-align:center;padding:10px;border-radius:8px;"
                    f"border:1px solid {color};background:{color}18'>"
                    f"<b>{pd.to_datetime(row['date']).strftime('%d %b')}</b><br>"
                    f"<span style='font-size:20px;font-weight:700;color:{color}'>"
                    f"{row['aqi_forecast']:.1f}</span><br>"
                    f"<small style='color:{color}'>{label}</small></div>",
                    unsafe_allow_html=True,
                )

        st.caption("Forecast uses ARIMA time series model trained on last 12 months of data.")


# ── Tab 4: All Graphs ──────────────────────────────────────────────────────────
with tab4:
    graphs = {
        "AQI Distribution":       "aqi_distribution.png",
        "Pollutants Heatmap":     "pollutants_heatmap.png",
        "Feature Correlation":    "feature_correlation.png",
    }
    for title, fname in graphs.items():
        path = os.path.join(GRAPHS_DIR, fname)
        if os.path.exists(path):
            st.markdown(f"**{title}**")
            st.image(path, use_container_width=True)
            st.markdown("---")
