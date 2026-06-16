from __future__ import annotations

import csv
import importlib.abc
import sys
import types
from datetime import datetime
from pathlib import Path

import plotly.graph_objects as go


class _BlockIPython(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path, target=None):
        if fullname == "IPython" or fullname.startswith("IPython."):
            raise ImportError("Disable Dash notebook integration for local app runtime")
        return None


_ipython_blocker = _BlockIPython()


class _ImmediateFuture:
    def __init__(self, function, *args, **kwargs):
        self._result = function(*args, **kwargs)

    def result(self, timeout=None):
        return self._result


class _CancelledError(Exception):
    pass


class _Executor:
    def submit(self, function, *args, **kwargs):
        return _ImmediateFuture(function, *args, **kwargs)

    def shutdown(self, wait=True, cancel_futures=False):
        return None


class _ThreadPoolExecutor:
    def __init__(self, max_workers=None, *args, **kwargs):
        self.max_workers = max_workers

    def submit(self, function, *args, **kwargs):
        return _ImmediateFuture(function, *args, **kwargs)

    def shutdown(self, wait=True, cancel_futures=False):
        return None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, traceback):
        self.shutdown()


if "concurrent.futures" not in sys.modules:
    concurrent_module = types.ModuleType("concurrent")
    futures_module = types.ModuleType("concurrent.futures")
    futures_module.ALL_COMPLETED = "ALL_COMPLETED"
    futures_module.FIRST_COMPLETED = "FIRST_COMPLETED"
    futures_module.FIRST_EXCEPTION = "FIRST_EXCEPTION"
    futures_module.CancelledError = _CancelledError
    futures_module.Executor = _Executor
    futures_module.Future = _ImmediateFuture
    futures_module.TimeoutError = TimeoutError
    futures_module.ThreadPoolExecutor = _ThreadPoolExecutor
    concurrent_module.futures = futures_module
    sys.modules["concurrent"] = concurrent_module
    sys.modules["concurrent.futures"] = futures_module

sys.meta_path.insert(0, _ipython_blocker)
from dash import Dash, Input, Output, dcc, html
sys.meta_path.remove(_ipython_blocker)


BASE_DIR = Path(__file__).resolve().parent
DASHBOARD_DIR = BASE_DIR / "outputs" / "dashboard_tables"
PROCESSED_DIR = BASE_DIR / "data" / "processed"

NOTE_TEXT = (
    "Note: Latest-month data may be preliminary. This dashboard uses public "
    "aggregate Medicaid/CHIP data and supports descriptive reporting, not "
    "beneficiary-level or causal analysis."
)
POLICY_NOTE = (
    "State differences may reflect policy, eligibility rules, administrative "
    "processes, economic conditions, and reporting practices. This dashboard "
    "does not estimate causal effects."
)


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as file:
        return list(csv.DictReader(file))


def to_float(value: str | int | float | None) -> float | None:
    if value is None or value == "":
        return None
    return float(value)


def format_value(value: str | int | float | None, kind: str = "integer") -> str:
    numeric = to_float(value)
    if numeric is None:
        return "Not available"
    if kind == "integer":
        return f"{numeric:,.0f}"
    if kind == "signed_integer":
        return f"{numeric:+,.0f}"
    if kind == "decimal":
        return f"{numeric:,.1f}"
    if kind == "percent":
        return f"{numeric:.1f}%"
    if kind == "ratio":
        return f"{numeric:.2f}"
    return str(value)


def month_label(value: str) -> str:
    if not value:
        return "Not available"
    return datetime.strptime(value[:10], "%Y-%m-%d").strftime("%B %Y")


