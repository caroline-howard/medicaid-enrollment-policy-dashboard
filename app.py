from __future__ import annotations

import csv
import importlib.abc
import os
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
from dash import Dash, Input, Output, dcc, html, ctx, no_update
sys.meta_path.remove(_ipython_blocker)


BASE_DIR = Path(__file__).resolve().parent
DASHBOARD_DIR = BASE_DIR / "outputs" / "dashboard_tables"
PROCESSED_DIR = BASE_DIR / "data" / "processed"
MANUAL_DIR = BASE_DIR / "data" / "manual"
CONTEXT_DIR = BASE_DIR / "data" / "context"

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


def format_short(value: str | int | float | None) -> str:
    numeric = to_float(value)
    if numeric is None:
        return "n/a"
    sign = "-" if numeric < 0 else ""
    numeric = abs(numeric)
    if numeric >= 1_000_000:
        return f"{sign}{numeric / 1_000_000:.1f}M"
    if numeric >= 1_000:
        return f"{sign}{numeric / 1_000:.0f}K"
    return f"{sign}{numeric:.0f}"


def format_signed_short(value: str | int | float | None) -> str:
    numeric = to_float(value)
    if numeric is None:
        return "n/a"
    sign = "+" if numeric > 0 else "-" if numeric < 0 else ""
    return f"{sign}{format_short(abs(numeric)) if numeric != 0 else '0'}"


def format_dollars_short(value: str | int | float | None) -> str:
    numeric = to_float(value)
    if numeric is None:
        return "Not available"
    sign = "-" if numeric < 0 else ""
    numeric = abs(numeric)
    if numeric >= 1_000_000_000:
        return f"{sign}${numeric / 1_000_000_000:.1f}B"
    if numeric >= 1_000_000:
        return f"{sign}${numeric / 1_000_000:.1f}M"
    if numeric >= 1_000:
        return f"{sign}${numeric / 1_000:.0f}K"
    return f"{sign}${numeric:,.0f}"


def month_label(value: str) -> str:
    if not value:
        return "Not available"
    return datetime.strptime(value[:10], "%Y-%m-%d").strftime("%B %Y")


def short_month_label(value: str) -> str:
    if not value:
        return "Not available"
    month = datetime.strptime(value[:10], "%Y-%m-%d").strftime("%b")
    month = {
        "Jan": "Jan.",
        "Feb": "Feb.",
        "Mar": "Mar.",
        "Apr": "Apr.",
        "Jun": "Jun.",
        "Jul": "Jul.",
        "Aug": "Aug.",
        "Sep": "Sep.",
        "Oct": "Oct.",
        "Nov": "Nov.",
        "Dec": "Dec.",
    }.get(month, month)
    return f"{month} {datetime.strptime(value[:10], '%Y-%m-%d').strftime('%Y')}"


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
state_context_rows = read_rows(MANUAL_DIR / "state_demographic_context_candidates.csv")
state_expenditure_rows = read_rows(MANUAL_DIR / "state_expenditure_context_candidates.csv")
medicaid_fmap_rows = read_rows(CONTEXT_DIR / "kff_medicaid_fmap_multiplier.csv")
chip_efmap_rows = read_rows(CONTEXT_DIR / "kff_chip_efmap.csv")
chip_structure_rows = read_rows(CONTEXT_DIR / "chip_program_structure.csv")

state_lookup = {row["state_abbreviation"]: row for row in state_rows}
DEFAULT_OVERVIEW_STATE = "FL" if "FL" in state_lookup else sorted_states(state_rows)[0]["value"]
DEFAULT_STATE_A = "AR" if "AR" in state_lookup else DEFAULT_OVERVIEW_STATE
DEFAULT_STATE_B = "CA" if "CA" in state_lookup and "CA" != DEFAULT_STATE_A else next(
    row["value"] for row in sorted_states(state_rows) if row["value"] != DEFAULT_STATE_A
)
state_map_lookup = {row["state_abbreviation"]: row for row in state_map_rows}
latest_balance_lookup = {row["state_abbreviation"]: row for row in latest_balance_rows}
peak_lookup = {row["state_abbreviation"]: row for row in peak_change_rows}
state_monitoring_lookup = {
    row["state_abbreviation"]: row for row in state_monitoring_rows
}
state_context_lookup: dict[str, dict[str, dict[str, str]]] = {}
for row in state_context_rows:
    state_context_lookup.setdefault(row["state_abbr"], {})[row["demographic_subcategory"]] = row
state_expenditure_lookup: dict[str, list[dict[str, str]]] = {}
for row in state_expenditure_rows:
    state_expenditure_lookup.setdefault(row["state_abbr"], []).append(row)
for rows in state_expenditure_lookup.values():
    rows.sort(key=lambda row: (row["fiscal_year"], row["program_category"], row["expenditure_category"]))
FISCAL_YEAR_VALUES = sorted(
    {row["fiscal_year"] for row in state_expenditure_rows if row.get("fiscal_year")},
    key=lambda value: int(value),
)
LATEST_FISCAL_YEAR_VALUE = FISCAL_YEAR_VALUES[-1] if FISCAL_YEAR_VALUES else "2024"
medicaid_fmap_lookup = {
    (row["state_abbr"], row["fiscal_year"]): row for row in medicaid_fmap_rows
}
chip_efmap_lookup = {
    (row["state_abbr"], row["fiscal_year"]): row for row in chip_efmap_rows
}
chip_structure_lookup = {
    row["state_abbr"]: row for row in chip_structure_rows
}
FINANCING_FISCAL_YEAR = max(
    set(row["fiscal_year"] for row in medicaid_fmap_rows)
    & set(row["fiscal_year"] for row in chip_efmap_rows)
) if medicaid_fmap_rows and chip_efmap_rows else LATEST_FISCAL_YEAR_VALUE
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
RELIABLE_MISSINGNESS_THRESHOLD = 5.0

quality_month_lookup = {row["reporting_month"]: row for row in quality_month_rows}


def month_quality_metrics(reporting_month: str) -> dict[str, object]:
    row = quality_month_lookup.get(reporting_month, {})
    missingness = to_float(row.get("missing_value_percent"))
    preliminary_records = int(row.get("preliminary_records") or 0) if row else 0
    is_preliminary = preliminary_records > 0 or str(row.get("all_records_final", "")).lower() == "false"
    elevated_missingness = missingness is not None and missingness > RELIABLE_MISSINGNESS_THRESHOLD
    return {
        "reporting_month": reporting_month,
        "missingness_percent": missingness,
        "is_preliminary": is_preliminary,
        "elevated_missingness": elevated_missingness,
    }


def latest_reliable_month_value() -> str:
    for month in reversed(MONTH_VALUES):
        quality = month_quality_metrics(month)
        if not quality["is_preliminary"] and not quality["elevated_missingness"]:
            return month
    return LATEST_MONTH_VALUE


LATEST_RELIABLE_MONTH_VALUE = latest_reliable_month_value()

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

MAP_EXPLORER_METRIC_KEYS = [
    "latest_total_medicaid_chip_enrollment",
    "latest_medicaid_enrollment",
    "latest_chip_enrollment",
    "medicaid_chip_enrollment_per_1000_residents",
    "percent_change_since_january_2019",
    "change_since_april_2023",
    "last_12_month_change",
    "applications_submitted_per_100000_residents",
    "eligibility_determinations_per_100000_residents",
    "applications_per_1000_enrollees",
    "determinations_per_1000_enrollees",
]

TWO_STATE_COMPARISON_METRIC_KEYS = [
    "medicaid_chip_enrollment_per_1000_residents",
    "percent_change_since_january_2019",
    "applications_submitted_per_100000_residents",
]

RANK_STRIP_METRIC_KEY = "medicaid_chip_enrollment_per_1000_residents"


def line_figure(
    rows: list[dict[str, str]],
    traces: list[tuple[str, str]],
    title: str | None = None,
    subtitle: str | None = None,
    y_axis_title: str | None = None,
    x_axis_title: str = "Reporting month",
    scope_label: str = "National",
    value_kind: str = "integer",
    reference_lines: list[tuple[str, str]] | None = None,
    add_latest_labels: bool = True,
    height: int = 430,
    show_range_slider: bool = True,
    show_post_peak_button: bool = True,
) -> go.Figure:
    fig = go.Figure()
    x_values = [row["reporting_month"] for row in rows]
    for field, label in traces:
        y_values = [to_float(row.get(field)) for row in rows]
        customdata = [
            [
                scope_label,
                label,
                "Preliminary" if row.get("preliminary_or_updated") == "P" else row.get("latest_month_preliminary_status", "Final/updated"),
            ]
            for row in rows
        ]
        fig.add_trace(
            go.Scatter(
                x=x_values,
                y=y_values,
                mode="lines",
                name=label,
                customdata=customdata,
                line={"width": 2.8},
                hovertemplate=(
                    "Scope: %{customdata[0]}<br>"
                    "Reporting month: %{x|%b %Y}<br>"
                    "Metric: %{customdata[1]}<br>"
                    "Value: %{y:,.2f}<br>"
                    "Reporting status: %{customdata[2]}<extra></extra>"
                ),
            )
        )
        if add_latest_labels:
            latest_points = [(x, y) for x, y in zip(x_values, y_values) if y is not None]
            if latest_points:
                latest_x, latest_y = latest_points[-1]
                fig.add_annotation(
                    x=latest_x,
                    y=latest_y,
                    text=f"{label}: {format_short(latest_y) if value_kind == 'integer' else format_value(latest_y, 'decimal')}",
                    showarrow=False,
                    xanchor="left",
                    xshift=8,
                    font={"size": 11, "color": "#243746"},
                    bgcolor="rgba(255,255,255,0.78)",
                    bordercolor="#dce2df",
                    borderwidth=1,
                )
    for reference_date, label in reference_lines or []:
        if reference_date in x_values:
            fig.add_vline(
                x=reference_date,
                line_width=1,
                line_dash="dash",
                line_color="#b7791f",
                annotation_text=label,
                annotation_position="top left",
                annotation_font_size=10,
            )
    fig.update_layout(
        title={"text": f"{title}<br><sup>{subtitle}</sup>" if title and subtitle else title},
        margin={"l": 58, "r": 90 if add_latest_labels else 24, "t": 84 if title else 38, "b": 48},
        height=height,
        hovermode="x unified",
        legend={"orientation": "h", "y": -0.32, "font": {"size": 12}},
        paper_bgcolor="white",
        plot_bgcolor="white",
        font={"family": "Inter, Arial, sans-serif", "color": "#253746"},
        xaxis={
            "title": x_axis_title,
            "rangeslider": {"visible": show_range_slider, "thickness": 0.08},
            "rangeselector": {
                "buttons": [
                    {"count": 1, "label": "1Y", "step": "year", "stepmode": "backward"},
                    {"count": 3, "label": "3Y", "step": "year", "stepmode": "backward"},
                    {"step": "all", "label": "All"},
                ]
            },
            "showgrid": True,
            "gridcolor": "#e8eef0",
        },
        yaxis={"title": y_axis_title, "showgrid": True, "gridcolor": "#eef2f3", "rangemode": "normal"},
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
                        "label": "Post-peak period",
                        "method": "relayout",
                        "args": [{"xaxis.range": [POST_PEAK_CONTEXT_MONTH, LATEST_MONTH_VALUE]}],
                    }
                ],
            }
        ] if show_post_peak_button else [],
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


def kpi_footer(*lines: str) -> html.Div:
    return html.Div(
        className="kpi-footer-stack",
        children=[html.Span(line) for line in lines if line],
    )


KPI_DETAILS = {
    "baseline": {
        "title": "Baseline enrollment",
        "measures": "National total Medicaid/CHIP enrollment at the January 2019 starting point for this project period.",
        "matters": "Medicaid and CHIP are major state-federal coverage programs, so the baseline establishes the national public coverage level before later pandemic-era and post-2023 eligibility operations patterns appear in the data.",
        "interpret": "A baseline value gives the dashboard a fixed reference month. Later increases or decreases show how national enrollment moved relative to the start of the project period.",
        "caution": "This is an aggregate enrollment count. It does not show individual eligibility experiences, access to care, service use, health outcomes, claims, or costs.",
        "related": "National Snapshot, State Map Explorer, Medicaid vs CHIP Drivers",
    },
    "peak": {
        "title": "Peak enrollment",
        "measures": "The highest observed national total Medicaid/CHIP enrollment month in the cleaned dashboard dataset.",
        "matters": "The observed high point helps viewers understand the scale of enrollment reached during the available reporting period and frames later declines, renewals, and coverage transitions described in unwinding context sources.",
        "interpret": "If latest enrollment is below this point, the dashboard is showing a descriptive shift away from the observed high-water mark in the cleaned data.",
        "caution": "Highest observed enrollment is descriptive. It does not explain why enrollment changed or estimate any policy effect.",
        "related": "National Snapshot, State Map Explorer, Methods & Limits",
    },
    "latest": {
        "title": "Latest enrollment",
        "measures": "National total Medicaid/CHIP enrollment in the latest CMS reporting month available in the dashboard.",
        "matters": "This is the current national coverage snapshot in the public CMS reporting extract, useful for routine Medicaid/CHIP monitoring and reporting conversations.",
        "interpret": "Read it as the latest position of national enrollment within the project period: whether current enrollment is closer to the baseline, the observed peak, or somewhere in between.",
        "caution": "Latest-month values may be preliminary and can be revised in later source updates.",
        "related": "National Snapshot, State Map Explorer, Methods & Limits",
    },
    "change-baseline": {
        "title": "Change since Jan. 2019",
        "measures": "The difference between latest national Medicaid/CHIP enrollment and the January 2019 baseline.",
        "matters": "This summarizes the net enrollment movement across the full reporting window, helping policy and operations audiences quickly see the size and direction of national change.",
        "interpret": "An upward arrow means latest enrollment is above the January 2019 starting point; a downward arrow means it is below that starting point. The percent gives scale relative to the baseline.",
        "caution": "This is descriptive monitoring and does not estimate what caused the change.",
        "related": "National Snapshot, State Map Explorer, Medicaid vs CHIP Drivers",
    },
    "change-peak": {
        "title": "Change from peak",
        "measures": "The difference between latest national Medicaid/CHIP enrollment and the highest observed enrollment month in the cleaned data.",
        "matters": "This helps interpret the post-peak enrollment position, especially for readers tracking the return to regular eligibility operations after the continuous enrollment period ended.",
        "interpret": "A downward arrow means latest enrollment is below the observed peak; an upward arrow would mean it is above the observed peak. The value describes distance from that high point.",
        "caution": "This describes the change from the observed enrollment peak in the cleaned data. It does not estimate the cause of the change.",
        "related": "National Snapshot, Methods & Limits",
    },
    "operations": {
        "title": "Latest operations activity",
        "measures": "Applications submitted and Medicaid/CHIP eligibility determinations in the latest reporting month.",
        "matters": "Applications and determinations give policy and operations readers a view of eligibility-system activity, separate from enrollment counts.",
        "interpret": "Read the two values together as same-month activity indicators: applications reflect people entering the financial-assistance process, while determinations reflect application-stage eligibility decisions reported that month.",
        "caution": "Applications and determinations are descriptive operations indicators. They are not backlog, timeliness, approval-rate, or performance measures.",
        "related": "Eligibility Operations, Monitoring Flags, Methods & Limits",
    },
}


KPI_VARIANTS = {
    "baseline": "baseline",
    "peak": "peak",
    "latest": "latest",
    "change-baseline": "delta-up",
    "change-peak": "delta-down",
    "operations": "operations",
}


def kpi_class(key: str, selected_key: str | None = None, variant: str | None = None) -> str:
    classes = ["kpi-card", "kpi-button", f"kpi-{variant or KPI_VARIANTS[key]}"]
    if key == selected_key:
        classes.append("kpi-selected")
    return " ".join(classes)


def kpi_classes_for_selection(selected_key: str | None = None) -> tuple[str, str, str, str, str]:
    story = national_enrollment_story()
    _, _, baseline_direction = signed_delta_parts(story["change_from_baseline"])
    _, _, peak_direction = signed_delta_parts(story["change_from_peak"])
    return (
        kpi_class("baseline", selected_key, "baseline"),
        kpi_class("peak", selected_key, "peak"),
        kpi_class("latest", selected_key, "latest"),
        kpi_class("change-baseline", selected_key, f"delta-{baseline_direction}"),
        kpi_class("change-peak", selected_key, f"delta-{peak_direction}"),
    )


TIMELINE_EVENTS = [
    {
        "key": "continuous",
        "period": "2020",
        "label": "Continuous coverage",
        "title": "COVID-19 public health emergency / continuous coverage begins",
        "context": "During the COVID-19 public health emergency, states received enhanced federal Medicaid funding and generally could not disenroll beneficiaries while the continuous coverage provision was in effect.",
        "matters": "This helps explain why Medicaid/CHIP enrollment rose during the pandemic period.",
        "source": "CMS / McIntyre et al. / KFF",
    },
    {
        "key": "growth",
        "period": "2020-2022",
        "label": "Enrollment growth",
        "title": "Pandemic-era enrollment growth",
        "context": "Medicaid/CHIP enrollment increased during the continuous coverage period.",
        "matters": "This period helps explain the broad rise in state and national enrollment trends.",
        "source": "CMS dashboard data / KFF",
    },
    {
        "key": "unwinding",
        "period": "2023",
        "label": "Unwinding",
        "title": "Unwinding begins",
        "context": "States resumed Medicaid renewals and disenrollments after the continuous coverage period ended.",
        "matters": "This helps explain why many states began seeing enrollment declines, while requiring caution because terminations, churn, and net enrollment loss are not the same thing.",
        "source": "McIntyre et al. (2025) / CMS",
    },
    {
        "key": "variation",
        "period": "2023-2024",
        "label": "State variation",
        "title": "State variation during unwinding",
        "context": "State experiences differed during unwinding. McIntyre et al. found substantial variation in net Medicaid enrollment losses across states.",
        "matters": "This supports using the map and selected-state comparison instead of relying only on national totals.",
        "source": "McIntyre et al. (2025)",
    },
    {
        "key": "renewals",
        "period": "2024-2025",
        "label": "Renewals and churn",
        "title": "Renewals, churn, and coverage transitions",
        "context": "After states resumed Medicaid renewals and disenrollments, enrollment patterns reflected more than simple coverage loss. Research and policy sources describe the importance of churn, re-enrollment, procedural disenrollments, and transitions to other coverage.",
        "matters": "A decline in aggregate Medicaid/CHIP enrollment does not directly show who became uninsured, who re-enrolled, or who moved to another coverage source. Users should interpret state trends alongside unwinding and renewal context.",
        "source": "McIntyre et al. (2025) / KFF / CMS/Medicaid.gov",
    },
    {
        "key": "reporting",
        "period": "2025-2026",
        "label": "CMS reporting caveats",
        "title": "Latest CMS reporting caveats",
        "context": "The latest reporting months in public CMS/Data.Medicaid.gov enrollment files may be preliminary or later revised. Some operational fields also have missingness or source caveats.",
        "matters": "Recent values are useful for monitoring, but they should be interpreted with reporting status, source notes, and Methods & Limits. The dashboard shows aggregate enrollment and eligibility operations, not individual coverage transitions, access to care, utilization, or outcomes.",
        "source": "CMS/Data.Medicaid.gov / CMS/Medicaid.gov source notes",
    },
]


