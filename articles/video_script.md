# ModelScope AI — video script (4:55 max)

## 0:00–0:25 — Problem

“Choosing a model is not just about a general ranking. For a specific business task, we need to see the accuracy, the actual cost, and how long a response takes. This is ModelScope AI, a dashboard for exploring those trade-offs.”

## 0:25–0:55 — Source

“The dashboard uses ModelVerdict's published results under CC BY 4.0. The data covers six business-document workflows. These are task-specific scores, not a universal measure of model intelligence. We retain the source credit and keep each comparison inside one task, language, and format.”

## 0:55–1:25 — Architecture

“GitHub Actions downloads the JSON, checks the license and schema, then writes a normalized CSV and metadata. If a download is empty or invalid, the last good snapshot remains. Docker runs the same app locally, and pytest checks data cleaning and metric calculations.”

## 1:25–2:00 — Filters and KPIs

“Here I choose the task, language, and document format. Then I can narrow by provider, model, accuracy, cost, and response time. The cards update from the selected cohort and show the model and provider counts, median cost per 1,000 documents, and median response time.”

## 2:00–2:55 — Main analysis and Pareto frontier

“This is the main accuracy-versus-cost chart. Hovering shows the model, provider, latency, sample size, and common error. Stars mark the Pareto-efficient models in this cohort: no other model is both more accurate and cheaper. That highlights trade-offs, not a universal winner.”

## 2:55–3:25 — Response time

“The source reports end-to-end p50 and p90 response time. P50 is the typical median, while p90 shows a slower tail. It does not report time-to-first-token or tokens per second, so the dashboard stays with the available measurements.”

## 3:25–3:55 — Providers and model comparison

“The provider section uses medians to reduce the effect of outliers. I can select two to four models and compare their accuracy, cost, response time, valid JSON rate, and evaluation sample size.”

## 3:55–4:25 — GitHub and Docker

“CI runs Ruff and pytest on code changes. The data workflow checks daily but only commits a new snapshot when ModelVerdict publishes a new run. Docker Compose provides a reproducible local launch.”

## 4:25–4:55 — Deployment and conclusion

“The repository is prepared for Streamlit Community Cloud, which can track the main branch. The main takeaway is to compare models within the same task and input conditions, then choose based on the trade-off that matters for your use case. The dashboard credits ModelVerdict and documents the limits of the benchmark.”

**Target runtime:** approximately 4 minutes 45 seconds at a measured speaking pace. Trim one chart interaction if rehearsal exceeds 5:00.
