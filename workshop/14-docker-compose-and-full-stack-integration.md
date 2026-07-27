# Module 14: Docker Compose and full-stack integration

**Guided effort:** 8 hours  
**Required branch:** `learning/14-compose-integration`  
**Phase:** Integration

## Objectives

- Define development and isolated acceptance stacks with explicit services, health, networks, volumes, and runtime configuration.
- Explain Docker DNS, startup dependency versus readiness, and persistent versus ephemeral data.
- Start the complete product with one documented command on a clean checkout.
- Inspect and diagnose cross-service failures without relying on fixed delays.

## Prerequisites

- Backend and frontend gates passed.
- Production images build independently.

## Concepts and context

Compose is a declarative local integration environment. `depends_on` can order startup, but health conditions provide a more meaningful readiness gate. Containers communicate through service DNS and container ports; the browser communicates through published host ports.

Development and production have different needs. Development uses source mounts/hot reload; acceptance uses production images and isolated deterministic data. A test stack should be disposable and should not share the developer database volume.

## Step-by-step lab

### 1. Map the development stack

Read `compose.yaml`. For each service document:

- image/build target;
- command;
- environment/config source;
- container and host ports;
- volumes;
- health check;
- dependency condition;
- expected process/user.

Explain why browser API base is `localhost` while server-side Nuxt base is `backend`.

### 2. Start from a clean state

```bash
make clean
make setup
make up
make ps
```

Time startup and observe health transitions. Verify migrations and seed are deterministic. Re-run `make up` and ensure seed does not create uncontrolled duplicates.

### 3. Inspect networking

```bash
docker compose exec frontend getent hosts backend || true
docker compose exec backend getent hosts db || true
docker compose exec backend python -c "import socket; print(socket.gethostbyname('db'))"
```

From the host, show that the service name is not normally the browser's DNS name. Explain container network isolation and port publishing.

### 4. Inspect persistence

Create a project, restart/replace containers, and prove data remains through the named PostgreSQL volume:

```bash
docker compose restart backend frontend
docker compose up -d --force-recreate backend frontend
```

Then run the guarded reset and prove data is recreated from migrations/seed. Do not use real data.

### 5. Build isolated acceptance stack

Read `compose.test.yaml`. Verify it:

- uses a different project name and database;
- does not publish unnecessary host ports;
- uses production frontend/backend targets;
- applies migrations and seed;
- waits on health;
- runs Playwright as an exit-code service;
- stores artifacts outside the container;
- tears down volumes.

Run:

```bash
make e2e-test
```

### 6. Failure drills

Perform three:

- wrong database service hostname;
- frontend internal API base points to host `localhost`;
- backend health path is wrong;
- migration intentionally fails;
- stale database volume has an unexpected revision.

For each, collect `compose ps`, service logs, health inspection, and one network/config command. Restore and re-run.

### 7. Resource and security review

Inspect final container users, mounts, writable paths, environment names, and exposed/published ports. Ensure no Docker socket mount, privileged mode, host network, or unnecessary database exposure exists in acceptance/production-like configuration.

### 8. Validate one-command onboarding

Give the documented clone/setup/up sequence to another person or a clean VM. Record every hidden prerequisite or correction and update docs/scripts rather than explaining it verbally only.

## Validation checklist

- [ ] Clean setup/up reaches a healthy full product.
- [ ] Development and acceptance stacks have separate state.
- [ ] I can explain service DNS versus host ports.
- [ ] Data survives container replacement but not intentional volume deletion.
- [ ] Acceptance uses production images and deterministic migration/seed.
- [ ] Three cross-service failure drills are diagnosed from evidence.
- [ ] No unnecessary privileged/socket/host-network configuration exists.

## Independent challenge

Add Compose profiles for an optional developer tool such as a database UI, while keeping it disabled by default, not exposed in acceptance, and protected by local-only configuration. Document the security tradeoff.

## Common failure modes

- Using `depends_on` without understanding readiness.
- Pointing container-to-container URLs at `localhost`.
- Sharing the developer database with E2E tests.
- Adding sleeps instead of health/observable state.
- Mounting source into a production-like acceptance container.

## Evidence to submit

- Service map.
- Clean-start timing and health transitions.
- Persistence/replacement proof.
- Three failure-diagnosis records.
- Clean-machine onboarding feedback and documentation correction.

## Commit checkpoint

```text
chore(compose): integrate reproducible development and test stacks
```

Update the learning log before requesting review. The reviewer records the module or gate decision in the linked issue.

## Official references

- [compose.yaml](../compose.yaml)
- [compose.test.yaml](../compose.test.yaml)
- [https://docs.docker.com/compose/](https://docs.docker.com/compose/)
- [https://docs.docker.com/compose/how-tos/networking/](https://docs.docker.com/compose/how-tos/networking/)
- [https://docs.docker.com/compose/how-tos/startup-order/](https://docs.docker.com/compose/how-tos/startup-order/)
