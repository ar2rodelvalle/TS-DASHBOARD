import os
import glob
import pandas as pd
from dash import Dash, html, dcc, Output, Input, State
import plotly.express as px

app = Dash(__name__)

app.layout = html.Div([
    html.H1("Time Series Dashboard"),
    html.Div([
        dcc.Input(id="folder-input", type="text", placeholder="Data folder", value="data/source"),
        dcc.Input(id="pattern-input", type="text", placeholder="Pattern", value="*.csv"),
        html.Button("Load Data", id="load-button"),
    ]),
    dcc.Store(id="data-store"),
    html.Div(id="mapping-div"),
    dcc.Graph(id="main-graph")
])


@app.callback(
    Output("data-store", "data"),
    Input("load-button", "n_clicks"),
    State("folder-input", "value"),
    State("pattern-input", "value"),
    prevent_initial_call=True,
)
def load_data(n_clicks, folder, pattern):
    files = glob.glob(os.path.join(folder, pattern))
    if not files:
        return {}
    frames = [pd.read_csv(f) for f in files]
    df = pd.concat(frames, ignore_index=True)
    return df.to_dict("records")


@app.callback(
    Output("mapping-div", "children"),
    Input("data-store", "data"),
)
def update_mapping(data):
    if not data:
        return ""
    df = pd.DataFrame(data)
    columns = [{"label": c, "value": c} for c in df.columns]
    return html.Div([
        dcc.Dropdown(id="time-col", options=columns, placeholder="Time column"),
        dcc.Dropdown(id="value-col", options=columns, placeholder="Value column"),
        dcc.Dropdown(id="group-col", options=columns, placeholder="Group field"),
        dcc.RadioItems(
            id="tz",
            options=[{"label": "UTC", "value": "utc"}, {"label": "Local", "value": "local"}],
            value="utc",
        ),
        dcc.Dropdown(
            id="freq",
            options=[
                {"label": "Native", "value": "native"},
                {"label": "5-min", "value": "5min"},
                {"label": "Hourly", "value": "H"},
                {"label": "Daily", "value": "D"},
            ],
            value="native",
        ),
        dcc.Dropdown(id="group-filter", multi=True, placeholder="Filter groups"),
    ])


@app.callback(
    Output("group-filter", "options"),
    Input("group-col", "value"),
    Input("data-store", "data"),
)
def update_group_filter(group_col, data):
    if not group_col or not data:
        return []
    df = pd.DataFrame(data)
    groups = sorted(df[group_col].dropna().unique())
    return [{"label": g, "value": g} for g in groups]


@app.callback(
    Output("main-graph", "figure"),
    Input("time-col", "value"),
    Input("value-col", "value"),
    Input("group-col", "value"),
    Input("group-filter", "value"),
    Input("tz", "value"),
    Input("freq", "value"),
    Input("data-store", "data"),
)
def update_graph(time_col, value_col, group_col, group_filter, tz, freq, data):
    if not data or not time_col or not value_col:
        return {}
    df = pd.DataFrame(data)
    df[time_col] = pd.to_datetime(df[time_col])
    if tz == "utc":
        df[time_col] = df[time_col].dt.tz_localize("UTC")
    else:
        df[time_col] = df[time_col].dt.tz_localize("UTC").dt.tz_convert(None)
    if group_col and group_filter:
        df = df[df[group_col].isin(group_filter)]
    if freq and freq != "native":
        agg = {value_col: "mean"}
        by = group_col if group_col else None
        df = df.set_index(time_col)
        df = df.groupby(by).resample(freq).agg(agg).reset_index()
    fig = px.line(df, x=time_col, y=value_col, color=group_col)
    return fig


if __name__ == "__main__":
    app.run_server(debug=True)
