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
    "Note: Latest-month data may be preliminary. This dashboard uses public aggregate "
    "Medicaid/CHIP data and supports descriptive reporting, not beneficiary-level or causal analysis."
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
national_balance_rows = read_rows(
    DASHBOARD_DIR / "national_application_determination_balance_trend.csv"
)
balance_rows = read_rows(DASHBOARD_DIR / "application_determination_balance.csv")
latest_balance_rows = read_rows(
    DASHBOARD_DIR / "application_determination_balance_latest.csv"
)
top_balance_rows = read_rows(
    DASHBOARD_DIR / "top_application_determination_balance_states.csv"
)
state_month_rows = read_rows(PROCESSED_DIR / "medicaid_state_month_summary.csv")
quality_field_rows = read_rows(DASHBOARD_DIR / "data_quality_by_field.csv")
quality_state_rows = read_rows(DASHBOARD_DIR / "data_quality_by_state.csv")
quality_month_rows = read_rows(DASHBOARD_DIR / "data_quality_by_month.csv")
peak_change_rows = read_rows(DASHBOARD_DIR / "enrollment_change_from_peak.csv")
monitoring_flag_rows = read_rows(DASHBOARD_DIR / "monitoring_review_flags.csv")
state_monitoring_rows = read_rows(DASHBOARD_DIR / "state_monitoring_summary.csv")
national_monitoring_rows = read_rows(DASHBOARD_DIR / "national_monitoring_summary.csv")

state_lookup = {row["state_abbreviation"]: row for row in state_rows}
latest_balance_lookup = {row["state_abbreviation"]: row for row in latest_balance_rows}
peak_lookup = {row["state_abbreviation"]: row for row in peak_change_rows}
state_monitoring_lookup = {
    row["state_abbreviation"]: row for row in state_monitoring_rows
}
state_month_lookup: dict[str, list[dict[str, str]]] = {}
for row in state_month_rows:
    state_month_lookup.setdefault(row["state_abbreviation"], []).append(row)
for rows in state_month_lookup.values():
    rows.sort(key=lambda row: row["reporting_month"])
balance_lookup: dict[str, list[dict[str, str]]] = {}
for row in balance_rows:
    balance_lookup.setdefault(row["state_abbreviation"], []).append(row)
for rows in balance_lookup.values():
    rows.sort(key=lambda row: row["reporting_month"])

MONTH_VALUES = sorted({row["reporting_month"] for row in state_month_rows})
MONTH_INDEX_BY_VALUE = {value: index for index, value in enumerate(MONTH_VALUES)}
LATEST_MONTH_VALUE = MONTH_VALUES[-1]
BASELINE_MONTH = "2019-01-01"
POST_PEAK_CONTEXT_MONTH = "2023-04-01"

latest_month = month_label(state_rows[0]["latest_reporting_month"])
population_year = state_rows[0]["population_denominator_year"]
latest_preliminary_status = (
    "Preliminary"
    if any(row["latest_month_preliminary_status"] != "Final/updated" for row in state_rows)
    else "Final/updated"
)

