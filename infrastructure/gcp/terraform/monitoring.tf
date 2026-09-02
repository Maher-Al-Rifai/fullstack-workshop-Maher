resource "google_monitoring_dashboard" "workboard" {
  dashboard_json = jsonencode({
    displayName = "Workboard Cloud Run operations"
    gridLayout = {
      columns = "2"
      widgets = [
        {
          title = "Backend request count"
          xyChart = {
            dataSets = [{
              timeSeriesQuery = {
                timeSeriesFilter = {
                  filter = "resource.type=\"cloud_run_revision\" resource.labels.service_name=\"workboard-api\" metric.type=\"run.googleapis.com/request_count\""
                  aggregation = {
                    alignmentPeriod    = "60s"
                    perSeriesAligner   = "ALIGN_RATE"
                    crossSeriesReducer = "REDUCE_SUM"
                  }
                }
              }
            }]
          }
        },
        {
          title = "Backend request latency"
          xyChart = {
            dataSets = [{
              timeSeriesQuery = {
                timeSeriesFilter = {
                  filter = "resource.type=\"cloud_run_revision\" resource.labels.service_name=\"workboard-api\" metric.type=\"run.googleapis.com/request_latencies\""
                  aggregation = {
                    alignmentPeriod    = "60s"
                    perSeriesAligner   = "ALIGN_PERCENTILE_99"
                    crossSeriesReducer = "REDUCE_MAX"
                  }
                }
              }
            }]
          }
        }
      ]
    }
  })
}

resource "google_monitoring_alert_policy" "backend_5xx" {
  display_name = "Workboard API elevated 5xx responses"
  combiner     = "OR"
  conditions {
    display_name = "Backend 5xx rate"
    condition_threshold {
      filter          = "resource.type=\"cloud_run_revision\" resource.labels.service_name=\"workboard-api\" metric.type=\"run.googleapis.com/request_count\" metric.labels.response_code_class=\"5xx\""
      comparison      = "COMPARISON_GT"
      threshold_value = 0
      duration        = "300s"
      aggregations {
        alignment_period     = "60s"
        per_series_aligner   = "ALIGN_RATE"
        cross_series_reducer = "REDUCE_SUM"
      }
    }
  }
  documentation {
    content   = "Inspect the affected revision, readiness, logs, latency, and Cloud SQL health. Follow docs/operating-runbook.md before shifting traffic."
    mime_type = "text/markdown"
  }
}