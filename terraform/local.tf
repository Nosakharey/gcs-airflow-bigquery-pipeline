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