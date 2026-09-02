# Module 19 Prioritized Risk Register

Status is intentionally explicit: `open` means the risk needs work before real users; `training` means it is accepted only for this workshop.

| Priority | Risk / user outcome | Owner | Next evidence | Blocks real users? | Status |
|---|---|---|---|---|---|
| P0 | No MFA, account recovery, refresh-token rotation, or mature abuse/rate controls; account takeover risk | Identity owner | Threat model, abuse tests, recovery drill | Yes | open |
| P0 | Production domain/session topology and cross-site refresh-cookie behavior are not proven | Platform owner | Browser matrix on final domains and ADR | Yes | open |
| P0 | Backup restore and Cloud SQL failure recovery are not rehearsed | Data/platform owner | Restore drill with RTO/RPO result | Yes | open |
| P1 | No formal privacy classification, retention, deletion, or audit policy | Security/privacy owner | Data inventory and retention decision | Yes | open |
| P1 | Alerting lacks notification ownership and an exercised paging path | Operations owner | Alert delivery test and on-call runbook | Yes | open |
| P1 | Capacity and latency under realistic load are unmeasured | Performance owner | Load test, limits, and scaling review | Yes | open |
| P1 | Images lack mandatory vulnerability scan, SBOM, provenance, and signing policy | Supply-chain owner | CI policy report and admission decision | Yes | open |
| P1 | Terraform state backend and organizational IAM policy are not established | Platform owner | Remote-state design and access review | Yes | open |
| P2 | Frontend API types are hand-maintained rather than generated from OpenAPI | Frontend owner | Generated-client spike and contract check | No | open |
| P2 | Product roles, invitations, comments, and audit UX are intentionally absent | Product owner | Prioritized product requirements | No | training |
| P2 | Dashboard signal is a starter metric rather than a full SLO/error budget | Operations owner | SLO proposal with cardinality/cost review | No | open |

## 30-day top-three roadmap

1. **Harden identity and session architecture.** Outcome: reduce account takeover and refresh-cookie risk. Evidence: threat model, browser matrix, MFA/recovery/rate-limit tests, staged rollout and rollback plan.
2. **Prove data recovery and service reliability.** Outcome: demonstrate recovery within agreed RTO/RPO. Evidence: Cloud SQL restore drill, load test, SLO/alert ownership, and rollback rehearsal.
3. **Harden delivery supply chain.** Outcome: prevent unreviewed or vulnerable images reaching Cloud Run. Evidence: lockfile migration, SBOM/vulnerability scan, provenance/signing policy, and deploy gate.