def timeline_event_by_key(key: str | None) -> dict[str, str]:
    for event in TIMELINE_EVENTS:
        if event["key"] == key:
            return event
    return TIMELINE_EVENTS[0]


def timeline_button(event: dict[str, str]) -> html.Button:
    tooltip = (
        f"{event['period']} - {event['title']}\n"
        f"Context: {event['context']}\n"
        f"Why this matters: {event['matters']}\n"
        f"Source: {event['source']}"
    )
    return html.Button(
        id=f"timeline-{event['key']}",
        n_clicks=0,
        className="timeline-event-button",
        title=tooltip,
        children=[
            html.Span(event["period"], className="timeline-date"),
            html.Strong(event["label"]),
        ],
    )


def timeline_detail(event: dict[str, str]) -> html.Div:
    return html.Div(
        className="timeline-detail-card",
        children=[
            html.Div(
                className="timeline-detail-meta",
                children=[
                    html.Span(f"Event: {event['title']}"),
                ],
            ),
            html.P([html.Strong("Context: "), event["context"]]),
            html.P([html.Strong("Why this matters: "), event["matters"]]),
        ],
    )


def kpi_button(
    key: str,
    title: str,
    value: str | list,
    footer: str | Component | None,
    badge: str | None = None,
    variant: str = "neutral",
    delta: str | None = None,
    percent: str | None = None,
) -> html.Button:
    children = [
        html.Div(
            className="kpi-topline",
            children=[
                html.Span(title),
                html.Em(badge, className="kpi-badge") if badge else None,
            ],
        ),
        html.Strong(value) if isinstance(value, str) else html.Div(value, className="operations-mini-grid"),
        html.Div(
            className="delta-row",
            children=[
                html.Span(delta, className="delta-value") if delta else None,
                html.Span(percent, className="delta-percent") if percent else None,
            ],
        )
        if delta or percent
        else None,
        html.Small(footer) if isinstance(footer, str) and footer else footer,
    ]
    return html.Button(
        id=f"kpi-{key}",
        className=kpi_class(key, variant=variant),
        children=[child for child in children if child is not None],
    )


def metric_details_panel(key: str = "total") -> html.Div:
    detail = KPI_DETAILS.get(key, KPI_DETAILS["baseline"])
    return html.Div(
        className="metric-detail-panel",
        children=[
            html.Div(
                className="metric-detail-heading",
                children=[
                    html.P("Metric details", className="eyebrow"),
                    html.H3(detail["title"]),
                ]
            ),
            html.Div(
                className="metric-detail-grid",
                children=[
                    html.Div([html.Span("Metric details"), html.P(detail["measures"])]),
                    html.Div([html.Span("What this means"), html.P(detail["interpret"])]),
                    html.Div([html.Span("Why it matters"), html.P(detail["matters"])]),
                ],
            ),
        ],
    )


def section_header(title: str, question: str, explanation: str) -> html.Div:
    children = [
        html.H2(title),
        html.Div(
            className="monitoring-question",
            children=[
                html.Span("Main question"),
                html.H3(question),
            ],
        ),
    ]
    if explanation:
        children.append(html.P(explanation))
    return html.Div(
        className="section-header",
        children=children,
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


def national_enrollment_story() -> dict[str, object]:
    baseline = national_enrollment[0]
    latest = national_enrollment[-1]
    peak = max(
        national_enrollment,
        key=lambda row: to_float(row.get("total_medicaid_and_chip_enrollment")) or 0,
    )
    baseline_value = to_float(baseline.get("total_medicaid_and_chip_enrollment"))
    latest_value = to_float(latest.get("total_medicaid_and_chip_enrollment"))
    peak_value = to_float(peak.get("total_medicaid_and_chip_enrollment"))
    return {
        "baseline": baseline,
        "latest": latest,
        "peak": peak,
        "baseline_value": baseline_value,
        "latest_value": latest_value,
        "peak_value": peak_value,
        "change_from_baseline": latest_value - baseline_value if latest_value is not None and baseline_value is not None else None,
        "percent_change_from_baseline": percent_change(latest_value, baseline_value),
        "change_from_peak": latest_value - peak_value if latest_value is not None and peak_value is not None else None,
        "percent_change_from_peak": percent_change(latest_value, peak_value),
    }


def signed_delta_parts(value: float | None) -> tuple[str, str, str]:
    if value is None:
        return "", "Not available", "neutral"
    if value > 0:
        return "↑", format_value(value, "signed_integer"), "up"
    if value < 0:
        return "↓", format_value(value, "signed_integer"), "down"
    return "→", format_value(value, "signed_integer"), "neutral"


def add_chart_point(fig: go.Figure, row: dict[str, str], field: str, label: str, color: str = "#b7791f") -> None:
    value = to_float(row.get(field))
    if value is None:
        return
    fig.add_trace(
        go.Scatter(
            x=[row["reporting_month"]],
            y=[value],
            mode="markers+text",
            name=label,
            text=[label],
            textposition="top center",
            marker={"size": 9, "color": color, "line": {"color": "white", "width": 1.5}},
            hovertemplate=f"{label}<br>Reporting month: %{{x|%b %Y}}<br>Value: %{{y:,.0f}}<extra></extra>",
            showlegend=False,
        )
    )


def indexed_state_national_rows(selected_state: str) -> list[dict[str, str | float | None]]:
    state_rows_for_chart = state_trend_rows(selected_state)
    if not state_rows_for_chart:
        return []
    national_by_month = {row["reporting_month"]: row for row in national_enrollment}
    state_by_month = {row["reporting_month"]: row for row in state_rows_for_chart}
    baseline_national_row = national_by_month.get(BASELINE_MONTH) or national_enrollment[0]
    baseline_state_row = state_by_month.get(BASELINE_MONTH) or state_rows_for_chart[0]
    baseline_national = to_float(baseline_national_row.get("total_medicaid_and_chip_enrollment"))
    baseline_state = to_float(baseline_state_row.get("total_medicaid_and_chip_enrollment"))
    output = []
    for reporting_month in sorted(set(national_by_month) & set(state_by_month)):
        national_row = national_by_month[reporting_month]
        state_row = state_by_month[reporting_month]
        national_raw = to_float(national_row.get("total_medicaid_and_chip_enrollment"))
        state_raw = to_float(state_row.get("total_medicaid_and_chip_enrollment"))
        output.append(
            {
                "reporting_month": reporting_month,
                "national_index": ratio(national_raw, baseline_national, 100),
                "state_index": ratio(state_raw, baseline_state, 100),
                "national_raw": national_raw,
                "state_raw": state_raw,
                "state_status": "Preliminary" if state_row.get("preliminary_or_updated") == "P" else "Final/updated",
            }
        )
    return output


def add_index_annotation(fig: go.Figure, row: dict[str, str | float | None], field: str, label: str, color: str, textposition: str = "top center") -> None:
    value = to_float(row.get(field))
    if value is None:
        return
    fig.add_trace(
        go.Scatter(
            x=[row["reporting_month"]],
            y=[value],
            mode="markers+text",
            name=label,
            text=[label],
            textposition=textposition,
            marker={"size": 9, "color": color, "line": {"color": "white", "width": 1.5}},
            textfont={"size": 11, "color": "#253746"},
            hovertemplate=f"{label}<br>Reporting month: %{{x|%b %Y}}<br>Index value: %{{y:,.1f}}<extra></extra>",
            showlegend=False,
            cliponaxis=False,
        )
    )


def national_enrollment_figure(selected_state: str = "CA") -> go.Figure:
    if selected_state not in state_lookup:
        selected_state = DEFAULT_OVERVIEW_STATE
    selected = state_lookup[selected_state]
    rows = indexed_state_national_rows(selected_state)
    if not rows:
        return go.Figure()
    baseline = rows[0]
    latest = rows[-1]
    state_peak = max(rows, key=lambda row: to_float(row.get("state_index")) or 0)
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=[row["reporting_month"] for row in rows],
            y=[row["state_index"] for row in rows],
            mode="lines",
            name=f"{selected['state_name']} Medicaid/CHIP enrollment index",
            line={"width": 4, "color": "#0072b2"},
            customdata=[[selected["state_name"], row["state_raw"], row["state_status"]] for row in rows],
            hovertemplate=(
                f"Series: {selected['state_name']} Medicaid/CHIP enrollment index<br>"
                "Geography: %{customdata[0]}<br>"
                "Reporting month: %{x|%b %Y}<br>"
                "Indexed enrollment: %{y:,.1f}<br>"
                "Raw enrollment: %{customdata[1]:,.0f}<br>"
                "Reporting status: %{customdata[2]}<extra></extra>"
            ),
        )
    )
    fig.add_trace(
        go.Scatter(
            x=[row["reporting_month"] for row in rows],
            y=[row["national_index"] for row in rows],
            mode="lines",
            name="National Medicaid/CHIP enrollment index",
            line={"width": 2.5, "color": "#6b7280", "dash": "dash"},
            customdata=[[row["national_raw"]] for row in rows],
            hovertemplate=(
                "Series: National Medicaid/CHIP enrollment index<br>"
                "Geography: National<br>"
                "Reporting month: %{x|%b %Y}<br>"
                "Indexed enrollment: %{y:,.1f}<br>"
                "Raw enrollment: %{customdata[0]:,.0f}<extra></extra>"
            ),
        )
    )
    add_index_annotation(fig, baseline, "national_index", "Baseline", "#6b8793", "bottom center")
    add_index_annotation(fig, state_peak, "state_index", "Selected state peak", "#0072b2", "top center")
    add_index_annotation(fig, latest, "state_index", "Latest", "#12324a", "bottom right")
    fig.update_layout(
        margin={"l": 58, "r": 28, "t": 18, "b": 52},
        height=390,
        hovermode="x unified",
        legend={"orientation": "h", "y": -0.2},
        paper_bgcolor="white",
        plot_bgcolor="white",
        font={"family": "Inter, Arial, sans-serif", "color": "#253746"},
        xaxis={
            "title": "Reporting month",
            "showgrid": True,
            "gridcolor": "#e8eef0",
            "range": [baseline["reporting_month"], latest["reporting_month"]],
        },
        yaxis={
            "title": "Index, Jan. 2019 = 100",
            "showgrid": True,
            "gridcolor": "#eef2f3",
        },
    )
    return fig


def selected_state_takeaway(selected_state: str = DEFAULT_OVERVIEW_STATE) -> html.Div:
    if selected_state not in state_lookup:
        selected_state = DEFAULT_OVERVIEW_STATE
    selected = state_lookup[selected_state]
    rows = indexed_state_national_rows(selected_state)
    latest = rows[-1] if rows else {}
    baseline = rows[0] if rows else {}
    state_latest_index = to_float(latest.get("state_index"))
    national_latest_index = to_float(latest.get("national_index"))
    latest_raw = to_float(latest.get("state_raw"))
    baseline_raw = to_float(baseline.get("state_raw"))
    raw_change = latest_raw - baseline_raw if latest_raw is not None and baseline_raw is not None else None
    diff = state_latest_index - national_latest_index if state_latest_index is not None and national_latest_index is not None else None
    comparison = "near the national indexed trend"
    if diff is not None and diff > 0.5:
        comparison = "above the national indexed trend"
    elif diff is not None and diff < -0.5:
        comparison = "below the national indexed trend"
    baseline_comparison = "near its January 2019 level"
    if raw_change is not None and raw_change > 0:
        baseline_comparison = "above its January 2019 level"
    elif raw_change is not None and raw_change < 0:
        baseline_comparison = "below its January 2019 level"
    return html.Div(
        className="selected-state-takeaway",
        children=[
            html.Div(
                className="takeaway-summary",
                children=[
                    html.H3(f"{selected['state_name']} takeaway"),
                    html.P(
                        f"{selected['state_name']} is {baseline_comparison} and {comparison} in the latest reporting month."
                    ),
                ],
            ),
            html.Div(
                className="takeaway-metrics",
                children=[
                    html.Span(f"Latest enrollment: {format_short(latest_raw)}"),
                    html.Span(f"Jan. 2019 enrollment: {format_short(baseline_raw)}"),
                    html.Span(f"Change since Jan. 2019: {format_signed_short(raw_change)}"),
                ],
            ),
        ],
    )


def overview_change_map(selected_state: str = DEFAULT_OVERVIEW_STATE) -> go.Figure:
    if selected_state not in state_map_lookup:
        selected_state = DEFAULT_OVERVIEW_STATE
    rows = sorted(state_map_rows, key=lambda row: row["state_name"])
    values = [to_float(row.get("map_percent_change_since_2019")) for row in rows]
    selected_outline_color = "#111827"
    fig = go.Figure(
        go.Choropleth(
            locations=[row["state_abbreviation"] for row in rows],
            z=values,
            locationmode="USA-states",
            colorscale="RdBu",
            reversescale=True,
            zmid=0,
            colorbar={"title": "% change"},
            customdata=[
                [
                    row["state_name"],
                    month_label(row["latest_reporting_month"]),
                    to_float(row.get("map_percent_change_since_2019")),
                    (to_float(row.get("map_percent_change_since_2019")) or 0) + 100,
                    to_float(row.get("latest_total_medicaid_chip_enrollment")),
                    row.get("latest_month_preliminary_status", "Not available"),
                    row["state_abbreviation"],
                ]
                for row in rows
            ],
            hovertemplate=(
                "<b>%{customdata[0]}</b><br>"
                "Latest reporting month: %{customdata[1]}<br>"
                "Percent change since Jan. 2019: %{customdata[2]:.1f}%<br>"
                "Latest enrollment index: %{customdata[3]:.1f}<br>"
                "Latest total Medicaid/CHIP enrollment: %{customdata[4]:,.0f}<br>"
                "Reporting status: %{customdata[5]}<extra></extra>"
            ),
            marker_line_color=[
                selected_outline_color if row["state_abbreviation"] == selected_state else "white"
                for row in rows
            ],
            marker_line_width=[
                4 if row["state_abbreviation"] == selected_state else 0.8
                for row in rows
            ],
            showscale=True,
        )
    )
    fig.update_layout(
        geo={"scope": "usa", "bgcolor": "rgba(0,0,0,0)", "lakecolor": "#f8fafc"},
        margin={"l": 0, "r": 0, "t": 0, "b": 0},
        height=410,
        paper_bgcolor="white",
        plot_bgcolor="white",
        font={"family": "Inter, Arial, sans-serif", "color": "#253746"},
    )
    return fig


