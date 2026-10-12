# ModelScope AI — implementation plan

## Selected source and data contract

Use the public ModelVerdict leaderboard JSON at `https://modelverdict.ai/data/leaderboards.json`. Its data page states that the downloadable results are licensed under CC BY 4.0, reusable with credit, and refreshed with weekly runs. The source includes measured field accuracy, error-free document rates, actual USD cost per 1,000 documents, median (p50) and p90 response latency, task, language, document level, provider, and sample size. The snapshot is grouped into task/language/format cohorts, so comparisons and Pareto calculations will stay within one selected cohort.

This changes the interpretation from a universal intelligence ranking to task-specific accuracy on six business-document workflows. Latency is a whole-response duration in milliseconds; the source does not report output tokens/second or time-to-first-token. The interface and technical article will say so explicitly and avoid conclusions beyond the measured cohort.

## Work plan

1. Keep the project isolated in this Desktop folder; do not touch the unrelated `New project 3` workspace.
2. Fetch and validate the licensed JSON snapshot; flatten it into a normalized CSV and record run/source/license metadata. Preserve the prior snapshot on a failed or invalid update.
3. Build cleaning, KPI, provider-summary, comparison, and Pareto logic.
4. Build the Streamlit interface with cohort and model filters, Plotly charts, comparison, explorer, attribution, and data status.
5. Add meaningful unit tests, Docker files, GitHub Actions CI and daily data refresh, README, article draft, video script, and submission link template.
6. Verify locally, then create/push the public GitHub repo and prepare Streamlit Cloud deployment.

## Publication notes

The Artificial Analysis API is not used in this version. The public project will attribute ModelVerdict and preserve its CC BY 4.0 license/source link in the app, README, and downloadable data. No API key is needed for the public JSON endpoint.

References:
- https://modelverdict.ai/en/data/
- https://modelverdict.ai/en/methodology/
- https://modelverdict.ai/data/leaderboards.json
