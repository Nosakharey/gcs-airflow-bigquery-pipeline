variable "project" {
  description = "my project id"
  default     = "de-project-495521"
}

variable "region" {
  description = "region location"
  default     = "africa-south1"
}

variable "location" {
  description = "project location"
  default     = "africa-south1"

}
variable "gcs_bucket_name" {
  description = "my storage bucket name"
  default     = "naija_cart_bucket"
}

variable "storage_class" {
  description = "bucket_storage_class"
  default     = "STANDARD"

}

variable "bigquery_dataset_name" {
  description = "my big query dataset name"
  default     = "naija_cart_dataset"
}

variable "bigquery_table_name" {
  description = "my table id"
  default     = "naija_market_place"
}