def sorted_states(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    return sorted(
        [{"label": f"{row['state_name']} ({row['state_abbreviation']})", "value": row["state_abbreviation"]} for row in rows],
        key=lambda item: item["label"],
    )


state_rows = read_rows(DASHBOARD_DIR / "state_population_adjusted_metrics.csv")
state_map_rows = read_rows(DASHBOARD_DIR / "state_map_metrics.csv")
national_enrollment = read_rows(DASHBOARD_DIR / "national_enrollment_trend.csv")
national_ops = read_rows(DASHBOARD_DIR / "national_applications_determinations_trend.csv")
state_month_rows = read_rows(PROCESSED_DIR / "medicaid_state_month_summary.csv")
quality_field_rows = read_rows(DASHBOARD_DIR / "data_quality_by_field.csv")
quality_state_rows = read_rows(DASHBOARD_DIR / "data_quality_by_state.csv")
quality_month_rows = read_rows(DASHBOARD_DIR / "data_quality_by_month.csv")

state_lookup = {row["state_abbreviation"]: row for row in state_rows}
state_month_lookup: dict[str, list[dict[str, str]]] = {}
for row in state_month_rows:
    state_month_lookup.setdefault(row["state_abbreviation"], []).append(row)

latest_month = month_label(state_rows[0]["latest_reporting_month"])
population_year = state_rows[0]["population_denominator_year"]

MAP_METRICS = {
    "latest_total_medicaid_chip_enrollment": {
        "label": "Latest total Medicaid/CHIP enrollment",
        "short": "Total Medicaid/CHIP enrollment",
        "kind": "integer",
        "scale": "Blues",
        "raw": True,
        "subtitle": "raw count",
    },
    "medicaid_chip_enrollment_per_1000_residents": {
        "label": "Medicaid/CHIP enrollment per 1,000 residents",
        "short": "Enrollment per 1,000 residents",
        "kind": "decimal",
        "scale": "Greens",
        "raw": False,
        "subtitle": "population-adjusted metric",
    },
    "latest_medicaid_enrollment": {
        "label": "Latest Medicaid enrollment",
        "short": "Medicaid enrollment",
        "kind": "integer",
        "scale": "Blues",
        "raw": True,
        "subtitle": "raw count",
    },
    "medicaid_enrollment_per_1000_residents": {
        "label": "Medicaid enrollment per 1,000 residents",
        "short": "Medicaid per 1,000 residents",
        "kind": "decimal",
        "scale": "Greens",
        "raw": False,
        "subtitle": "population-adjusted metric",
    },
    "latest_chip_enrollment": {
        "label": "Latest CHIP enrollment",
        "short": "CHIP enrollment",
        "kind": "integer",
        "scale": "Teal",
        "raw": True,
        "subtitle": "raw count",
    },
    "chip_enrollment_per_1000_residents": {
        "label": "CHIP enrollment per 1,000 residents",
        "short": "CHIP per 1,000 residents",
        "kind": "decimal",
        "scale": "Teal",
        "raw": False,
        "subtitle": "population-adjusted metric",
    },
    "percent_change_since_january_2019": {
        "label": "Percent change in Medicaid/CHIP enrollment since January 2019",
        "short": "Percent change since January 2019",
        "kind": "percent",
        "scale": "RdBu",
        "raw": False,
        "subtitle": "descriptive change metric",
    },
    "last_12_month_change": {
        "label": "Last 12-month Medicaid/CHIP enrollment change",
        "short": "Last 12-month change",
        "kind": "signed_integer",
        "scale": "RdBu",
        "raw": False,
        "subtitle": "descriptive change metric",
    },
    "applications_submitted_per_100000_residents": {
        "label": "Applications submitted per 100,000 residents",
        "short": "Applications per 100,000 residents",
        "kind": "decimal",
        "scale": "Viridis",
        "raw": False,
        "subtitle": "population-adjusted operational indicator",
    },
    "eligibility_determinations_per_100000_residents": {
        "label": "Eligibility determinations per 100,000 residents",
        "short": "Determinations per 100,000 residents",
        "kind": "decimal",
        "scale": "Viridis",
        "raw": False,
        "subtitle": "population-adjusted operational indicator",
    },
    "applications_per_1000_enrollees": {
        "label": "Applications per 1,000 Medicaid/CHIP enrollees",
        "short": "Applications per 1,000 enrollees",
        "kind": "decimal",
        "scale": "Viridis",
        "raw": False,
        "subtitle": "enrollee-normalized operational indicator",
    },
    "determinations_per_1000_enrollees": {
        "label": "Determinations per 1,000 Medicaid/CHIP enrollees",
        "short": "Determinations per 1,000 enrollees",
        "kind": "decimal",
        "scale": "Viridis",
        "raw": False,
        "subtitle": "enrollee-normalized operational indicator",
    },
}


def line_figure(rows: list[dict[str, str]], traces: list[tuple[str, str]]) -> go.Figure:
    fig = go.Figure()
    x_values = [row["reporting_month"] for row in rows]
    for field, label in traces:
        fig.add_trace(
            go.Scatter(
                x=x_values,
                y=[to_float(row.get(field)) for row in rows],
                mode="lines",
                name=label,
                hovertemplate=f"{label}: %{{y:,.0f}}<br>Month: %{{x|%b %Y}}<extra></extra>",
            )
        )
    fig.update_layout(
        margin={"l": 40, "r": 20, "t": 34, "b": 34},
        hovermode="x unified",
        legend={"orientation": "h", "y": -0.22},
        paper_bgcolor="white",
        plot_bgcolor="white",
        xaxis_title=None,
        yaxis_title=None,
    )
    return fig


def bar_figure(rows: list[dict[str, str]], x_field: str, y_field: str, title: str) -> go.Figure:
    fig = go.Figure(
        go.Bar(
            x=[row[x_field] for row in rows],
            y=[to_float(row[y_field]) for row in rows],
            marker_color="#276a62",
            hovertemplate="%{x}<br>%{y:,.1f}<extra></extra>",
        )
    )
    fig.update_layout(
        title=title,
        margin={"l": 40, "r": 20, "t": 48, "b": 74},
        paper_bgcolor="white",
        plot_bgcolor="white",
        xaxis_tickangle=-35,
        yaxis_title=None,
    )
    return fig


def card(label: str, value: str, note: str = "") -> html.Div:
    return html.Div(
        className="kpi-card",
        children=[html.Span(label), html.Strong(value), html.Small(note)],
    )


def current_national_totals() -> dict[str, float]:
    latest = national_enrollment[-1]
    ops = national_ops[-1]
    return {
        "total": to_float(latest["total_medicaid_and_chip_enrollment"]) or 0,
        "medicaid": to_float(latest["total_medicaid_enrollment"]) or 0,
        "chip": to_float(latest["total_chip_enrollment"]) or 0,
        "applications": to_float(ops["applications_submitted"]) or 0,
        "determinations": to_float(ops["total_medicaid_and_chip_determinations"]) or 0,
    }


def build_overview_tab() -> html.Div:
    totals = current_national_totals()
    return html.Div(
        className="tab-page",
        children=[
            html.Div(className="note-banner", children=NOTE_TEXT),
            html.Div(
                className="kpi-grid",
                children=[
                    card("Latest reporting month", latest_month, "CMS state-month aggregate data"),
                    card("Total Medicaid/CHIP enrollment", format_value(totals["total"]), "National latest month"),
                    card("Medicaid enrollment", format_value(totals["medicaid"]), "National latest month"),
                    card("CHIP enrollment", format_value(totals["chip"]), "National latest month"),
                    card("Applications submitted", format_value(totals["applications"]), "Descriptive operations indicator"),
                    card("Eligibility determinations", format_value(totals["determinations"]), "Descriptive operations indicator"),
                ],
            ),
            html.Div(
                className="two-column",
                children=[
                    html.Div(
                        className="panel",
                        children=[
                            html.H2("National Enrollment Trend"),
                            dcc.Graph(
                                figure=line_figure(
                                    national_enrollment,
                                    [
                                        ("total_medicaid_and_chip_enrollment", "Total Medicaid/CHIP"),
                                        ("total_medicaid_enrollment", "Medicaid"),
                                        ("total_chip_enrollment", "CHIP"),
                                    ],
                                ),
                                config={"displayModeBar": False},
                            ),
                        ],
                    ),
                    html.Div(
                        className="panel",
                        children=[
                            html.H2("Applications And Determinations Trend"),
                            dcc.Graph(
                                figure=line_figure(
                                    national_ops,
                                    [
                                        ("applications_submitted", "Applications submitted"),
                                        ("total_medicaid_and_chip_determinations", "Eligibility determinations"),
                                    ],
                                ),
                                config={"displayModeBar": False},
                            ),
                        ],
                    ),
                ],
            ),
            html.Div(
                className="policy-note wide",
                children=[
                    html.H2("Plain-Language Summary"),
                    html.P(
                        "This dashboard summarizes Medicaid/CHIP enrollment, CHIP enrollment, and eligibility "
                        "operations using official public state-level aggregate data. Population-adjusted measures "
                        "help compare relative enrollment scale across states, while raw counts remain useful for "
                        "understanding total program size and operational volume."
                    ),
                ],
            ),
        ],
    )


def map_title(metric_key: str) -> tuple[str, str]:
    metric = MAP_METRICS[metric_key]
    if "per_1000_residents" in metric_key or "per_100000_residents" in metric_key:
        subtitle = (
            f"Map color represents {metric['label'].lower()}, {latest_month} Medicaid data "
            f"using {population_year} state population denominators."
        )
    else:
        subtitle = f"Map color represents {metric['label'].lower()}, {latest_month} Medicaid data."
    return metric["label"], subtitle


def build_hover(row: dict[str, str], metric_key: str) -> str:
    metric = MAP_METRICS[metric_key]
    return (
        f"<b>{row['state_name']}</b><br>"
        f"Reporting month: {latest_month}<br>"
        f"{metric['label']}: {format_value(row.get(metric_key), metric['kind'])}<br>"
        f"Total Medicaid/CHIP enrollment: {format_value(row['latest_total_medicaid_chip_enrollment'])}<br>"
        f"Enrollment per 1,000 residents: {format_value(row['medicaid_chip_enrollment_per_1000_residents'], 'decimal')}<br>"
        f"Population denominator year: {row['population_denominator_year']}<br>"
        f"Applications submitted: {format_value(row['latest_applications_submitted'])}<br>"
        f"Eligibility determinations: {format_value(row['latest_total_determinations'])}<br>"
        f"Preliminary status: {row['latest_month_preliminary_status']}"
    )


def build_map(metric_key: str, selected_state: str) -> go.Figure:
    metric = MAP_METRICS[metric_key]
    fig = go.Figure(
        go.Choropleth(
            locations=[row["state_abbreviation"] for row in state_rows],
            z=[to_float(row.get(metric_key)) for row in state_rows],
            locationmode="USA-states",
            colorscale=metric["scale"],
            colorbar={"title": metric["short"]},
            text=[build_hover(row, metric_key) for row in state_rows],
            hovertemplate="%{text}<extra></extra>",
            marker_line_color="white",
            marker_line_width=0.8,
        )
    )
    if selected_state in state_lookup:
        fig.add_trace(
            go.Scattergeo(
                locations=[selected_state],
                locationmode="USA-states",
                text=[selected_state],
                mode="text",
                textfont={"size": 12, "color": "#111827"},
                hoverinfo="skip",
                showlegend=False,
            )
        )
    fig.update_layout(
        geo={"scope": "usa", "bgcolor": "rgba(0,0,0,0)", "lakecolor": "#f8fafc"},
        margin={"l": 0, "r": 0, "t": 0, "b": 0},
        paper_bgcolor="white",
        plot_bgcolor="white",
    )
    return fig


def build_state_profile(selected_state: str) -> html.Div:
    row = state_lookup.get(selected_state, state_rows[0])
    fields = [
        ("Latest reporting month", latest_month),
        ("Total Medicaid/CHIP enrollment", format_value(row["latest_total_medicaid_chip_enrollment"])),
        ("Enrollment per 1,000 residents", format_value(row["medicaid_chip_enrollment_per_1000_residents"], "decimal")),
        ("Change since January 2019", format_value(row["change_since_january_2019"], "signed_integer")),
        ("Last 12-month change", format_value(row["last_12_month_change"], "signed_integer")),
        ("Applications submitted", format_value(row["latest_applications_submitted"])),
        ("Eligibility determinations", format_value(row["latest_total_determinations"])),
        ("Data missingness", format_value(row["missingness_percent"], "percent")),
    ]
    return html.Div(
        className="state-profile",
        children=[
            html.P("Selected State", className="eyebrow"),
            html.H3(f"{row['state_name']} ({row['state_abbreviation']})"),
            html.Div(
                className="profile-list",
                children=[
                    html.Div(className="profile-row", children=[html.Span(label), html.Strong(value)])
                    for label, value in fields
                ],
            ),
            html.Div(className="caution-box", children=[html.Strong("Caution flag"), html.P(row["data_quality_note"])]),
        ],
    )


def ranking_table(metric_key: str) -> html.Div:
    metric = MAP_METRICS[metric_key]
    ranked = sorted(
        [row for row in state_rows if to_float(row.get(metric_key)) is not None],
        key=lambda row: to_float(row.get(metric_key)) or 0,
        reverse=True,
    )
    selected = ranked[:5] + list(reversed(ranked[-5:]))
    return html.Table(
        className="compact-table",
        children=[
            html.Thead(html.Tr([html.Th("State"), html.Th(metric["short"])])),
            html.Tbody(
                [
                    html.Tr(
                        [
                            html.Td(f"{row['state_name']} ({row['state_abbreviation']})"),
                            html.Td(format_value(row.get(metric_key), metric["kind"])),
                        ]
                    )
                    for row in selected
                ]
            ),
        ],
    )


def build_maps_tab() -> html.Div:
    return html.Div(
        className="tab-page",
        children=[
            html.Div(
                className="controls",
                children=[
                    html.Label(
                        [html.Span("Map metric"), dcc.Dropdown(id="map-metric", options=[{"label": cfg["label"], "value": key} for key, cfg in MAP_METRICS.items()], value="medicaid_chip_enrollment_per_1000_residents", clearable=False)]
                    ),
                    html.Label([html.Span("Selected state"), dcc.Dropdown(id="state-selector", options=sorted_states(state_rows), value="CA", clearable=False)]),
                ],
            ),
            html.Div(className="map-title-block", children=[html.H2(id="map-title"), html.P(id="map-subtitle")]),
            html.Div(
                className="map-layout",
                children=[
                    html.Div(className="panel map-panel", children=[dcc.Graph(id="state-map", className="state-map", config={"displayModeBar": False}), html.P(id="raw-map-note", className="small-note")]),
                    html.Aside(id="state-profile", className="profile-panel"),
                ],
            ),
            html.Div(
                className="two-column",
                children=[
                    html.Div(className="panel", children=[html.H2("Top And Bottom States"), html.Div(id="metric-rankings")]),
                    html.Div(
                        className="policy-note",
                        children=[
                            html.H2("Raw Counts Vs Population Context"),
                            html.P(
                                "Raw enrollment counts are affected by state population size. Population-adjusted "
                                "metrics such as enrollment per 1,000 residents are better for comparing relative "
                                "coverage scale across states."
                            ),
                            html.P(POLICY_NOTE),
                        ],
                    ),
                ],
            ),
        ],
    )


def state_trend_rows(selected_state: str) -> list[dict[str, str]]:
    return state_month_lookup.get(selected_state, [])


def build_chip_tab() -> html.Div:
    return html.Div(
        className="tab-page",
        children=[
            html.Div(className="note-banner subdued", children="CHIP reporting can vary by state, and CHIP may include adults in some states according to source caveats."),
            html.Div(
                className="two-column",
                children=[
                    html.Div(className="panel", children=[html.H2("National Medicaid Vs CHIP Enrollment"), dcc.Graph(figure=line_figure(national_enrollment, [("total_medicaid_enrollment", "Medicaid"), ("total_chip_enrollment", "CHIP")]), config={"displayModeBar": False})]),
                    html.Div(className="panel", children=[html.H2("Selected State Medicaid Vs CHIP Trend"), dcc.Graph(id="state-chip-trend", config={"displayModeBar": False})]),
                ],
            ),
            html.Div(id="state-chip-summary", className="kpi-grid compact"),
        ],
    )


def build_operations_tab() -> html.Div:
    return html.Div(
        className="tab-page",
        children=[
            html.Div(className="note-banner subdued", children="Eligibility operations metrics are descriptive operational indicators, not performance scores."),
            html.Div(
                className="two-column",
                children=[
                    html.Div(className="panel", children=[html.H2("National Applications And Determinations"), dcc.Graph(figure=line_figure(national_ops, [("applications_submitted", "Applications submitted"), ("total_medicaid_and_chip_determinations", "Determinations")]), config={"displayModeBar": False})]),
                    html.Div(className="panel", children=[html.H2("Selected State Operations Trend"), dcc.Graph(id="state-operations-trend", config={"displayModeBar": False})]),
                ],
            ),
            html.Div(id="state-operations-summary", className="kpi-grid compact"),
        ],
    )


def table_from_rows(rows: list[dict[str, str]], columns: list[tuple[str, str]], limit: int = 10) -> html.Table:
    return html.Table(
        className="compact-table",
        children=[
            html.Thead(html.Tr([html.Th(label) for _, label in columns])),
            html.Tbody(
                [
                    html.Tr([html.Td(row.get(field, "")) for field, _ in columns])
                    for row in rows[:limit]
                ]
            ),
        ],
    )


def build_quality_tab() -> html.Div:
    excluded = [
        ("Adult Medicaid enrollment", "High missingness; excluded from headline KPIs."),
        ("Call center volume", "High missingness and state reporting variation."),
        ("Call center wait time", "Incomplete field for Version 1 headline reporting."),
        ("Call center abandonment rate", "Incomplete field for Version 1 headline reporting."),
        ("Processing-time fields", "Substantial missingness; supplemental only."),
        ("Renewals/redeterminations", "Not available as a clean dedicated numeric field."),
        ("Pending applications", "Not available in the preserved source fields."),
    ]
    top_field_missing = sorted(quality_field_rows, key=lambda row: to_float(row.get("missing_percent")) or 0, reverse=True)
    top_state_missing = sorted(quality_state_rows, key=lambda row: to_float(row.get("missing_value_percent")) or 0, reverse=True)
    return html.Div(
        className="tab-page",
        children=[
            html.Div(
                className="three-column",
                children=[
                    html.Div(className="panel", children=[html.H2("Missingness By Field"), table_from_rows(top_field_missing, [("field_name", "Field"), ("missing_percent", "Missing %")], 12)]),
                    html.Div(className="panel", children=[html.H2("Missingness By State"), table_from_rows(top_state_missing, [("state_abbreviation", "State"), ("missing_value_percent", "Missing %")], 12)]),
                    html.Div(className="panel", children=[html.H2("Latest Month Status"), table_from_rows(quality_month_rows[-6:], [("reporting_month", "Month"), ("preliminary_records", "Preliminary records")], 6)]),
                ],
            ),
            html.Div(
                className="two-column",
                children=[
                    html.Div(className="panel", children=[html.H2("Excluded From Headline Metrics"), html.Ul([html.Li([html.Strong(f"{field}: "), reason]) for field, reason in excluded])]),
                    html.Div(
                        className="policy-note",
                        children=[
                            html.H2("Population Denominator Notes"),
                            html.P(
                                f"Population-adjusted metrics use official Census {population_year} state resident "
                                "population estimates. They provide approximate descriptive context and are not "
                                "healthcare utilization measures."
                            ),
                        ],
                    ),
                ],
            ),
        ],
    )


def build_about_tab() -> html.Div:
    return html.Div(
        className="tab-page",
        children=[
            html.Div(
                className="policy-note wide",
                children=[
                    html.H2("Data Sources And Coverage"),
                    html.P("Medicaid data source: CMS/Data.Medicaid.gov State Medicaid and CHIP Applications, Eligibility Determinations, and Enrollment Data."),
                    html.P("Population denominator source: U.S. Census Bureau NST-EST2024-POP annual resident population estimates."),
                    html.P("Medicaid data coverage: January 2019 through February 2026. Geography: all 50 states plus DC. Grain: monthly state-level aggregate data."),
                ],
            ),
            html.Div(
                className="two-column",
                children=[
                    html.Div(className="panel", children=[html.H2("What The Dashboard Can Show"), html.Ul([html.Li("National and state Medicaid/CHIP enrollment trends."), html.Li("Raw and population-adjusted state comparisons."), html.Li("Descriptive applications and eligibility determinations indicators."), html.Li("Data quality and preliminary reporting context.")])]),
                    html.Div(className="panel", children=[html.H2("What The Dashboard Cannot Show"), html.Ul([html.Li("No beneficiary-level data."), html.Li("No county-level data."), html.Li("No claims, utilization, or cost data."), html.Li("No causal policy effects."), html.Li("Applications and determinations are not complete performance measures.")])]),
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
                html.H1("Healthcare Policy Analytics Dashboard"),
                html.P(
                    "A descriptive Medicaid/CHIP reporting tool combining enrollment trends, population context, "
                    "eligibility operations indicators, and data quality interpretation.",
                    className="header-copy",
                ),
            ],
        ),
        dcc.Tabs(
            id="main-tabs",
            value="overview",
            className="tabs",
            children=[
                dcc.Tab(label="Overview", value="overview", children=build_overview_tab()),
                dcc.Tab(label="Enrollment Maps", value="maps", children=build_maps_tab()),
                dcc.Tab(label="Medicaid vs CHIP", value="chip", children=build_chip_tab()),
                dcc.Tab(label="Eligibility Operations", value="operations", children=build_operations_tab()),
                dcc.Tab(label="Data Quality", value="quality", children=build_quality_tab()),
                dcc.Tab(label="About / Limitations", value="about", children=build_about_tab()),
            ],
        ),
    ],
)


@app.callback(
    Output("map-title", "children"),
    Output("map-subtitle", "children"),
    Output("state-map", "figure"),
    Output("state-profile", "children"),
    Output("metric-rankings", "children"),
    Output("raw-map-note", "children"),
    Input("map-metric", "value"),
    Input("state-selector", "value"),
)
def update_map(metric_key: str, selected_state: str):
    if metric_key not in MAP_METRICS:
        metric_key = "medicaid_chip_enrollment_per_1000_residents"
    if selected_state not in state_lookup:
        selected_state = "CA"
    title, subtitle = map_title(metric_key)
    raw_note = (
        "Raw enrollment counts are affected by state population size. Use population-adjusted metrics for relative state comparison."
        if MAP_METRICS[metric_key]["raw"]
        else "This metric uses population or enrollment denominators for descriptive comparison; it is not a utilization or performance rate."
    )
    return title, subtitle, build_map(metric_key, selected_state), build_state_profile(selected_state), ranking_table(metric_key), raw_note


@app.callback(
    Output("state-chip-trend", "figure"),
    Output("state-chip-summary", "children"),
    Output("state-operations-trend", "figure"),
    Output("state-operations-summary", "children"),
    Input("state-selector", "value"),
)
def update_state_sections(selected_state: str):
    if selected_state not in state_lookup:
        selected_state = "CA"
    selected = state_lookup[selected_state]
    rows = state_trend_rows(selected_state)
    chip_fig = line_figure(rows, [("total_medicaid_enrollment", "Medicaid"), ("total_chip_enrollment", "CHIP")])
    ops_fig = line_figure(rows, [("total_applications_for_financial_assistance_submitted_at_state_level", "Applications submitted"), ("total_medicaid_and_chip_determinations", "Determinations")])
    chip_summary = [
        card("Selected state", f"{selected['state_name']} ({selected_state})"),
        card("Latest Medicaid enrollment", format_value(selected["latest_medicaid_enrollment"])),
        card("Latest CHIP enrollment", format_value(selected["latest_chip_enrollment"])),
        card("Medicaid per 1,000 residents", format_value(selected["medicaid_enrollment_per_1000_residents"], "decimal")),
        card("CHIP per 1,000 residents", format_value(selected["chip_enrollment_per_1000_residents"], "decimal")),
    ]
    ops_summary = [
        card("Applications submitted", format_value(selected["latest_applications_submitted"])),
        card("Eligibility determinations", format_value(selected["latest_total_determinations"])),
        card("Applications per 100,000 residents", format_value(selected["applications_submitted_per_100000_residents"], "decimal")),
        card("Determinations per 100,000 residents", format_value(selected["eligibility_determinations_per_100000_residents"], "decimal")),
        card("Applications per 1,000 enrollees", format_value(selected["applications_per_1000_enrollees"], "decimal")),
        card("Determinations per application", format_value(selected["determinations_per_application"], "ratio")),
    ]
    return chip_fig, chip_summary, ops_fig, ops_summary


if __name__ == "__main__":
    app.run(debug=False, host="127.0.0.1", port=8050, use_reloader=False)
