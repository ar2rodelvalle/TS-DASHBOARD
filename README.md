# TS-DASHBOARD

Prototype dashboard for visualizing time series data from CSV files using [Dash](https://dash.plotly.com/).

## Setup

1. Install dependencies: `pip install -r requirements.txt`
2. Start the app: `python dashboard/app.py`

## Usage

1. Enter a folder and file pattern to load CSV files (e.g., `data/source` and `file_name_*.csv`).
2. Map columns for time, value, and an optional grouping field.
3. Choose timezone display and sampling frequency.
4. Filter groups and inspect the resulting time series in the interactive chart.

This skeleton implements a subset of the desired dashboard features and can be extended for richer exploration, comparison, and export options.