def national_ops_figure() -> go.Figure:
    highest_applications = max(national_ops, key=lambda row: to_float(row.get("applications_submitted")) or 0)
    highest_determinations = max(national_ops, key=lambda row: to_float(row.get("total_medicaid_and_chip_determinations")) or 0)
    latest = national_ops[-1]
    fig = line_figure(
        national_ops,
        [
            ("applications_submitted", "Applications submitted"),
            ("total_medicaid_and_chip_determinations", "Eligibility determinations"),
        ],
        "National Applications And Eligibility Determinations Over Time",
        f"Question: compare latest activity with highest observed application and determination months through {latest_month}.",
        "Applications / determinations",
        scope_label="National",
        reference_lines=[(POST_PEAK_CONTEXT_MONTH, "Post-peak monitoring period begins")],
        height=390,
    )
    add_chart_point(fig, latest, "applications_submitted", "Latest applications", "#12324a")
    add_chart_point(fig, highest_applications, "applications_submitted", "Highest applications", "#b7791f")
    add_chart_point(fig, highest_determinations, "total_medicaid_and_chip_determinations", "Highest determinations", "#2f7d78")
    return fig


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
    story = national_enrollment_story()
    _, _, baseline_direction = signed_delta_parts(story["change_from_baseline"])
    _, _, peak_direction = signed_delta_parts(story["change_from_peak"])
    return html.Div(
        className="tab-page",
        children=[
            section_header(
                "National Snapshot",
                "How have national Medicaid/CHIP enrollment, applications, and eligibility determinations changed over time?",
                "",
            ),
            html.Div(
                className="section-subhead",
                children=[
                    html.Div(
                        className="section-title-row",
                        children=[
	                            html.H2("National Monitoring Summary"),
	                            html.Span("Click any card for details.", className="instruction-pill"),
                        ],
                    ),
                ],
            ),
            html.Div(
                className="kpi-grid overview-kpis",
                children=[
	                    kpi_button(
	                        "baseline",
	                        "Baseline enrollment",
	                        format_short(story["baseline_value"]),
	                        kpi_footer(
                                short_month_label(story["baseline"]["reporting_month"]),
                                "Starting point for comparison",
                            ),
	                        variant="baseline",
	                    ),
                    kpi_button(
                        "peak",
                        "Peak enrollment",
                        format_short(story["peak_value"]),
	                        kpi_footer(
                                short_month_label(story["peak"]["reporting_month"]),
                                "Highest observed level",
                            ),
	                        variant="peak",
	                    ),
                    kpi_button(
                        "latest",
                        "Latest enrollment",
                        format_short(story["latest_value"]),
                        kpi_footer(
                            short_month_label(story["latest"]["reporting_month"]),
                            "Most recent reported value",
                        ),
	                        "Preliminary" if latest_preliminary_status == "Preliminary" else None,
	                        variant="latest",
	                    ),
                    kpi_button(
                        "change-baseline",
                        "Change since Jan. 2019",
                        format_signed_short(story["change_from_baseline"]),
	                        "Compared with baseline",
                        variant=f"delta-{baseline_direction}",
	                        percent=format_value(story["percent_change_from_baseline"], "percent"),
	                    ),
                    kpi_button(
                        "change-peak",
                        "Change from peak",
                        format_signed_short(story["change_from_peak"]),
	                        "Compared with peak level",
                        variant=f"delta-{peak_direction}",
	                        percent=format_value(story["percent_change_from_peak"], "percent"),
	                    ),
                ],
            ),
            html.Div(id="national-kpi-details"),
            html.Div(
                className="enrollment-visual-section",
                children=[
                    html.Div(
                        className="visual-section-header",
                        children=[
                            html.Div(
                                children=[
                                    html.H2("Enrollment Trend and State Context"),
                                ],
                            ),
                            html.Div(
                                className="shared-state-control",
                                children=[
                                    html.Label(
                                        [
                                            html.Span("Select a state"),
                                            dcc.Dropdown(
                                                id="overview-state-selector",
                                                options=sorted_states(state_rows),
                                                value=DEFAULT_OVERVIEW_STATE,
                                                clearable=False,
                                            ),
                                        ],
                                        className="control-label compact-control",
                                    ),
                                    html.Div(
                                        id="overview-selected-state-label",
                                        className="selected-state-label",
                                        children=f"Selected state: {state_lookup[DEFAULT_OVERVIEW_STATE]['state_name']}",
                                    ),
                                ],
                            ),
                        ],
                    ),
                    html.Div(
                        className="visual-guide-bar",
                        children=[
                            html.Div(
                                className="visual-guide-step trend-step",
                                children=[
                                    html.Span("Trend", className="guide-step-label"),
                                    html.H3("Trend view"),
                                    html.P("Use the indexed line chart to compare the selected state with the national Medicaid/CHIP trend over time."),
                                    html.Span("Indexed trend", className="guide-step-pill"),
                                ],
                            ),
                            html.Div("Then compare", className="guide-connector"),
                            html.Div(
                                className="visual-guide-step map-step",
                                children=[
                                    html.Span("Map", className="guide-step-label"),
                                    html.H3("State context"),
                                    html.P("Use the map to see how the selected state compares with other states on enrollment change since January 2019."),
                                    html.Span("State comparison", className="guide-step-pill"),
                                ],
                            ),
                        ],
                    ),
                    html.Div(
                        className="overview-visual-grid",
                        children=[
                            html.Div(
                                className="panel chart-panel",
                                children=[
                                    html.Div(
                                        className="chart-card-header stacked",
                                        children=[
                                            html.Div(
                                                children=[
                                                    html.H2("Indexed Enrollment Trend: Selected State vs National"),
                                                    html.P("Indexed to Jan. 2019 = 100"),
                                                ]
                                            ),
                                        ],
                                    ),
                                    dcc.Graph(
                                        id="national-index-trend",
                                        figure=national_enrollment_figure(DEFAULT_OVERVIEW_STATE),
                                        config={"displayModeBar": False},
                                    ),
                                ],
                            ),
                            html.Div(
                                className="panel chart-panel",
                                children=[
                                    html.Div(
                                        className="chart-card-header stacked",
                                        children=[
                                            html.Div(
                                                children=[
                                                    html.H2("State Medicaid/CHIP Enrollment Change Since January 2019"),
                                                    html.P(
                                                        "Outline = selected state. Color = percent change since Jan. 2019.",
                                                        className="map-selection-note",
                                                    ),
                                                ]
                                            ),
                                        ],
                                    ),
                                    dcc.Graph(
                                        id="overview-change-map",
                                        figure=overview_change_map(DEFAULT_OVERVIEW_STATE),
                                        config={"displayModeBar": False},
                                    ),
                                ],
                            ),
                        ],
                    ),
                    html.Div(
                        id="selected-state-takeaway",
                        children=selected_state_takeaway(DEFAULT_OVERVIEW_STATE),
                    ),
                    html.Div(
                        className="trend-context-block",
                        children=[
                            html.Span("Policy context", className="context-label"),
                            html.H3("Policy timeline for Medicaid/CHIP enrollment trends"),
                            html.P(
                                "Click a period to view policy and reporting context related to the enrollment trend.",
                                className="timeline-subtitle",
                            ),
                            html.Div(
                                className="policy-timeline",
                                children=[timeline_button(event) for event in TIMELINE_EVENTS],
                            ),
                            html.Div(id="timeline-detail", children=timeline_detail(TIMELINE_EVENTS[0])),
                            html.P(
                                "Dashboard metrics: CMS/Data.Medicaid.gov. Timeline context: McIntyre et al. (2025), KFF, MACPAC, CMS, and Medicaid.gov.",
                                className="source-note",
                            ),
                        ],
                    ),
                ],
            ),
        ],
    )


def map_title(metric_key: str, reporting_month: str) -> tuple[str, str]:
    return "Selected states locator map", f"Geographic context for the selected comparison states in {month_label(reporting_month)}."


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


def ranked_metric_rows(reporting_month: str, metric_key: str) -> list[dict[str, object]]:
    return sorted(
        [row for row in map_rows_for_month(reporting_month, metric_key) if row.get("metric_value") is not None],
        key=lambda row: row.get("metric_value") or 0,
        reverse=True,
    )


def selected_state_metric_rank(metric_key: str, reporting_month: str, selected_state: str) -> tuple[int | None, int]:
    ranked = ranked_metric_rows(reporting_month, metric_key)
    for index, row in enumerate(ranked, start=1):
        if row["state_abbreviation"] == selected_state:
            return index, len(ranked)
    return None, len(ranked)


def ranking_title(metric_key: str, ranking_view: str) -> str:
    metric_label = map_metric_dropdown_label(metric_key)
    if ranking_view == "top10":
        return f"National Ranking<br><sup>Top states by {metric_label.lower()}</sup>"
    if ranking_view == "bottom10":
        return f"National Ranking<br><sup>Bottom states by {metric_label.lower()}</sup>"
    return f"National Ranking<br><sup>All states by {metric_label.lower()}</sup>"


def map_metric_dropdown_label(metric_key: str) -> str:
    labels = {
        "latest_total_medicaid_chip_enrollment": "Total enrollment",
        "latest_medicaid_enrollment": "Medicaid enrollment",
        "latest_chip_enrollment": "CHIP enrollment",
        "medicaid_chip_enrollment_per_1000_residents": "Enrollment per 1,000 residents",
        "percent_change_since_january_2019": "Percent change since Jan. 2019",
        "change_since_april_2023": "Change since Apr. 2023",
        "last_12_month_change": "Last 12-month change",
        "applications_submitted_per_100000_residents": "Applications per 100,000 residents",
        "eligibility_determinations_per_100000_residents": "Determinations per 100,000 residents",
        "applications_per_1000_enrollees": "Applications per 1,000 enrollees",
        "determinations_per_1000_enrollees": "Determinations per 1,000 enrollees",
    }
    return labels.get(metric_key, MAP_METRICS[metric_key]["label"])


def difference_summary_text(metric_key: str, reporting_month: str, state_a: str, state_b: str) -> str:
    metric = MAP_METRICS[metric_key]
    value_a = month_metric_value(state_a, reporting_month, metric_key)
    value_b = month_metric_value(state_b, reporting_month, metric_key)
    diff = (value_b - value_a) if value_a is not None and value_b is not None else None
    if diff is None or abs(diff) < 1e-9:
        return f"Both states have the same value in {month_label(reporting_month)}."
    unit_phrase = {
        "medicaid_chip_enrollment_per_1000_residents": " per 1,000 residents",
        "percent_change_since_january_2019": " percentage points",
        "applications_submitted_per_100000_residents": " per 100,000 residents",
        "eligibility_determinations_per_100000_residents": " per 100,000 residents",
    }.get(metric_key, "")
    diff_text = f"{abs(diff):,.1f}{unit_phrase}"
    if diff > 0:
        return (
            f"{state_lookup[state_b]['state_name']} is +{diff_text} "
            f"higher than {state_lookup[state_a]['state_name']} in {month_label(reporting_month)}."
        )
    return (
        f"{state_lookup[state_a]['state_name']} is +{diff_text} "
        f"higher than {state_lookup[state_b]['state_name']} in {month_label(reporting_month)}."
    )


def comparison_month_status(reporting_month: str) -> html.Div:
    return html.Div(className="comparison-month-status")


def compare_trend_figure(metric_key: str, state_a: str, state_b: str, reporting_month: str) -> go.Figure:
    metric = MAP_METRICS[metric_key]
    series = []
    for state_key, color, dash in ((state_a, "#b8860b", "solid"), (state_b, "#4f5fbf", "solid")):
        rows = []
        for month in MONTH_VALUES:
            value = month_metric_value(state_key, month, metric_key)
            rank, total = selected_state_metric_rank(metric_key, month, state_key)
            rows.append({
                "reporting_month": month,
                "metric_value": value,
                "rank": rank,
                "total": total,
                "state_name": state_lookup[state_key]["state_name"],
            })
        series.append((state_key, color, dash, rows))
    fig = go.Figure()
    for state_key, color, dash, rows in series:
        fig.add_trace(
            go.Scatter(
                x=[row["reporting_month"] for row in rows],
                y=[row["metric_value"] for row in rows],
                mode="lines",
                name=state_lookup[state_key]["state_name"],
                line={"color": color, "width": 3, "dash": dash},
                customdata=[[row["state_name"], row["rank"], row["total"]] for row in rows],
                hovertemplate=(
                    "State: %{customdata[0]}<br>"
                    "Month: %{x|%b %Y}<br>"
                    f"Value: %{{y:,.1f}}<br>"
                    "Rank: %{customdata[1]} of %{customdata[2]}<extra></extra>"
                ),
            )
        )
        latest_valid = [(row["reporting_month"], row["metric_value"]) for row in rows if row["metric_value"] is not None]
        if latest_valid:
            latest_x, latest_y = latest_valid[-1]
            fig.add_annotation(
                x=latest_x,
                y=latest_y,
                text=f"{state_lookup[state_key]['state_name']}: {format_value(latest_y, metric['kind'])}",
                showarrow=False,
                xanchor="left",
                xshift=8,
                font={"size": 11, "color": color},
                bgcolor="rgba(255,255,255,0.88)",
                bordercolor=color,
                borderwidth=1,
            )
    preliminary_months = [month for month in MONTH_VALUES if month_quality_metrics(month)["is_preliminary"]]
    if preliminary_months:
        fig.add_vrect(
            x0=preliminary_months[0],
            x1=MONTH_VALUES[-1],
            fillcolor="#f6d58b",
            opacity=0.12,
            line_width=0,
            layer="below",
        )
        fig.add_annotation(
            x=preliminary_months[0],
            y=1,
            xref="x",
            yref="paper",
            text="Preliminary reporting window",
            showarrow=False,
            xanchor="left",
            yanchor="bottom",
            yshift=6,
            font={"size": 11, "color": "#7a5a00"},
            bgcolor="rgba(255,249,230,0.96)",
            bordercolor="#e6c96b",
            borderwidth=1,
        )
    fig.update_layout(
        title={
            "text": (
                "Enrollment trend over time<br>"
                f"<sup>{state_lookup[state_a]['state_name']} and {state_lookup[state_b]['state_name']} · "
                f"{map_metric_dropdown_label(metric_key)} · {month_label(reporting_month)}</sup>"
            )
        },
        margin={"l": 58, "r": 84, "t": 72, "b": 40},
        height=320,
        paper_bgcolor="white",
        plot_bgcolor="white",
        hovermode="x unified",
        legend={"orientation": "h", "y": -0.24},
        xaxis={"title": "Reporting month", "showgrid": True, "gridcolor": "#e8eef0", "range": [MONTH_VALUES[0], MONTH_VALUES[-1]]},
        yaxis={"title": metric["short"], "showgrid": True, "gridcolor": "#eef2f3"},
    )
    return fig


def comparison_dot_lineup(metric_key: str, reporting_month: str, state_a: str, state_b: str) -> html.Div:
    metric_key = RANK_STRIP_METRIC_KEY
    ranked_all = ranked_metric_rows(reporting_month, metric_key)
    total = len(ranked_all)
    if total == 0:
        return html.Div()
    rank_lookup = {
        row["state_abbreviation"]: index
        for index, row in enumerate(ranked_all, start=1)
    }
    dots = []
    for index, row in enumerate(ranked_all, start=1):
        left = ((index - 1) / max(total - 1, 1)) * 100
        dots.append(
            html.Span(
                className="lineup-dot",
                style={"left": f"{left}%"},
                title=f"{row['state_name']} #{index}",
            )
        )
    ticks = []
    tick_values = [1, 10, 20, 30, 40, total]
    seen_ticks: set[int] = set()
    for tick in tick_values:
        if tick in seen_ticks or tick < 1 or tick > total:
            continue
        seen_ticks.add(tick)
        left = ((tick - 1) / max(total - 1, 1)) * 100
        ticks.append(
            html.Div(
                className="lineup-tick",
                style={"left": f"{left}%"},
                children=[html.Span(str(tick))],
            )
        )
    highlight_nodes = []
    selected_states = [(state_a, "state-a"), (state_b, "state-b")]
    positions = []
    ranks_for_gap = []
    for state_key, variant in selected_states:
        rank = rank_lookup.get(state_key)
        if rank is None:
            continue
        left = ((rank - 1) / max(total - 1, 1)) * 100
        label_offset = 0
        if positions and abs(positions[0] - left) < 10:
            label_offset = 22
        positions.append(left)
        ranks_for_gap.append((rank, left))
        highlight_nodes.append(
            html.Div(
                className=f"lineup-highlight {variant}",
                style={"left": f"{left}%", "top": f"{label_offset}px"},
                children=[
                    html.Span(
                        f"{state_lookup[state_key]['state_name']} #{rank}",
                        className="lineup-label-chip",
                    )
                ],
            )
        )
    gap_note = None
    if len(ranks_for_gap) == 2:
        rank_gap = abs(ranks_for_gap[0][0] - ranks_for_gap[1][0])
        mid_left = (ranks_for_gap[0][1] + ranks_for_gap[1][1]) / 2
        gap_note = html.Div(
            className="lineup-gap-note",
            style={"left": f"{mid_left}%"},
            children=f"{rank_gap}-rank gap",
        )
    return html.Div(
        className="lineup-box-inner",
        children=[
            html.Div(
                className="lineup-header",
                children=[
                    html.H3("Where the selected states rank nationally"),
                    html.Small("Lower rank numbers indicate higher values."),
                ],
            ),
            html.Div(
                className="lineup-scale",
                children=[
                    html.Span("Best rank: 1"),
                    html.Span(f"Worst rank: {total}"),
                ],
            ),
            html.Div(
                className="lineup-zones",
                children=[
                    html.Span("Top ranked"),
                    html.Span("Upper middle"),
                    html.Span("Middle"),
                    html.Span("Lower ranked"),
                ],
            ),
            html.Div(
                className="lineup-track",
                children=[
                    html.Div(className="lineup-track-line"),
                    *ticks,
                    *dots,
                    *highlight_nodes,
                    gap_note,
                ],
            ),
            html.P(
                f"{month_label(reporting_month)} monthly reported values · {map_metric_dropdown_label(metric_key)}",
                className="lineup-subtitle-bottom",
            ),
        ],
    )


def ranking_table_component(metric_key: str, reporting_month: str, state_a: str, state_b: str) -> html.Div:
    metric_key = RANK_STRIP_METRIC_KEY
    ranked_all = ranked_metric_rows(reporting_month, metric_key)
    rows = list(ranked_all)
    metric = MAP_METRICS[metric_key]
    headers = ["Rank", "State", "Value", "Marker"]
    body_rows = []
    for row in rows:
        rank, total = selected_state_metric_rank(metric_key, reporting_month, row["state_abbreviation"])
        is_selected_a = row["state_abbreviation"] == state_a
        is_selected_b = row["state_abbreviation"] == state_b
        marker_parts = []
        if is_selected_a:
            marker_parts.append("State A")
        if is_selected_b:
            marker_parts.append("State B")
        row_class = "ranking-row"
        if is_selected_a:
            row_class += " ranking-row-a"
        elif is_selected_b:
            row_class += " ranking-row-b"
        body_rows.append(
            html.Tr(
                className=row_class,
                children=[
                    html.Td(f"#{rank}" if rank is not None else "n/a"),
                    html.Td(row["state_name"]),
                    html.Td(format_value(row["metric_value"], metric["kind"])),
                    html.Td(" · ".join(marker_parts) if marker_parts else ""),
                ],
            )
        )
    return html.Div(
        className="ranking-table-wrap",
        children=[
            html.Div(
                className="section-subhead compact",
                children=[
                    html.P(f"{month_label(reporting_month)} · {map_metric_dropdown_label(metric_key)}"),
                ],
            ),
            html.Div(
                className="ranking-table-scroll",
                children=[
                    html.Table(
                        className="ranking-table",
                        children=[
                            html.Thead(html.Tr([html.Th(header) for header in headers])),
                            html.Tbody(body_rows),
                        ],
                    )
                ],
            ),
        ],
    )


