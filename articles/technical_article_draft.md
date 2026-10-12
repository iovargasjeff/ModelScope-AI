# Which AI Models Give You More for Your Money? A Task-Aware Streamlit Dashboard

> Draft for Dev.to, Medium, or Hashnode. Refresh cohort dates and observations from the committed snapshot immediately before publication.

## Introduction

Choosing a language model for a business workflow involves more than a broad ranking. The model needs to complete the specific task accurately, at an acceptable cost and response time. This project turns published task measurements into an interactive comparison.

[INSERT DASHBOARD SCREENSHOT]

## The question

For a selected business-document task, language, and input format, how do model accuracy, cost, and response time trade off?

The dashboard uses a task-specific accuracy score. It does not claim to measure universal intelligence.

## Dataset and license

The source is ModelVerdict's public leaderboard JSON, published under CC BY 4.0 with attribution to ModelVerdict. The feed groups measurements by task, language, and document format. It includes correct-field accuracy, error-free-document accuracy, cost per 1,000 documents, p50/p90 latency, provider, and sample size.

The benchmark covers six document workflows. Its documents are synthetic, which helps make the expected answers known and avoids real personal or company data. The results still represent a bounded test set; they should not be treated as a guarantee for other tasks or customer documents.

[INSERT SOURCE / METHODOLOGY SCREENSHOT]

## Technologies

The implementation uses Python, Pandas, Streamlit, Plotly, Requests, pytest, Ruff, Docker, and GitHub Actions. Streamlit presents the interactive explorer; Plotly handles the cohort-level charts; Python separates the ETL, metric calculations, and presentation layer.

## Data pipeline

The refresh script downloads the published JSON, verifies the declared license and required run metadata, validates rows, flattens each task/language/format leaderboard, and atomically writes a normalized CSV plus metadata. It refuses empty or unexpectedly licensed responses and preserves the previous snapshot on failure.

[INSERT PIPELINE DIAGRAM]

## Cleaning and transformation

The ETL normalizes field names, converts scores, cost, latency, and sample sizes to numeric columns, keeps source metadata, and removes duplicate model rows within the same cohort. Invalid ranges become missing values rather than being silently interpreted as valid measurements.

## Dashboard design

The first selection is a task, language, and document format. Restricting comparisons to one cohort avoids mixing unlike workloads. The dashboard then offers provider/model filters and ranges for accuracy, cost, and response time.

Four headline metrics summarize models, providers, median cost per 1,000 documents, and median p50 response time. Provider comparisons use medians to reduce the effect of outliers.

[INSERT FILTERS + KPI SCREENSHOT]

## Accuracy versus cost and the Pareto frontier

The main scatter plot places task accuracy against cost per 1,000 documents. Tooltips show the model, provider, p50/p90 response time, sample size, and most common error. A Pareto-efficient model is one for which no other model in the selected cohort is both more accurate and less expensive. That is a two-metric efficiency boundary, not a universal winner list.

[INSERT ACCURACY / COST SCREENSHOT]

## Response time

The source provides end-to-end p50 and p90 response times. P50 is the median; p90 describes a slower part of the observed response distribution. The source does not report time-to-first-token or output tokens per second, so the dashboard does not infer those quantities.

## Results and observations

The committed source run is dated 2026-10-10. In the default English invoice cohort with all document formats, 14 models were evaluated on 150 cases each. Two models tied at 100% correct fields and 100% error-free documents: Claude Haiku 5.5 and Claude Sonnet 5.5. Among models marked as passing ModelVerdict's source bar, Gemma 4 31B had the lowest cost at $0.1675 per 1,000 documents, with 97.64% correct fields. The cost/accuracy Pareto frontier contained Gemma 4 31B, GPT-6 Luna, and Claude Haiku 5.5.

Across those 14 models, median p50 response time was 3,488.5 ms and median p90 was 5,446.5 ms. The frontier shows the trade-off directly: Gemma 4 31B had lower cost but slower response (p50 8.869 s); GPT-6 Luna and Claude Haiku 5.5 were faster (p50 3.435 s and 3.393 s) at higher cost. These observations describe one published run and one task/language/format cohort; they should not be generalized to other prompts or business documents.
## Automation and deployment

GitHub Actions runs CI on pushes and pull requests. A separate daily workflow checks the public JSON source and commits the snapshot only when the source run changes. Docker Compose offers a repeatable local launch. Streamlit Community Cloud can deploy `app.py` from the public GitHub repository.

[INSERT GITHUB ACTIONS SCREENSHOT]
[INSERT LIVE DASHBOARD SCREENSHOT]

## Lessons learned

- A metric needs a clearly described task and unit.
- Scores from different task, language, and format cohorts should not be compared as if they were the same test.
- Data rights are part of source selection, especially when the dashboard and snapshot will be public.
- A Pareto frontier helps explain trade-offs; it does not replace task-specific validation.

## Links

- GitHub repository: https://github.com/iovargasjeff/ModelScope-AI
- Live dashboard: https://modelscope-ai.streamlit.app/
- Data and methodology: [ModelVerdict open data](https://modelverdict.ai/en/data/) · [methodology](https://modelverdict.ai/en/methodology/)
- Article draft: https://github.com/iovargasjeff/ModelScope-AI/blob/main/articles/technical_article_draft.md
- Video script: https://github.com/iovargasjeff/ModelScope-AI/blob/main/articles/video_script.md

## Attribution

Data from [ModelVerdict](https://modelverdict.ai), licensed under CC BY 4.0. This article and dashboard are independent analyses and are not endorsed by ModelVerdict.
