"""ModelScope AI — task accuracy, cost, and latency explorer."""

from __future__ import annotations

import math
from html import escape
from pathlib import Path

import pandas as pd
import streamlit as st

from src.charts import (
    accuracy_cost_chart,
    accuracy_latency_chart,
    cost_rank_chart,
    latency_distribution_chart,
    provider_cost_chart,
)
from src.data_loader import load_snapshot
from src.data_processing import DATA_URL, SOURCE_URL
from src.metrics import SCORE_LABELS, calculate_kpis, pareto_frontier, provider_summary
from src.theme import theme_css

ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data"

st.set_page_config(
    page_title="ModelScope AI | Model Performance Explorer",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="auto",
)

if "appearance_mode" not in st.session_state:
    st.session_state["appearance_mode"] = "Dark"
st.markdown(theme_css(st.session_state["appearance_mode"]), unsafe_allow_html=True)


@st.cache_data(ttl=300, show_spinner="Loading the latest validated snapshot…")
def get_snapshot() -> tuple[pd.DataFrame, dict[str, object]]:
    return load_snapshot(DATA_DIR / "models.csv", DATA_DIR / "metadata.json")


def pretty(value: object) -> str:
    return str(value).replace("_", " ").title()


def apply_range_filter(
    frame: pd.DataFrame, column: str, label: str, step: float,
    reference: pd.DataFrame | None = None,
) -> pd.DataFrame:
    values = pd.to_numeric((reference if reference is not None else frame)[column], errors="coerce").dropna()
    if values.empty:
        return frame
    low, high = float(values.min()), float(values.max())
    if math.isclose(low, high):
        st.caption(f"{label}: {low:,.2f} (all available rows)")
        return frame[pd.to_numeric(frame[column], errors="coerce").eq(low)]
    scale = 100.0 if column in SCORE_LABELS else 1.0
    slider_step = step * scale
    low = round(math.floor(low * scale / slider_step) * slider_step, 8)
    high = round(math.ceil(high * scale / slider_step) * slider_step, 8)
    if scale == 100.0:
        low, high = max(0.0, low), min(100.0, high)
        label += " (%)"
    selected = st.slider(
        label, min_value=low, max_value=high, value=(low, high), step=slider_step,
        format="%.1f" if scale == 100.0 else ("%.2f" if step < 1 else "%.0f"),
    )
    numeric = pd.to_numeric(frame[column], errors="coerce")
    return frame[numeric.between(float(selected[0]) / scale, float(selected[1]) / scale, inclusive="both")]


def render_table(frame: pd.DataFrame, *, index: bool = False) -> None:
    """Render an escaped, scrollable table that follows the app appearance."""
    st.markdown(
        '<div class="ms-table">' + frame.to_html(index=index, escape=True, border=0) + '</div>',
        unsafe_allow_html=True,
    )


def metric_display(value: object, kind: str) -> str:
    if pd.isna(value):
        return "—"
    number = float(value)
    if kind == "accuracy":
        return f"{number:.1%}"
    if kind == "cost":
        return f"${number:,.2f}"
    if kind == "seconds":
        return f"{number / 1000:,.2f} s"
    if kind == "milliseconds":
        return f"{number:,.0f} ms"
    return f"{number:,.2f}"


