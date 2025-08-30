# TS-DASHBOARD

Streamlit-based dashboard for exploring time series data from CSV files.

## Features

- Load multiple CSVs from a folder pattern.
- Map time, value, and grouping columns.
- Filter by grouping fields and plot selected series.
- Optional overlays: rolling mean and percent change.
- Resample data to common cadence (5-minute, hourly, daily).

## Usage

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Run the app:
   ```bash
   streamlit run app.py
   ```
3. Provide the data folder and filename pattern then map columns to start exploring.

