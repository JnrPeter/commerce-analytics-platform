# Commerce Analytics Platform

A production-grade analytics engineering project built on realistic e-commerce data. The pipeline ingests operational data from a PostgreSQL source, models it through a layered dbt project with slowly changing dimensions, incremental loads, data quality checks, a semantic layer, and CI/CD — orchestrated end-to-end with Airflow.

## Architecture

```
PostgreSQL (operational source)
    │
    ▼
dlt (ingestion)
    │
    ▼
Snowflake / DuckDB (warehouse)
    │
    ▼
dbt (staging → intermediate → marts)
    │   ├── SCD Type 2 (dim_retailers via snapshots)
    │   ├── SCD Type 1 (dim_customers)
    │   ├── Incremental fact tables
    │   ├── Data quality (dbt tests + Elementary)
    │   └── Semantic layer (dbt metrics)
    │
    ▼
Airflow + Cosmos (orchestration)
GitHub Actions (CI/CD)
```

## Stack

| Component | Tool |
|-----------|------|
| Source database | PostgreSQL |
| Ingestion | dlt |
| Warehouse | Snowflake (or DuckDB for local dev) |
| Transformation | dbt |
| Data quality | dbt tests, dbt_expectations, Elementary |
| Orchestration | Airflow + astronomer-cosmos |
| CI/CD | GitHub Actions |
| Containerization | Docker |

## Project Structure

```
commerce-analytics-platform/
├── .github/workflows/       # CI/CD pipeline
├── data_generator/          # Python scripts to generate and mutate source data
├── ingestion/               # dlt pipeline: Postgres → warehouse
├── dbt_project/             # Full dbt project (staging, intermediate, marts, snapshots)
├── dags/                    # Airflow DAG with Cosmos integration
├── docker-compose.yml       # Local infrastructure (Postgres)
├── Makefile                 # Shortcuts for common tasks
├── requirements.txt         # Python dependencies
└── README.md
```

## Quick Start

```bash
# 1. Clone the repo
git clone https://github.com/your-username/commerce-analytics-platform.git
cd commerce-analytics-platform

# 2. Start local infrastructure
docker-compose up -d

# 3. Install dependencies
pip install -r requirements.txt

# 4. Generate seed data
make generate

# 5. Ingest to warehouse
make ingest

# 6. Run dbt
make dbt-run

# 7. Run the full pipeline
make full-pipeline
```

## Data Model

### Source Tables
- `orders` — one row per order
- `order_items` — one row per line item
- `customers` — customer profiles (mutated over time)
- `retailers` — retailer profiles (zone changes, status changes tracked via SCD2)
- `products` — product catalog

### Warehouse Layers
- **Staging** — 1:1 with source, cleaned and typed
- **Intermediate** — enriched joins (orders + customer + retailer context)
- **Marts** — star schema with dimensions (SCD1 + SCD2) and incremental facts

## Key Features

- **SCD Type 2** on retailers dimension (tracks zone reassignments, status changes over time)
- **SCD Type 1** on customers dimension (latest state only)
- **Incremental models** on fact tables (merge strategy on updated_at)
- **Three-layer data quality**: dbt generic tests, dbt_expectations, Elementary anomaly detection
- **Semantic layer**: dbt metrics for revenue, AOV, active retailers
- **CI/CD**: GitHub Actions runs dbt build + test on every pull request
- **Orchestration**: Airflow DAG with Cosmos rendering each dbt model as a task

## License

MIT