def comparison_state_metrics(selected_state: str, reporting_month: str, metric_key: str) -> dict[str, object]:
    row = state_lookup.get(selected_state, state_rows[0])
    state_abbreviation = row["state_abbreviation"]
    month_row = row_for_state_month(state_abbreviation, reporting_month) or row_for_state_month(state_abbreviation, LATEST_MONTH_VALUE) or {}
    story = state_enrollment_story(state_abbreviation)
    rank, total_states = selected_state_metric_rank(metric_key, reporting_month, state_abbreviation)
    preliminary_status = "Preliminary" if month_row.get("preliminary_or_updated") == "P" else "Final/updated"
    return {
        "state_abbreviation": state_abbreviation,
        "state_name": row["state_name"],
        "metric_value": month_metric_value(state_abbreviation, reporting_month, metric_key),
        "metric_rank": rank,
        "metric_rank_total": total_states,
        "percent_change_since_2019": story["percent_change_from_baseline"],
        "percent_change_from_peak": story["percent_change_from_peak"],
        "applications_per_100000": month_metric_value(state_abbreviation, reporting_month, "applications_submitted_per_100000_residents"),
        "determinations_per_100000": month_metric_value(state_abbreviation, reporting_month, "eligibility_determinations_per_100000_residents"),
        "total_enrollment": to_float(month_row.get("total_medicaid_and_chip_enrollment")),
        "medicaid_enrollment": to_float(month_row.get("total_medicaid_enrollment")),
        "chip_enrollment": to_float(month_row.get("total_chip_enrollment")),
        "applications_submitted": to_float(month_row.get("total_applications_for_financial_assistance_submitted_at_state_level")),
        "eligibility_determinations": to_float(month_row.get("total_medicaid_and_chip_determinations")),
        "application_determination_balance": to_float(latest_balance_lookup.get(state_abbreviation, {}).get("application_determination_balance")),
        "medicaid_share": ratio(to_float(month_row.get("total_medicaid_enrollment")), to_float(month_row.get("total_medicaid_and_chip_enrollment")), 100),
        "chip_share": ratio(to_float(month_row.get("total_chip_enrollment")), to_float(month_row.get("total_medicaid_and_chip_enrollment")), 100),
        "missingness_percent": to_float(row.get("missingness_percent")),
        "preliminary_status": preliminary_status,
        "data_quality_note": row.get("data_quality_note", ""),
        "population_year_value": row.get("population_denominator_year") or population_year,
    }


def format_comparison_metric_value(metric_key: str, value: float | int | None) -> str:
    if metric_key == "medicaid_chip_enrollment_per_1000_residents":
        return format_value(value, "decimal")
    return format_value(value, MAP_METRICS[metric_key]["kind"])


def comparison_difference_text(label: str, a_value: float | int | None, b_value: float | int | None, kind: str, a_name: str, b_name: str) -> str:
    a_num = to_float(a_value)
    b_num = to_float(b_value)
    if a_num is None or b_num is None:
        return "Difference unavailable"
    if abs(a_num - b_num) < 1e-9:
        return "No difference"
    if kind == "rank":
        better_name = a_name if a_num < b_num else b_name
        gap = int(abs(a_num - b_num))
        return f"{better_name} ahead by {gap} ranks"
    diff = abs(a_num - b_num)
    leader_name = a_name if a_num > b_num else b_name
    if kind == "percent":
        return f"{leader_name} +{diff:.1f} pts"
    if kind == "decimal":
        return f"{leader_name} +{diff:,.1f}"
    return f"{leader_name} +{format_value(diff, kind)}"


def comparison_cell_state(
    value: float | int | None,
    other_value: float | int | None,
    mode: str,
    kind: str,
) -> tuple[str, str]:
    value_num = to_float(value)
    other_num = to_float(other_value)
    if value_num is None:
        return "", "is-neutral"
    if mode == "sign":
        if value_num > 0:
            return "▲", "is-better"
        if value_num < 0:
            return "▼", "is-worse"
        return "", "is-neutral"
    if other_num is None or abs(value_num - other_num) < 1e-9:
        return "", "is-neutral"
    if mode == "lower":
        return ("▲", "is-better") if value_num < other_num else ("▼", "is-worse")
    if mode == "closer_zero":
        return ("▲", "is-better") if abs(value_num) < abs(other_num) else ("▼", "is-worse")
    return ("▲", "is-better") if value_num > other_num else ("▼", "is-worse")


def comparison_diff_chip(
    a_name: str,
    b_name: str,
    a_value: float | int | None,
    b_value: float | int | None,
    mode: str,
    kind: str,
) -> tuple[str, str]:
    a_num = to_float(a_value)
    b_num = to_float(b_value)
    if a_num is None or b_num is None:
        return "Difference unavailable", "is-neutral"
    if abs(a_num - b_num) < 1e-9:
        return "No difference", "is-neutral"
    if mode == "lower":
        better_name = a_name if a_num < b_num else b_name
        gap = int(abs(a_num - b_num))
        return f"▲ {better_name} ahead by {gap} ranks", "is-better"
    if mode == "closer_zero":
        better_name = a_name if abs(a_num) < abs(b_num) else b_name
        return f"▲ {better_name} closer to peak", "is-better"
    if mode == "sign":
        leader_name = a_name if a_num > b_num else b_name
        diff = abs(a_num - b_num)
        return f"{'▲' if max(a_num, b_num) > 0 else '▼'} {leader_name} +{diff:.1f} pts", "is-better" if max(a_num, b_num) > 0 else "is-worse"
    leader_name = a_name if a_num > b_num else b_name
    diff = abs(a_num - b_num)
    if kind == "percent":
        return f"▲ {leader_name} +{diff:.1f} pts", "is-better"
    if kind == "decimal":
        return f"▲ {leader_name} +{diff:,.1f}", "is-better"
    return f"▲ {leader_name} +{format_value(diff, kind)}", "is-better"


def build_state_comparison_summary(state_a: str, state_b: str, reporting_month: str, metric_key: str) -> html.Div:
    a = comparison_state_metrics(state_a, reporting_month, metric_key)
    b = comparison_state_metrics(state_b, reporting_month, metric_key)
    metric_label = map_metric_dropdown_label(metric_key)
    metric_label_lower = metric_label[0].lower() + metric_label[1:]
    rows = [
        (
            f"{metric_label}",
            a["metric_value"],
            b["metric_value"],
            format_comparison_metric_value(metric_key, a["metric_value"]),
            format_comparison_metric_value(metric_key, b["metric_value"]),
            "higher",
            MAP_METRICS[metric_key]["kind"],
        ),
        (
            f"National rank for {metric_label_lower}, {short_month_label(reporting_month)}",
            a["metric_rank"],
            b["metric_rank"],
            f"#{a['metric_rank']}" if a["metric_rank"] is not None else "n/a",
            f"#{b['metric_rank']}" if b["metric_rank"] is not None else "n/a",
            "lower",
            "rank",
        ),
        (
            "Change since Jan. 2019",
            a["percent_change_since_2019"],
            b["percent_change_since_2019"],
            format_value(a["percent_change_since_2019"], "percent"),
            format_value(b["percent_change_since_2019"], "percent"),
            "sign",
            "percent",
        ),
        (
            "Change from peak",
            a["percent_change_from_peak"],
            b["percent_change_from_peak"],
            format_value(a["percent_change_from_peak"], "percent"),
            format_value(b["percent_change_from_peak"], "percent"),
            "closer_zero",
            "percent",
        ),
        (
            "Applications per 100,000",
            a["applications_per_100000"],
            b["applications_per_100000"],
            format_value(a["applications_per_100000"], "decimal"),
            format_value(b["applications_per_100000"], "decimal"),
            "higher",
            "decimal",
        ),
        (
            "Determinations per 100,000",
            a["determinations_per_100000"],
            b["determinations_per_100000"],
            format_value(a["determinations_per_100000"], "decimal"),
            format_value(b["determinations_per_100000"], "decimal"),
            "higher",
            "decimal",
        ),
    ]
    metric_leader = a["state_name"] if (to_float(a["metric_value"]) or 0) > (to_float(b["metric_value"]) or 0) else b["state_name"]
    apps_leader = a["state_name"] if (to_float(a["applications_per_100000"]) or 0) > (to_float(b["applications_per_100000"]) or 0) else b["state_name"]
    det_leader = a["state_name"] if (to_float(a["determinations_per_100000"]) or 0) > (to_float(b["determinations_per_100000"]) or 0) else b["state_name"]
    takeaway = (
        f"{metric_leader} has higher {metric_label_lower}, while {apps_leader} has higher application activity and {det_leader} has higher determination activity per 100,000 residents."
    )
    return html.Div(
        className="comparison-summary-panel",
        children=[
            html.Div(
                className="comparison-summary-header",
                children=[
                    html.H3("Key comparison"),
                    html.P(f"Direct side-by-side comparison for {month_label(reporting_month)}."),
                ],
            ),
            html.P(takeaway, className="comparison-summary-takeaway"),
            html.Div(
                className="comparison-summary-grid",
                children=[
                    html.Div("Measure", className="comparison-summary-colhead measure"),
                    html.Div(a["state_name"], className="comparison-summary-colhead"),
                    html.Div(b["state_name"], className="comparison-summary-colhead"),
                    html.Div("Difference", className="comparison-summary-colhead diff"),
                    *[
                        item
                        for label, a_value, b_value, a_text, b_text, mode, kind in rows
                        for item in (
                            html.Div(label, className="comparison-summary-cell measure"),
                            html.Div(
                                html.Span(a_text),
                                className=f"comparison-summary-cell value state-a {comparison_cell_state(a_value, b_value, mode, kind)[1]}",
                            ),
                            html.Div(
                                html.Span(b_text),
                                className=f"comparison-summary-cell value state-b {comparison_cell_state(b_value, a_value, mode, kind)[1]}",
                            ),
                            html.Div(
                                comparison_diff_chip(a["state_name"], b["state_name"], a_value, b_value, mode, kind)[0],
                                className=f"comparison-summary-cell diff-chip {comparison_diff_chip(a['state_name'], b['state_name'], a_value, b_value, mode, kind)[1]}",
                            ),
                        )
                    ],
                ],
            ),
        ],
    )


def build_comparison_status_row(state_a: str, state_b: str, reporting_month: str, metric_key: str) -> html.Div:
    return html.Div()


def build_state_profile(selected_state: str, reporting_month: str, metric_key: str, state_label: str, accent_class: str) -> html.Div:
    metrics = comparison_state_metrics(selected_state, reporting_month, metric_key)
    grouped_fields = [
        (
            "Scale and context",
            [
                ("Total Medicaid/CHIP enrollment", format_value(metrics["total_enrollment"])),
                ("Medicaid enrollment", format_value(metrics["medicaid_enrollment"])),
                ("CHIP enrollment", format_value(metrics["chip_enrollment"])),
                ("Applications submitted", format_value(metrics["applications_submitted"])),
                ("Eligibility determinations", format_value(metrics["eligibility_determinations"])),
                ("Application-determination balance", format_value(metrics["application_determination_balance"], "signed_integer")),
            ],
        ),
        (
            "Program mix",
            [
                ("Medicaid share", format_value(metrics["medicaid_share"], "percent")),
                ("CHIP share", format_value(metrics["chip_share"], "percent")),
                ("Population denominator year", str(metrics["population_year_value"])),
            ],
        ),
    ]

    return html.Div(
        className=f"state-profile-groups comparison-profile {accent_class}",
        children=[
            html.Div(
                className="comparison-profile-header",
                children=[
                    html.Span(state_label, className="comparison-profile-eyebrow"),
                    html.H3(f"{metrics['state_name']} supporting profile"),
                ],
            ),
            html.Div(
                className="comparison-profile-sections",
                children=[
                    html.Div(
                        className="comparison-profile-section",
                        children=[
                            html.H3(title),
                            html.Div(
                                className="comparison-profile-list",
                                children=[
                                    html.Div(className="comparison-profile-row", children=[html.Span(label), html.Strong(value)])
                                    for label, value in values
                                ],
                            ),
                        ],
                    )
                    for title, values in grouped_fields
                ],
            ),
            html.Div(className="comparison-profile-note", children=[html.Strong("Data quality note"), html.P(metrics["data_quality_note"])]),
        ],
    )


def indexed_story_bounds(states: list[str]) -> tuple[float, float]:
    values: list[float] = []
    for state in states:
        story = state_enrollment_story(state)
        for month_row in state_trend_rows(state):
            indexed = ratio(to_float(month_row.get("total_medicaid_and_chip_enrollment")), story["baseline_value"], 100)
            if indexed is not None:
                values.append(indexed)
    if not values:
        return 95.0, 105.0
    return max(0.0, min(values) - 5), max(values) + 5


def selected_state_self_comparison(selected_state: str, label: str, accent_color: str, shared_y_range: tuple[float, float]) -> html.Div:
    row = state_lookup.get(selected_state, state_rows[0])
    rows = state_trend_rows(row["state_abbreviation"])
    latest = rows[-1]
    story = state_enrollment_story(row["state_abbreviation"])

    bar_fig = go.Figure(
        go.Bar(
            x=["January 2019", month_label(story["peak"]["reporting_month"]), month_label(latest["reporting_month"])],
            y=[story["baseline_value"], story["peak_value"], story["latest_value"]],
            marker_color=["#a8bac6", accent_color, "#203647"],
            text=[format_short(story["baseline_value"]), format_short(story["peak_value"]), format_short(story["latest_value"])],
            textposition="outside",
            hovertemplate="%{x}<br>Enrollment: %{y:,.0f}<extra></extra>",
        )
    )
    bar_fig.update_layout(
        title="Baseline, Peak, And Latest Enrollment<br><sup>Selected-state Medicaid/CHIP enrollment at key points in the reporting period.</sup>",
        margin={"l": 45, "r": 20, "t": 66, "b": 44},
        height=300,
        paper_bgcolor="white",
        plot_bgcolor="white",
        yaxis_title="Enrollment",
    )

    indexed_fig = go.Figure(
        go.Scatter(
            x=[month_row["reporting_month"] for month_row in rows],
            y=[ratio(to_float(month_row.get("total_medicaid_and_chip_enrollment")), story["baseline_value"], 100) for month_row in rows],
            mode="lines",
            line={"color": accent_color, "width": 3},
            hovertemplate=(
                f"{row['state_name']}<br>"
                "Reporting month: %{x|%b %Y}<br>"
                "Enrollment index: %{y:,.1f}<extra></extra>"
            ),
            name=f"{row['state_name']} Medicaid/CHIP enrollment index",
        )
    )
    indexed_fig.update_layout(
        title="Indexed Enrollment Trend<br><sup>Jan. 2019 = 100</sup>",
        margin={"l": 58, "r": 24, "t": 66, "b": 46},
        height=300,
        paper_bgcolor="white",
        plot_bgcolor="white",
        showlegend=False,
        xaxis={"title": "Reporting month", "showgrid": True, "gridcolor": "#e8eef0"},
        yaxis={"title": "Index, Jan. 2019 = 100", "showgrid": True, "gridcolor": "#eef2f3", "range": list(shared_y_range)},
    )

    baseline_phrase = "is near"
    if story["change_from_baseline"] is not None and story["change_from_baseline"] > 0:
        baseline_phrase = "remains above"
    elif story["change_from_baseline"] is not None and story["change_from_baseline"] < 0:
        baseline_phrase = "is below"

    return html.Div(
        className="panel self-comparison-card",
        children=[
            html.Div(
                className="section-subhead compact",
                children=[
                    html.H2(f"{label}: {row['state_name']}"),
                    html.P("Compare this state with its own baseline, peak, latest month, and full reporting-period trend."),
                ],
            ),
            html.Div(
                className="two-column self-comparison-grid",
                children=[
                    html.Div(className="panel inset-panel", children=[dcc.Graph(figure=bar_fig, config={"displayModeBar": False})]),
                    html.Div(className="panel inset-panel", children=[dcc.Graph(figure=indexed_fig, config={"displayModeBar": False})]),
                ],
            ),
            html.Div(
                className="panel compact-panel self-comparison-takeaway",
                children=[
                    html.H3("Self-comparison takeaway"),
                    html.P(
                        f"{row['state_name']} {baseline_phrase} its January 2019 baseline and is "
                        f"{format_signed_short(story['change_from_peak'])} from its observed peak by "
                        f"{month_label(latest['reporting_month'])}."
                    ),
                ],
            ),
        ],
    )


def balance_row_for_month(selected_state: str, reporting_month: str) -> dict[str, str]:
    rows = state_balance_rows(selected_state)
    for row in rows:
        if row["reporting_month"] == reporting_month:
            return row
    return latest_balance_lookup.get(selected_state, {})


def within_state_indexed_figure(selected_state: str, accent_color: str, shared_y_range: tuple[float, float]) -> go.Figure:
    row = state_lookup.get(selected_state, state_rows[0])
    rows = state_trend_rows(row["state_abbreviation"])
    story = state_enrollment_story(row["state_abbreviation"])
    indexed_values = [ratio(to_float(month_row.get("total_medicaid_and_chip_enrollment")), story["baseline_value"], 100) for month_row in rows]
    latest_index = indexed_values[-1]
    peak_index = ratio(story["peak_value"], story["baseline_value"], 100)
    fig = go.Figure(
        go.Scatter(
            x=[month_row["reporting_month"] for month_row in rows],
            y=indexed_values,
            mode="lines",
            line={"color": accent_color, "width": 3},
            hovertemplate=(
                f"{row['state_name']}<br>"
                "Reporting month: %{x|%b %Y}<br>"
                "Enrollment index: %{y:,.1f}<extra></extra>"
            ),
            showlegend=False,
        )
    )
    fig.add_hline(y=100, line_dash="dot", line_color="#9fb1ba")
    if peak_index is not None:
        fig.add_trace(
            go.Scatter(
                x=[story["peak"]["reporting_month"]],
                y=[peak_index],
                mode="markers+text",
                marker={"size": 8, "color": accent_color},
                text=["Peak"],
                textposition="top center",
                hovertemplate="Observed peak<br>%{x|%b %Y}<br>Index: %{y:,.1f}<extra></extra>",
                showlegend=False,
            )
        )
    if latest_index is not None:
        fig.add_annotation(
            x=rows[-1]["reporting_month"],
            y=latest_index,
            text=f"Current: {latest_index:,.1f}",
            showarrow=False,
            xanchor="left",
            xshift=8,
            font={"size": 11, "color": accent_color},
            bgcolor="rgba(255,255,255,0.88)",
            bordercolor=accent_color,
            borderwidth=1,
        )
    fig.update_layout(
        margin={"l": 50, "r": 22, "t": 34, "b": 42},
        height=260,
        paper_bgcolor="white",
        plot_bgcolor="white",
        xaxis={"title": "Reporting month", "showgrid": True, "gridcolor": "#e8eef0"},
        yaxis={"title": "Index, Jan. 2019 = 100", "showgrid": True, "gridcolor": "#eef2f3", "range": list(shared_y_range)},
    )
    return fig


