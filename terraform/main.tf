# terraform block
terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "7.35.0"
    }
  }
}

# provider block
provider "google" {
  project = var.project 
  region  = var.region
}

# resource block for bucket
resource "google_storage_bucket" "auto-expire" {
  name          = var.gcs_bucket_name
  location      = var.location
  force_destroy = true
  storage_class = var.storage_class

  uniform_bucket_level_access = true

  versioning {
    enabled = true
  }

  lifecycle_rule {
    condition {
      age = 3
    }
    action {
      type = "Delete"
    }
  }

    lifecycle_rule {
    condition {
      age = 1
    }
    action {
      type = "AbortIncompleteMultipartUpload"
    }
  }
}

# resource block for bigquery 
resource "google_bigquery_dataset" "naija_cart_dataset" {
  dataset_id = var.bigquery_dataset_name
  location   = var.location
}

# resource block for bigquery table
resource "google_bigquery_table" "naija_cart_table" {
  dataset_id = google_bigquery_dataset.naija_cart_dataset.dataset_id
  table_id   = var.bigquery_table_name
  schema     = jsonencode(local.table_schema)
}
