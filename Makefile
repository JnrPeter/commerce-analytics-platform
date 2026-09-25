.PHONY: setup generate mutate ingest dbt-deps dbt-snapshot dbt-run dbt-test dbt-docs full-pipeline clean

# ── Infrastructure ──────────────────────────────────────────
setup:
	docker-compose up -d
	pip install -r requirements.txt
	cd dbt_project && dbt deps

# ── Data Generation ─────────────────────────────────────────
generate:
	python data_generator/generate.py

mutate:
	python data_generator/mutate.py

# ── Ingestion ───────────────────────────────────────────────
ingest:
	python ingestion/load_to_warehouse.py

# ── dbt ─────────────────────────────────────────────────────
dbt-deps:
	cd dbt_project && dbt deps

dbt-snapshot:
	cd dbt_project && dbt snapshot

dbt-run:
	cd dbt_project && dbt build

dbt-test:
	cd dbt_project && dbt test

dbt-docs:
	cd dbt_project && dbt docs generate && dbt docs serve

# ── Full Pipeline ───────────────────────────────────────────
full-pipeline: generate ingest dbt-snapshot dbt-run dbt-test
	@echo "Pipeline complete."

# ── Cleanup ─────────────────────────────────────────────────
clean:
	docker-compose down -v
