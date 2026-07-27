# Full-stack intern workshop — learner starter

This is the intentionally small starting point exported from the complete instructor/reference package. It proves that the workstation, Docker network, FastAPI process, Nuxt process, and PostgreSQL connection work. The numbered workshop modules guide you from this baseline to the complete Workboard application.

## Start here

```bash
cp .env.example .env
./scripts/setup.sh
docker compose up --build
```

Open:

- frontend: <http://localhost:3000>
- backend live health: <http://localhost:8000/health/live>
- backend ready health: <http://localhost:8000/health/ready>
- backend OpenAPI: <http://localhost:8000/docs>

Validate the exported package and run the starter tests:

```bash
make validate
make test
```

Stop and delete the disposable database volume:

```bash
make clean
```

## What is deliberately absent

The starter does not contain the completed authentication/domain implementation, migrations, project/task routes, typed frontend service layer, production-quality tests, Playwright suite, complete CI gates, or a proven cloud deployment. It does include deliberately incomplete CI/deployment and infrastructure scaffolds so later modules have a reviewable destination. Those outcomes are the learning work. Do not copy an entire completed reference tree: implement module-sized changes, explain them, test them, and submit evidence.

## Learning path

Read [the starter scope](STARTER_SCOPE.md) and [validation baseline](VALIDATION_REPORT.md). Then begin with [Module 00](workshop/00-orientation-and-definition-of-done.md), follow [the workshop index](workshop/README.md), and keep a personal copy of [the learning log](learner/LEARNING_LOG.md).

## Starter architecture

```text
browser -> Nuxt :3000
              |
              v
          FastAPI :8000 -> PostgreSQL :5432
```

The frontend starter calls its own Nuxt health route so that it can render before the application API contract is introduced. Module 03 defines the contract; subsequent modules replace the placeholder screen with the full product.
