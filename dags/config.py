DATA_SOURCE_PATH="/usr/local/airflow/dags/data/users_clean.csv"
GCS_BUCKET_NAME="naija_cart_bucket"
GCS_FILE_NAME="users.csv"
PROJECT_ID="de-project-495521"


table_schema = [
    { "name": "account_status", "type" : "STRING", "mode" : "NULLABLE" },
    { "name": "user_id"," type" : "STRING", "mode" : "NULLABLE" },
    { "name" : "pharmacy_name", "type" : "STRING", "mode" : "NULLABLE" },
    { "name" :"owner_name", "type" : "STRING", "mode" : "NULLABLE" },
    { "name" :"phone", "type" : "STRING", "mode" : "NULLABLE" },
    { "name" : "email", "type" : "STRING", "mode" : "NULLABLE" },
    { "name" :"state", "type" : "STRING", "mode" : "NULLABLE" },
    { "name" : "city", "type" : "STRING", "mode" : "NULLABLE" },
    { "name" : "registration_date", "type" : "DATE", "mode" : "NULLABLE" },
    { "name" : "pharmacy_license_number", "type" : "STRING","mode" : "NULLABLE" }
  ]