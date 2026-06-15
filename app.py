from pathlib import Path

import pandas as pd
import plotly.express as px
from dash import Dash, Input, Output, State, dcc, html


BASE_DIR = Path(__file__).resolve().parent
STATE_MAP_PATH = BASE_DIR / "outputs" / "dashboard_tables" / "state_map_metrics.csv"

POLICY_NOTE = (
    "State differences may reflect policy, eligibility rules, administrative "
    "processes, economic conditions, and reporting practices. This dashboard "
    "does not estimate causal effects."
)

METRIC_CONFIG = {
    "map_latest_enrollment": {
        "label": "Latest total Medicaid/CHIP enrollment",
        "short_label": "Total Medicaid/CHIP enrollment",
        "kind": "integer",
        "scale": "Blues",
        "caveat": "This is an aggregate state-level count for the latest available reporting month.",
    },
    "latest_medicaid_enrollment": {
        "label": "Latest Medicaid enrollment",
        "short_label": "Medicaid enrollment",
        "kind": "integer",
        "scale": "Blues",
        "caveat": "This count excludes separate CHIP enrollment where states report those values separately.",
    },
    "latest_chip_enrollment": {
        "label": "Latest CHIP enrollment",
        "short_label": "CHIP enrollment",
        "kind": "integer",
        "scale": "Teal",
        "caveat": "CHIP enrollment is smaller than Medicaid enrollment in most states, so map shading is not comparable to total enrollment.",
    },
    "map_percent_change_since_2019": {
        "label": "Percent change since January 2019",
        "short_label": "Percent change since January 2019",
        "kind": "percent",
        "scale": "RdBu",
        "caveat": "Percent change is descriptive and does not identify the cause of enrollment change.",
    },
    "map_last_12_month_change": {
        "label": "Last 12-month enrollment change",
        "short_label": "Last 12-month change",
        "kind": "integer",
        "scale": "RdBu",
        "caveat": "Enrollment declines are expected to appear as negative values for this metric.",
    },
    "map_applications_per_1000_enrollees": {
        "label": "Applications per 1,000 enrollees",
        "short_label": "Applications per 1,000 enrollees",
        "kind": "decimal",
        "scale": "Viridis",
        "caveat": "Application volume is a descriptive operational indicator and should not be interpreted as processing performance.",
    },
    "map_determinations_per_1000_enrollees": {
        "label": "Determinations per 1,000 enrollees",
        "short_label": "Determinations per 1,000 enrollees",
        "kind": "decimal",
        "scale": "Viridis",
        "caveat": "Determination volume is a descriptive operational indicator and does not measure timeliness or accuracy.",
    },
    "map_missingness_percent": {
        "label": "Data missingness percent",
        "short_label": "Missingness percent",
        "kind": "percent",
        "scale": "Reds",
        "caveat": "Higher values indicate less complete reporting across fields used in the dashboard-ready state table.",
    },
}

PROFILE_FIELDS = [
    ("Latest reporting month", "latest_reporting_month", "date"),
    ("Total Medicaid/CHIP enrollment", "latest_total_medicaid_chip_enrollment", "integer"),
    ("Change since January 2019", "change_since_january_2019", "signed_integer"),
    ("Last 12-month change", "last_12_month_change", "signed_integer"),
    ("Applications submitted", "latest_applications_submitted", "integer"),
    ("Eligibility determinations", "latest_total_determinations", "integer"),
]


def load_state_map_data() -> pd.DataFrame:
    if not STATE_MAP_PATH.exists():
        raise FileNotFoundError(f"Missing state map metrics table: {STATE_MAP_PATH}")

    data = pd.read_csv(STATE_MAP_PATH, parse_dates=["latest_reporting_month"])
    data["latest_reporting_month_label"] = data["latest_reporting_month"].dt.strftime("%B %Y")
    data["latest_month_preliminary_status"] = data["latest_month_preliminary_status"].fillna("Not specified")
    data["data_quality_note"] = data["data_quality_note"].fillna("No additional note available.")
    data["caution_flag"] = data["caution_flag"].fillna(False).astype(bool)
    return data.sort_values("state_name").reset_index(drop=True)


state_map_df = load_state_map_data()


