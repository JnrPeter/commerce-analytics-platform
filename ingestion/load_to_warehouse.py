"""
dlt pipeline: PostgreSQL (source) -> Snowflake or DuckDB (warehouse).
Extracts all five source tables and loads them into a raw schema.
Uses merge write disposition for incremental loads after the first run.
"""

import os

import dlt
from dlt.sources.sql_database import sql_database
from dotenv import load_dotenv

load_dotenv()


def build_pipeline():
    """Configure and return the dlt pipeline."""

    # Source: PostgreSQL
    pg_conn = (
        f"postgresql://{os.getenv('PG_USER')}:{os.getenv('PG_PASSWORD')}"
        f"@{os.getenv('PG_HOST')}:{os.getenv('PG_PORT')}/{os.getenv('PG_DATABASE')}"
    )

    source = sql_database(
        credentials=pg_conn,
        table_names=["customers", "retailers", "products", "orders", "order_items"],
    )

    # Destination: Snowflake or DuckDB based on env config
    snowflake_account = os.getenv("SNOWFLAKE_ACCOUNT", "")

    if snowflake_account:
        destination = "snowflake"
        dataset_name = os.getenv("SNOWFLAKE_SCHEMA", "raw")
    else:
        destination = "duckdb"
        dataset_name = "raw"

    pipeline = dlt.pipeline(
        pipeline_name="commerce_ingestion",
        destination=destination,
        dataset_name=dataset_name,
    )

    return pipeline, source


def main():
    pipeline, source = build_pipeline()

    print(f"Loading to {pipeline.destination.destination_name}...")
    info = pipeline.run(source, write_disposition="replace")
    print(info)
    print("Ingestion complete.")


if __name__ == "__main__":
    main()
