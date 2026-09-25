"""
Commerce Analytics Pipeline DAG

Schedule: Daily
Flow: generate_new_data -> ingest_to_warehouse -> dbt_snapshot -> dbt_build -> elementary_report

Non-dbt steps use BashOperator.
dbt build step uses astronomer-cosmos to render each dbt model as its own Airflow task.
"""

from datetime import datetime
from pathlib import Path

from airflow import DAG
from airflow.operators.bash import BashOperator

from cosmos import DbtTaskGroup, ProjectConfig, ProfileConfig, RenderConfig

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DBT_PROJECT_PATH = PROJECT_ROOT / "dbt_project"

default_args = {
    "owner": "analytics_engineering",
    "retries": 1,
}

with DAG(
    dag_id="commerce_analytics_pipeline",
    default_args=default_args,
    description="Full e-commerce analytics pipeline: generate, ingest, snapshot, build, test",
    schedule="@daily",
    start_date=datetime(2026, 1, 1),
    catchup=False,
    tags=["commerce", "dbt", "analytics"],
) as dag:

    generate_data = BashOperator(
        task_id="generate_new_data",
        bash_command=f"cd {PROJECT_ROOT}/data_generator && python mutate.py",
    )

    ingest = BashOperator(
        task_id="ingest_to_warehouse",
        bash_command=f"cd {PROJECT_ROOT}/ingestion && python load_to_warehouse.py",
    )

    dbt_snapshot = BashOperator(
        task_id="dbt_snapshot",
        bash_command=f"cd {DBT_PROJECT_PATH} && dbt snapshot",
    )

    dbt_build = DbtTaskGroup(
        group_id="dbt_build",
        project_config=ProjectConfig(str(DBT_PROJECT_PATH)),
        profile_config=ProfileConfig(
            profile_name="commerce",
            target_name="dev",
        ),
        render_config=RenderConfig(
            select=["path:models"],
        ),
    )

    elementary_report = BashOperator(
        task_id="elementary_report",
        bash_command=f"cd {DBT_PROJECT_PATH} && edr report",
    )

    generate_data >> ingest >> dbt_snapshot >> dbt_build >> elementary_report
