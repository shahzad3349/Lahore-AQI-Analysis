# 🌫️ Lahore Air Quality Dashboard

[![Live Demo](https://img.shields.io/badge/🚀%20Live%20Demo-Streamlit-FF4B4B?style=for-the-badge)](https://lahore-aqi-dashboard.streamlit.app)
[![GitHub](https://img.shields.io/badge/GitHub-Repository-181717?style=for-the-badge&logo=github)](https://github.com/shahzad3349/Lahore-AQI-Dashboard)

Real-time AQI analytics and forecasting dashboard for Lahore, Pakistan — built using OpenWeatherMap API, Python, and Streamlit.

🔴 **Live Demo:** [lahore-aqi-dashboard.streamlit.app](https://lahore-aqi-dashboard.streamlit.app)

> Pakistan mein smog ek serious issue hai. Yeh project Lahore ki air quality ke trends, patterns aur future forecast dikhata hai.

---

## Features

- 📡 **Live Data** — OpenWeatherMap API se real Lahore AQI data
- 📈 **Trend Analysis** — Daily, monthly, seasonal AQI trends
- 🕐 **Hourly Patterns** — Worst hours of the day for air quality
- 🔮 **7-Day Forecast** — ARIMA time series forecasting
- 📊 **Pollutant Breakdown** — PM2.5, PM10, NO2, O3, CO, SO2
- 🗓️ **Date Filter** — Custom date range analysis

---

## How to Run

### 1. Setup API Key
Create `config.py` in root folder:
```python
API_KEY = "my_api_key"
CITY = "Lahore"
LAT = 31.5204
LON = 74.3587
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Run pipeline
```bash
python src/01_fetch_data.py
python src/02_data_cleaning.py
python src/03_feature_engineering.py
python src/04_eda_graphs.py
python src/05_forecasting.py
```

### 4. Launch dashboard
```bash
streamlit run app.py
```

---

## Project Structure

```
Lahore_AQI/
├── data/
│   ├── raw/              ← Fetched API data
│   └── processed/        ← Cleaned & engineered data
├── src/
│   ├── 01_fetch_data.py
│   ├── 02_data_cleaning.py
│   ├── 03_feature_engineering.py
│   ├── 04_eda_graphs.py
│   └── 05_forecasting.py
├── outputs/
│   ├── graphs/           ← 7 visualizations
│   └── models/           ← Forecast CSV
├── app.py                ← Streamlit dashboard
├── config.py             ← API key (NOT on GitHub)
└── requirements.txt
```

---

## Tech Stack

Python · Pandas · Requests · Matplotlib · Seaborn · Statsmodels (ARIMA) · Streamlit

---
