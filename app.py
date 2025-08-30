import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

# Title
st.title("Time Series Dashboard")

# Setup section
data_folder = st.text_input("Data folder", value="data/source")
file_pattern = st.text_input("Filename pattern", value="*.csv")

@st.cache_data
def load_data(folder: str, pattern: str) -> pd.DataFrame:
    files = sorted(Path(folder).glob(pattern))
    if not files:
        return pd.DataFrame()
    dfs = []
    for f in files:
        try:
            df = pd.read_csv(f)
            df["_source"] = f.name
            dfs.append(df)
        except Exception as exc:
            st.warning(f"Failed to load {f.name}: {exc}")
    if dfs:
        return pd.concat(dfs, ignore_index=True)
    return pd.DataFrame()

if data_folder:
    df = load_data(data_folder, file_pattern)
else:
    df = pd.DataFrame()

if df.empty:
    st.info("No data loaded. Check folder and pattern.")
    st.stop()

st.subheader("Column mapping")
cols = df.columns.tolist()
time_col = st.selectbox("Time column", options=cols, index=0)
value_col = st.selectbox("Value column", options=cols, index=min(1, len(cols)-1))
other_cols = [c for c in cols if c not in (time_col, value_col)]
group_cols = st.multiselect("Grouping columns", options=other_cols, default=[c for c in other_cols[:1]])

# Parse timestamps
timezone = st.radio("Display timezone", ["UTC", "Local"], index=0)
df[time_col] = pd.to_datetime(df[time_col], utc=True, errors='coerce')
if timezone == "Local":
    df[time_col] = df[time_col].dt.tz_convert(None)

# Sampling
sample = st.selectbox("Sampling", ["native", "5T", "1H", "1D"], index=0)
if sample != "native":
    df = df.set_index(time_col)
    agg = {value_col: "mean"}
    df = df.groupby(group_cols).resample(sample)[value_col].mean().reset_index()
else:
    df = df.sort_values(time_col)

# Filtering
filters = {}
for col in group_cols:
    options = sorted(df[col].dropna().unique())
    selection = st.multiselect(f"Filter {col}", options=options, default=options)
    filters[col] = selection

mask = pd.Series(True, index=df.index)
for col, selected in filters.items():
    mask &= df[col].isin(selected)
filtered = df[mask]

# Series discovery and selection
st.subheader("Series")
if group_cols:
    group_values = filtered[group_cols].drop_duplicates()
    group_values["label"] = group_values.astype(str).agg(" | ".join, axis=1)
    series_options = group_values["label"].tolist()
    selected_series = st.multiselect("Select series to plot", options=series_options, default=series_options[:1])
    if not selected_series:
        st.stop()
    selected_df = filtered.merge(group_values[group_values["label"].isin(selected_series)], on=group_cols)
else:
    selected_df = filtered

# Overlays
st.subheader("Overlays")
rolling = st.checkbox("Rolling mean", value=False)
window = st.slider("Window", min_value=2, max_value=50, value=5) if rolling else None
pct_change = st.checkbox("% change", value=False)

plot_df = selected_df.copy()
plot_df = plot_df.sort_values(time_col)

if rolling:
    plot_df["rolling_mean"] = plot_df.groupby(group_cols)[value_col].transform(lambda s: s.rolling(window, min_periods=1).mean())
if pct_change:
    plot_df["pct_change"] = plot_df.groupby(group_cols)[value_col].transform(lambda s: s.pct_change())

fig = px.line(plot_df, x=time_col, y=value_col, color=group_cols[0] if group_cols else None, hover_data=group_cols)
if rolling:
    fig.add_traces(px.line(plot_df, x=time_col, y="rolling_mean", color=group_cols[0] if group_cols else None).data)
if pct_change:
    fig.add_traces(px.line(plot_df, x=time_col, y="pct_change", color=group_cols[0] if group_cols else None).data)

st.plotly_chart(fig, use_container_width=True)

st.subheader("Data preview")
st.dataframe(filtered.head())
