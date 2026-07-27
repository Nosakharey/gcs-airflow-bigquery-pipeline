# Project Walkthrough

## Project

Building a pipeline to transfer data using this tech stack:

- **Terraform** — IaC tool, used to create a bucket, dataset, and table
- **Linux** — used to create files and folders, makes life easier
- **Airflow** — orchestration tool, used to transfer the data from my home directory to the bucket, then to BigQuery
- **BigQuery** — cloud storage system for real-time analysis
- **GCS bucket** — Google's designated cloud storage device, connected to BigQuery
- **Laptop folder** — this is where my data lives

---

## Step One — Project Setup

The file path of my working folder: `/This PC/C drive/Users/godwi/Documents`

The working files are B2B marketplace data — these files contain every attribute and data point a growing B2B marketplace company should track.

The name of my project folder is `gcs_airflow_project`. The name reflects what the project is really about: understanding how to implement Airflow as an orchestration tool in the data engineering field.

---

## Step Two — Terraform (IaC Tool)

Terraform is my Infrastructure as Code (IaC) tool. The Terraform setup for this project contains three files:

- `main.tf`
- `variable.tf`
- `local.tf`

**`main.tf`** contains the provider and resource blocks used for this project. The provider is Google Cloud Platform, which then comprises the different resources used in the project:

- Creation of the GCS bucket
- Creation of the BigQuery dataset
- Creation of the BigQuery table, referencing that dataset

**`variable.tf`** contains reusable values referenced throughout `main.tf`.

**`local.tf`** — this was actually my first time using this. It holds reusable schema definitions pointed at the table creation resource. Instead of writing the schema directly inside `main.tf` and making that file cluttered and harder to read, I moved it into `local.tf` and referenced it back in `main.tf`.

Example:

```hcl
# the table schema
locals {
  table_schema = [
    { name = "user_id", type = "STRING", mode = "NULLABLE" },
    { name = "pharmacy_name", type = "STRING", mode = "NULLABLE" },
    { name = "owner_name", type = "STRING", mode = "NULLABLE" },
    { name = "phone", type = "STRING", mode = "NULLABLE" },
    { name = "email", type = "STRING", mode = "NULLABLE" },
    { name = "state", type = "STRING", mode = "NULLABLE" },
    { name = "city", type = "STRING", mode = "NULLABLE" },
    { name = "registration_date", type = "DATE", mode = "NULLABLE" },
    { name = "account_status", type = "STRING", mode = "NULLABLE" },
    { name = "pharmacy_license_number", type = "STRING", mode = "NULLABLE" }
  ]
}

# resource block for the BigQuery table
resource "google_bigquery_table" "naija_cart_table" {
  dataset_id = google_bigquery_dataset.naija_cart_dataset.dataset_id
  table_id   = var.bigquery_table_name
  schema     = jsonencode(local.table_schema)
}
```

After writing all the `.tf` files, run:

```bash
terraform init
terraform fmt
terraform plan
terraform apply
```

---

## Step Three — Creating the Airflow Configuration

Using `astro dev init` on the root folder of the project. Just like `terraform init`, `astro dev init` initialises the project by creating the required files Apache Airflow needs.

Airflow runs inside Docker, so it's important to understand that the project runs inside a container, not directly on a fully designated OS — the file paths are different from your home directory.

One of the files created during initialisation is `requirements.txt`. If you want a Python package available inside your Airflow DAGs, listing it in `requirements.txt` is the standard way to add it.

I listed the Apache Airflow Google provider package from PyPI:

```
apache-airflow-providers-google==22.2.2
```

This package gives access to `BigQueryInsertJobOperator`, `BigQueryCreateEmptyTableOperator`, `GCSCreateBucketOperator`, `LocalFilesystemToGCSOperator`, `DataflowCreatePythonJobOperator`, and `DataprocSubmitJobOperator`. The Google provider package adds specialised GCP operators that enable Airflow to interact with GCP — this is what allows the pipeline to transfer data from local storage to GCS and BigQuery using those specialised operators.

Then run:

```bash
astro dev start
```

to start up the project's running container. This produces a website at `localhost:8080`, where you can see Airflow's user interface.

---

## Step Four — Creating the DAG File

DAGs are specific written tasks given to Airflow to perform the required implementation. My DAG consists of tasks written to pull data from my local computer into the GCS bucket, then pull data from the GCS bucket into the BigQuery table created with Terraform.

