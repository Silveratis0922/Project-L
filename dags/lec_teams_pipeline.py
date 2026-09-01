from datetime import datetime

from airflow.providers.standard.operators.bash import BashOperator
from airflow.sdk import DAG

PROJET_DIR = "/opt/airflow/project"

with DAG(
    dag_id="lec_teams_pipeline",
    start_date=datetime(2026, 1, 1),
    schedule="0 3 * * 0",
    catchup=False,
    tags=["lec"],
) as dag:

    extraction = BashOperator(
        task_id="extraction_teams",
        bash_command=f"cd {PROJET_DIR} && python extract_teams.py",
    )

    load_bronze = BashOperator(
        task_id="load_bronze",
        bash_command=f"cd {PROJET_DIR} && python load_bronze.py",
    )

    dbt_run = BashOperator(
        task_id="dbt_run",
        bash_command=f"dbt run --project-dir {PROJET_DIR}/lec_dbt --profiles-dir {PROJET_DIR}/lec_dbt",
    )

    dbt_test = BashOperator(
        task_id="dbt_test",
        bash_command=f"dbt test --project-dir {PROJET_DIR}/lec_dbt --profiles-dir {PROJET_DIR}/lec_dbt",
    )

    extraction >> load_bronze >> dbt_run >> dbt_test