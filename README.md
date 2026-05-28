# Job Market Data Pipeline

An automated data engineering pipeline that scrapes, merges, cleans, validates, and analyzes remote/AI/ML job listings from multiple public APIs. Built with **Apache Airflow**, **KNIME**, and **n8n**.

## Pipeline Overview

```
[Arbeitnow API] ──┐
[RemoteOK API]  ──┤
[Himalayas API] ──┤──> Merge ──> KNIME Clean ──> Patch ──> Validate ──> Metrics ──> n8n Notify ──> Archive
[RemoteJobs API] ─┘
```

| Stage | Tool | Description |
|---|---|---|
| **Extract** | Python / `requests` | 4 parallel scrapers fetching jobs from Arbeitnow, RemoteOK, Himalayas, RemoteJobs.org |
| **Merge** | Python / `pandas` | Standardizes schemas, deduplicates, normalizes remote status & job type |
| **Clean** | KNIME | Visual workflow to filter AI/ML jobs, clean fields, categorize experience brackets |
| **Patch** | Python | Converts salaries to USD, extracts skills from job descriptions |
| **Validate** | Python | Schema checks, missing value analysis, remote status & experience bracket validation |
| **Metrics** | Python | Computes total jobs, source breakdown, remote ratio, avg salary, entry-level count |
| **Notify** | n8n | Sends webhook-triggered automation (email/Slack) with metrics summary |
| **Archive** | Bash | Placeholder for output archival |

## Tech Stack

- **Apache Airflow 2.9.1** — Workflow orchestration (CeleryExecutor)
- **KNIME** — Visual data cleaning and transformation
- **n8n** — Automation and notification workflows
- **Python 3.12** — Extraction, transformation, validation, and metrics scripts
- **PostgreSQL 13** — Airflow metadata database
- **Redis** — Celery message broker
- **Docker Compose** — Container orchestration

## Project Structure

```
job_market_project/
├── dags/
│   └── job_market_pipeline.py      # Airflow DAG definition
├── scripts/
│   ├── extract_arbeitnow.py        # Arbeitnow API scraper
│   ├── extract_remoteok.py         # RemoteOK API scraper
│   ├── extract_himalayas.py        # Himalayas API scraper
│   ├── extract_remotejobs.py       # RemoteJobs.org API scraper
│   ├── merge_sources.py            # Merge & standardize all sources
│   ├── patch_knime_output.py       # USD salary conversion & skill extraction
│   ├── validate_outputs.py         # Data quality validation checks
│   └── calculate_metrics.py        # Business metrics computation
├── knime_workflow/
│   └── job_market_cleaning.knwf    # KNIME cleaning workflow
├── data/
│   ├── raw/                        # Raw extracted CSVs (4 sources)
│   ├── merged/                     # Deduplicated merged dataset
│   └── processed/                  # Final cleaned & patched output
├── config/                         # Airflow config overrides
├── plugins/                        # Airflow custom plugins
├── screenshots/                    # UI screenshots (Airflow, KNIME, n8n)
├── docker-compose.yaml             # Docker services configuration
├── .env                            # Environment variables
└── requirements.txt                # Python dependencies
```

## Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) (with WSL2 backend on Windows)
- [KNIME Analytics Platform](https://www.knime.com/downloads) (installed at default path)

## Quick Start

### 1. Clone and configure

```bash
cd job_market_project
```

### 2. Start Airflow services

```bash
docker compose up -d
```

This starts: PostgreSQL, Redis, Airflow webserver (port 8080), scheduler, worker, and n8n (port 5678).

### 3. Access Airflow UI

Open [http://localhost:8080](http://localhost:8080) — credentials: `airflow` / `airflow`

### 4. Run the pipeline

From the Airflow UI, unpause the `job_market_pipeline` DAG and trigger a manual run.

### 5. View results

Outputs are saved in the `data/` directory:
- `data/merged/merged_raw_jobs.csv` — Merged job listings
- `data/processed/clean_ai_ml_data_jobs.csv` — Final cleaned dataset
- `data/processed/metrics_summary.json` — Computed metrics payload

## Running Scripts Individually

Each script can be run standalone from the project root:

```bash
python scripts/extract_arbeitnow.py
python scripts/merge_sources.py
python scripts/validate_outputs.py
python scripts/calculate_metrics.py
```

## KNIME Workflow

The KNIME workflow (`knime_workflow/job_market_cleaning.knwf`) performs:
- Column selection and type casting
- AI/ML job filtering by title keywords
- HTML tag removal from descriptions
- Experience bracket categorization (0-1, 1-3, 3-5, 5-8, 8+ years)
- Job category standardization

On Windows, KNIME can be invoked from the DAG via:
```
"C:\Program Files\KNIME\knime.exe" -nosplash -application org.knime.product.KNIME_BATCH_APPLICATION -workflowFile="<path-to-workflow>"
```

## Notes

- The pipeline is designed for **Windows** (KNIME path, volume mounts). Adjust accordingly for Linux/macOS.
- API rate limits apply — the Himalayas scraper includes a 1-second delay between requests.
- Currency conversion rates (EUR, GBP, PKR → USD) are hardcoded and may need updating.
- n8n webhook endpoint: `http://localhost:5678/webhook/job-market-trigger` (create the workflow in n8n UI).