def within_state_peak_current_figure(selected_state: str, accent_color: str) -> go.Figure:
    row = state_lookup.get(selected_state, state_rows[0])
    story = state_enrollment_story(row["state_abbreviation"])
    peak_value = story["peak_value"] or 0
    latest_value = story["latest_value"] or 0
    percent_from_peak = story["percent_change_from_peak"]
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=[latest_value, peak_value],
            y=["Enrollment", "Enrollment"],
            mode="lines",
            line={"color": "#cad7dc", "width": 6},
            hoverinfo="skip",
            showlegend=False,
        )
    )
    fig.add_trace(
        go.Scatter(
            x=[peak_value],
            y=["Enrollment"],
            mode="markers+text",
            marker={"size": 12, "color": "#9fb1ba"},
            text=[f"Peak {format_short(peak_value)}"],
            textposition="top center",
            showlegend=False,
            hovertemplate="Observed peak<br>Enrollment: %{x:,.0f}<extra></extra>",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=[latest_value],
            y=["Enrollment"],
            mode="markers+text",
            marker={"size": 12, "color": accent_color},
            text=[f"Current {format_short(latest_value)}"],
            textposition="bottom center",
            showlegend=False,
            hovertemplate="Current month<br>Enrollment: %{x:,.0f}<extra></extra>",
        )
    )
    if percent_from_peak is not None:
        fig.add_annotation(
            x=(peak_value + latest_value) / 2 if peak_value or latest_value else 0,
            y="Enrollment",
            text=f"{format_value(percent_from_peak, 'percent')} from peak",
            showarrow=False,
            yshift=-38,
            font={"size": 11, "color": "#41515b"},
            bgcolor="rgba(255,255,255,0.9)",
            bordercolor="#d8e2e5",
            borderwidth=1,
        )
    fig.update_layout(
        margin={"l": 50, "r": 20, "t": 28, "b": 26},
        height=200,
        paper_bgcolor="white",
        plot_bgcolor="white",
        xaxis={"title": "Enrollment", "showgrid": False},
        yaxis={"showticklabels": False, "showgrid": False},
    )
    return fig


def within_state_program_mix_figure(selected_state: str, reporting_month: str, accent_color: str) -> go.Figure:
    metrics = comparison_state_metrics(selected_state, reporting_month, "medicaid_chip_enrollment_per_1000_residents")
    medicaid_share = to_float(metrics.get("medicaid_share")) or 0
    chip_share = to_float(metrics.get("chip_share")) or 0
    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=[medicaid_share],
            y=["Program mix"],
            orientation="h",
            name="Medicaid share",
            marker={"color": "#4d6f8f"},
            hovertemplate="Medicaid share<br>%{x:.1f}%<extra></extra>",
        )
    )
    fig.add_trace(
        go.Bar(
            x=[chip_share],
            y=["Program mix"],
            orientation="h",
            name="CHIP share",
            marker={"color": "#aab9c5"},
            hovertemplate="CHIP share<br>%{x:.1f}%<extra></extra>",
        )
    )
    fig.update_layout(
        barmode="stack",
        margin={"l": 6, "r": 6, "t": 4, "b": 4},
        height=44,
        paper_bgcolor="white",
        plot_bgcolor="white",
        showlegend=False,
        xaxis={"range": [0, 100], "showgrid": False, "showticklabels": False, "fixedrange": True},
        yaxis={"showgrid": False, "showticklabels": False, "fixedrange": True},
    )
    return fig


def within_state_meta_list(items: list[tuple[str, str]]) -> html.Div:
    return html.Div(
        className="within-state-meta-list",
        children=[
            html.Div(
                className="within-state-meta-row",
                children=[html.Span(label), html.Strong(value)],
            )
            for label, value in items
        ],
    )


def within_state_heatmap_figure(selected_state: str, reporting_month: str, accent_color: str) -> go.Figure:
    row = state_lookup.get(selected_state, state_rows[0])
    rows = state_trend_rows(row["state_abbreviation"])
    story = state_enrollment_story(row["state_abbreviation"])
    month_names = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    years = sorted({datetime.strptime(month_row["reporting_month"][:10], "%Y-%m-%d").year for month_row in rows})
    z_values: list[list[float | None]] = []
    hover_text: list[list[str]] = []
    lookup: dict[tuple[int, int], dict[str, str]] = {}
    for month_row in rows:
        dt = datetime.strptime(month_row["reporting_month"][:10], "%Y-%m-%d")
        lookup[(dt.year, dt.month)] = month_row
    for year in years:
        year_values: list[float | None] = []
        year_hover: list[str] = []
        for month_number in range(1, 13):
            month_row = lookup.get((year, month_number))
            if not month_row:
                year_values.append(None)
                year_hover.append("No reported value")
                continue
            total_enrollment = to_float(month_row.get("total_medicaid_and_chip_enrollment"))
            change_from_baseline = None if total_enrollment is None or story["baseline_value"] is None else total_enrollment - story["baseline_value"]
            change_from_peak = None if total_enrollment is None or story["peak_value"] is None else total_enrollment - story["peak_value"]
            year_values.append(total_enrollment)
            year_hover.append(
                "<br>".join(
                    [
                        f"State: {row['state_name']}",
                        f"Reporting month: {month_label(month_row['reporting_month'])}",
                        f"Total Medicaid/CHIP enrollment: {format_value(total_enrollment)}",
                        f"Jan. 2019 baseline enrollment: {format_value(story['baseline_value'])}",
                        f"Change from Jan. 2019 baseline: {format_value(change_from_baseline, 'signed_integer')}",
                        f"Change from observed peak: {format_value(change_from_peak, 'signed_integer')}",
                    ]
                )
            )
        z_values.append(year_values)
        hover_text.append(year_hover)

    fig = go.Figure(
        go.Heatmap(
            z=z_values,
            x=month_names,
            y=[str(year) for year in years],
            text=hover_text,
            hovertemplate="%{text}<extra></extra>",
            colorscale=[
                [0.00, "#eef3f4"],
                [0.25, "#d5e2e6"],
                [0.50, "#9dbcc6"],
                [0.75, "#5f8fa3"],
                [1.00, "#294f63"],
            ],
            showscale=False,
            xgap=3,
            ygap=3,
            hoverongaps=False,
        )
    )

    peak_dt = datetime.strptime(story["peak"]["reporting_month"][:10], "%Y-%m-%d")
    fig.add_trace(
        go.Scatter(
            x=[month_names[peak_dt.month - 1]],
            y=[str(peak_dt.year)],
            mode="markers+text",
            marker={"symbol": "star", "size": 11, "color": "#8b5e12", "line": {"width": 1, "color": "#ffffff"}},
            text=["Peak"],
            textfont={"color": "#ffffff"},
            textposition="top center",
            hovertemplate="Observed peak month<extra></extra>",
            showlegend=False,
        )
    )

    fig.update_layout(
        margin={"l": 36, "r": 4, "t": 4, "b": 22},
        height=330,
        paper_bgcolor="white",
        plot_bgcolor="white",
        xaxis={"side": "top", "tickfont": {"size": 10}, "showgrid": False, "fixedrange": True},
        yaxis={"autorange": "reversed", "tickfont": {"size": 10}, "showgrid": False, "fixedrange": True},
    )
    return fig


def within_state_heatmap_legend(selected_state: str) -> html.Div:
    rows = state_trend_rows(selected_state)
    monthly_values = [
        to_float(row.get("total_medicaid_and_chip_enrollment"))
        for row in rows
        if to_float(row.get("total_medicaid_and_chip_enrollment")) is not None
    ]
    low_value = min(monthly_values) if monthly_values else None
    high_value = max(monthly_values) if monthly_values else None
    return html.Div(
        className="within-heatmap-legend",
        children=[
            html.Div(
                className="within-heatmap-legend-scale",
                children=[
                    html.Span("Monthly enrollment", className="within-heatmap-legend-label"),
                    html.Div(className="within-heatmap-gradient"),
                    html.Div(
                        className="within-heatmap-range",
                        children=[
                            html.Span(f"Low: {format_short(low_value)}"),
                            html.Span(f"High: {format_short(high_value)}"),
                        ],
                    ),
                ],
            ),
            html.Div(
                className="within-heatmap-key",
                children=[
                    html.Span("Star = peak month"),
                ],
            ),
        ],
    )


def within_state_operations_program_mix_module(
    selected_state: str,
    reporting_month: str,
    accent_class: str,
    accent_color: str,
) -> html.Div:
    row = state_lookup.get(selected_state, state_rows[0])
    month_row = row_for_state_month(row["state_abbreviation"], reporting_month) or {}
    balance_row = balance_row_for_month(row["state_abbreviation"], reporting_month)
    metrics = comparison_state_metrics(selected_state, reporting_month, "medicaid_chip_enrollment_per_1000_residents")
    applications = to_float(month_row.get("total_applications_for_financial_assistance_submitted_at_state_level"))
    determinations = to_float(month_row.get("total_medicaid_and_chip_determinations"))
    balance = to_float(balance_row.get("application_determination_balance"))
    coverage = ratio(determinations, applications, 100)
    return html.Div(
        className="within-panel-module operations-program-mix-module",
        children=[
            html.Div(
                className="within-inline-section",
                children=[
                    html.Div(
                        className="within-module-header",
                        children=[html.H4("Eligibility operations"), html.P("Selected-month workflow")],
                    ),
                    html.Div(
                        className="operations-flow-inline",
                        children=[
                            html.Span("Applications submitted", className="operations-flow-inline-label"),
                            html.Strong(
                                f"{format_short(applications)} \u2192 {format_short(determinations)}",
                                className="operations-flow-inline-value",
                            ),
                            html.Span("Determinations completed", className="operations-flow-inline-label trailing"),
                        ],
                    ),
                    html.Div(
                        className="within-inline-stats",
                        children=[
                            html.Span(f"Balance: {format_value(balance, 'signed_integer')} applications"),
                            html.Span(f"Determination coverage: {format_value(coverage, 'percent')}"),
                        ],
                    ),
                ],
            ),
            html.Div(
                className="within-inline-section",
                children=[
                    html.Div(
                        className="within-module-header",
                        children=[html.H4("Program mix"), html.P("Medicaid and CHIP composition")],
                    ),
                    dcc.Graph(
                        figure=within_state_program_mix_figure(selected_state, reporting_month, accent_color),
                        config={"displayModeBar": False},
                    ),
                    html.Div(
                        className="within-program-mix-values",
                        children=[
                            html.Span(f"Medicaid: {format_value(metrics['medicaid_share'], 'percent')}"),
                            html.Span(f"CHIP: {format_value(metrics['chip_share'], 'percent')}"),
                        ],
                    ),
                    html.P(
                        f"Population denominator year: {metrics['population_year_value']}",
                        className="within-program-mix-year",
                    ),
                ],
            ),
        ],
    )


def within_state_history_summary_module(selected_state: str, reporting_month: str) -> html.Div:
    row = state_lookup.get(selected_state, state_rows[0])
    story = state_enrollment_story(row["state_abbreviation"])
    selected_row = row_for_state_month(row["state_abbreviation"], reporting_month) or story["latest"]
    selected_value = to_float(selected_row.get("total_medicaid_and_chip_enrollment"))
    baseline_value = story["baseline_value"]
    peak_value = story["peak_value"]
    selected_change_from_baseline = None if selected_value is None or baseline_value is None else selected_value - baseline_value
    selected_change_from_peak = None if selected_value is None or peak_value is None else selected_value - peak_value
    baseline_status = (
        "Above Jan. 2019 baseline" if (selected_change_from_baseline or 0) > 0
        else "Below Jan. 2019 baseline" if (selected_change_from_baseline or 0) < 0
        else "At Jan. 2019 baseline"
    )
    peak_status = (
        "Down from observed peak" if (selected_change_from_peak or 0) < 0
        else "At observed peak" if abs(to_float(selected_change_from_peak) or 0) < 1e-9
        else "Above observed peak"
    )
    return html.Div(
        className="within-history-summary",
        children=[
            html.Div(
                className="within-history-primary history-stat-grid",
                children=[
                    html.Div(
                        className="history-stat-card primary",
                        children=[
                            html.Span(short_month_label(selected_row["reporting_month"]), className="within-overview-label"),
                            html.Strong(format_short(selected_value), className="within-overview-value"),
                            html.Small("Current enrollment", className="within-overview-caption"),
                        ],
                    ),
                    html.Div(
                        className="history-stat-card",
                        children=[
                            html.Span("Jan. 2019 baseline", className="within-overview-label"),
                            html.Strong(format_short(baseline_value), className="within-history-stat-value"),
                        ],
                    ),
                    html.Div(
                        className="history-stat-card",
                        children=[
                            html.Span("Observed peak", className="within-overview-label"),
                            html.Strong(format_short(peak_value), className="within-history-stat-value"),
                        ],
                    ),
                ],
            ),
            html.Div(
                className="within-overview-status",
                children=[
                    html.Span(baseline_status, className="journey-status-chip"),
                    html.Span(peak_status, className="journey-status-chip muted"),
                ],
            ),
            within_state_meta_list(
                [
                    ("Distance from Jan. 2019 baseline", f"{format_signed_short(selected_change_from_baseline)} ({format_value(percent_change(selected_value, baseline_value), 'percent')})"),
                    ("Distance from observed peak", f"{format_signed_short(selected_change_from_peak)} ({format_value(percent_change(selected_value, peak_value), 'percent')})"),
                ]
            ),
        ],
    )


def within_state_history_module(selected_state: str, reporting_month: str, accent_color: str) -> html.Div:
    return html.Div(
        className="within-panel-module history-heatmap-module",
        children=[
            html.Div(
                className="within-module-header within-history-header",
                children=[
                    html.H4("Monthly Medicaid/CHIP enrollment"),
                    html.P("Raw monthly enrollment counts"),
                ],
            ),
            dcc.Graph(
                figure=within_state_heatmap_figure(selected_state, reporting_month, accent_color),
                config={"displayModeBar": False},
            ),
            within_state_heatmap_legend(selected_state),
            html.Div(
                className="enrollment-trend-blurbs",
                children=[
                    html.Div(
                        className="enrollment-trend-blurb",
                        children=[
                            html.Span("Latest enrollment"),
                            html.Strong(format_context_value(selected_state, "total_medicaid_chip_enrollment_current_month")),
                        ],
                    ),
                    html.Div(
                        className="enrollment-trend-blurb",
                        children=[
                            html.Span("Monthly change"),
                            html.Strong(format_context_value(selected_state, "month_to_month_percent_change")),
                        ],
                    ),
                    html.Div(
                        className="enrollment-trend-blurb",
                        children=[
                            html.Span("Change from pre-open-enrollment baseline"),
                            html.Strong(format_context_value(selected_state, "percent_change_pre_open_enrollment_to_current_month")),
                        ],
                    ),
                ],
            ),
        ],
    )


CONTEXT_ENROLLMENT_LABELS = {
    "total_medicaid_chip_enrollment_current_month": "Current Medicaid/CHIP enrollment",
    "total_medicaid_chip_enrollment_previous_month": "Previous enrollment",
    "month_to_month_percent_change": "Month-to-month change",
    "net_change_pre_open_enrollment_to_current_month": "Change from July-Sept. 2013 baseline",
    "percent_change_pre_open_enrollment_to_current_month": "Percent change from July-Sept. 2013 baseline",
    "medicaid_expansion_status": "Medicaid expansion flag",
    "marketplace_type": "Marketplace type",
}

ELIGIBILITY_THRESHOLD_LABELS = [
    ("children_medicaid_ages_0_1", "Children Medicaid ages 0-1"),
    ("children_medicaid_ages_1_5", "Children Medicaid ages 1-5"),
    ("children_medicaid_ages_6_18", "Children Medicaid ages 6-18"),
    ("separate_chip", "Separate CHIP"),
    ("pregnant_women_medicaid", "Pregnant women Medicaid"),
    ("pregnant_women_chip", "Pregnant women CHIP"),
    ("parents", "Parents"),
    ("other_adults", "Other adults"),
]

ELIGIBILITY_THRESHOLD_GROUPS = [
    (
        "Children",
        [
            ("children_medicaid_ages_0_1", "Ages 0-1"),
            ("children_medicaid_ages_1_5", "Ages 1-5"),
            ("children_medicaid_ages_6_18", "Ages 6-18"),
        ],
    ),
    (
        "Pregnant women / CHIP",
        [
            ("pregnant_women_medicaid", "Pregnant women Medicaid"),
            ("pregnant_women_chip", "Pregnant women CHIP"),
            ("separate_chip", "Separate CHIP"),
        ],
    ),
    (
        "Adults",
        [
            ("parents", "Parents"),
            ("other_adults", "Other adults"),
        ],
    ),
]


def context_value(selected_state: str, subcategory: str) -> str | None:
    row = state_context_lookup.get(selected_state, {}).get(subcategory)
    if not row:
        return None
    value = row.get("value")
    return value if value not in (None, "") else None


def format_context_value(selected_state: str, subcategory: str) -> str:
    row = state_context_lookup.get(selected_state, {}).get(subcategory)
    if not row:
        return "Not available"
    value = row.get("value")
    if value in (None, ""):
        return "Not available"
    value_type = row.get("value_type")
    if value_type == "count":
        return format_short(value)
    if value_type == "percent":
        return format_value(value, "percent")
    if subcategory == "medicaid_expansion_status":
        return "Yes" if value == "Y" else "No" if value == "N" else value
    return value


def eligibility_threshold_width(value: str | None) -> float:
    if not value:
        return 0
    match = "".join(ch for ch in value if ch.isdigit() or ch == ".")
    if not match:
        return 0
    return min(max(to_float(match) or 0, 0), 320) / 320 * 100


