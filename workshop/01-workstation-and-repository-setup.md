# Module 01: Workstation and repository setup

**Guided effort:** 3 hours  
**Required branch:** `learning/01-setup`  
**Phase:** Foundation

## Objectives

- Verify Git, Docker, Docker Compose, browser, and later cloud tooling with exact version evidence.
- Create local configuration without committing secrets.
- Start the reference or starter stack and interpret service health.
- Diagnose one setup failure using logs and targeted inspection rather than reinstalling everything.

## Prerequisites

- Module 00 complete.
- Administrator rights or a support path for installing required tools.

## Concepts and context

A reproducible setup has declared prerequisites, deterministic commands, expected outputs, and a troubleshooting path. “It worked on my laptop” is not reproducibility if the required state is undocumented.

Docker reduces host-language dependencies but does not eliminate host requirements: virtualization, architecture, memory, ports, filesystem permissions, line endings, and network policy still matter. `.env.example` documents names and safe local defaults; `.env` is local state and must remain untracked.

## Step-by-step lab

### 1. Verify tools and system context

Run:

```bash
git --version
docker --version
docker compose version
uname -a 2>/dev/null || ver
```

For future cloud modules, install and record:

```bash
gcloud --version
terraform version
gh --version
```

Record operating system, CPU architecture, available memory, and Docker resource allocation in the setup checklist.

### 2. Clone and inspect safety boundaries

```bash
git clone <assigned-repository-url>
cd fullstack-intern-workshop
git status
git remote -v
git check-ignore -v .env || true
```

Read `.gitignore`, `.dockerignore`, and `.env.example`. Explain why `.dockerignore` and `.gitignore` solve different problems.

### 3. Run the setup helper

```bash
make setup
```

PowerShell alternative:

```powershell
./scripts/setup.ps1
```

Confirm `.env` was created and remains untracked:

```bash
git status --short
```

Do not post the full file in a pull request or screenshot.

### 4. Start and observe the stack

```bash
make up
make ps
```

Wait for healthy services, then inspect:

```bash
curl --fail http://localhost:8000/health/live
curl --fail http://localhost:8000/health/ready
curl --fail http://localhost:3000/api/health
```

Open the frontend and FastAPI documentation. Sign in with the seeded local account and open the public project page.

### 5. Inspect logs and runtime identity

```bash
make logs
# In another terminal:
docker compose exec backend whoami
docker compose exec frontend whoami
docker compose exec backend python --version
docker compose exec frontend node --version
```

The development image may have different runtime behavior from the final production image; record what you observed and defer the production-user proof to Module 04.

### 6. Perform a controlled failure drill

Stop only PostgreSQL:

```bash
docker compose stop db
curl -i http://localhost:8000/health/live
curl -i http://localhost:8000/health/ready
```

Predict the difference before running the requests. Inspect backend logs, restart the database, and verify recovery:

```bash
docker compose start db
make ps
curl --fail http://localhost:8000/health/ready
```

Explain why liveness should not necessarily fail during a temporary dependency outage.

### 7. Clean shutdown

```bash
make down
```

Confirm the named database volume still exists and understand that `make clean` or `down -v` has a different data effect.

## Validation checklist

- [ ] Required tool versions and system context are recorded.
- [ ] `.env` exists locally and is ignored by Git.
- [ ] All three services become healthy and the product journey can be opened.
- [ ] I can explain liveness versus readiness using the database-stop drill.
- [ ] I can locate relevant Compose logs without revealing secret values.
- [ ] I know the difference between stopping containers and deleting volumes.

## Independent challenge

Change the host PostgreSQL port through `.env`, restart the stack, and prove that backend-to-database communication still uses the container port and service DNS. Restore the default afterward.

## Common failure modes

- Using `localhost` for database access from inside the backend container.
- Deleting volumes before collecting evidence from a startup failure.
- Committing `.env` or posting complete environment output in a PR.
- Confusing a host port with the port used on the Compose network.

## Evidence to submit

- Completed setup checklist.
- `docker compose ps` output with healthy state.
- Health request results before, during, and after the database outage.
- Root-cause note for any setup issue and the exact command that resolved it.

## Commit checkpoint

```text
docs(learning): complete reproducible workstation setup
```

Update the learning log before requesting review. The reviewer records the module or gate decision in the linked issue.

## Official references

- [SETUP_CHECKLIST.md](../learner/SETUP_CHECKLIST.md)
- [troubleshooting.md](../docs/troubleshooting.md)
- [https://docs.docker.com/compose/](https://docs.docker.com/compose/)
- [https://docs.docker.com/compose/how-tos/startup-order/](https://docs.docker.com/compose/how-tos/startup-order/)
