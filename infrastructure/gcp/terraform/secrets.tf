resource "random_password" "application_secret" {
  length  = 64
  special = false
}

resource "google_secret_manager_secret" "database_url" {
  secret_id = "workboard-database-url"
  labels    = var.labels

  replication {
    auto {}
  }

  depends_on = [google_project_service.required["secretmanager.googleapis.com"]]
}

resource "google_secret_manager_secret_version" "database_url" {
  secret      = google_secret_manager_secret.database_url.id
  secret_data = format(
    "postgresql+psycopg://%s:%s@/%s?host=/cloudsql/%s",
    var.database_user,
    urlencode(random_password.database.result),
    var.database_name,
    google_sql_database_instance.postgres.connection_name,
  )
}

resource "google_secret_manager_secret" "application_secret" {
  secret_id = "workboard-secret-key"
  labels    = var.labels

  replication {
    auto {}
  }

  depends_on = [google_project_service.required["secretmanager.googleapis.com"]]
}

resource "google_secret_manager_secret_version" "application_secret" {
  secret      = google_secret_manager_secret.application_secret.id
  secret_data = random_password.application_secret.result
}
