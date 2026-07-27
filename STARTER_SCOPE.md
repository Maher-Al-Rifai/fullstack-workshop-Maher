# Learner starter scope

This repository is deliberately incomplete. It is the beginning of the assessment, not a reduced copy of the answer key.

## Included at baseline

- a small FastAPI application with live and database-readiness health routes;
- a small Nuxt application with a server health route and placeholder page;
- PostgreSQL 17, Dockerfiles, and Docker Compose development/test scaffolds;
- a minimal backend test and starter CI checks;
- all numbered workshop modules, learner material, instructor rubric/gates, architecture/security/testing guidance, official references, templates, and GCP infrastructure guidance after export;
- a deployment workflow scaffold that becomes usable only after the learner implements migrations, production configuration, tests, and the complete delivery gates.

## Deliberately absent

- Workboard users, projects, tasks, repositories, services, and migrations;
- authentication, authorization, password hashing, JWT/session implementation, and frontend auth state;
- completed API contracts and application pages;
- production-level backend/frontend/API/browser test suites;
- completed Playwright package and test service;
- a proven deployment from this starter commit.

The learner must implement those outcomes through modules 03–18 and defend the result in module 19.

## Baseline definition of done

Before module work begins:

```bash
cp .env.example .env
make setup
make up
make test
```

The learner records tool versions, URLs, test output, and any workstation deviation in the learning log. A failure in this baseline is an environment/support issue; a failure introduced after the first approved module is diagnosed through normal pull-request work.

## Solution-control expectation

Use a separate private reference repository when independent work matters. Do not grant learners read access to the completed implementation and then assess memorization as implementation ability. Reference access policy must be published before the workshop begins.