def metric_options() -> list[dict[str, str]]:
    available = []
    for value, config in METRIC_CONFIG.items():
        if value in state_map_df.columns and state_map_df[value].notna().any():
            available.append({"label": config["label"], "value": value})
    return available


def format_value(value, value_kind: str) -> str:
    if pd.isna(value):
        return "Not available"
    if value_kind == "integer":
        return f"{value:,.0f}"
    if value_kind == "signed_integer":
        return f"{value:+,.0f}"
    if value_kind == "decimal":
        return f"{value:,.1f}"
    if value_kind == "percent":
        return f"{value:.1f}%"
    if value_kind == "date":
        if hasattr(value, "strftime"):
            return value.strftime("%B %Y")
        return str(value)
    return str(value)


def build_hover_text(data: pd.DataFrame, metric_key: str) -> pd.Series:
    metric = METRIC_CONFIG[metric_key]
    return data.apply(
        lambda row: (
            f"<b>{row['state_name']}</b><br>"
            f"{metric['short_label']}: {format_value(row[metric_key], metric['kind'])}<br>"
            f"Latest reporting month: {row['latest_reporting_month_label']}<br>"
            f"Total enrollment: {format_value(row['latest_total_medicaid_chip_enrollment'], 'integer')}<br>"
            f"Missingness: {format_value(row['map_missingness_percent'], 'percent')}<br>"
            f"Latest month status: {row['latest_month_preliminary_status']}"
        ),
        axis=1,
    )


def build_map_figure(metric_key: str, selected_state: str):
    metric = METRIC_CONFIG[metric_key]
    plot_data = state_map_df.copy()
    plot_data["hover_text"] = build_hover_text(plot_data, metric_key)

    fig = px.choropleth(
        plot_data,
        locations="state_abbreviation",
        locationmode="USA-states",
        color=metric_key,
        scope="usa",
        color_continuous_scale=metric["scale"],
        custom_data=["hover_text"],
    )
    fig.update_traces(
        hovertemplate="%{customdata[0]}<extra></extra>",
        marker_line_color="white",
        marker_line_width=0.8,
    )

    selected = plot_data[plot_data["state_abbreviation"] == selected_state]
    if not selected.empty:
        fig.add_scattergeo(
            locations=selected["state_abbreviation"],
            locationmode="USA-states",
            text=selected["state_abbreviation"],
            mode="text",
            textfont={"size": 12, "color": "#111827"},
            hoverinfo="skip",
            showlegend=False,
        )

    fig.update_layout(
        margin={"r": 0, "t": 0, "l": 0, "b": 0},
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        geo={"bgcolor": "rgba(0,0,0,0)", "lakecolor": "#f8fafc"},
        coloraxis_colorbar={
            "title": metric["short_label"],
            "tickformat": ".1f" if metric["kind"] in {"decimal", "percent"} else ",.0f",
            "ticksuffix": "%" if metric["kind"] == "percent" else "",
        },
    )
    return fig


def build_state_profile(selected_state: str):
    row = state_map_df[state_map_df["state_abbreviation"] == selected_state]
    if row.empty:
        row = state_map_df.iloc[[0]]
    row = row.iloc[0]

    profile_items = [
        html.Div(
            className="profile-row",
            children=[
                html.Span(label, className="profile-label"),
                html.Strong(format_value(row[field], value_kind), className="profile-value"),
            ],
        )
        for label, field, value_kind in PROFILE_FIELDS
        if field in row.index
    ]

    caution_text = (
        row["data_quality_note"]
        if row["caution_flag"]
        else "No caution flag was recorded in the state map metrics table."
    )

    return html.Div(
        className="state-profile",
        children=[
            html.Div(
                className="profile-heading",
                children=[
                    html.P("Selected State", className="eyebrow"),
                    html.H3(row["state_name"]),
                    html.Span(row["state_abbreviation"], className="state-chip"),
                ],
            ),
            html.Div(profile_items, className="profile-list"),
            html.Div(
                className="caution-box",
                children=[
                    html.Strong("Data quality note"),
                    html.P(caution_text),
                ],
            ),
        ],
    )


app = Dash(__name__, title="Medicaid Enrollment Policy Dashboard")
server = app.server

