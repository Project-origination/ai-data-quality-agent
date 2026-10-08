# AI Data Quality Agent

**Data quality observability, explainable controls, and local LLM-assisted remediation.**

AI Data Quality Agent is a Python application that profiles CSV and Excel datasets, detects quality issues through deterministic rules, evaluates five quality dimensions, and translates the findings into actionable business recommendations using a **locally hosted Qwen3 4B model**.

Its guiding principle is simple: **Python determines what is wrong; the LLM helps explain why it matters and what to investigate next.** 

![Data Quality Observatory dashboard](screenshots/Data%20quality%20agent%201.JPG)

## Features

- **CSV / XLSX ingestion**, with a synthetic demo dataset for immediate exploration.
- **Rule-based checks** for missing values, duplicate customer identifiers, malformed email addresses, invalid age values, and unexpected country values.
- **Statistical outlier detection** for revenue using the interquartile range (IQR) method. Outliers are signals for investigation, not automatically confirmed errors.
- **Five-dimensional quality scoring:** Completeness, Uniqueness, Validity, Consistency, and Statistical Health.
- **Interactive Plotly dashboard:** overall score, severity distribution, radar chart, dimension comparison, risk matrix, and issue prioritization.
- **Local AI Advisor:** business-oriented executive summary, priority actions, business impact, and suggested remediation via Qwen3 4B running in LM Studio.
- **On-demand inference:** the AI runs only when the user selects **Generate AI Analysis**.
- **Dataset-aware results:** previous AI recommendations are cleared when the dataset changes.
- **Markdown report export** including the quality findings and, when generated, the AI assessment.

## Screenshots

### Quality dimensions and severity distribution

![Quality score, severity distribution, and dimension charts](screenshots/Data%20quality%20agent%202.JPG)

### Data quality control matrix

![Quality control matrix and prioritized risks](screenshots/Data%20quality%20agent%203.JPG)

### Local AI Advisor

![Qwen-powered remediation guidance](screenshots/Data%20quality%20agent%20%206.JPG)

### Report export

![Markdown report download](screenshots/Data%20quality%20agent%20%207.JPG)

Additional views: [Dataset preview and control architecture](screenshots/Data%20quality%20agent%204.JPG) · [Detailed quality findings](screenshots/Data%20quality%20agent%205.JPG)

## How it works

```text
CSV / XLSX / demo dataset
          |
          v
  Pandas data ingestion
          |
          v
  Deterministic controls + IQR outlier detection
          |
          v
  Severity-weighted quality assessment
          |
          +-----------------------------+
          |                             |
          v                             v
  Streamlit + Plotly             Structured findings
  dashboard                      (no full raw dataset)
          |                             |
          |                             v
          |                      OpenAI-compatible SDK
          |                             |
          |                             v
          |                      LM Studio local API
          |                             |
          |                             v
          |                         Qwen3 4B
          |                             |
          +--------------+--------------+
                         |
                         v
                Markdown report export
```

The application uses the **OpenAI Python SDK as an API client**, pointed at LM Studio's local OpenAI-compatible endpoint (`http://127.0.0.1:1234/v1`). **It does not require an OpenAI API key or paid OpenAI inference.**

### Quality scoring

The prototype evaluates these five dimensions:

| Dimension | Weight | Example check |
| --- | ---: | --- |
| Completeness | 15% | Missing values |
| Uniqueness | 30% | Duplicate `customer_id` values |
| Validity | 30% | Email format and permitted age range |
| Consistency | 10% | Country values outside the configured list |
| Statistical Health | 15% | Revenue IQR outliers |

Issue severity and affected record counts influence the scores. The overall score is a weighted combination of the evaluated dimensions. **These weights and thresholds are prototype design choices, not an industry-certified scoring standard.**

## Tech stack

| Component | Technology |
| --- | --- |
| Application UI | Streamlit |
| Data processing and rules | Python, pandas |
| Interactive visualizations | Plotly |
| Excel support | openpyxl |
| Local LLM | Qwen3 4B |
| Local model serving | LM Studio |
| LLM API client | OpenAI Python SDK (local endpoint) |
| Export | Markdown |

## Getting started

### Prerequisites

- Python and a terminal (examples below use PowerShell on Windows).
- LM Studio with a locally available `qwen/qwen3-4b-2507` model for optional AI recommendations.

### 1. Create an environment and install dependencies

Run these commands **from the project root**:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

If the demo CSV is not present, generate it with:

```powershell
python create_sample_data.py
```

### 2. Start local inference (optional)

In **LM Studio**:

1. Load `qwen/qwen3-4b-2507`.
2. Open **Developer / Local Server** and start the server on port **1234**.
3. Keep LM Studio running while using the AI Advisor.

Without LM Studio, the deterministic checks, charts, and quality report remain usable; AI-generated recommendations are unavailable.

### 3. Launch the dashboard

```powershell
python -m streamlit run app.py
```

Select **Load demo dataset** or upload a `.csv` / `.xlsx` file. Review the detected issues, then select **Generate AI Analysis** if the local model is running. Use **Download Quality Report** to export the results.

## Project structure

```text
ai-data-quality-agent/
├── app.py                 # Streamlit dashboard and interactions
├── data_quality.py        # Rule-based detection and quality scoring
├── ai_advisor.py          # Context preparation and local LLM integration
├── report_export.py       # Markdown report generation
├── create_sample_data.py # Reproducible synthetic demo dataset
├── requirements.txt
├── data/
│   └── customers_dirty.csv
└── screenshots/
    ├── Data quality agent 1.JPG
    ├── Data quality agent 2.JPG
    ├── Data quality agent 3.JPG
    ├── Data quality agent 4.JPG
    ├── Data quality agent 5.JPG
    ├── Data quality agent  6.JPG
    └── Data quality agent  7.JPG
```

## Example use case

A customer data extract contains missing contact information, repeated customer identifiers, unrealistic ages, inconsistent country names, and an unusually large revenue value. The application identifies and prioritizes these findings, then the AI Advisor explains possible consequences for downstream reporting, CRM workflows, and business decisions.

The synthetic demo dataset deliberately includes these problems so the workflow can be explored without access to private customer data.

## Scope and limitations

- Rules currently focus on a **customer-data example** and expected column names; arbitrary datasets may not support every check.
- The email check is based on a simplified pattern, **not comprehensive RFC-compliant email validation**.
- The configured country list is intentionally limited for the demo; it is **not a complete country reference dataset**.
- IQR outliers can be valid observations and should be reviewed by a human.
- The score is a **transparent heuristic**, not an externally validated quality benchmark.
- LLM recommendations can be incomplete or inaccurate. **No automatic data modification, production ETL repair, or regulatory compliance certification is provided.**
- AI generation requires the locally running model and sufficient hardware resources.

## Why this project?

This portfolio project demonstrates how **data quality engineering, analytical visualization, data governance thinking, and generative AI** can work together without giving the LLM responsibility for factual validation. It is designed as a compact, explainable prototype rather than a full enterprise data governance platform.

---

**Built with Python, Streamlit, Plotly, pandas, LM Studio, and Qwen3 4B.**
