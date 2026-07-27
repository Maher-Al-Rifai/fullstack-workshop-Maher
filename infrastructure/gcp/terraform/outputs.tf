output "artifact_repository" {
  value       = google_artifact_registry_repository.containers.repository_id
  description = "GitHub variable GCP_ARTIFACT_REPOSITORY"
}

output "cloud_sql_connection_name" {
  value       = google_sql_database_instance.postgres.connection_name
  description = "GitHub variable GCP_CLOUD_SQL_CONNECTION_NAME"
}

output "runtime_service_account" {
  value       = google_service_account.runtime.email
  description = "GitHub variable GCP_RUNTIME_SERVICE_ACCOUNT"
}

output "deploy_service_account" {
  value       = google_service_account.deployer.email
  description = "GitHub variable GCP_DEPLOY_SERVICE_ACCOUNT"
}

output "workload_identity_provider" {
  value       = google_iam_workload_identity_pool_provider.github.name
  description = "GitHub variable GCP_WORKLOAD_IDENTITY_PROVIDER"
}

output "region" {
  value       = var.region
  description = "GitHub variable GCP_REGION"
}

output "project_id" {
  value       = var.project_id
  description = "GitHub variable GCP_PROJECT_ID"
}

output "github_variable_commands" {
  description = "Run from an authenticated GitHub CLI in the repository."
  value       = <<-EOT
    gh variable set GCP_PROJECT_ID --body '${var.project_id}'
    gh variable set GCP_REGION --body '${var.region}'
    gh variable set GCP_ARTIFACT_REPOSITORY --body '${google_artifact_registry_repository.containers.repository_id}'
    gh variable set GCP_CLOUD_SQL_CONNECTION_NAME --body '${google_sql_database_instance.postgres.connection_name}'
    gh variable set GCP_RUNTIME_SERVICE_ACCOUNT --body '${google_service_account.runtime.email}'
    gh variable set GCP_DEPLOY_SERVICE_ACCOUNT --body '${google_service_account.deployer.email}'
    gh variable set GCP_WORKLOAD_IDENTITY_PROVIDER --body '${google_iam_workload_identity_pool_provider.github.name}'
  EOT
}
