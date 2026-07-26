from datetime import datetime, timedelta
from airflow import DAG
from airflow.providers.google.cloud.transfers.local_to_gcs import LocalFilesystemToGCSOperator
from airflow.providers.google.cloud.transfers.gcs_to_bigquery import GCSToBigQueryOperator

from config import (
    table_schema, DATA_SOURCE_PATH,GCS_BUCKET_NAME,
    GCS_FILE_NAME,PROJECT_ID
)

default_args = {
    "owner" : "nosa",
    "depends_on_past": False,
    "start_date": datetime(2026, 7, 23),
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

with DAG (
    dag_id="gcs_by",
    schedule= "@hourly",
    catchup=False,
    default_args=default_args
) as dags:

    #Task 1 : Upload local desktop file to GCS
    upload_to_gcs = LocalFilesystemToGCSOperator(
        task_id="upload_local_file_to_gcs",
        src=DATA_SOURCE_PATH,
        dst=GCS_FILE_NAME,
        bucket=GCS_BUCKET_NAME,
    )

        # Task 2: Load CSV file from GCS into BigQuery
    load_gcs_to_bigquery = GCSToBigQueryOperator(
        task_id="load_gcs_to_bigquery",
        bucket=GCS_BUCKET_NAME,
        source_objects=[GCS_FILE_NAME],
        destination_project_dataset_table=f"{PROJECT_ID}.naija_cart_dataset.naija_market_place",
        source_format="CSV",
        skip_leading_rows=1, # Skips the CSV header row
        write_disposition="WRITE_TRUNCATE", # Overwrites the table; use WRITE_APPEND to accumulate
        autodetect=True
    )

    # Task Dependencies
    (
        upload_to_gcs >> load_gcs_to_bigquery
    )