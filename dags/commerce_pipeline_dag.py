"""
Commerce Analytics Pipeline DAG

Schedule: Daily
Flow: mutate_data -> ingest_to_warehouse -> dbt_snapshot -> dbt_build -> elementary_report

All steps use BashOperator. Each runs from the project root directory
using the project's Python virtual environment.
"""

from datetime import datetime

from airflow.providers.standard.operators.bash import BashOperator
from airflow import DAG

PROJECT_ROOT = "/home/penning/commerce-analytics-platform"
VENV_ACTIVATE = f"source {PROJECT_ROOT}/venv/bin/activate"
DBT_DIR = f"{PROJECT_ROOT}/dbt_project"

default_args = {
    "owner": "analytics_engineering",
    "retries": 1,
}

with DAG(
    dag_id="commerce_analytics_pipeline",
    default_args=default_args,
    description="Full e-commerce analytics pipeline: mutate, ingest, snapshot, build, test",
    schedule="@daily",
    start_date=datetime(2026, 1, 1),
    catchup=False,
    tags=["commerce", "dbt", "analytics"],
) as dag:

    mutate_data = BashOperator(
        task_id="mutate_source_data",
        bash_command=f"{VENV_ACTIVATE} && cd {PROJECT_ROOT} && python data_generator/mutate.py",
    )

    ingest = BashOperator(
        task_id="ingest_to_warehouse",
        bash_command=f"{VENV_ACTIVATE} && cd {PROJECT_ROOT} && python ingestion/load_to_warehouse.py",
    )

    dbt_snapshot = BashOperator(
        task_id="dbt_snapshot",
        bash_command=f"{VENV_ACTIVATE} && cd {DBT_DIR} && dbt snapshot",
    )

    dbt_build = BashOperator(
        task_id="dbt_build",
        bash_command=f"{VENV_ACTIVATE} && cd {DBT_DIR} && dbt build --fail-fast",
    )

    elementary_report = BashOperator(
        task_id="elementary_report",
        bash_command=f"{VENV_ACTIVATE} && cd {DBT_DIR} && edr report",
    )

    mutate_data >> ingest >> dbt_snapshot >> dbt_build >> elementary_report
