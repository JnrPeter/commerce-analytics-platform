# Commerce Analytics Platform

An end-to-end analytics engineering project that simulates a multi-category e-commerce marketplace and processes it through a production-grade data pipeline: from transactional source data to SCD-tracked dimensions and analytics-ready fact tables, orchestrated daily with Airflow and tested on every pull request.

```
PostgreSQL  -->  dlt  -->  DuckDB  -->  dbt  -->  Marts
  (source)    (ingest)   (warehouse)  (transform)  (analytics)
```

## What This Project Demonstrates

- **Incremental ingestion** with dlt (merge strategy, high-water mark cursors, schema contracts)
- **Layered dbt transformations** following staging > intermediate > marts conventions
- **SCD Type 2 tracking** on retailers (zone moves, status changes) and products (price history) via dbt snapshots
- **Incremental fact tables** that grow without full rebuilds, alongside aggregated summary tables that do
- **Data quality at three layers**: dlt schema contracts at ingestion, dbt tests + dbt_expectations at transformation, Elementary anomaly detection at observability
- **Airflow orchestration** with a 5-task DAG running daily on LocalExecutor + Postgres backend
- **CI/CD** via GitHub Actions: every PR runs the full pipeline from scratch in a clean environment

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Source Layer                              │
│  PostgreSQL 16 (Docker, port 5433)                              │
│  generate.py (seed) + mutate.py (daily changes)                 │
│  5 tables: customers, retailers, products, orders, order_items  │
└──────────────────────────┬──────────────────────────────────────┘
                           │  dlt (incremental merge)
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                      DuckDB Warehouse                           │
│                                                                 │
│  raw          dlt-owned tables (source mirror)                  │
│  staging      dbt views (cleaned, renamed, retyped)             │
│  snapshots    dbt snapshots (SCD versioning)                    │
│  marts        dimensions + facts (what analysts query)          │
└──────────────────────────┬──────────────────────────────────────┘
                           │  Airflow (daily @ midnight UTC)
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│  mutate > ingest > dbt snapshot > dbt build > edr report        │
└─────────────────────────────────────────────────────────────────┘
```

## Project Structure

```
commerce-analytics-platform/
├── dags/                        # Airflow DAG (symlinked to ~/airflow/dags/)
│   └── commerce_pipeline_dag.py
├── data_generator/
│   ├── config.py                # DB connection, table configs
│   ├── generate.py              # One-time seed: 4k customers, 1k retailers, 20k orders
│   ├── mutate.py                # Daily simulation: 500 orders, zone moves, price changes
│   └── test_integrity.py        # 20+ validation checks on source data
├── ingestion/
│   └── load_to_warehouse.py     # dlt pipeline: Postgres to DuckDB
├── dbt_project/
│   ├── models/
│   │   ├── staging/             # 5 views (1:1 with raw, clean interface)
│   │   ├── intermediate/        # 2 ephemeral models (joins + business logic)
│   │   └── marts/               # 3 dimensions + 5 fact tables
│   ├── snapshots/               # 3 snapshots (retailers, products, customers)
│   ├── seeds/                   # zone_lookup (region + area_type enrichment)
│   ├── tests/                   # Custom test definitions
│   └── macros/
├── .github/workflows/
│   └── dbt_ci.yml               # Full pipeline test on every PR
├── docker-compose.yml           # PostgreSQL 16 container
├── Makefile                     # Common commands
└── requirements.txt
```

## Data Model

### Dimensions

| Table | SCD Type | Tracks |
|-------|----------|--------|
| dim_customers | Type 1 (overwrite) | Latest name, email, tier |
| dim_retailers | Type 2 (history) | Zone moves, status changes, rebrands |
| dim_products | Type 2 (history) | Price changes over time |

### Facts

| Table | Materialization | Key Metrics |
|-------|----------------|-------------|
| fct_orders | Incremental (merge) | subtotal, discount, delivery_fee, total_amount, delivery_performance, rating |
| fct_order_items | Incremental (merge) | quantity, unit_price, line_total, product_category |
| fct_daily_zone_summary | Full rebuild | Revenue, on_time_pct, cancellation_rate per zone per day |
| fct_retailer_performance | Full rebuild | Lifetime revenue, avg_rating, on_time_pct per retailer |
| fct_payment_channel_summary | Full rebuild | Revenue and cancellation_rate per payment_method + channel per day |

### Source Data Profile

| Table | Rows | Daily Mutations |
|-------|------|-----------------|
| customers | 4,000 | 25 tier upgrades, 15 email updates |
| retailers | 1,000 | 8 zone moves, 5 status changes |
| products | 1,000 | 15 price changes (+/- 15%) |
| orders | 20,000+ | 500 new orders per run |
| order_items | ~60,000+ | ~1,500 new items per run |

## Setup

### Prerequisites

- Python 3.12+
- Docker and Docker Compose

### Quick Start

```bash
# Clone the repo
git clone https://github.com/jnrpeter/commerce-analytics-platform.git
cd commerce-analytics-platform