def within_state_eligibility_context_module(selected_state: str) -> html.Div:
    context = state_context_lookup.get(selected_state, {})
    reporting_periods = sorted({row.get("reporting_period", "") for row in context.values() if row.get("reporting_period")})
    source_note = " · ".join(reporting_periods[:2]) if reporting_periods else "Medicaid.gov State Profile context"
    return html.Div(
        className="within-panel-module eligibility-context-module",
        children=[
            html.Div(
                className="within-module-header",
                children=[
                    html.H4("Eligibility context"),
                    html.P(source_note),
                ],
            ),
            html.Div(
                className="eligibility-context-pills",
                children=[
                    html.Div(
                        className="eligibility-context-pill",
                        children=[
                            html.Span("Medicaid expansion"),
                            html.Strong(format_context_value(selected_state, "medicaid_expansion_status")),
                        ],
                    ),
                    html.Div(
                        className="eligibility-context-pill",
                        children=[
                            html.Span("Marketplace type"),
                            html.Strong(format_context_value(selected_state, "marketplace_type")),
                        ],
                    ),
                ],
            ),
            html.Div(
                className="eligibility-threshold-groups",
                children=[
                    html.Div(
                        className="eligibility-threshold-group",
                        children=[
                            html.H5(group_name),
                            html.Div(
                                className="eligibility-threshold-table",
                                children=[
                                    html.Div(
                                        className="eligibility-threshold-row",
                                        children=[
                                            html.Span(label),
                                            html.Div(
                                                className="eligibility-threshold-bar-track",
                                                children=[
                                                    html.Div(
                                                        className="eligibility-threshold-bar",
                                                        style={"width": f"{eligibility_threshold_width(context_value(selected_state, key)):.1f}%"},
                                                    )
                                                ],
                                            ),
                                            html.Strong(format_context_value(selected_state, key)),
                                        ],
                                    )
                                    for key, label in group_items
                                ],
                            ),
                        ],
                    )
                    for group_name, group_items in ELIGIBILITY_THRESHOLD_GROUPS
                ],
            ),
            html.P(
                "Eligibility thresholds describe program rules, not observed enrollee demographic shares.",
                className="within-state-note context-caveat",
            ),
        ],
    )


EXPENDITURE_SERIES = [
    ("Medicaid Program", "Total Net Expenditures", "Medicaid Program"),
    ("Medicaid Administration", "Total Net Expenditures", "Medicaid Administration"),
    ("CHIP", "Total", "CHIP"),
]


def expenditure_rows_for_state(selected_state: str, program_category: str, expenditure_category: str) -> list[dict[str, str]]:
    return [
        row
        for row in state_expenditure_lookup.get(selected_state, [])
        if row["program_category"] == program_category and row["expenditure_category"] == expenditure_category
    ]


def latest_expenditure_year(selected_state: str) -> str:
    years = sorted({row["fiscal_year"] for row in state_expenditure_lookup.get(selected_state, [])})
    return years[-1] if years else "2024"


def expenditure_row_for_year(selected_state: str, program_category: str, expenditure_category: str, fiscal_year: str) -> dict[str, str]:
    return next(
        (
            row
            for row in expenditure_rows_for_state(selected_state, program_category, expenditure_category)
            if row["fiscal_year"] == fiscal_year
        ),
        {},
    )


def expenditure_core_rows_for_year(selected_state: str, fiscal_year: str) -> dict[str, dict[str, str]]:
    return {
        label: expenditure_row_for_year(selected_state, program, category, fiscal_year)
        for program, category, label in EXPENDITURE_SERIES
    }


def expenditure_amount(row: dict[str, str]) -> float | None:
    return to_float(row.get("total_computable_expenditure") or row.get("expenditure_amount"))


def expenditure_total(rows_by_label: dict[str, dict[str, str]]) -> float | None:
    values = [expenditure_amount(row) for row in rows_by_label.values()]
    valid_values = [value for value in values if value is not None]
    return sum(valid_values) if valid_values else None


def within_state_expenditure_context_module(
    selected_state: str,
    accent_color: str,
    fiscal_year: str,
) -> html.Div:
    available_years = {row["fiscal_year"] for row in state_expenditure_lookup.get(selected_state, [])}
    if fiscal_year not in available_years:
        fiscal_year = latest_expenditure_year(selected_state)
    latest_rows = expenditure_core_rows_for_year(selected_state, fiscal_year)
    total = expenditure_total(latest_rows)
    date_accessed = next((item.get("date_accessed") for item in latest_rows.values() if item.get("date_accessed")), "Not available")
    return html.Div(
        className="within-panel-module expenditure-context-module",
        children=[
            html.Div(
                className="within-module-header",
                children=[
                    html.H4("Fiscal profile"),
                    html.P(f"FY{fiscal_year} expenditure snapshot · MBES/CBES financial reporting"),
                ],
            ),
            html.Div(
                className="expenditure-hero",
                children=[
                    html.Span("Total expenditure"),
                    html.Strong(format_dollars_short(total)),
                ],
            ),
            html.Div(
                className="expenditure-breakdown-list",
                children=[
                    html.Div(
                        className="expenditure-breakdown-row",
                        children=[html.Span(label), html.Strong(format_dollars_short(expenditure_amount(expenditure_row)))],
                    )
                    for label, expenditure_row in latest_rows.items()
                ],
            ),
            html.P(
                f"Source: Medicaid.gov MBES/CBES, FY2019-FY{fiscal_year} · Accessed {date_accessed}",
                className="expenditure-source-line",
            ),
        ],
    )


def within_state_unavailable_module(title: str, message: str) -> html.Div:
    return html.Div(
        className="within-panel-module context-unavailable-module",
        children=[
            html.Div(className="within-module-header", children=[html.H4(title)]),
            html.Div(
                className="within-policy-placeholder",
                children=message,
            ),
        ],
    )


def state_outline_figure(selected_state: str, accent_color: str) -> go.Figure:
    row = state_lookup.get(selected_state, state_rows[0])
    fig = go.Figure(
        go.Choropleth(
            locations=[row["state_abbreviation"]],
            z=[1],
            locationmode="USA-states",
            colorscale=[[0, "rgba(255,255,255,0)"], [1, "rgba(255,255,255,0)"]],
            showscale=False,
            hoverinfo="skip",
            marker_line_color=accent_color,
            marker_line_width=1.8,
        )
    )
    fig.update_geos(
        scope="usa",
        fitbounds="locations",
        visible=False,
        showcountries=False,
        showcoastlines=False,
        showland=False,
        showlakes=False,
        bgcolor="rgba(0,0,0,0)",
        projection_type="albers usa",
    )
    fig.update_layout(
        margin={"l": 0, "r": 0, "t": 0, "b": 0},
        width=72,
        height=54,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )
    return fig


def within_state_profile_panel(
    selected_state: str,
    reporting_month: str,
    state_label: str,
    accent_class: str,
    accent_color: str,
    selected_view: str,
    show_footer: bool,
    fiscal_year: str,
) -> html.Div:
    metrics = comparison_state_metrics(selected_state, reporting_month, "medicaid_chip_enrollment_per_1000_residents")
    row = state_lookup.get(selected_state, state_rows[0])
    footer = (
        f"Missingness: {format_value(metrics['missingness_percent'], 'percent')} · "
        f"Population denominator: {metrics['population_year_value']}"
    )
    view_children: html.Component | list[html.Component]
    if selected_view == "enrollment_history":
        view_children = [within_state_history_module(selected_state, reporting_month, accent_color)]
    elif selected_view == "eligibility_enrollment_context":
        view_children = [within_state_eligibility_context_module(selected_state)]
    elif selected_view == "expenditure_context":
        view_children = [within_state_expenditure_context_module(selected_state, accent_color, fiscal_year)]
    else:
        view_children = [
            within_state_unavailable_module(
                "Context unavailable",
                "This view is not available for the selected state context configuration.",
            )
        ]
    return html.Div(
        className=f"panel within-state-profile-panel {accent_class}",
        children=[
            html.Div(
                className="within-profile-header",
                children=[
                    html.Div(
                        className="within-profile-header-copy",
                        children=[
                            html.Span(state_label, className="comparison-profile-eyebrow"),
                            html.H3(row["state_name"]),
                        ],
                    ),
                    html.Div(
                        className="within-profile-outline",
                        children=[
                            dcc.Graph(
                                figure=state_outline_figure(selected_state, accent_color),
                                config={"displayModeBar": False, "staticPlot": True},
                            )
                        ],
                    ),
                ],
            ),
            html.Div(
                className=f"within-profile-grid within-profile-grid--{selected_view}",
                children=view_children,
            ),
        ],
    )


def build_within_state_section(
    state_a: str,
    state_b: str,
    reporting_month: str,
    selected_view: str,
    fiscal_year: str,
) -> html.Div:
    return html.Div(
        className="within-state-stack",
        children=[
            html.Div(
                className="two-column within-state-profile-grid",
                children=[
                    within_state_profile_panel(
                        state_a,
                        reporting_month,
                        "State A",
                        "state-a-accent",
                        "#d4a017",
                        selected_view,
                        False,
                        fiscal_year,
                    ),
                    within_state_profile_panel(
                        state_b,
                        reporting_month,
                        "State B",
                        "state-b-accent",
                        "#5c6ac4",
                        selected_view,
                        False,
                        fiscal_year,
                    ),
                ],
            ),
        ],
    )


def build_maps_tab() -> html.Div:
    metric_options = [{"label": map_metric_dropdown_label(key), "value": key} for key in TWO_STATE_COMPARISON_METRIC_KEYS if key in MAP_METRICS]
    month_options = [{"label": month_label(value), "value": value} for value in MONTH_VALUES]
    return html.Div(
        className="tab-page",
        children=[
            section_header(
                "State Map Explorer",
                "How does Medicaid/CHIP enrollment vary across states?",
                "Compare raw enrollment, population-adjusted enrollment, and recent enrollment change across states.",
            ),
            html.Div(
                className="workflow-band workflow-band-context",
                children=[
                    html.Div(
                        className="workflow-band-header",
                        children=[
                            html.P("Section 1", className="workflow-band-step"),
                            html.H2("1. Selected states in national context"),
                        ],
                    ),
                    html.Div(
                        className="comparison-explorer panel",
                        children=[
                            dcc.Dropdown(id="state-selector", options=sorted_states(state_rows), value=DEFAULT_STATE_A, clearable=False, style={"display": "none"}),
                            html.Div(
                                className="compare-controls-highlight compare-state-primary-module",
                                children=[
                                    html.Div(
                                        className="section-subhead compact",
                                        children=[
                                            html.H2("Compare Two States"),
                                            html.P("Choose the two states first. The strip below shows where they rank nationally."),
                                        ],
                                    ),
                                    html.Div(
                                        className="state-chooser-module",
                                        children=[
                                            html.Div(
                                                className="state-selector-primary-row",
                                                children=[
                                                    html.Label(
                                                        [
                                                            html.Span("State A"),
                                                            dcc.Dropdown(id="state-a-selector", options=sorted_states(state_rows), value=DEFAULT_STATE_A, clearable=False),
                                                        ],
                                                        className="state-selector-primary",
                                                    ),
                                                    html.Div("vs", className="state-selector-vs"),
                                                    html.Label(
                                                        [
                                                            html.Span("State B"),
                                                            dcc.Dropdown(id="state-b-selector", options=sorted_states(state_rows), value=DEFAULT_STATE_B, clearable=False),
                                                        ],
                                                        className="state-selector-primary",
                                                    ),
                                                ],
                                            ),
                                        ],
                                    ),
                                    html.P(id="comparison-difference-text", className="comparison-difference-text"),
                                ],
                            ),
                            html.Div(
                                className="panel comparison-lineup-panel",
                                children=[
                                    html.Div(
                                        className="ranking-modal-launcher",
                                        children=[
                                            html.Button(
                                                "Open full state rankings ↗",
                                                id="ranking-modal-open",
                                                className="ranking-open-button",
                                                n_clicks=0,
                                            ),
                                        ],
                                    ),
                                    html.Div(id="comparison-lineup"),
                                ],
                            ),
                            html.Div(
                                id="ranking-modal",
                                className="ranking-modal",
                                children=[
                                    html.Div(
                                        id="ranking-modal-backdrop",
                                        className="ranking-modal-backdrop",
                                        n_clicks=0,
                                    ),
                                    html.Div(
                                        className="ranking-modal-dialog",
                                        children=[
                                            html.Div(
                                                className="ranking-modal-header",
                                                children=[
                                                    html.H3(id="ranking-modal-title"),
                                                    html.Button(
                                                        "Close",
                                                        id="ranking-modal-close",
                                                        className="ranking-modal-close",
                                                        n_clicks=0,
                                                    ),
                                                ],
                                            ),
                                            html.Div(id="ranking-modal-body"),
                                        ],
                                    ),
                                ],
                            ),
                        ],
                    ),
                ],
            ),
            html.Div(
                className="workflow-band workflow-band-comparison",
                children=[
                    html.Div(
                        className="workflow-band-header",
                        children=[
                            html.P("Section 2", className="workflow-band-step"),
                            html.H2("2. Direct state-to-state comparison"),
                            html.P("Compare the selected states side by side on the same measures."),
                        ],
                    ),
                    html.Div(
                        className="panel comparison-trend-panel",
                        children=[
                            html.Div(
                                className="comparison-trend-controls",
                                children=[
                                    html.Div(className="section-subhead compact", children=[html.H2("Trend over time")]),
                                    html.Div(
                                        className="comparison-secondary-controls",
                                        children=[
                                            html.Label(
                                                [
                                                    html.Span("Metric"),
                                                    dcc.Dropdown(id="map-metric", options=metric_options, value="medicaid_chip_enrollment_per_1000_residents", clearable=False),
                                                ]
                                            ),
                                        ],
                                    ),
                                ],
                            ),
                            dcc.Graph(id="comparison-trend-chart", config={"displayModeBar": False}),
                        ],
                    ),
                    html.Div(
                        className="selected-state-focus comparison-focus-panel",
                        children=[
                            html.Div(
                                className="comparison-month-controls comparison-month-controls-inline",
                                children=[
                                    html.Label(
                                        [
                                            html.Span("Selected month"),
                                            dcc.Dropdown(id="map-month-value", options=month_options, value=LATEST_RELIABLE_MONTH_VALUE, clearable=False),
                                        ]
                                    ),
                                    html.Div(id="comparison-month-status"),
                                ],
                            ),
                            html.Div(id="state-comparison-summary"),
                            html.Div(id="state-comparison-status"),
                        ],
                    ),
                ],
            ),
            html.Div(
                className="workflow-band workflow-band-profile",
                children=[
                    html.Div(
                        className="workflow-band-header",
                        children=[
                            html.P("Section 3", className="workflow-band-step"),
                            html.H2("3. Within-state state profiles"),
                            html.P("Review each selected state's enrollment trend, eligibility rules, and fiscal profile."),
                        ],
                    ),
                    html.Div(
                        className="within-state-view-bar",
                        children=[
                            html.Span("View", className="within-state-view-label"),
                            dcc.RadioItems(
                                id="within-state-view",
                                className="segmented-control within-state-view-selector",
                                inputClassName="within-state-view-input",
                                labelClassName="within-state-view-option",
                                options=[
                                    {"label": "Enrollment trend", "value": "enrollment_history"},
                                    {"label": "Eligibility context", "value": "eligibility_enrollment_context"},
                                    {"label": "Fiscal profile", "value": "expenditure_context"},
                                ],
                                value="enrollment_history",
                                inline=True,
                            ),
                        ],
                    ),
                    html.Div(
                        id="section3-fiscal-controls",
                        className="section3-fiscal-controls is-hidden",
                        children=[
                            html.Div(
                                className="section3-fiscal-control-copy",
                                children=[
                                    html.Strong("Fiscal profile controls"),
                                    html.Span("Expenditure uses fiscal-year MBES/CBES financial reporting data."),
                                ],
                            ),
                            html.Label(
                                className="compact-control",
                                children=[
                                    html.Span("Expenditure year"),
                                    dcc.Dropdown(
                                        id="fiscal-year-selector",
                                        options=[
                                            {"label": f"FY{year}", "value": year}
                                            for year in FISCAL_YEAR_VALUES
                                        ],
                                        value=LATEST_FISCAL_YEAR_VALUE,
                                        clearable=False,
                                        searchable=False,
                                    ),
                                ],
                            ),
                        ],
                    ),
                    html.Div(id="state-self-comparison", className="wide-stack"),
                    html.Div(className="helper-strip state-map-helper", children=[]),
                ],
            ),
        ],
    )


def state_trend_rows(selected_state: str) -> list[dict[str, str]]:
    return state_month_lookup.get(selected_state, [])


def state_balance_rows(selected_state: str) -> list[dict[str, str]]:
    return balance_lookup.get(selected_state, [])


def state_enrollment_story(selected_state: str) -> dict[str, object]:
    rows = state_trend_rows(selected_state)
    baseline = row_for_state_month(selected_state, BASELINE_MONTH) or rows[0]
    latest = rows[-1]
    peak = max(rows, key=lambda record: to_float(record.get("total_medicaid_and_chip_enrollment")) or 0)
    prior_12 = row_months_before(selected_state, latest["reporting_month"]) or {}
    baseline_value = to_float(baseline.get("total_medicaid_and_chip_enrollment"))
    latest_value = to_float(latest.get("total_medicaid_and_chip_enrollment"))
    peak_value = to_float(peak.get("total_medicaid_and_chip_enrollment"))
    prior_12_value = to_float(prior_12.get("total_medicaid_and_chip_enrollment"))
    return {
        "baseline": baseline,
        "latest": latest,
        "peak": peak,
        "prior_12": prior_12,
        "baseline_value": baseline_value,
        "latest_value": latest_value,
        "peak_value": peak_value,
        "prior_12_value": prior_12_value,
        "change_from_baseline": latest_value - baseline_value if latest_value is not None and baseline_value is not None else None,
        "percent_change_from_baseline": percent_change(latest_value, baseline_value),
        "change_from_peak": latest_value - peak_value if latest_value is not None and peak_value is not None else None,
        "percent_change_from_peak": percent_change(latest_value, peak_value),
        "last_12_month_change": latest_value - prior_12_value if latest_value is not None and prior_12_value is not None else None,
        "last_12_month_percent_change": percent_change(latest_value, prior_12_value),
    }


