# Module gates

Use this document for formal gate reviews. The numbered module contains detailed acceptance criteria; this file defines the compact oral/practical check.

## Foundation gate — after module 04

Ask the learner to:

- clone and start the assigned baseline;
- create a branch and focused commit;
- explain request method, URL, headers, body, response status, and response body;
- build an image and run it as a non-root user;
- identify a container through logs, inspect, ports, and health;
- explain where database state persists after a container is replaced.

Pass only when the learner can distinguish source, image, container, volume, and service.

## Backend gate — after module 09

Ask the learner to:

- build an empty database from Alembic migrations;
- trace one authenticated request through all backend layers;
- demonstrate an ownership denial;
- break the task transition rule and show the expected unit/API failure;
- explain access versus refresh token behavior;
- identify which constraints live in validation, service rules, and PostgreSQL.

Pass only when authorization and migration reasoning are correct.

## Frontend gate — after module 13

Ask the learner to:

- trace sign-in and token refresh;
- demonstrate loading, error, empty, and success states;
- explain why one piece of state is local and another is shared;
- inspect the initial HTML and metadata of the public page;
- operate the product by keyboard;
- break a component/API-client behavior and show the targeted test fail.

Pass only when the learner distinguishes browser rendering from server rendering and tests user-observable behavior.

## Delivery gate — after module 16

Ask the learner to:

- run the full local verification path;
- recreate an E2E failure without fixed sleeps;
- show required pull-request checks and artifacts;
- identify every secret/config boundary;
- inspect production container users and processes;
- explain why frontend and backend are separate production services.

Pass only when a clean checkout is reproducible and CI failures are diagnosable.

## Cloud gate — after module 18

Ask the learner to:

- map GitHub identity, deployer service account, runtime service account, and secret access;
- identify the image digest/tag behind a revision;
- explain how the migration job connects to Cloud SQL;
- find a request or failure in logs;
- trigger a safe failing revision and roll traffic back;
- estimate ongoing cost categories and remove training resources.

Pass only after an actual rollback and recovery smoke check.

## Final gate — module 19

Use the complete learner demo and rubric. Require independent execution and explicit risk disclosure.
