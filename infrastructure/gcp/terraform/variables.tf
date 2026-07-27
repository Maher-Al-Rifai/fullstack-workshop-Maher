variable "project_id" {
  description = "Existing Google Cloud project ID with billing enabled."
  type        = string
}

variable "region" {
  description = "Region for Artifact Registry, Cloud SQL, and Cloud Run deployments."
  type        = string
  default     = "us-central1"
}

variable "github_repository" {
  description = "Exact GitHub repository in owner/name form. OIDC admission is restricted to this repository."
  type        = string
}

variable "artifact_repository" {
  description = "Artifact Registry Docker repository ID."
  type        = string
  default     = "workboard"
}

variable "cloud_sql_instance_name" {
  description = "Cloud SQL instance name."
  type        = string
  default     = "workboard-postgres"
}

variable "database_name" {
  description = "Application database name."
  type        = string
  default     = "workboard"
}

variable "database_user" {
  description = "Application database user."
  type        = string
  default     = "workboard_app"
}

variable "database_tier" {
  description = "Cloud SQL machine tier. The default minimizes training cost, not production risk."
  type        = string
  default     = "db-f1-micro"
}

variable "deletion_protection" {
  description = "Protect Cloud SQL from Terraform deletion. Set true outside disposable training projects."
  type        = bool
  default     = false
}

variable "runtime_service_account_id" {
  description = "Cloud Run runtime service account ID."
  type        = string
  default     = "workboard-runtime"
}

variable "deploy_service_account_id" {
  description = "Service account impersonated by GitHub Actions."
  type        = string
  default     = "workboard-github-deployer"
}

variable "labels" {
  description = "Labels applied to supported resources."
  type        = map(string)
  default     = {
    application = "workboard"
    environment = "training"
    managed_by  = "terraform"
  }
}