def state_summary_cards(selected_state: str) -> list[html.Div]:
    story = state_enrollment_story(selected_state)
    return [
        card("Baseline enrollment", format_value(story["baseline_value"]), month_label(story["baseline"]["reporting_month"])),
        card("Peak enrollment", format_value(story["peak_value"]), month_label(story["peak"]["reporting_month"])),
        card("Latest enrollment", format_value(story["latest_value"]), month_label(story["latest"]["reporting_month"])),
        card("Change from baseline", format_value(story["change_from_baseline"], "signed_integer"), format_value(story["percent_change_from_baseline"], "percent")),
        card("Change from peak", format_value(story["change_from_peak"], "signed_integer"), format_value(story["percent_change_from_peak"], "percent")),
        card("Last 12-month change", format_value(story["last_12_month_change"], "signed_integer"), format_value(story["last_12_month_percent_change"], "percent")),
    ]


def component_change_focus(medicaid_change: float | None, chip_change: float | None) -> str:
    if medicaid_change is None or chip_change is None:
        return "the available component fields"
    medicaid_abs = abs(medicaid_change)
    chip_abs = abs(chip_change)
    if medicaid_abs == 0 and chip_abs == 0:
        return "neither component"
    if medicaid_abs > chip_abs * 1.25:
        return "Medicaid"
    if chip_abs > medicaid_abs * 1.25:
        return "CHIP"
    return "both Medicaid and CHIP"


def chip_trend_rows(rows: list[dict[str, str]], mode: str) -> list[dict[str, str | float | None]]:
    baseline = rows[0]
    baseline_medicaid = to_float(baseline.get("total_medicaid_enrollment"))
    baseline_chip = to_float(baseline.get("total_chip_enrollment"))
    output = []
    for row in rows:
        medicaid = to_float(row.get("total_medicaid_enrollment"))
        chip = to_float(row.get("total_chip_enrollment"))
        medicaid_index = ratio(medicaid, baseline_medicaid, 100)
        chip_index = ratio(chip, baseline_chip, 100)
        if mode == "indexed":
            output.append(
                {
                    **row,
                    "medicaid_series": medicaid_index,
                    "chip_series": chip_index,
                    "medicaid_raw": medicaid,
                    "chip_raw": chip,
                    "medicaid_index": medicaid_index,
                    "chip_index": chip_index,
                }
            )
        else:
            output.append(
                {
                    **row,
                    "medicaid_series": medicaid,
                    "chip_series": chip,
                    "medicaid_raw": medicaid,
                    "chip_raw": chip,
                    "medicaid_index": medicaid_index,
                    "chip_index": chip_index,
                }
            )
    return output


def chip_component_figure(rows: list[dict[str, str | float | None]], state_name: str, mode: str) -> go.Figure:
    indexed = mode == "indexed"
    title = (
        "Selected State Medicaid vs CHIP Enrollment, Indexed to Jan. 2019"
        if indexed
        else "Selected State Medicaid vs CHIP Enrollment, Raw Counts"
    )
    subtitle = (
        f"{state_name}: index values show relative movement since January 2019. Medicaid and CHIP are both set to 100 at the January 2019 baseline so their trends can be compared despite different enrollment sizes."
        if indexed
        else f"{state_name}: raw counts show program size. Because Medicaid enrollment is usually much larger than CHIP enrollment, CHIP movement may be harder to see in this view."
    )
    fig = go.Figure()
    traces = [
        ("medicaid_series", "Medicaid enrollment index" if indexed else "Medicaid enrollment", "medicaid_raw", "medicaid_index", "#12324a"),
        ("chip_series", "CHIP enrollment index" if indexed else "CHIP enrollment", "chip_raw", "chip_index", "#2f7d78"),
    ]
    for value_field, label, raw_field, index_field, color in traces:
        fig.add_trace(
            go.Scatter(
                x=[row["reporting_month"] for row in rows],
                y=[to_float(row.get(value_field)) for row in rows],
                mode="lines",
                name=label,
                line={"width": 2.8, "color": color},
                customdata=[
                    [
                        state_name,
                        "Medicaid" if "medicaid" in value_field else "CHIP",
                        to_float(row.get(raw_field)),
                        to_float(row.get(index_field)),
                        "Preliminary" if row.get("preliminary_or_updated") == "P" else "Final/updated",
                    ]
                    for row in rows
                ],
                hovertemplate=(
                    "State: %{customdata[0]}<br>"
                    "Reporting month: %{x|%b %Y}<br>"
                    "Program component: %{customdata[1]}<br>"
                    "Raw enrollment: %{customdata[2]:,.0f}<br>"
                    "Indexed value: %{customdata[3]:,.1f}<br>"
                    "Reporting status: %{customdata[4]}<extra></extra>"
                ),
            )
        )
    fig.update_layout(
        title={"text": f"{title}<br><sup>{subtitle}</sup>"},
        margin={"l": 58, "r": 28, "t": 88, "b": 48},
        height=420,
        hovermode="x unified",
        legend={"orientation": "h", "y": -0.24},
        paper_bgcolor="white",
        plot_bgcolor="white",
        font={"family": "Inter, Arial, sans-serif", "color": "#253746"},
        xaxis={
            "title": "Reporting month",
            "rangeselector": {
                "buttons": [
                    {"count": 1, "label": "1Y", "step": "year", "stepmode": "backward"},
                    {"count": 3, "label": "3Y", "step": "year", "stepmode": "backward"},
                    {"step": "all", "label": "All"},
                ]
            },
            "rangeslider": {"visible": True, "thickness": 0.07},
            "showgrid": True,
            "gridcolor": "#e8eef0",
        },
        yaxis={
            "title": "Index, Jan. 2019 = 100" if indexed else "Enrollment count",
            "showgrid": True,
            "gridcolor": "#eef2f3",
        },
    )
    return fig


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
        margin={"l": 44, "r": 18, "t": 46, "b": 34},
        height=330,
        paper_bgcolor="white",
        plot_bgcolor="white",
        yaxis_title="Enrollment",
    )
    return fig


def program_share_parts(medicaid: float | None, chip: float | None) -> dict[str, float | None]:
    total = (medicaid or 0) + (chip or 0)
    return {
        "total": total,
        "medicaid_share": ratio(medicaid, total, 100),
        "chip_share": ratio(chip, total, 100),
    }


def current_split_figure(selected_state: str) -> go.Figure:
    selected = state_lookup[selected_state]
    state_medicaid = to_float(selected.get("latest_medicaid_enrollment"))
    state_chip = to_float(selected.get("latest_chip_enrollment"))
    national = current_national_totals()
    national_parts = program_share_parts(national["medicaid"], national["chip"])
    state_parts = program_share_parts(state_medicaid, state_chip)
    rows = [
        {
            "label": "National",
            "medicaid": national["medicaid"],
            "chip": national["chip"],
            "medicaid_share": national_parts["medicaid_share"],
            "chip_share": national_parts["chip_share"],
        },
        {
            "label": selected["state_name"],
            "medicaid": state_medicaid,
            "chip": state_chip,
            "medicaid_share": state_parts["medicaid_share"],
            "chip_share": state_parts["chip_share"],
        },
    ]
    fig = go.Figure()
    for program, share_key, count_key, color in [
        ("Medicaid", "medicaid_share", "medicaid", "#12324a"),
        ("CHIP", "chip_share", "chip", "#2f7d78"),
    ]:
        fig.add_trace(
            go.Bar(
                y=[row["label"] for row in rows],
                x=[to_float(row[share_key]) or 0 for row in rows],
                orientation="h",
                name=program,
                marker_color=color,
                text=[format_value(row[share_key], "percent") for row in rows],
                textposition="inside",
                insidetextanchor="middle",
                customdata=[
                    [
                        program,
                        to_float(row[count_key]),
                        to_float(row[share_key]),
                    ]
                    for row in rows
                ],
                hovertemplate=(
                    "%{customdata[0]} enrollment: %{customdata[1]:,.0f}<br>"
                    "Share of total: %{customdata[2]:.1f}%<extra></extra>"
                ),
            )
        )
    fig.update_layout(
        barmode="stack",
        height=270,
        margin={"l": 84, "r": 20, "t": 20, "b": 34},
        xaxis={"range": [0, 100], "ticksuffix": "%", "showgrid": False, "title": None},
        yaxis={"title": None},
        legend={"orientation": "h", "y": -0.18},
        paper_bgcolor="white",
        plot_bgcolor="white",
        font={"family": "Inter, Arial, sans-serif", "color": "#253746"},
    )
    return fig


def change_reference_row(selected_state: str, period: str, latest_row: dict[str, str], story: dict[str, object]) -> tuple[dict[str, str] | None, str]:
    if period == "since_baseline":
        return row_for_state_month(selected_state, BASELINE_MONTH) or state_trend_rows(selected_state)[0], "since Jan. 2019"
    if period == "since_peak":
        return story["peak"], "since observed peak"
    return row_months_before(selected_state, latest_row["reporting_month"], 1), "latest month"


def component_changes_for_period(selected_state: str, period: str) -> dict[str, object]:
    rows = state_trend_rows(selected_state)
    latest_row = rows[-1]
    story = state_enrollment_story(selected_state)
    reference_row, label = change_reference_row(selected_state, period, latest_row, story)
    latest_medicaid = to_float(latest_row.get("total_medicaid_enrollment"))
    latest_chip = to_float(latest_row.get("total_chip_enrollment"))
    latest_total = to_float(latest_row.get("total_medicaid_and_chip_enrollment"))
    ref_medicaid = to_float(reference_row.get("total_medicaid_enrollment")) if reference_row else None
    ref_chip = to_float(reference_row.get("total_chip_enrollment")) if reference_row else None
    ref_total = to_float(reference_row.get("total_medicaid_and_chip_enrollment")) if reference_row else None
    medicaid_change = latest_medicaid - ref_medicaid if latest_medicaid is not None and ref_medicaid is not None else None
    chip_change = latest_chip - ref_chip if latest_chip is not None and ref_chip is not None else None
    total_change = latest_total - ref_total if latest_total is not None and ref_total is not None else None
    absolute_total = (abs(medicaid_change) if medicaid_change is not None else 0) + (abs(chip_change) if chip_change is not None else 0)
    return {
        "period_label": label,
        "latest_row": latest_row,
        "reference_row": reference_row,
        "medicaid_change": medicaid_change,
        "chip_change": chip_change,
        "total_change": total_change,
        "medicaid_share_of_abs_change": ratio(abs(medicaid_change) if medicaid_change is not None else None, absolute_total, 100),
        "chip_share_of_abs_change": ratio(abs(chip_change) if chip_change is not None else None, absolute_total, 100),
        "main_driver": component_change_focus(medicaid_change, chip_change),
    }


def change_contribution_figure(change_data: dict[str, object]) -> go.Figure:
    medicaid_share = to_float(change_data.get("medicaid_share_of_abs_change")) or 0
    chip_share = to_float(change_data.get("chip_share_of_abs_change")) or 0
    medicaid_change = to_float(change_data.get("medicaid_change"))
    chip_change = to_float(change_data.get("chip_change"))
    period_label = change_data["period_label"]
    fig = go.Figure()
    for program, share, change, color in [
        ("Medicaid", medicaid_share, medicaid_change, "#12324a"),
        ("CHIP", chip_share, chip_change, "#2f7d78"),
    ]:
        fig.add_trace(
            go.Bar(
                y=["Share of absolute change"],
                x=[share],
                orientation="h",
                name=program,
                marker_color=color,
                text=[format_value(share, "percent") if share else ""],
                textposition="inside",
                customdata=[[program, change, share, period_label]],
                hovertemplate=(
                    "%{customdata[0]} change: %{customdata[1]:+,.0f}<br>"
                    "Share of %{customdata[3]} change: %{customdata[2]:.1f}%<extra></extra>"
                ),
            )
        )
    fig.update_layout(
        barmode="stack",
        height=180,
        margin={"l": 10, "r": 10, "t": 12, "b": 34},
        xaxis={"range": [0, 100], "ticksuffix": "%", "visible": False},
        yaxis={"visible": False},
        legend={"orientation": "h", "y": -0.28},
        paper_bgcolor="white",
        plot_bgcolor="white",
        font={"family": "Inter, Arial, sans-serif", "color": "#253746"},
    )
    return fig


def chip_kpi_summary(selected_state: str, change_data: dict[str, object]) -> list[html.Div]:
    selected = state_lookup[selected_state]
    latest_row = change_data["latest_row"]
    latest_medicaid = to_float(latest_row.get("total_medicaid_enrollment"))
    latest_chip = to_float(latest_row.get("total_chip_enrollment"))
    latest_total = to_float(latest_row.get("total_medicaid_and_chip_enrollment"))
    return [
        card("Latest enrollment", format_short(latest_total), month_label(latest_row["reporting_month"])),
        card("Medicaid share", format_value(ratio(latest_medicaid, latest_total, 100), "percent"), selected["state_name"]),
        card("CHIP share", format_value(ratio(latest_chip, latest_total, 100), "percent"), selected["state_name"]),
        card("Main movement", str(change_data["main_driver"]).capitalize(), change_data["period_label"]),
    ]


def change_summary_children(change_data: dict[str, object]) -> html.Div:
    return html.Div(
        className="chip-change-summary",
        children=[
            html.Div(
                children=[
                    html.Span("Medicaid change"),
                    html.Strong(format_value(change_data["medicaid_change"], "signed_integer")),
                ],
            ),
            html.Div(
                children=[
                    html.Span("CHIP change"),
                    html.Strong(format_value(change_data["chip_change"], "signed_integer")),
                ],
            ),
            html.Div(
                children=[
                    html.Span("Total change"),
                    html.Strong(format_value(change_data["total_change"], "signed_integer")),
                ],
            ),
        ],
    )


def financing_percent(value: str | int | float | None) -> str:
    numeric = to_float(value)
    if numeric is None:
        return "Not available"
    return f"{numeric * 100:.1f}%"


def financing_multiplier_text(value: str | int | float | None) -> str:
    numeric = to_float(value)
    if numeric is None:
        return "Not available"
    return f"${numeric:.2f} federal per $1 state"


def chip_multiplier_text(efmap: str | int | float | None, multiplier: str | int | float | None) -> str:
    efmap_numeric = to_float(efmap)
    if efmap_numeric is not None and efmap_numeric >= 1:
        return "100% federal match / no state share"
    return financing_multiplier_text(multiplier)


def selected_state_financing_cards(selected_state: str) -> html.Div:
    fmap_row = medicaid_fmap_lookup.get((selected_state, FINANCING_FISCAL_YEAR), {})
    chip_row = chip_efmap_lookup.get((selected_state, FINANCING_FISCAL_YEAR), {})
    cards = [
        ("Medicaid FMAP", financing_percent(fmap_row.get("medicaid_fmap")), f"FY{FINANCING_FISCAL_YEAR} federal matching rate"),
        ("Medicaid multiplier", financing_multiplier_text(fmap_row.get("medicaid_multiplier")), "Federal dollars per $1 state dollar"),
        ("CHIP eFMAP", financing_percent(chip_row.get("chip_enhanced_fmap")), f"FY{FINANCING_FISCAL_YEAR} enhanced CHIP match"),
        ("CHIP multiplier", chip_multiplier_text(chip_row.get("chip_enhanced_fmap"), chip_row.get("chip_multiplier_calculated")), "Calculated from enhanced FMAP"),
    ]
    return html.Div(
        className="financing-card-grid",
        children=[
            html.Div(
                className="financing-card",
                children=[
                    html.Span(label),
                    html.Strong(value),
                    html.P(helper),
                ],
            )
            for label, value, helper in cards
        ],
    )


CHIP_STRUCTURE_CATEGORIES = [
    "Separate CHIP only",
    "Medicaid expansion CHIP only",
    "Both separate CHIP and Medicaid expansion CHIP",
]
CHIP_STRUCTURE_COLORS = {
    "Separate CHIP only": "#c9792a",
    "Medicaid expansion CHIP only": "#f1c75b",
    "Both separate CHIP and Medicaid expansion CHIP": "#6fa8dc",
}


def chip_structure_map_figure(selected_state: str) -> go.Figure:
    rows = [row for row in chip_structure_rows if row.get("state_abbr") in state_lookup]
    z_values = [CHIP_STRUCTURE_CATEGORIES.index(row["chip_program_structure"]) for row in rows]
    colorscale = []
    max_index = len(CHIP_STRUCTURE_CATEGORIES) - 1
    for index, category in enumerate(CHIP_STRUCTURE_CATEGORIES):
        start = index / max_index if max_index else 0
        end = (index + 0.999) / max_index if max_index else 1
        colorscale.append([start, CHIP_STRUCTURE_COLORS[category]])
        colorscale.append([min(end, 1), CHIP_STRUCTURE_COLORS[category]])

    fig = go.Figure()
    fig.add_trace(
        go.Choropleth(
            locations=[row["state_abbr"] for row in rows],
            z=z_values,
            locationmode="USA-states",
            colorscale=colorscale,
            zmin=0,
            zmax=max_index,
            marker_line_color="#ffffff",
            marker_line_width=0.7,
            customdata=[[row["state"], row["chip_program_structure"]] for row in rows],
            hovertemplate="%{customdata[0]}<br>%{customdata[1]}<extra></extra>",
            showscale=False,
        )
    )
    if selected_state in chip_structure_lookup:
        fig.add_trace(
            go.Choropleth(
                locations=[selected_state],
                z=[0],
                locationmode="USA-states",
                colorscale=[[0, "rgba(0,0,0,0)"], [1, "rgba(0,0,0,0)"]],
                marker_line_color="#17212b",
                marker_line_width=3,
                hoverinfo="skip",
                showscale=False,
            )
        )
    fig.update_geos(
        scope="usa",
        fitbounds="locations",
        showlakes=False,
        bgcolor="rgba(0,0,0,0)",
    )
    fig.update_layout(
        margin={"l": 0, "r": 0, "t": 0, "b": 0},
        height=390,
        paper_bgcolor="white",
        plot_bgcolor="white",
        font={"family": "Inter, Arial, sans-serif", "color": "#253746"},
    )
    return fig


