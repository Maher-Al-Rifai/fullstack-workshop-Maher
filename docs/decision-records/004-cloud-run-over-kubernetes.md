# ADR 004: Use Cloud Run instead of Kubernetes

- Status: Accepted
- Date: 2026-07-22

## Context

The learner must deploy containers and understand runtime configuration, IAM, revisions, scaling, health, logs, and managed data. Kubernetes would introduce cluster operations, workloads, services, ingress, config, autoscaling, and policy before the application delivery fundamentals are stable.

## Decision

Deploy frontend and backend containers to Cloud Run, use a Cloud Run Job for migrations, and use Cloud SQL/Secret Manager for managed dependencies.

## Consequences

Positive:

- direct path from container image to immutable revision;
- no cluster lifecycle in the core course;
- independent service traffic and rollback;
- scale-to-zero supports training cost control.

Negative:

- less exposure to portable orchestration primitives;
- managed platform constraints influence process/network design;
- Cloud SQL can remain an always-on cost.

## Revisit when

The explicit objective is Kubernetes operations or the application requires platform capabilities unavailable in Cloud Run.