MAP_METRICS = {
    "latest_total_medicaid_chip_enrollment": {
        "label": "Total Medicaid/CHIP enrollment",
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
        "label": "Medicaid enrollment",
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
        "label": "CHIP enrollment",
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
    "change_since_april_2023": {
        "label": "Change in Medicaid/CHIP enrollment since April 2023",
        "short": "Change since April 2023",
        "kind": "signed_integer",
        "scale": "RdBu",
        "raw": False,
        "subtitle": "descriptive post-peak context metric",
    },
}


def line_figure(
    rows: list[dict[str, str]],
    traces: list[tuple[str, str]],
    title: str | None = None,
    subtitle: str | None = None,
    y_axis_title: str | None = None,
) -> go.Figure:
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
        title={"text": f"{title}<br><sup>{subtitle}</sup>" if title and subtitle else title},
        margin={"l": 40, "r": 20, "t": 34, "b": 34},
        hovermode="x unified",
        legend={"orientation": "h", "y": -0.22},
        paper_bgcolor="white",
        plot_bgcolor="white",
        xaxis_title=None,
        yaxis_title=y_axis_title,
        xaxis={
            "rangeslider": {"visible": True, "thickness": 0.08},
            "rangeselector": {
                "buttons": [
                    {"count": 1, "label": "1Y", "step": "year", "stepmode": "backward"},
                    {"count": 3, "label": "3Y", "step": "year", "stepmode": "backward"},
                    {"step": "all", "label": "All"},
                ]
            },
        },
        updatemenus=[
            {
                "type": "buttons",
                "direction": "right",
                "showactive": False,
                "x": 1,
                "xanchor": "right",
                "y": 1.18,
                "yanchor": "top",
                "buttons": [
                    {
                        "label": "Post-peak",
                        "method": "relayout",
                        "args": [{"xaxis.range": [POST_PEAK_CONTEXT_MONTH, LATEST_MONTH_VALUE]}],
                    }
                ],
            }
        ],
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


def section_header(title: str, question: str, explanation: str) -> html.Div:
    return html.Div(
        className="section-header",
        children=[
            html.P("Monitoring question", className="eyebrow"),
            html.H2(title),
            html.H3(question),
            html.P(explanation),
        ],
    )


def month_slider_marks() -> dict[int, str]:
    return {
        index: datetime.strptime(month[:10], "%Y-%m-%d").strftime("%Y")
        for index, month in enumerate(MONTH_VALUES)
        if month.endswith("-01-01")
    }


def row_for_state_month(state_abbreviation: str, reporting_month: str) -> dict[str, str] | None:
    for row in state_month_lookup.get(state_abbreviation, []):
        if row["reporting_month"] == reporting_month:
            return row
    return None


def row_at_or_before(state_abbreviation: str, reporting_month: str) -> dict[str, str] | None:
    rows = [
        row
        for row in state_month_lookup.get(state_abbreviation, [])
        if row["reporting_month"] <= reporting_month
    ]
    return rows[-1] if rows else None


def row_months_before(state_abbreviation: str, reporting_month: str, months: int = 12) -> dict[str, str] | None:
    index = MONTH_INDEX_BY_VALUE.get(reporting_month)
    if index is None or index - months < 0:
        return None
    return row_for_state_month(state_abbreviation, MONTH_VALUES[index - months])


def ratio(numerator: float | None, denominator: float | None, multiplier: float = 1) -> float | None:
    if numerator is None or denominator in (None, 0):
        return None
    return numerator / denominator * multiplier


def percent_change(current: float | None, prior: float | None) -> float | None:
    if current is None or prior in (None, 0):
        return None
    return (current - prior) / prior * 100


def month_metric_value(state_abbreviation: str, reporting_month: str, metric_key: str) -> float | None:
    row = row_for_state_month(state_abbreviation, reporting_month)
    if row is None:
        return None
    state = state_lookup.get(state_abbreviation, {})
    population = to_float(state.get("state_population"))
    enrollment = to_float(row.get("total_medicaid_and_chip_enrollment"))
    medicaid = to_float(row.get("total_medicaid_enrollment"))
    chip = to_float(row.get("total_chip_enrollment"))
    applications = to_float(row.get("total_applications_for_financial_assistance_submitted_at_state_level"))
    determinations = to_float(row.get("total_medicaid_and_chip_determinations"))
    baseline = row_at_or_before(state_abbreviation, BASELINE_MONTH)
    april_2023 = row_at_or_before(state_abbreviation, POST_PEAK_CONTEXT_MONTH)
    prior_12 = row_months_before(state_abbreviation, reporting_month)
    baseline_enrollment = to_float(baseline.get("total_medicaid_and_chip_enrollment")) if baseline else None
    april_2023_enrollment = to_float(april_2023.get("total_medicaid_and_chip_enrollment")) if april_2023 else None
    prior_12_enrollment = to_float(prior_12.get("total_medicaid_and_chip_enrollment")) if prior_12 else None
    values = {
        "latest_total_medicaid_chip_enrollment": enrollment,
        "latest_medicaid_enrollment": medicaid,
        "latest_chip_enrollment": chip,
        "medicaid_chip_enrollment_per_1000_residents": ratio(enrollment, population, 1000),
        "medicaid_enrollment_per_1000_residents": ratio(medicaid, population, 1000),
        "chip_enrollment_per_1000_residents": ratio(chip, population, 1000),
        "applications_submitted_per_100000_residents": ratio(applications, population, 100000),
        "eligibility_determinations_per_100000_residents": ratio(determinations, population, 100000),
        "applications_per_1000_enrollees": ratio(applications, enrollment, 1000),
        "determinations_per_1000_enrollees": ratio(determinations, enrollment, 1000),
        "percent_change_since_january_2019": percent_change(enrollment, baseline_enrollment),
        "last_12_month_change": enrollment - prior_12_enrollment if enrollment is not None and prior_12_enrollment is not None else None,
        "change_since_april_2023": enrollment - april_2023_enrollment if enrollment is not None and april_2023_enrollment is not None else None,
    }
    return values.get(metric_key)


def map_rows_for_month(reporting_month: str, metric_key: str) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for state in state_rows:
        state_abbreviation = state["state_abbreviation"]
        month_row = row_for_state_month(state_abbreviation, reporting_month)
        if not month_row:
            continue
        rows.append(
            {
                **state,
                "reporting_month": reporting_month,
                "metric_value": month_metric_value(state_abbreviation, reporting_month, metric_key),
                "month_total_enrollment": to_float(month_row.get("total_medicaid_and_chip_enrollment")),
                "month_medicaid_enrollment": to_float(month_row.get("total_medicaid_enrollment")),
                "month_chip_enrollment": to_float(month_row.get("total_chip_enrollment")),
                "month_applications": to_float(month_row.get("total_applications_for_financial_assistance_submitted_at_state_level")),
                "month_determinations": to_float(month_row.get("total_medicaid_and_chip_determinations")),
                "month_preliminary_status": "Preliminary" if month_row.get("preliminary_or_updated") == "P" else "Final/updated",
            }
        )
    return rows


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


def selected_state_options_with_all() -> list[dict[str, str]]:
    return [{"label": "All states", "value": "ALL"}] + sorted_states(state_rows)


def flag_type_options() -> list[dict[str, str]]:
    labels = {
        "large_month_over_month_enrollment_change": "Large month-over-month enrollment change",
        "large_applications_spike": "Large applications spike",
        "large_determinations_spike": "Large determinations spike",
        "latest_month_preliminary_reporting_caution": "Latest-month preliminary reporting caution",
        "high_missingness_caution": "High missingness caution",
    }
    values = sorted({row["flag_type"] for row in monitoring_flag_rows})
    return [{"label": "All review flags", "value": "ALL"}] + [
        {"label": labels.get(value, value.replace("_", " ").title()), "value": value}
        for value in values
    ]


def build_overview_tab() -> html.Div:
    totals = current_national_totals()
    return html.Div(
        className="tab-page",
        children=[
            section_header(
                "National Snapshot",
                "How have national Medicaid/CHIP enrollment, applications, and eligibility determinations changed over time?",
                "Use the KPI cards and interactive time-series explorers to review national trends without treating descriptive operations fields as performance scores.",
            ),
            html.Div(
                className="kpi-grid",
                children=[
                    card("Latest total Medicaid/CHIP enrollment", format_value(totals["total"]), f"{latest_month}; combined public coverage monitoring"),
                    card("Latest Medicaid enrollment", format_value(totals["medicaid"]), f"{latest_month}; Medicaid component of combined enrollment"),
                    card("Latest CHIP enrollment", format_value(totals["chip"]), f"{latest_month}; CHIP component of combined enrollment"),
                    card("Latest applications submitted", format_value(totals["applications"]), f"{latest_month}; not a backlog or performance score"),
                    card("Latest eligibility determinations", format_value(totals["determinations"]), f"{latest_month}; not an approval rate"),
                    card("Latest reporting status", latest_preliminary_status, f"{latest_month}; interpret preliminary data cautiously"),
                ],
            ),
            html.Div(
                className="two-column",
                children=[
                    html.Div(
                        className="panel",
                        children=[
                            html.H2("National Enrollment Trend Explorer"),
                            dcc.Graph(
                                figure=line_figure(
                                    national_enrollment,
                                    [
                                        ("total_medicaid_and_chip_enrollment", "Total Medicaid/CHIP"),
                                        ("total_medicaid_enrollment", "Medicaid"),
                                        ("total_chip_enrollment", "CHIP"),
                                    ],
                                    "National Medicaid/CHIP Enrollment Over Time",
                                    "Use the range slider and selector buttons to inspect specific periods.",
                                ),
                                config={"displayModeBar": False},
                            ),
                        ],
                    ),
                    html.Div(
                        className="panel",
                        children=[
                            html.H2("Applications And Determinations Trend Explorer"),
                            dcc.Graph(
                                figure=line_figure(
                                    national_ops,
                                    [
                                        ("applications_submitted", "Applications submitted"),
                                        ("total_medicaid_and_chip_determinations", "Eligibility determinations"),
                                    ],
                                    "National Eligibility Operations Over Time",
                                    "Same-month applications and determinations are descriptive operations indicators.",
                                ),
                                config={"displayModeBar": False},
                            ),
                        ],
                    ),
                ],
            ),
            html.Div(
                className="two-column",
                children=[
                    html.Div(
                        className="policy-note",
                        children=[
                            html.H2("Monitoring Questions"),
                            html.Ul(
                                [
                                    html.Li("Is combined Medicaid/CHIP enrollment rising, falling, or stabilizing nationally?"),
                                    html.Li("Are applications and determinations moving together or diverging descriptively?"),
                                    html.Li("Which periods require more source context before interpretation?"),
                                ]
                            ),
                        ],
                    ),
                    html.Div(
                        className="policy-note",
                        children=[
                            html.H2("Why Medicaid And CHIP Are Shown Together"),
                            html.P(
                                "The official CMS source reports Medicaid and CHIP both together and separately. "
                                "Combined Medicaid/CHIP enrollment supports overall public coverage monitoring, "
                                "while separate Medicaid and CHIP views help show whether changes are concentrated "
                                "in Medicaid, CHIP, or both."
                            ),
                        ],
                    ),
                ],
            ),
        ],
    )


def map_title(metric_key: str, reporting_month: str) -> tuple[str, str]:
    metric = MAP_METRICS[metric_key]
    if "per_1000_residents" in metric_key or "per_100000_residents" in metric_key:
        subtitle = (
            f"Map color represents {month_label(reporting_month)} {metric['label'].lower()} "
            f"using {population_year} state population denominators."
        )
    elif metric_key in {"percent_change_since_january_2019", "last_12_month_change", "change_since_april_2023"}:
        subtitle = f"Map color represents {metric['label'].lower()} as of {month_label(reporting_month)}."
    else:
        subtitle = f"Map color represents {month_label(reporting_month)} {metric['label'].lower()}."
    return f"State choropleth: {metric['label']}", subtitle


def build_hover(row: dict[str, object], metric_key: str) -> str:
    metric = MAP_METRICS[metric_key]
    return (
        f"<b>{row['state_name']}</b><br>"
        f"Reporting month: {month_label(str(row['reporting_month']))}<br>"
        f"{metric['label']}: {format_value(row.get('metric_value'), metric['kind'])}<br>"
        f"Total Medicaid/CHIP enrollment: {format_value(row['month_total_enrollment'])}<br>"
        f"Medicaid enrollment: {format_value(row['month_medicaid_enrollment'])}<br>"
        f"CHIP enrollment: {format_value(row['month_chip_enrollment'])}<br>"
        f"Enrollment per 1,000 residents: {format_value(row['medicaid_chip_enrollment_per_1000_residents'], 'decimal')}<br>"
        f"Population denominator year: {row['population_denominator_year']}<br>"
        f"Applications submitted: {format_value(row['month_applications'])}<br>"
        f"Eligibility determinations: {format_value(row['month_determinations'])}<br>"
        f"Preliminary/final reporting status: {row['month_preliminary_status']}"
    )


def build_map(metric_key: str, selected_state: str, reporting_month: str) -> go.Figure:
    metric = MAP_METRICS[metric_key]
    rows = map_rows_for_month(reporting_month, metric_key)
    fig = go.Figure(
        go.Choropleth(
            locations=[row["state_abbreviation"] for row in rows],
            z=[row.get("metric_value") for row in rows],
            locationmode="USA-states",
            colorscale=metric["scale"],
            colorbar={"title": metric["short"]},
            text=[build_hover(row, metric_key) for row in rows],
            customdata=[row["state_abbreviation"] for row in rows],
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


def build_state_profile(selected_state: str, reporting_month: str) -> html.Div:
    row = state_lookup.get(selected_state, state_rows[0])
    month_row = row_for_state_month(row["state_abbreviation"], reporting_month) or row_for_state_month(row["state_abbreviation"], LATEST_MONTH_VALUE) or {}
    peak = peak_lookup.get(row["state_abbreviation"], {})
    balance = latest_balance_lookup.get(row["state_abbreviation"], {})
    medicaid = to_float(month_row.get("total_medicaid_enrollment"))
    chip = to_float(month_row.get("total_chip_enrollment"))
    total = to_float(month_row.get("total_medicaid_and_chip_enrollment"))
    medicaid_share = ratio(medicaid, total, 100)
    chip_share = ratio(chip, total, 100)
    fields = [
        ("Reporting month", month_label(reporting_month)),
        ("Total Medicaid/CHIP enrollment", format_value(total)),
        ("Enrollment per 1,000 residents", format_value(month_metric_value(row["state_abbreviation"], reporting_month, "medicaid_chip_enrollment_per_1000_residents"), "decimal")),
        ("Medicaid enrollment", format_value(medicaid)),
        ("CHIP enrollment", format_value(chip)),
        ("Medicaid share of combined enrollment", format_value(medicaid_share, "percent")),
        ("CHIP share of combined enrollment", format_value(chip_share, "percent")),
        ("Change since January 2019", format_value(month_metric_value(row["state_abbreviation"], reporting_month, "latest_total_medicaid_chip_enrollment") - (to_float((row_for_state_month(row["state_abbreviation"], BASELINE_MONTH) or {}).get("total_medicaid_and_chip_enrollment")) or 0), "signed_integer") if total is not None else "Not available"),
        ("Change from peak", format_value(peak.get("change_from_peak"), "signed_integer")),
        ("Last 12-month change", format_value(month_metric_value(row["state_abbreviation"], reporting_month, "last_12_month_change"), "signed_integer")),
        ("Applications submitted", format_value(month_row.get("total_applications_for_financial_assistance_submitted_at_state_level"))),
        ("Eligibility determinations", format_value(month_row.get("total_medicaid_and_chip_determinations"))),
        ("Application-Determination Balance", format_value(balance.get("application_determination_balance"), "signed_integer")),
        ("Preliminary status", "Preliminary" if month_row.get("preliminary_or_updated") == "P" else "Final/updated"),
        ("Data missingness", format_value(row["missingness_percent"], "percent")),
    ]
    return html.Div(
        className="state-profile",
        children=[
            html.P("Selected State Snapshot", className="eyebrow"),
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


def ranking_bar(metric_key: str, reporting_month: str, ranking_view: str, selected_state: str) -> go.Figure:
    metric = MAP_METRICS[metric_key]
    ranked = sorted(
        [row for row in map_rows_for_month(reporting_month, metric_key) if row.get("metric_value") is not None],
        key=lambda row: row.get("metric_value") or 0,
        reverse=ranking_view != "bottom10",
    )
    if ranking_view in {"top10", "bottom10"}:
        ranked = ranked[:10]
    ranked = list(reversed(ranked))
    colors = ["#12324a" if row["state_abbreviation"] == selected_state else "#2f7d78" for row in ranked]
    fig = go.Figure(
        go.Bar(
            x=[row["metric_value"] for row in ranked],
            y=[f"{row['state_name']} ({row['state_abbreviation']})" for row in ranked],
            orientation="h",
            marker_color=colors,
            customdata=[row["state_abbreviation"] for row in ranked],
            hovertemplate=f"%{{y}}<br>{metric['label']}: %{{x:,.2f}}<extra></extra>",
        )
    )
    fig.update_layout(
        title={
            "text": f"State ranking: {metric['label']}<br><sup>Sorted for {month_label(reporting_month)}. Higher or lower rank is descriptive, not good or bad performance.</sup>"
        },
        margin={"l": 150, "r": 20, "t": 70, "b": 40},
        paper_bgcolor="white",
        plot_bgcolor="white",
        xaxis_title=metric["short"],
        yaxis_title=None,
    )
    return fig


def selected_state_self_comparison(selected_state: str) -> html.Div:
    row = state_lookup.get(selected_state, state_rows[0])
    rows = state_trend_rows(row["state_abbreviation"])
    baseline = row_for_state_month(row["state_abbreviation"], BASELINE_MONTH) or rows[0]
    latest = rows[-1]
    peak = max(rows, key=lambda record: to_float(record.get("total_medicaid_and_chip_enrollment")) or 0)
    prior_12 = row_months_before(row["state_abbreviation"], latest["reporting_month"]) or {}
    baseline_value = to_float(baseline.get("total_medicaid_and_chip_enrollment"))
    latest_value = to_float(latest.get("total_medicaid_and_chip_enrollment"))
    peak_value = to_float(peak.get("total_medicaid_and_chip_enrollment"))
    prior_12_value = to_float(prior_12.get("total_medicaid_and_chip_enrollment"))
    latest_medicaid = to_float(latest.get("total_medicaid_enrollment"))
    latest_chip = to_float(latest.get("total_chip_enrollment"))
    latest_applications = to_float(latest.get("total_applications_for_financial_assistance_submitted_at_state_level"))
    latest_determinations = to_float(latest.get("total_medicaid_and_chip_determinations"))
    balance = latest_balance_lookup.get(row["state_abbreviation"], {})
    comparison_cards = [
        card("January 2019 enrollment", format_value(baseline_value), "Baseline for indexed and change views"),
        card("Peak enrollment", format_value(peak_value), month_label(peak["reporting_month"])),
        card("Latest enrollment", format_value(latest_value), month_label(latest["reporting_month"])),
        card("Change since January 2019", format_value(latest_value - baseline_value if latest_value is not None and baseline_value is not None else None, "signed_integer"), format_value(percent_change(latest_value, baseline_value), "percent")),
        card("Change from peak", format_value(latest_value - peak_value if latest_value is not None and peak_value is not None else None, "signed_integer"), format_value(percent_change(latest_value, peak_value), "percent")),
        card("Last 12-month change", format_value(latest_value - prior_12_value if latest_value is not None and prior_12_value is not None else None, "signed_integer"), format_value(percent_change(latest_value, prior_12_value), "percent")),
        card("Latest Medicaid enrollment", format_value(latest_medicaid), "Latest state month"),
        card("Latest CHIP enrollment", format_value(latest_chip), "Latest state month"),
        card("Latest applications submitted", format_value(latest_applications), "Descriptive operations field"),
        card("Latest eligibility determinations", format_value(latest_determinations), "Descriptive operations field"),
        card("Application-Determination Balance", format_value(balance.get("application_determination_balance"), "signed_integer"), "Applications minus determinations; not backlog"),
    ]
    bar_fig = go.Figure(
        go.Bar(
            x=["January 2019", month_label(peak["reporting_month"]), month_label(latest["reporting_month"])],
            y=[baseline_value, peak_value, latest_value],
            marker_color=["#8aa6b2", "#2f7d78", "#12324a"],
            hovertemplate="%{x}<br>Enrollment: %{y:,.0f}<extra></extra>",
        )
    )
    bar_fig.update_layout(
        title="Baseline, Peak, And Latest Enrollment",
        margin={"l": 45, "r": 20, "t": 48, "b": 50},
        paper_bgcolor="white",
        plot_bgcolor="white",
        yaxis_title="Enrollment",
    )
    index_rows = []
    for month_row in rows:
        enrollment = to_float(month_row.get("total_medicaid_and_chip_enrollment"))
        index_rows.append(
            {
                "reporting_month": month_row["reporting_month"],
                "indexed_enrollment": ratio(enrollment, baseline_value, 100),
            }
        )
    indexed_fig = line_figure(
        index_rows,
        [("indexed_enrollment", "Indexed enrollment")],
        "Selected State Enrollment Trend Indexed To Jan. 2019",
        "Shows relative change over time for the selected state; index values do not show raw enrollment size.",
        "Index, Jan. 2019 = 100",
    )
    return html.Div(
        className="wide-stack",
        children=[
            html.Div(className="section-subhead", children=[html.H2("Selected State Self-Comparison"), html.P("Compare the selected state against its own baseline, peak, latest month, and recent history.")]),
            html.Div(className="kpi-grid compact", children=comparison_cards),
            html.Div(
                className="two-column",
                children=[
                    html.Div(className="panel", children=[dcc.Graph(figure=bar_fig, config={"displayModeBar": False})]),
                    html.Div(className="panel", children=[dcc.Graph(figure=indexed_fig, config={"displayModeBar": False})]),
                ],
            ),
        ],
    )


def build_maps_tab() -> html.Div:
    return html.Div(
        className="tab-page",
        children=[
            section_header(
                "State Map Explorer",
                "Which states show the largest enrollment counts, population-adjusted enrollment levels, or enrollment changes?",
                "Use the metric dropdown, reporting month slider, and ranking control to compare geographic distribution with relative state position.",
            ),
            html.Div(
                className="controls",
                children=[
                    html.Label(
                        [html.Span("Map metric"), dcc.Dropdown(id="map-metric", options=[{"label": cfg["label"], "value": key} for key, cfg in MAP_METRICS.items()], value="medicaid_chip_enrollment_per_1000_residents", clearable=False)]
                    ),
                    html.Label([html.Span("Selected state"), dcc.Dropdown(id="state-selector", options=sorted_states(state_rows), value="CA", clearable=False)]),
                    html.Label(
                        [
                            html.Span("Ranking view"),
                            dcc.RadioItems(
                                id="map-ranking-view",
                                options=[
                                    {"label": "Top 10", "value": "top10"},
                                    {"label": "Bottom 10", "value": "bottom10"},
                                    {"label": "All states", "value": "all"},
                                ],
                                value="top10",
                                className="segmented-control",
                                inline=True,
                            ),
                        ]
                    ),
                ],
            ),
            html.Div(
                className="month-control",
                children=[
                    html.Label("Reporting month / time control"),
                    dcc.Slider(
                        id="map-month-slider",
                        min=0,
                        max=len(MONTH_VALUES) - 1,
                        step=1,
                        value=len(MONTH_VALUES) - 1,
                        marks=month_slider_marks(),
                        tooltip={"placement": "bottom", "always_visible": False},
                    ),
                    html.Strong(id="selected-map-month"),
                ],
            ),
            html.Div(className="map-title-block", children=[html.H2(id="map-title"), html.P(id="map-subtitle")]),
            html.Div(
                className="map-chart-layout",
                children=[
                    html.Div(className="panel map-panel", children=[dcc.Graph(id="state-map", className="state-map", config={"displayModeBar": False}), html.P(id="raw-map-note", className="small-note")]),
                    html.Div(className="panel ranking-panel", children=[dcc.Graph(id="state-ranking-chart", config={"displayModeBar": False})]),
                ],
            ),
            html.P(
                className="small-note map-note",
                children="The map shows geographic distribution, while the ranking chart shows relative state position for the selected metric. High or low rank is descriptive, not good or bad performance.",
            ),
            html.Div(
                className="two-column",
                children=[
                    html.Aside(id="state-profile", className="profile-panel"),
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
            html.Div(id="state-self-comparison"),
        ],
    )


def state_trend_rows(selected_state: str) -> list[dict[str, str]]:
    return state_month_lookup.get(selected_state, [])


def state_balance_rows(selected_state: str) -> list[dict[str, str]]:
    return balance_lookup.get(selected_state, [])


def latest_split_bar(selected_state: str | None = None) -> go.Figure:
    if selected_state and selected_state in state_lookup:
        row = state_lookup[selected_state]
        title = f"Latest Medicaid Vs CHIP Split: {row['state_name']}"
        medicaid = to_float(row["latest_medicaid_enrollment"])
        chip = to_float(row["latest_chip_enrollment"])
    else:
        totals = current_national_totals()
        title = "Latest National Medicaid Vs CHIP Split"
        medicaid = totals["medicaid"]
        chip = totals["chip"]
    fig = go.Figure(
        go.Bar(
            x=["Medicaid", "CHIP"],
            y=[medicaid, chip],
            marker_color=["#12324a", "#2f7d78"],
            hovertemplate="%{x}<br>Enrollment: %{y:,.0f}<extra></extra>",
        )
    )
    fig.update_layout(
        title=title,
        margin={"l": 44, "r": 20, "t": 52, "b": 42},
        paper_bgcolor="white",
        plot_bgcolor="white",
        yaxis_title="Enrollment",
    )
    return fig


def build_chip_tab() -> html.Div:
    return html.Div(
        className="tab-page",
        children=[
            section_header(
                "Medicaid vs CHIP Drivers",
                "Are enrollment patterns concentrated in Medicaid, CHIP, or both?",
                "Compare combined Medicaid/CHIP enrollment with separate Medicaid and CHIP components to understand which program contributes to descriptive changes.",
            ),
            html.Div(className="note-banner subdued", children="CHIP reporting can vary by state, and CHIP may include adults in some states according to source caveats."),
            html.Div(
                className="two-column",
                children=[
                    html.Div(className="panel", children=[dcc.Graph(figure=latest_split_bar(), config={"displayModeBar": False})]),
                    html.Div(className="panel", children=[dcc.Graph(id="state-chip-split", config={"displayModeBar": False})]),
                ],
            ),
            html.Div(
                className="panel",
                children=[
                    html.H2("Selected State Medicaid Vs CHIP Trend Explorer"),
                    dcc.Graph(id="state-chip-trend", config={"displayModeBar": False}),
                ],
            ),
            html.Div(id="state-chip-summary", className="kpi-grid compact"),
            html.Div(
                className="policy-note wide",
                children=[
                    html.H2("Medicaid Vs CHIP Interpretation"),
                    html.P(
                        "Combined Medicaid/CHIP enrollment supports overall coverage monitoring. Separate Medicaid "
                        "and CHIP views help identify which program contributes to state-level changes. Contribution "
                        "metrics are descriptive and do not estimate policy effects."
                    ),
                ],
            ),
        ],
    )


def build_operations_tab() -> html.Div:
    return html.Div(
        className="tab-page",
        children=[
            section_header(
                "Eligibility Operations",
                "How do applications submitted and eligibility determinations compare across states and over time?",
                "Use applications, determinations, and Application-Determination Balance as descriptive operations indicators, not performance scores.",
            ),
            html.Div(
                className="note-banner subdued",
                children=(
                    "Application-Determination Balance compares same-month applications submitted with "
                    "Medicaid/CHIP determinations. It is a descriptive operations indicator and should "
                    "not be interpreted as backlog, timeliness, approval rate, or performance."
                ),
            ),
            html.Div(
                className="two-column",
                children=[
                    html.Div(className="panel", children=[html.H2("National Applications And Determinations Explorer"), dcc.Graph(figure=line_figure(national_ops, [("applications_submitted", "Applications submitted"), ("total_medicaid_and_chip_determinations", "Determinations")], "National Eligibility Operations", "Range controls support descriptive review over time."), config={"displayModeBar": False})]),
                    html.Div(className="panel", children=[html.H2("Selected State Operations Trend Explorer"), dcc.Graph(id="state-operations-trend", config={"displayModeBar": False})]),
                ],
            ),
            html.Div(id="state-operations-summary", className="kpi-grid compact"),
            html.Div(
                className="two-column",
                children=[
                    html.Div(
                        className="panel",
                        children=[
                            html.H2("Latest Balance Per 100,000 Residents"),
                            balance_top_table(),
                        ],
                    ),
                    html.Div(
                        className="policy-note",
                        children=[
                            html.H2("Operations Interpretation"),
                            html.P(
                                "A positive same-month balance means applications submitted exceeded determinations "
                                "in that month; a negative balance means determinations exceeded applications. This "
                                "does not identify backlog, delay, timeliness, approval rate, or state performance."
                            ),
                        ],
                    ),
                ],
            ),
            html.Div(id="state-balance-summary", className="kpi-grid compact"),
            html.Div(className="panel visually-hidden", children=[dcc.Graph(id="state-balance-trend", config={"displayModeBar": False})]),
        ],
    )


def balance_top_table() -> html.Table:
    group_labels = {
        "highest_positive_balance_per_100000_residents": "Highest positive balance",
        "highest_negative_balance_per_100000_residents": "Highest negative balance",
    }
    return html.Table(
        className="compact-table",
        children=[
            html.Thead(
                html.Tr(
                    [
                        html.Th("Group"),
                        html.Th("Rank"),
                        html.Th("State"),
                        html.Th("Latest month"),
                        html.Th("Balance"),
                        html.Th("Balance per 100,000 residents"),
                    ]
                )
            ),
            html.Tbody(
                [
                    html.Tr(
                        [
                            html.Td(group_labels.get(row["direction"], row["direction"])),
                            html.Td(row["rank"]),
                            html.Td(row["state_abbreviation"]),
                            html.Td(row["latest_reporting_month"]),
                            html.Td(format_value(row["application_determination_balance"], "signed_integer")),
                            html.Td(
                                format_value(
                                    row[
                                        "application_determination_balance_per_100000_residents"
                                    ],
                                    "decimal",
                                )
                            ),
                        ]
                    )
                    for row in top_balance_rows
                ]
            ),
        ],
    )


def count_by(rows: list[dict[str, str]], field: str) -> list[dict[str, object]]:
    counts: dict[str, int] = {}
    for row in rows:
        counts[row[field]] = counts.get(row[field], 0) + 1
    return [
        {"label": label, "count": count}
        for label, count in sorted(counts.items(), key=lambda item: item[1], reverse=True)
    ]


def flag_count_bar(rows: list[dict[str, str]], field: str, title: str, limit: int = 12) -> go.Figure:
    counts = count_by(rows, field)[:limit]
    fig = go.Figure(
        go.Bar(
            x=[row["label"] for row in counts],
            y=[row["count"] for row in counts],
            marker_color="#276a62",
            hovertemplate="%{x}<br>Review flags: %{y:,.0f}<extra></extra>",
        )
    )
    fig.update_layout(
        title=title,
        margin={"l": 42, "r": 18, "t": 48, "b": 86},
        paper_bgcolor="white",
        plot_bgcolor="white",
        xaxis_tickangle=-35,
        yaxis_title="Review flags",
    )
    return fig


def recent_change_bar() -> go.Figure:
    ranked = sorted(
        state_monitoring_rows,
        key=lambda row: abs(to_float(row["last_12_month_change"]) or 0),
        reverse=True,
    )[:12]
    values = [to_float(row["last_12_month_change"]) or 0 for row in ranked]
    colors = ["#276a62" if value >= 0 else "#b45309" for value in values]
    fig = go.Figure(
        go.Bar(
            x=[f"{row['state_name']} ({row['state_abbreviation']})" for row in ranked],
            y=values,
            marker_color=colors,
            hovertemplate="%{x}<br>Last 12-month change: %{y:+,.0f}<extra></extra>",
        )
    )
    fig.update_layout(
        title="Largest Recent Enrollment Changes",
        margin={"l": 42, "r": 18, "t": 48, "b": 100},
        paper_bgcolor="white",
        plot_bgcolor="white",
        xaxis_tickangle=-35,
        yaxis_title="Last 12-month change",
    )
    return fig


def monitoring_table(rows: list[dict[str, str]], limit: int = 25) -> html.Table:
    flag_labels = {
        "large_month_over_month_enrollment_change": "Large month-over-month enrollment change",
        "large_applications_spike": "Large applications spike",
        "large_determinations_spike": "Large determinations spike",
        "latest_month_preliminary_reporting_caution": "Latest-month preliminary reporting caution",
        "high_missingness_caution": "High missingness caution",
    }
    columns = [
        ("state_abbreviation", "State"),
        ("reporting_month", "Month"),
        ("flag_type", "Review flag"),
        ("flag_description", "Description"),
        ("metric_value", "Metric value"),
        ("comparison_value", "Comparison"),
    ]
    return html.Table(
        className="compact-table",
        children=[
            html.Thead(html.Tr([html.Th(label) for _, label in columns])),
            html.Tbody(
                [
                    html.Tr(
                        [
                            html.Td(flag_labels.get(row.get(field, ""), row.get(field, "")))
                            if field == "flag_type"
                            else html.Td(row.get(field, ""))
                            if field not in {"metric_value", "comparison_value"}
                            else html.Td(format_value(row.get(field), "decimal"))
                            for field, _ in columns
                        ]
                    )
                    for row in rows[:limit]
                ]
            ),
        ],
    )


def build_monitoring_tab() -> html.Div:
    national = national_monitoring_rows[0]
    return html.Div(
        className="tab-page",
        children=[
            section_header(
                "Monitoring Flags",
                "Which state-month changes may warrant context review?",
                "Review flags identify unusual changes or reporting caveats that may deserve follow-up; they do not identify errors, failures, or causal effects.",
            ),
            html.Div(
                className="note-banner subdued",
                children=(
                    "Review flags identify unusual changes or reporting caveats that may deserve follow-up. "
                    "They do not identify errors, performance failures, or causal effects."
                ),
            ),
            html.Div(
                className="kpi-grid compact",
                children=[
                    card("Total review flags", format_value(national["total_review_flags"]), "Across state-month monitoring outputs"),
                    card("Enrollment change flags", format_value(national["enrollment_change_flag_count"]), "Large month-over-month changes"),
                    card("Applications spike flags", format_value(national["applications_spike_flag_count"]), "Compared with recent state patterns"),
                    card("Determinations spike flags", format_value(national["determinations_spike_flag_count"]), "Compared with recent state patterns"),
                    card("Latest preliminary flags", format_value(national["latest_month_preliminary_flag_count"]), "Latest month reporting caution"),
                    card("High missingness flags", format_value(national["high_missingness_flag_count"]), "Data quality caution"),
                ],
            ),
            html.Div(
                className="controls",
                children=[
                    html.Label(
                        [
                            html.Span("State filter"),
                            dcc.Dropdown(
                                id="monitoring-state-filter",
                                options=selected_state_options_with_all(),
                                value="ALL",
                                clearable=False,
                            ),
                        ]
                    ),
                    html.Label(
                        [
                            html.Span("Review flag type"),
                            dcc.Dropdown(
                                id="monitoring-flag-filter",
                                options=flag_type_options(),
                                value="ALL",
                                clearable=False,
                            ),
                        ]
                    ),
                ],
            ),
            html.Div(
                className="two-column",
                children=[
                    html.Div(className="panel", children=[dcc.Graph(id="flags-by-state", config={"displayModeBar": False})]),
                    html.Div(className="panel", children=[dcc.Graph(id="flags-by-month", config={"displayModeBar": False})]),
                ],
            ),
            html.Div(
                className="two-column",
                children=[
                    html.Div(className="panel", children=[dcc.Graph(figure=recent_change_bar(), config={"displayModeBar": False})]),
                    html.Div(
                        className="policy-note",
                        children=[
                            html.H2("How To Read Review Flags"),
                            html.P(
                                "Monitoring flags use transparent thresholds to identify records that warrant context review. "
                                "They are prompts for source review and follow-up questions, not labels of state problems or policy impact."
                            ),
                            html.P(
                                "Use these alongside source notes, preliminary reporting status, and data quality tables."
                            ),
                        ],
                    ),
                ],
            ),
            html.Div(className="panel", children=[html.H2("State/Month Review Flags"), html.Div(id="monitoring-flags-table")]),
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


def missingness_field_bar() -> go.Figure:
    rows = sorted(quality_field_rows, key=lambda row: to_float(row.get("missing_percent")) or 0, reverse=True)[:14]
    rows = list(reversed(rows))
    fig = go.Figure(
        go.Bar(
            x=[to_float(row.get("missing_percent")) for row in rows],
            y=[row["field_name"] for row in rows],
            orientation="h",
            marker_color="#b7791f",
            hovertemplate="%{y}<br>Missingness: %{x:.1f}%<extra></extra>",
        )
    )
    fig.update_layout(
        title="Missingness By Field",
        margin={"l": 210, "r": 20, "t": 50, "b": 42},
        paper_bgcolor="white",
        plot_bgcolor="white",
        xaxis_title="Missing percent",
        yaxis_title=None,
    )
    return fig


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
            section_header(
                "Data Quality Review",
                "Which fields are reliable enough for headline reporting, and which require caution?",
                "Review missingness, preliminary reporting, and excluded fields before interpreting headline metrics.",
            ),
            html.Div(
                className="two-column",
                children=[
                    html.Div(className="panel", children=[dcc.Graph(figure=missingness_field_bar(), config={"displayModeBar": False})]),
                    html.Div(className="panel", children=[html.H2("Missingness By State"), table_from_rows(top_state_missing, [("state_abbreviation", "State"), ("missing_value_percent", "Missing %")], 12)]),
                ],
            ),
            html.Div(
                className="two-column",
                children=[
                    html.Div(className="panel", children=[html.H2("Latest Month Status"), table_from_rows(quality_month_rows[-6:], [("reporting_month", "Month"), ("preliminary_records", "Preliminary records")], 6)]),
                    html.Div(className="panel", children=[html.H2("Excluded From Headline Metrics"), html.Ul([html.Li([html.Strong(f"{field}: "), reason]) for field, reason in excluded])]),
                ],
            ),
            html.Div(
                className="two-column",
                children=[
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
            section_header(
                "Methods & Limits",
                "What can this public aggregate dataset show, and what can it not show?",
                "This section documents source coverage, analytic grain, appropriate uses, and interpretation limits.",
            ),
            html.Div(
                className="policy-note wide",
                children=[
                    html.H2("Policy Context"),
                    html.Ul(
                        [
                            html.Li("Medicaid and CHIP are state-federal coverage programs, and states administer them within federal rules."),
                            html.Li("State variation in eligibility rules, program structure, reporting practices, and administrative processes affects comparisons."),
                            html.Li("Pandemic-era continuous enrollment and the post-2023 unwinding period are important context for interpreting enrollment changes."),
                            html.Li("Population-adjusted metrics help compare states of different sizes, but they are not usage rates or healthcare utilization measures."),
                            html.Li("Applications and determinations are descriptive operations indicators, not approval rates, timeliness measures, or performance scores."),
                            html.Li("The dashboard supports descriptive monitoring and context review; it does not estimate causal policy effects."),
                        ]
                    ),
                ],
            ),
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
                    html.Div(className="panel", children=[html.H2("What The Dashboard Can Show"), html.Ul([html.Li("Medicaid/CHIP enrollment trends."), html.Li("Medicaid vs CHIP patterns."), html.Li("State variation."), html.Li("Applications and eligibility determinations."), html.Li("Population-adjusted context."), html.Li("Data quality caveats."), html.Li("Review flags for unusual changes.")])]),
                    html.Div(className="panel", children=[html.H2("What The Dashboard Cannot Show"), html.Ul([html.Li("No beneficiary-level outcomes."), html.Li("No county-level patterns."), html.Li("No claims, utilization, cost, or diagnosis data."), html.Li("No causal policy effects."), html.Li("No pending applications."), html.Li("No renewal volumes as clean standalone measures."), html.Li("No complete operations performance across all fields.")])]),
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
                html.P("CMS public data monitoring tool", className="eyebrow"),
                html.H1("Medicaid Enrollment & Eligibility Operations Analytics"),
                html.P(
                    "A public CMS data monitoring tool for Medicaid/CHIP enrollment, eligibility operations, "
                    "state variation, and reporting quality.",
                    className="header-copy",
                ),
                html.Div(
                    className="hero-badges",
                    children=[
                        html.Span("CMS public data"),
                        html.Span("Jan. 2019-Feb. 2026"),
                        html.Span("50 states + DC"),
                        html.Span("State-month aggregate panel"),
                        html.Span("Descriptive monitoring"),
                        html.Span("Latest month preliminary", className="amber-chip"),
                    ],
                ),
            ],
        ),
        html.Div(className="global-warning", children=NOTE_TEXT),
        dcc.Tabs(
            id="main-tabs",
            value="overview",
            className="tabs",
            children=[
                dcc.Tab(label="National Snapshot", value="overview", children=build_overview_tab()),
                dcc.Tab(label="State Map Explorer", value="maps", children=build_maps_tab()),
                dcc.Tab(label="Medicaid vs CHIP Drivers", value="chip", children=build_chip_tab()),
                dcc.Tab(label="Eligibility Operations", value="operations", children=build_operations_tab()),
                dcc.Tab(label="Monitoring Flags", value="monitoring", children=build_monitoring_tab()),
                dcc.Tab(label="Data Quality Review", value="quality", children=build_quality_tab()),
                dcc.Tab(label="Methods & Limits", value="about", children=build_about_tab()),
            ],
        ),
        html.Footer(
            className="app-footer",
            children="Built from official CMS/Data.Medicaid.gov public aggregate data. Descriptive monitoring only; not causal policy evaluation.",
        ),
    ],
)


@app.callback(
    Output("map-title", "children"),
    Output("map-subtitle", "children"),
    Output("state-map", "figure"),
    Output("state-ranking-chart", "figure"),
    Output("state-profile", "children"),
    Output("raw-map-note", "children"),
    Output("selected-map-month", "children"),
    Output("state-self-comparison", "children"),
    Input("map-metric", "value"),
    Input("state-selector", "value"),
    Input("map-month-slider", "value"),
    Input("map-ranking-view", "value"),
)
def update_map(metric_key: str, selected_state: str, month_index: int, ranking_view: str):
    if metric_key not in MAP_METRICS:
        metric_key = "medicaid_chip_enrollment_per_1000_residents"
    if selected_state not in state_lookup:
        selected_state = "CA"
    if month_index is None or month_index < 0 or month_index >= len(MONTH_VALUES):
        month_index = len(MONTH_VALUES) - 1
    reporting_month = MONTH_VALUES[month_index]
    if ranking_view not in {"top10", "bottom10", "all"}:
        ranking_view = "top10"
    title, subtitle = map_title(metric_key, reporting_month)
    raw_note = (
        "Raw enrollment counts are affected by state population size. Use population-adjusted metrics for relative state comparison."
        if MAP_METRICS[metric_key]["raw"]
        else "This metric uses population or enrollment denominators for descriptive comparison; it is not a utilization or performance rate."
    )
    return (
        title,
        subtitle,
        build_map(metric_key, selected_state, reporting_month),
        ranking_bar(metric_key, reporting_month, ranking_view, selected_state),
        build_state_profile(selected_state, reporting_month),
        raw_note,
        month_label(reporting_month),
        selected_state_self_comparison(selected_state),
    )


@app.callback(
    Output("state-selector", "value"),
    Input("state-map", "clickData"),
    Input("state-ranking-chart", "clickData"),
    prevent_initial_call=True,
)
def select_state_from_visuals(map_click, bar_click):
    from dash import callback_context

    trigger = callback_context.triggered[0]["prop_id"] if callback_context.triggered else ""
    click_data = bar_click if trigger.startswith("state-ranking-chart") else map_click
    if click_data and click_data.get("points"):
        point = click_data["points"][0]
        state = point.get("customdata") or point.get("location")
        if state in state_lookup:
            return state
    return "CA"


@app.callback(
    Output("state-chip-split", "figure"),
    Output("state-chip-trend", "figure"),
    Output("state-chip-summary", "children"),
    Output("state-operations-trend", "figure"),
    Output("state-operations-summary", "children"),
    Output("state-balance-trend", "figure"),
    Output("state-balance-summary", "children"),
    Input("state-selector", "value"),
)
def update_state_sections(selected_state: str):
    if selected_state not in state_lookup:
        selected_state = "CA"
    selected = state_lookup[selected_state]
    rows = state_trend_rows(selected_state)
    balance = latest_balance_lookup.get(selected_state, {})
    balance_trend_rows = state_balance_rows(selected_state)
    chip_split = latest_split_bar(selected_state)
    chip_fig = line_figure(
        rows,
        [("total_medicaid_enrollment", "Medicaid"), ("total_chip_enrollment", "CHIP")],
        f"{selected['state_name']} Medicaid And CHIP Enrollment",
        "Separate component trends help show whether changes are concentrated in Medicaid, CHIP, or both.",
    )
    ops_fig = line_figure(
        rows,
        [("total_applications_for_financial_assistance_submitted_at_state_level", "Applications submitted"), ("total_medicaid_and_chip_determinations", "Determinations")],
        f"{selected['state_name']} Applications And Determinations",
        "Same-month fields are descriptive operations indicators.",
    )
    balance_fig = line_figure(
        balance_trend_rows,
        [("application_determination_balance", "Application-Determination Balance")],
        f"{selected['state_name']} Application-Determination Balance",
        "Applications minus determinations; not backlog, timeliness, approval rate, or performance.",
    )
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
    balance_summary = [
        card("Selected state balance", format_value(balance.get("application_determination_balance"), "signed_integer"), "Applications minus determinations"),
        card("Balance per 100,000 residents", format_value(balance.get("application_determination_balance_per_100000_residents"), "decimal"), "Population-adjusted context"),
        card("Applications submitted", format_value(balance.get("applications_submitted")), "Latest month"),
        card("Eligibility determinations", format_value(balance.get("total_medicaid_chip_determinations")), "Latest month"),
        card("Determinations per application", format_value(balance.get("determinations_per_application"), "ratio"), "Descriptive relationship"),
    ]
    return chip_split, chip_fig, chip_summary, ops_fig, ops_summary, balance_fig, balance_summary


@app.callback(
    Output("flags-by-state", "figure"),
    Output("flags-by-month", "figure"),
    Output("monitoring-flags-table", "children"),
    Input("monitoring-state-filter", "value"),
    Input("monitoring-flag-filter", "value"),
)
def update_monitoring_flags(selected_state: str, flag_type: str):
    filtered = monitoring_flag_rows
    if selected_state and selected_state != "ALL":
        filtered = [row for row in filtered if row["state_abbreviation"] == selected_state]
    if flag_type and flag_type != "ALL":
        filtered = [row for row in filtered if row["flag_type"] == flag_type]

    if not filtered:
        empty_fig = go.Figure()
        empty_fig.update_layout(
            title="No review flags match the selected filters",
            paper_bgcolor="white",
            plot_bgcolor="white",
        )
        return empty_fig, empty_fig, html.P("No review flags match the selected filters.")

    return (
        flag_count_bar(filtered, "state_abbreviation", "Review Flags By State"),
        flag_count_bar(filtered, "reporting_month", "Review Flags By Month"),
        monitoring_table(filtered),
    )


if __name__ == "__main__":
    app.run(debug=False, host="127.0.0.1", port=8050, use_reloader=False)