def selected_chip_structure_label(selected_state: str) -> html.Div:
    row = chip_structure_lookup.get(selected_state, {})
    state_name = state_lookup.get(selected_state, {}).get("state_name", selected_state)
    structure = row.get("chip_program_structure", "Not available")
    return html.Div(
        className="chip-structure-selected-label",
        children=[
            html.Span("Selected state"),
            html.Strong(f"{state_name}: {structure}"),
        ],
    )


def chip_structure_legend() -> html.Div:
    return html.Div(
        className="chip-structure-legend",
        children=[
            html.Div(
                className="chip-structure-legend-item",
                children=[
                    html.Span(
                        className="chip-structure-swatch",
                        style={"backgroundColor": CHIP_STRUCTURE_COLORS[category]},
                    ),
                    html.Span(category),
                ],
            )
            for category in CHIP_STRUCTURE_CATEGORIES
        ],
    )


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
                    html.Div(
                        className="chart-card-header",
                        children=[
                            html.Div(
                                children=[
                                    html.H2("Selected State Medicaid Vs CHIP Trend Explorer"),
                                    html.P("Raw counts show program size; indexed view shows relative movement since Jan. 2019."),
                                ]
                            ),
                            dcc.RadioItems(
                                id="chip-trend-mode",
                                options=[
                                    {"label": "Raw count", "value": "raw"},
                                    {"label": "Indexed to Jan. 2019 = 100", "value": "indexed"},
                                ],
                                value="indexed",
                                inline=True,
                                className="segmented-control",
                            ),
                        ],
                    ),
                    html.Div(id="state-chip-component-summary", className="kpi-grid compact"),
                    dcc.Graph(id="state-chip-trend", config={"displayModeBar": False}),
                    html.Div(
                        className="policy-note chart-interpretation compact",
                        children=[
                            html.H2("Why use an indexed view?"),
                            html.P(
                                "Medicaid enrollment is usually much larger than CHIP enrollment, so raw-count charts can make CHIP appear visually flat. "
                                "The indexed view sets Medicaid and CHIP to 100 in January 2019, making relative movement easier to compare."
                            ),
                            html.P("Indexed trends show relative change, not raw enrollment size."),
                        ],
                    ),
                ],
            ),
            html.Div(id="state-chip-summary", className="kpi-grid compact"),
            html.Div(id="state-chip-interpretation", className="policy-note wide"),
            html.Div(
                className="panel financing-context-panel",
                children=[
                    html.Div(
                        className="chart-card-header",
                        children=[
                            html.Div(
                                children=[
                                    html.H2(f"Federal financing context · FY{FINANCING_FISCAL_YEAR}"),
                                    html.P(
                                        "FMAP and multipliers describe federal-state financing context. "
                                        "They help explain funding structure, not monthly enrollment movement by themselves."
                                    ),
                                ]
                            )
                        ],
                    ),
                    html.Div(id="chip-financing-cards"),
                ],
            ),
            html.Div(
                className="panel chip-structure-panel",
                children=[
                    html.Div(
                        className="chart-card-header",
                        children=[
                            html.Div(
                                children=[
                                    html.H2("CHIP program design by state"),
                                    html.P(
                                        "Categorical Medicaid.gov view of whether states operate separate CHIP, "
                                        "Medicaid expansion CHIP, or both."
                                    ),
                                ]
                            )
                        ],
                    ),
                    html.Div(id="chip-structure-selected"),
                    chip_structure_legend(),
                    dcc.Graph(id="chip-structure-map", config={"displayModeBar": False}),
                ],
            ),
            html.Div(
                className="policy-note wide source-note-compact",
                children=[
                    html.P(
                        "Sources: KFF State Health Facts FMAP/eFMAP; Medicaid.gov CHIP program structure. "
                        "Accessed 2026-06-22."
                    ),
                ],
            ),
        ],
    )


def build_program_context_tab() -> html.Div:
    return html.Div(
        className="tab-page",
        children=[
            section_header(
                "Medicaid & CHIP Program Context",
                "Are enrollment changes concentrated in Medicaid, CHIP, or both?",
                "",
            ),
            html.Div(
                className="chip-page-controls",
                children=[
                    html.Label(
                        children=[
                            html.Span("Select a state"),
                            dcc.Dropdown(
                                id="chip-state-selector",
                                options=sorted_states(state_rows),
                                value=DEFAULT_STATE_A,
                                clearable=False,
                            ),
                        ]
                    )
                ],
            ),
            html.Div(id="chip-kpi-summary", className="kpi-grid compact chip-kpi-row"),
            html.Div(
                className="two-column chip-main-grid",
                children=[
                    html.Div(
                        className="panel chip-analysis-card",
                        children=[
                            html.Div(
                                className="chart-card-header",
                                children=[
                                    html.Div(
                                        children=[
                                            html.H2("Current enrollment split"),
                                            html.P("National and selected-state Medicaid/CHIP shares in the latest reporting month."),
                                        ]
                                    )
                                ],
                            ),
                            dcc.Graph(id="chip-current-split", config={"displayModeBar": False}),
                        ],
                    ),
                    html.Div(
                        className="panel chip-analysis-card",
                        children=[
                            html.Div(
                                className="chart-card-header",
                                children=[
                                    html.Div(
                                        children=[
                                            html.H2("What changed?"),
                                            html.P("Signed component changes and each program's share of absolute enrollment movement."),
                                        ]
                                    ),
                                    dcc.RadioItems(
                                        id="chip-change-period",
                                        options=[
                                            {"label": "Latest month", "value": "latest_month"},
                                            {"label": "Since Jan. 2019", "value": "since_baseline"},
                                            {"label": "Since peak", "value": "since_peak"},
                                        ],
                                        value="latest_month",
                                        inline=True,
                                        className="segmented-control",
                                    ),
                                ],
                            ),
                            html.Div(id="chip-change-values"),
                            dcc.Graph(id="chip-change-contribution", config={"displayModeBar": False}),
                        ],
                    ),
                ],
            ),
            html.Div(
                className="two-column chip-support-grid",
                children=[
                    html.Div(
                        className="panel financing-context-panel",
                        children=[
                            html.Div(
                                className="chart-card-header",
                                children=[
                                    html.Div(
                                        children=[
                                            html.H2(f"Federal financing context · FY{FINANCING_FISCAL_YEAR}"),
                                            html.P("Financing context, not a monthly enrollment driver by itself."),
                                        ]
                                    )
                                ],
                            ),
                            html.Div(id="chip-financing-cards"),
                        ],
                    ),
                    html.Div(
                        className="panel chip-structure-panel",
                        children=[
                            html.Div(
                                className="chart-card-header",
                                children=[
                                    html.Div(
                                        children=[
                                            html.H2("CHIP program design by state"),
                                            html.P("Categorical Medicaid.gov structure. Click a state to update the page."),
                                        ]
                                    )
                                ],
                            ),
                            html.Div(id="chip-structure-selected"),
                            chip_structure_legend(),
                            dcc.Graph(id="chip-structure-map", config={"displayModeBar": False}),
                        ],
                    ),
                ],
            ),
            html.Div(
                className="policy-note wide source-note-compact",
                children=[
                    html.P("Sources: Medicaid.gov monthly enrollment files; KFF State Health Facts FMAP/eFMAP; Medicaid.gov CHIP program structure."),
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
                                "Use these alongside source notes and the data quality caveats in Methods & Limits."
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


def data_quality_caveats_section() -> html.Div:
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
    latest_month_rows = sorted(quality_month_rows, key=lambda row: row.get("reporting_month", ""))[-6:]
    return html.Div(
        className="methods-quality-section",
        children=[
            html.Div(
                className="policy-note wide",
                children=[
                    html.H2("Data Quality and Reporting Caveats"),
                    html.P(
                        "Public aggregate CMS reporting is useful for descriptive monitoring, but field completeness, "
                        "state reporting variation, and preliminary latest-month records affect how headline metrics "
                        "should be interpreted."
                    ),
                    html.Ul(
                        [
                            html.Li("Latest-month values may be preliminary and can be revised in later source updates."),
                            html.Li("Missingness varies by field, state, and reporting month."),
                            html.Li("Fields with high missingness or unclear standalone interpretation are excluded from headline KPIs."),
                            html.Li("Applications and determinations are operations indicators, not complete performance scores."),
                        ]
                    ),
                ],
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
                    html.Div(className="panel", children=[html.H2("Missingness By Month And Preliminary Status"), table_from_rows(latest_month_rows, [("reporting_month", "Month"), ("missing_value_percent", "Missing %"), ("preliminary_records", "Preliminary records")], 6)]),
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
                    html.H2("Data Sources and Coverage"),
                    html.P("Medicaid data source: CMS/Data.Medicaid.gov State Medicaid and CHIP Applications, Eligibility Determinations, and Enrollment Data."),
                    html.P("Population denominator source: U.S. Census Bureau NST-EST2024-POP annual resident population estimates."),
                    html.P("Medicaid data coverage: January 2019 through February 2026. Geography: all 50 states plus DC. Grain: monthly state-level aggregate data."),
                ],
            ),
            html.Div(
                className="panel",
                children=[
                    html.H2("What The Dashboard Can Show"),
                    html.Ul(
                        [
                            html.Li("Medicaid/CHIP enrollment trends across the full reporting period."),
                            html.Li("State-level variation and selected state vs national indexed trends."),
                            html.Li("Medicaid vs CHIP component patterns."),
                            html.Li("Applications and eligibility determinations as descriptive operations indicators."),
                            html.Li("Population-adjusted context for comparing states of different sizes."),
                            html.Li("Reporting and data quality caveats, including missingness and preliminary latest-month status."),
                            html.Li("Monitoring flags for changes that may warrant further policy or operations review."),
                        ]
                    ),
                ],
            ),
            data_quality_caveats_section(),
            html.Div(
                className="panel",
                children=[
                    html.H2("What The Dashboard Cannot Show"),
                    html.Ul(
                        [
                            html.Li("Beneficiary-level outcomes or individual coverage transitions."),
                            html.Li("Direct measures of churn, uninsured status, or transitions to other coverage."),
                            html.Li("County-level patterns."),
                            html.Li("Claims, utilization, cost, diagnosis, access-to-care, or health outcome data."),
                            html.Li("Causal policy effects."),
                            html.Li("Pending applications as a validated dashboard field."),
                            html.Li("Renewal volumes as a clean standalone measure."),
                            html.Li("Complete operations performance across all source fields."),
                        ]
                    ),
                ],
            ),
            html.Div(
	                className="policy-note wide",
	                children=[
	                    html.H2("Policy timeline sources"),
	                    html.H3("Dashboard metrics"),
	                    html.Ul(
	                        [
	                            html.Li("CMS/Data.Medicaid.gov State Medicaid and CHIP Applications, Eligibility Determinations, and Enrollment Data."),
	                            html.Li("U.S. Census Bureau NST-EST2024-POP annual resident population estimates for population denominators."),
	                        ]
	                    ),
	                    html.H3("Policy and reporting context"),
	                    html.Ul(
	                        [
	                            html.Li("CMS/Medicaid.gov for continuous coverage, renewals, and reporting context."),
	                            html.Li("McIntyre et al. (2025), JAMA Health Forum, for unwinding, churn, coverage transitions, and net enrollment context."),
	                            html.Li("KFF for Medicaid enrollment, unwinding, and state variation context."),
	                            html.Li("MACPAC for Medicaid/CHIP and children's coverage context."),
	                        ]
	                    ),
	                    html.P("Timeline sources provide policy and reporting context only. Dashboard metrics remain derived from CMS/Data.Medicaid.gov."),
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
                html.H1("Medicaid Enrollment & Eligibility Operations Analytics"),
                html.P(
                    "A public CMS data monitoring tool for Medicaid/CHIP enrollment, eligibility operations, "
                    "state variation, and reporting quality.",
                    className="header-copy",
                ),
            ],
        ),
        dcc.Tabs(
            id="main-tabs",
            value="overview",
            className="tabs",
            children=[
                dcc.Tab(label="National Snapshot", value="overview", children=build_overview_tab()),
                dcc.Tab(label="State Comparison Explorer", value="maps", children=build_maps_tab()),
            ],
        ),
        html.Footer(
            className="app-footer",
            children="© 2026 Caroline Howard & Prashant Shekhar",
        ),
    ],
)


@app.callback(
    Output("national-kpi-details", "children"),
    Output("kpi-baseline", "className"),
    Output("kpi-peak", "className"),
    Output("kpi-latest", "className"),
    Output("kpi-change-baseline", "className"),
    Output("kpi-change-peak", "className"),
    Input("kpi-baseline", "n_clicks"),
    Input("kpi-peak", "n_clicks"),
    Input("kpi-latest", "n_clicks"),
    Input("kpi-change-baseline", "n_clicks"),
    Input("kpi-change-peak", "n_clicks"),
)
def update_national_kpi_details(*_clicks):
    if not ctx.triggered_id:
        return ([], *kpi_classes_for_selection())
    triggered = ctx.triggered_id
    key = str(triggered).replace("kpi-", "")
    return (metric_details_panel(key), *kpi_classes_for_selection(key))


@app.callback(
    Output("timeline-detail", "children"),
    Input("timeline-continuous", "n_clicks"),
    Input("timeline-growth", "n_clicks"),
    Input("timeline-unwinding", "n_clicks"),
    Input("timeline-variation", "n_clicks"),
    Input("timeline-renewals", "n_clicks"),
    Input("timeline-reporting", "n_clicks"),
)
def update_timeline_detail(*_clicks):
    if not ctx.triggered_id:
        return timeline_detail(TIMELINE_EVENTS[0])
    key = str(ctx.triggered_id).replace("timeline-", "")
    return timeline_detail(timeline_event_by_key(key))


@app.callback(
    Output("national-index-trend", "figure"),
    Output("overview-change-map", "figure"),
    Output("overview-selected-state-label", "children"),
    Output("selected-state-takeaway", "children"),
    Input("overview-state-selector", "value"),
)
def update_national_index_trend(selected_state: str):
    if selected_state not in state_lookup:
        selected_state = DEFAULT_OVERVIEW_STATE
    return (
        national_enrollment_figure(selected_state),
        overview_change_map(selected_state),
        f"Selected state: {state_lookup[selected_state]['state_name']}",
        selected_state_takeaway(selected_state),
    )


@app.callback(
    Output("overview-state-selector", "value"),
    Input("overview-change-map", "clickData"),
    prevent_initial_call=True,
)
def update_overview_state_from_map(click_data: dict | None):
    if not click_data or not click_data.get("points"):
        return no_update
    point = click_data["points"][0]
    state = point.get("location")
    if state in state_lookup:
        return state
    customdata = point.get("customdata")
    if isinstance(customdata, list) and customdata and customdata[-1] in state_lookup:
        return customdata[-1]
    return no_update


@app.callback(
    Output("comparison-lineup", "children"),
    Output("comparison-difference-text", "children"),
    Output("comparison-month-status", "children"),
    Output("comparison-trend-chart", "figure"),
    Output("ranking-modal-title", "children"),
    Output("ranking-modal-body", "children"),
    Output("state-comparison-summary", "children"),
    Output("state-comparison-status", "children"),
    Output("state-self-comparison", "children"),
    Input("within-state-view", "value"),
    Input("map-metric", "value"),
    Input("state-a-selector", "value"),
    Input("state-b-selector", "value"),
    Input("map-month-value", "value"),
    Input("fiscal-year-selector", "value"),
)
def update_map(
    within_state_view: str,
    metric_key: str,
    state_a: str,
    state_b: str,
    reporting_month: str,
    fiscal_year: str,
):
    if within_state_view not in {
        "enrollment_history",
        "eligibility_enrollment_context",
        "expenditure_context",
    }:
        within_state_view = "enrollment_history"
    if metric_key not in TWO_STATE_COMPARISON_METRIC_KEYS or metric_key not in MAP_METRICS:
        metric_key = "medicaid_chip_enrollment_per_1000_residents"
    if state_a not in state_lookup:
        state_a = DEFAULT_STATE_A
    if state_b not in state_lookup or state_b == state_a:
        state_b = DEFAULT_STATE_B if DEFAULT_STATE_B != state_a else next(
            row["value"] for row in sorted_states(state_rows) if row["value"] != state_a
        )
    if reporting_month not in MONTH_VALUES:
        reporting_month = LATEST_RELIABLE_MONTH_VALUE
    if fiscal_year not in FISCAL_YEAR_VALUES:
        fiscal_year = LATEST_FISCAL_YEAR_VALUE
    return (
        comparison_dot_lineup(metric_key, reporting_month, state_a, state_b),
        difference_summary_text(metric_key, reporting_month, state_a, state_b),
        comparison_month_status(reporting_month),
        compare_trend_figure(metric_key, state_a, state_b, reporting_month),
        f"Full national ranking table · {map_metric_dropdown_label(RANK_STRIP_METRIC_KEY)} · {month_label(reporting_month)}",
        ranking_table_component(metric_key, reporting_month, state_a, state_b),
        build_state_comparison_summary(state_a, state_b, reporting_month, metric_key),
        build_comparison_status_row(state_a, state_b, reporting_month, metric_key),
        build_within_state_section(state_a, state_b, reporting_month, within_state_view, fiscal_year),
    )


@app.callback(
    Output("section3-fiscal-controls", "className"),
    Input("within-state-view", "value"),
)
def toggle_section3_fiscal_controls(selected_view: str) -> str:
    if selected_view == "expenditure_context":
        return "section3-fiscal-controls"
    return "section3-fiscal-controls is-hidden"


@app.callback(
    Output("ranking-modal", "className"),
    Input("ranking-modal-open", "n_clicks"),
    Input("ranking-modal-close", "n_clicks"),
    Input("ranking-modal-backdrop", "n_clicks"),
)
def toggle_ranking_modal(open_clicks: int, close_clicks: int, backdrop_clicks: int) -> str:
    trigger = ctx.triggered_id
    if trigger == "ranking-modal-open":
        return "ranking-modal is-open"
    return "ranking-modal"


@app.callback(
    Output("state-selector", "value"),
    Input("state-a-selector", "value"),
)
def sync_primary_state(state_a: str):
    if state_a in state_lookup:
        return state_a
    return DEFAULT_STATE_A


if __name__ == "__main__":
    app.run(
        debug=False,
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 8050)),
        use_reloader=False,
    )