I created two files under the `dags` folder: `config.py` and `gcs_bq.py`.

- **`gcs_bq.py`** is where the DAG tasks are written.
- **`config.py`** holds reusable values connected to `gcs_bq.py` — things like dataset names, table names, bucket names, etc. This makes the DAG configuration inside `gcs_bq.py` much shorter and easier to read.

Here are the reusable values essential for the project, defined in `config.py`:

```python
DATA_SOURCE_PATH = "/usr/local/airflow/dags/data/users_clean.csv"
GCS_BUCKET_NAME   = "naija_cart_bucket"
GCS_FILE_NAME     = "users.csv"
PROJECT_ID        = "de-project-495521"
table_schema      = "..."
```

Getting the data source file path right is very important. The path doesn't exist on your local computer — it lives inside the Docker container provisioned by Astro. To get the correct file path, you have to go inside the running container and print the full working directory. The process:

```bash
astro dev bash        # now inside the running container
cd data                # navigate to the folder where the data lives
pwd                    # print the working directory to get the full file path
```

That printed path is used as the data source. The rest of the values (bucket name, project ID) come directly from your GCP account.

### The DAG Setup (`gcs_bq.py`)

The DAG file starts with the imported modules required for it to work:

```python
from datetime import datetime, timedelta
from airflow import DAG
from airflow.providers.google.cloud.transfers.local_to_gcs import LocalFilesystemToGCSOperator
from airflow.providers.google.cloud.transfers.gcs_to_bigquery import GCSToBigQueryOperator

from config import (
    table_schema, DATA_SOURCE_PATH, GCS_BUCKET_NAME,
    GCS_FILE_NAME, PROJECT_ID
)
```

That last import is used to reference the original setup from the config file.

Next comes `default_args`. Note that this is defined *outside* the DAG. `default_args` is a Python dictionary used to pass a baseline set of parameters to every task inside the DAG — it stops you from writing the same settings over and over for each individual task.

```python
default_args = {
    "owner": "nosa",
    "depends_on_past": False,
    "start_date": datetime(2026, 7, 23),
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}
```

Now, writing the parameters needed for the DAG setup — I use the `with` statement to define the tasks used in the pipeline:

```python
with DAG(
    dag_id="gcs_bq",
    schedule="@hourly",
    catchup=False,
    default_args=default_args,
) as dag:
```

Under the `with` block, the tasks are defined — the tasks must live inside this block. The first task transports data from the local machine into the GCS bucket:

```python
    # Task 1: Upload local desktop file to GCS
    upload_to_gcs = LocalFilesystemToGCSOperator(
        task_id="upload_local_file_to_gcs",
        src=DATA_SOURCE_PATH,
        dst=GCS_FILE_NAME,
        bucket=GCS_BUCKET_NAME,
    )
```

The reusable variables here come directly from the config file.

```python
    # Task 2: Load CSV file from GCS into BigQuery
    load_gcs_to_bigquery = GCSToBigQueryOperator(
        task_id="load_gcs_to_bigquery",
        bucket=GCS_BUCKET_NAME,
        source_objects=[GCS_FILE_NAME],
        destination_project_dataset_table=f"{PROJECT_ID}.naija_cart_dataset.naija_market_place",
        source_format="CSV",
        skip_leading_rows=1,        # Skips the CSV header row
        write_disposition="WRITE_TRUNCATE",  # Overwrites the table; use WRITE_APPEND to accumulate
        autodetect=True,
    )
```

The second task loads data from the GCS bucket into BigQuery. First the operator is defined — this is the BigQuery operator for transferring files — then the important parameters are added: `task_id`, `bucket`, `source_objects`, and so on.

The task dependencies are the last thing defined in the DAG. This tells Airflow which task runs before the other:

```python
    upload_to_gcs >> load_gcs_to_bigquery
```

---

## Step Five — Connecting Airflow to GCP

The next step is giving Airflow access to GCP. There are two distinct concerns Airflow has to work through before it's fully set up:

- **Authorization ("what")** — what is Airflow actually allowed to do in GCP?
- **Authentication ("who")** — who is asking, and are they permitted?

Per my research, there are **three** ways to connect Airflow to GCP:

### a) Raw Service Account JSON Key on Disk