app.layout = html.Div(
    className="app-shell",
    children=[
        html.Header(
            className="app-header",
            children=[
                html.P("Medicaid Enrollment & Eligibility Operations Dashboard", className="eyebrow"),
                html.H1("State Map Explorer"),
                html.P(
                    "A state-level GIS-style view of Medicaid/CHIP enrollment, eligibility operations, "
                    "and reporting completeness using official public CMS aggregate data.",
                    className="header-copy",
                ),
            ],
        ),
        html.Main(
            children=[
                html.Section(
                    className="warning-banner",
                    children=[
                        html.Strong("Data quality warning"),
                        html.Span(
                            " Latest-month data may be preliminary. Adult Medicaid enrollment, call center fields, "
                            "processing-time fields, renewals/redeterminations, and pending applications are excluded "
                            "from headline map metrics because they are unavailable, incomplete, or not appropriate "
                            "for Version 1 choropleth reporting."
                        ),
                    ],
                ),
                html.Section(
                    className="controls",
                    children=[
                        html.Label(
                            children=[
                                html.Span("Map metric"),
                                dcc.Dropdown(
                                    id="map-metric",
                                    options=metric_options(),
                                    value="map_latest_enrollment",
                                    clearable=False,
                                    searchable=False,
                                ),
                            ]
                        ),
                        html.Label(
                            children=[
                                html.Span("Selected state"),
                                dcc.Dropdown(
                                    id="state-selector",
                                    options=[
                                        {"label": f"{row.state_name} ({row.state_abbreviation})", "value": row.state_abbreviation}
                                        for row in state_map_df.itertuples()
                                    ],
                                    value="CA" if "CA" in set(state_map_df["state_abbreviation"]) else state_map_df.iloc[0]["state_abbreviation"],
                                    clearable=False,
                                ),
                            ]
                        ),
                    ],
                ),
                html.Section(
                    className="map-layout",
                    children=[
                        html.Div(
                            className="map-panel",
                            children=[
                                dcc.Graph(id="state-map", className="state-map", config={"displayModeBar": False}),
                                html.P(id="metric-caveat", className="metric-caveat"),
                            ],
                        ),
                        html.Aside(id="state-profile", className="profile-panel"),
                    ],
                ),
                html.Section(
                    className="note-grid",
                    children=[
                        html.Div(
                            className="policy-note",
                            children=[
                                html.H2("Policy Interpretation"),
                                html.P(POLICY_NOTE),
                            ],
                        ),
                        html.Div(
                            className="policy-note",
                            children=[
                                html.H2("What This Map Cannot Show"),
                                html.Ul(
                                    children=[
                                        html.Li("No beneficiary-level, county-level, claims, utilization, or cost data."),
                                        html.Li("No causal estimates of Medicaid policy effects."),
                                        html.Li("Incomplete operational fields are not used as headline map metrics."),
                                        html.Li("Latest reporting month values may be preliminary or later revised."),
                                    ]
                                ),
                            ],
                        ),
                    ],
                ),
            ]
        ),
    ],
)


@app.callback(
    Output("state-selector", "value"),
    Input("state-map", "clickData"),
    State("state-selector", "value"),
)
def update_selected_state(click_data, current_state):
    if click_data and click_data.get("points"):
        location = click_data["points"][0].get("location")
        if location in set(state_map_df["state_abbreviation"]):
            return location
    return current_state


@app.callback(
    Output("state-map", "figure"),
    Output("state-profile", "children"),
    Output("metric-caveat", "children"),
    Input("map-metric", "value"),
    Input("state-selector", "value"),
)
def update_map(metric_key, selected_state):
    if metric_key not in METRIC_CONFIG:
        metric_key = "map_latest_enrollment"
    if selected_state not in set(state_map_df["state_abbreviation"]):
        selected_state = state_map_df.iloc[0]["state_abbreviation"]

    metric = METRIC_CONFIG[metric_key]
    caveat = f"Metric note: {metric['caveat']}"
    if metric_key in {
        "map_applications_per_1000_enrollees",
        "map_determinations_per_1000_enrollees",
        "map_missingness_percent",
    }:
        caveat += " Review the data quality section before comparing states."

    return (
        build_map_figure(metric_key, selected_state),
        build_state_profile(selected_state),
        caveat,
    )


if __name__ == "__main__":
    app.run(debug=False, host="127.0.0.1", port=8050, use_reloader=False)