# Start Postgres and install dependencies
docker-compose up -d
pip install -r requirements.txt
cd dbt_project && dbt deps && cd ..

# Generate source data
python data_generator/generate.py

# Run the full pipeline
python ingestion/load_to_warehouse.py
cd dbt_project
dbt seed
dbt snapshot
dbt build
```

### Run the Pipeline with Make

```bash
make setup              # Docker + deps + dbt deps
make generate           # Seed source data
make full-pipeline      # generate > ingest > snapshot > build > test
```

## Airflow Orchestration

The pipeline runs daily via Airflow 3.1.1 with LocalExecutor and a Postgres metadata backend.

### Starting Airflow

```bash
# Start Postgres container first
cd ~/commerce-analytics-platform && docker-compose up -d

# Activate Airflow venv and start services
source ~/airflow/airflow_venv/bin/activate
airflow api-server -p 8080 -D && airflow scheduler

# UI at http://localhost:8080
```

### DAG: commerce_analytics_pipeline

```
mutate_source_data > ingest_to_warehouse > dbt_snapshot > dbt_build > elementary_report
```

All 5 tasks use BashOperator. The DAG file is symlinked from `dags/commerce_pipeline_dag.py` to `~/airflow/dags/`.

## CI/CD

Every pull request to `main` triggers a GitHub Actions workflow that builds the entire pipeline from scratch in a clean environment:

1. Spins up a fresh Postgres 16 container
2. Generates source data (4,000 customers, 1,000 retailers, 20,000 orders)
3. Runs dlt ingestion into a fresh DuckDB
4. Executes dbt seed, snapshot, build (with all tests), and docs generation
5. Fails the PR on any error

The workflow only triggers when files in `dbt_project/` change.

## Data Quality

Three layers of defense:

| Layer | Tool | What It Catches |
|-------|------|-----------------|
| Ingestion | dlt schema contract | Upstream schema drift (new/changed columns block the load) |
| Transformation | dbt tests + dbt_expectations | Uniqueness, nulls, accepted values, range checks |
| Observability | Elementary | Volume anomalies, freshness gaps, schema changes (learned from history) |

## Tech Stack

| Layer | Tool |
|-------|------|
| Source database | PostgreSQL 16 (Docker) |
| Data generation | Python (Faker) |
| Ingestion | dlt |
| Warehouse | DuckDB |
| Transformation | dbt (dbt-duckdb) |
| Data quality | dbt tests, dbt_expectations, Elementary |
| Orchestration | Airflow 3.1.1 (LocalExecutor + Postgres) |
| CI/CD | GitHub Actions |

## Key Design Decisions

**Why DuckDB?** Fast, embedded, zero infrastructure. Ideal for a project that runs on a single machine. The dbt models are SQL-standard and portable to Snowflake or BigQuery.

**Why dlt over custom Python?** 40 lines replace hundreds of boilerplate (connection handling, schema creation, type mapping, state tracking). Same idea as dbt replacing raw SQL.

**Why snapshots before build?** Snapshots capture row versions before dbt overwrites dimensions. dim_retailers and dim_products read from snapshots to build SCD Type 2 history. Skipping the snapshot step means new zone moves and price changes are invisible to the marts.

**Why incremental + full rebuild facts?** Row-level facts (fct_orders, fct_order_items) grow over time and benefit from incremental merge. Aggregated facts (zone summary, retailer performance) are cheap to rebuild and need to reflect status changes in older orders.