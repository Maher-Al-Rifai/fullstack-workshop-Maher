resource "google_iam_workload_identity_pool" "github" {
  workload_identity_pool_id = "workboard-github"
  display_name              = "Workboard GitHub Actions"
  description               = "Short-lived identities for the exact workshop repository"
  disabled                  = false

  depends_on = [
    google_project_service.required["iam.googleapis.com"],
    google_project_service.required["iamcredentials.googleapis.com"],
    google_project_service.required["sts.googleapis.com"],
  ]
}

resource "google_iam_workload_identity_pool_provider" "github" {
  workload_identity_pool_id          = google_iam_workload_identity_pool.github.workload_identity_pool_id
  workload_identity_pool_provider_id = "github-repository"
  display_name                       = "GitHub repository OIDC"
  description                        = "Only tokens issued for ${var.github_repository} are admitted"

  attribute_mapping = {
    "google.subject"             = "assertion.sub"
    "attribute.actor"            = "assertion.actor"
    "attribute.repository"       = "assertion.repository"
    "attribute.repository_owner" = "assertion.repository_owner"
    "attribute.ref"              = "assertion.ref"
  }

  attribute_condition = "assertion.repository == '${var.github_repository}'"

  oidc {
    issuer_uri = "https://token.actions.githubusercontent.com"
  }
}

resource "google_service_account_iam_member" "github_impersonation" {
  service_account_id = google_service_account.deployer.name
  role               = "roles/iam.workloadIdentityUser"
  member             = format(
    "principalSet://iam.googleapis.com/%s/attribute.repository/%s",
    google_iam_workload_identity_pool.github.name,
    var.github_repository,
  )
}