def main() -> None:
    data, metadata = get_snapshot()

    st.markdown(
        """
        <div class="hero">
          <div class="eyebrow">MODEL PERFORMANCE · BUSINESS DOCUMENTS</div>
          <h1>ModelScope AI</h1>
          <p>Compare accuracy, cost and response time across real business-document tasks.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.caption(
        f"{metadata.get('attribution', 'Based on data from ModelVerdict (CC BY 4.0)')} · "
        f"[Source and methodology]({SOURCE_URL})"
    )
    st.radio(
        "Appearance",
        options=["Light", "Dark"],
        key="appearance_mode",
        horizontal=True,
        format_func=lambda mode: "☀ Light" if mode == "Light" else "◐ Dark",
        help="Switch the dashboard between light and dark appearance.",
    )
    appearance = str(st.session_state["appearance_mode"])

    if data.empty:
        st.warning("No validated data snapshot is available yet. Run `python scripts/fetch_data.py` to retrieve the public dataset.")
        st.link_button("Open the source data", DATA_URL)
        return

    tasks = sorted(data["task"].dropna().astype(str).unique())
    default_task = "invoices" if "invoices" in tasks else tasks[0]

    with st.sidebar:
        st.markdown("### Explore a cohort")
        st.caption("Choose a task and refine the model set.")
        task = st.selectbox("Business task", tasks, index=tasks.index(default_task), format_func=pretty)
        task_data = data[data["task"].eq(task)]
        languages = sorted(task_data["language_code"].dropna().astype(str).unique())
        default_language = "en" if "en" in languages else languages[0]
        language = st.selectbox("Document language", languages, index=languages.index(default_language), format_func=str.upper)
        language_data = task_data[task_data["language_code"].eq(language)]
        levels = sorted(language_data["level"].dropna().astype(str).unique(), key=lambda value: (value != "all", value))
        default_level = "all" if "all" in levels else levels[0]
        level = st.selectbox("Document format", levels, index=levels.index(default_level), format_func=pretty)
        score_column = st.selectbox(
            "Accuracy measure",
            options=list(SCORE_LABELS),
            format_func=lambda value: SCORE_LABELS[value],
        )

        cohort = data[
            data["task"].eq(task)
            & data["language_code"].eq(language)
            & data["level"].eq(level)
        ].copy()
        providers = sorted(cohort["provider"].dropna().astype(str).unique())
        selected_providers = st.multiselect("Providers", providers, default=providers)
        search = st.text_input("Search model", placeholder="Type a model name")
        model_names = sorted(cohort["model_name"].dropna().astype(str).unique())
        selected_models = st.multiselect("Limit to models", model_names, default=[])
        st.caption("No model selection means all models in this cohort.")

        filtered = cohort[cohort["provider"].isin(selected_providers)]
        if search.strip():
            filtered = filtered[filtered["model_name"].str.contains(search.strip(), case=False, regex=False, na=False)]
        if selected_models:
            filtered = filtered[filtered["model_name"].isin(selected_models)]

        with st.expander("Accuracy, cost & speed ranges", expanded=False):
            range_source = filtered.copy()
            filtered = apply_range_filter(filtered, score_column, SCORE_LABELS[score_column], 0.01, range_source)
            filtered = apply_range_filter(
                filtered,
                "cost_usd_per_1000_documents",
                "Cost per 1,000 documents (USD)",
                0.05,
                range_source,
            )
            filtered = apply_range_filter(
                filtered, "latency_p50_ms", "Median response time p50 (ms)", 100.0, range_source
            )

    if filtered.empty:
        st.info("No models match these filters. Expand or clear one of the selections in the sidebar.")
        return

    efficient = pareto_frontier(filtered, score_column=score_column)
    kpis = calculate_kpis(filtered, score_column=score_column)
    score_label = SCORE_LABELS[score_column]

    st.markdown("#### Cohort snapshot")
    cards = [
        ("Models", f"{kpis['models']:,}"),
        ("Providers", f"{kpis['providers']:,}"),
        ("Median cost / 1k docs", metric_display(kpis["median_cost"], "cost")),
        ("Median response p50", metric_display(kpis["median_latency"], "seconds")),
    ]
    st.markdown(
        '<div class="kpi-grid">' + ''.join(
            f'<div class="kpi-card"><div class="kpi-label">{escape(label)}</div>'
            f'<div class="kpi-value">{escape(value)}</div></div>' for label, value in cards
        ) + '</div>', unsafe_allow_html=True,
    )

    frontier_count = int(efficient["is_pareto_efficient"].sum())
    st.markdown("#### Accuracy vs. cost")
    st.caption(
        f"Each point is one model in the selected task, language and format. "
        f"{frontier_count} model(s) are Pareto-efficient on {score_label.lower()} and cost. "
        "A frontier model is not universally better; it is not beaten on both measures within this cohort."
    )
    st.plotly_chart(
        accuracy_cost_chart(efficient, score_column, score_label, appearance),
        width="stretch",
        theme=None,
    )

    cost_tab, speed_tab, provider_tab, compare_tab, explorer_tab = st.tabs(
        ["Cost analysis", "Response time", "Provider analysis", "Compare models", "Model Explorer"]
    )

    with cost_tab:
        control_columns = st.columns([1, 1, 3])
        max_rows = max(1, len(filtered))
        top_n = int(control_columns[0].number_input("Top N", min_value=1, max_value=max_rows, value=min(10, max_rows), step=1))
        order = control_columns[1].selectbox("Order", ["Highest cost", "Lowest cost"])
        control_columns[2].caption("Cost is actual API token spend scaled to 1,000 documents for the selected task and cohort.")
        st.plotly_chart(cost_rank_chart(filtered, top_n, order, appearance), width="stretch", theme=None)
        st.caption("A higher document cost can still be preferable when it materially improves task accuracy; compare both axes.")

    with speed_tab:
        left, right = st.columns(2)
        left.markdown("##### Accuracy and response time")
        left.caption("Median response time p50 is the typical end-to-end time for a valid response in this run.")
        left.plotly_chart(
            accuracy_latency_chart(filtered, score_column, score_label, appearance),
            width="stretch",
            theme=None,
        )
        right.markdown("##### Typical and slower responses")
        right.caption("P50 marks the median; p90 marks the slower tail. These are whole-response times, not time-to-first-token or tokens/second.")
        right.plotly_chart(latency_distribution_chart(filtered, appearance), width="stretch", theme=None)

    summary = provider_summary(filtered, score_column)
    with provider_tab:
        if summary.empty:
            st.info("Provider summaries are not available for this cohort.")
        else:
            left, right = st.columns([1.1, 1])
            left.plotly_chart(provider_cost_chart(summary, appearance), width="stretch", theme=None)
            display_summary = summary.copy()
            display_summary["Median accuracy"] = display_summary["Median accuracy"].map(lambda value: metric_display(value, "accuracy"))
            display_summary["Median cost / 1k docs"] = display_summary["Median cost / 1k docs"].map(lambda value: metric_display(value, "cost"))
            display_summary["Median p50 latency (ms)"] = display_summary["Median p50 latency (ms)"].map(lambda value: metric_display(value, "milliseconds"))
            with right:
                render_table(display_summary)

    with compare_tab:
        ranked_names = (
            filtered.sort_values(score_column, ascending=False)["model_name"].drop_duplicates().tolist()
        )
        compare_default = ranked_names[:2]
        compare_names = st.multiselect(
            "Choose 2–4 models",
            sorted(filtered["model_name"].dropna().astype(str).unique()),
            default=compare_default,
            max_selections=4,
        )
        if len(compare_names) < 2:
            st.info("Select at least two models to compare them side by side.")
        else:
            compare = filtered[filtered["model_name"].isin(compare_names)].drop_duplicates("model_name").set_index("model_name")
            compare_table = pd.DataFrame(
                {
                    model: {
                        "Provider": row["provider"],
                        "Correct fields": metric_display(row["field_accuracy"], "accuracy"),
                        "Error-free documents": metric_display(row["document_accuracy"], "accuracy"),
                        "Cost per 1,000 documents": metric_display(row["cost_usd_per_1000_documents"], "cost"),
                        "Median response p50": metric_display(row["latency_p50_ms"], "seconds"),
                        "Response p90": metric_display(row["latency_p90_ms"], "seconds"),
                        "Valid JSON responses": metric_display(1 - row["invalid_json_rate"], "accuracy") if pd.notna(row["invalid_json_rate"]) else "—",
                        "Cases evaluated": f"{int(row['case_count']):,}" if pd.notna(row["case_count"]) else "—",
                    }
                    for model, row in compare.iterrows()
                }
            )
            render_table(compare_table, index=True)
            st.caption("Models are compared only within the currently selected task, language, and document format.")

    with explorer_tab:
        display_columns = [
            "model_name", "provider", "field_accuracy", "document_accuracy",
            "cost_usd_per_1000_documents", "latency_p50_ms", "latency_p90_ms",
            "invalid_json_rate", "case_count", "passes_threshold", "top_error",
        ]
        table = filtered[display_columns].copy()
        table = table.rename(columns={
            "model_name": "Model",
            "provider": "Provider",
            "field_accuracy": "Correct fields",
            "document_accuracy": "Error-free documents",
            "cost_usd_per_1000_documents": "Cost / 1k docs (USD)",
            "latency_p50_ms": "Response p50 (ms)",
            "latency_p90_ms": "Response p90 (ms)",
            "invalid_json_rate": "Invalid JSON rate",
            "case_count": "Cases",
            "passes_threshold": "Meets accuracy threshold",
            "top_error": "Most common error",
        })
        sort_column = st.selectbox("Sort results by", table.columns, index=2)
        descending = st.checkbox("Descending order", value=True)
        table = table.sort_values(sort_column, ascending=not descending, na_position="last")
        table = table.style.format({
            "Correct fields": "{:.1%}", "Error-free documents": "{:.1%}",
            "Cost / 1k docs (USD)": "${:,.2f}", "Response p50 (ms)": "{:,.0f}",
            "Response p90 (ms)": "{:,.0f}", "Invalid JSON rate": "{:.1%}",
        }, na_rep="—", escape="html").hide(axis="index")
        st.markdown('<div class="ms-table">' + table.to_html() + '</div>', unsafe_allow_html=True)
        csv = filtered.to_csv(index=False).encode("utf-8")
        st.download_button(
            "Download filtered results (CSV)",
            data=csv,
            file_name=f"model-scope-{task}-{language}-{level}.csv",
            mime="text/csv",
        )
        st.caption("Downloaded rows retain source and license metadata. Credit ModelVerdict when redistributing them.")

    st.divider()
    st.markdown("#### Data status")
    status_columns = st.columns(4)
    status_columns[0].markdown(f"**Source**  \n[ModelVerdict]({SOURCE_URL})")
    status_columns[1].markdown(f"**Latest source run**  \n{metadata.get('run_date', 'Unknown')}")
    status_columns[2].markdown(f"**Model/cohort rows**  \n{int(metadata.get('row_count', len(data))):,}")
    status_columns[3].markdown(f"**Pipeline**  \n{pretty(metadata.get('status', 'snapshot'))}")
    st.markdown(
        "<div class='source-note'>Based on ModelVerdict results, licensed under CC BY 4.0. "
        "ModelScope AI is an independent educational analysis and is not endorsed by ModelVerdict.</div>",
        unsafe_allow_html=True,
    )
    st.caption("Methodology and source: [modelverdict.ai](https://modelverdict.ai/en/methodology/) · [Open data](https://modelverdict.ai/en/data/)")


if __name__ == "__main__":
    main()