Download the `.json` key from the service account in GCP, and place the key inside the project directory — for example, in a `/data` folder. Confirm that this `/data` folder, where the key lives, is visible inside the running Astro Airflow container — the path should look something like `/usr/local/airflow/data/gcp_key.json`. To configure this, add the path to Airflow's UI Connections — similar to method (b) below, except here you are not exposing the service account email and project ID directly.

**How it works:** Airflow reads the physical `.json` file stored on disk (e.g. `/usr/local/airflow/include/gcp_key.json`).

**Verification:** Airflow opens the mounted file, extracts the `client_email` and `private_key`, and presents them to GCP. GCP validates the key and confirms: *"You are my-sa@project.iam.gserviceaccount.com."*

**Authorization:** Managed by GCP IAM roles. GCP looks up the IAM permissions assigned to that service account to decide whether it can execute the requested BigQuery or Cloud Storage operations.

### b) Application Default Credentials (ADC) with Impersonation

Generate a local ADC token with:

```bash
gcloud auth application-default login
```

Or, if you've already done this before, go to your local `C:` drive → `AppData` → `gcloud`, where you'll find the credentials token. Copy it into your `/data` folder so Docker knows where it is, then set the credential path in an environment variable. Create and open a `.env` file at the project root, and add:

```
GOOGLE_APPLICATION_CREDENTIALS=/usr/local/airflow/dags/data/application_default_credentials.json
```

**Authentication ("who"):** Driven by `gcloud auth application-default login` on your local machine, creating a local credential token. GCP verifies your personal identity (e.g. `your-email@gmail.com`).

**Authorization ("what"):** Managed in two steps:
1. **Impersonation permission** — GCP IAM checks whether `your-email@gmail.com` has the `Service Account Token Creator` role on `target-sa@project.iam.gserviceaccount.com`. If yes, GCP grants Airflow a temporary, 1-hour OAuth token to act as `target-sa`.
2. **Resource permissions** — GCP checks `target-sa`'s own IAM roles (e.g. `BigQuery Data Editor`) to determine what tasks Airflow can actually execute on storage buckets or tables.

### c) Raw Service Account JSON Pasted Directly into the Airflow UI

Download the service account `.json` key from GCP — one that already has the required IAM permissions (e.g. `BigQuery Admin` or `Storage Admin`). Paste the key directly into the Airflow UI, under `Admin → Connections`, in the **Keyfile JSON** field.

**Authentication ("who"):** You paste the full service account `.json` string directly into the Airflow UI connection box. Airflow extracts the `client_email` and `private_key` from it and sends a signed token to GCP. GCP checks the private key's signature and confirms identity.

**Authorization ("what"):** Managed by GCP IAM roles. Once GCP confirms identity, it checks the roles assigned to that service account (e.g. `roles/bigquery.admin`, `roles/storage.objectAdmin`) to allow or deny tasks like writing to GCS or loading into BigQuery.

---

### The Method Used in This Project

For this project, I relied on **method (b)** for simplicity — it was the most straightforward.

The process:

1. Create the service account with the required permissions.
2. In the Airflow UI, add a new connection. Instead of pasting a raw key file, paste the service account email and project ID into the connection's extra fields:
   ```
   "extra__google_cloud_platform__impersonation_chain": "airflow-gcs-bq-sa@de-project-495521.iam.gserviceaccount.com",
   "extra__google_cloud_platform__project": "de-project-495521"
   ```
3. Click **Save** — this handles the **authorization** side of things.

The next step is authentication — GCP needs to know: *who am I? Am I the owner of this Airflow setup, and do I have authorization to work on this GCP platform?* Before GCP allows entry, I need to prove ownership. This is where copying the ADC file comes in — either by generating fresh `gcloud` login credentials, or manually copying the existing credentials file from the host machine (the file path is shown above).

Once the credentials file is obtained, paste it into the folder where the Airflow container is running — e.g. the `/data` folder. Next, create a `.env` file (an environment variable file) so the file path can be pointed to that credential.

By doing this, Airflow now has approval to reach GCP and perform its tasks. Running:

```bash
astro dev restart
```

makes Airflow pick up the credentials from the `.env` file, present them to Google Cloud, and effectively say: *"Hey, I have your access — allow me in."* Airflow then gets both authentication and authorization to perform the data loading.