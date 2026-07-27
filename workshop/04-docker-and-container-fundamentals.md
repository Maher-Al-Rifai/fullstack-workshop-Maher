# Module 04: Docker and container fundamentals

**Guided effort:** 7 hours  
**Required branch:** `learning/04-docker-fundamentals`  
**Phase:** Foundation

## Objectives

- Explain images, layers, containers, registries, networks, volumes, ports, environment, and build context.
- Build multi-stage development and production images.
- Run the final process as a non-root user with a meaningful health check.
- Inspect image history and diagnose build/runtime failures.

## Prerequisites

- Modules 00–03 complete.
- Docker/Compose available and sufficient local resources.

## Concepts and context

An image is an immutable template assembled from cached layers. A container is a process plus isolated filesystem/network configuration created from an image. A registry distributes images. A volume provides durable data independent of a specific container. Port publishing maps a host port to a container port; Compose service DNS connects containers without host publishing.

A Dockerfile is production code. Layer order affects cache and rebuild speed; build context affects performance and accidental data exposure; final stage contents affect attack surface. Runtime configuration belongs in environment/secrets, not baked into an image.

## Step-by-step lab

### 1. Read the three Dockerfiles

Inspect:

```bash
sed -n '1,220p' backend/Dockerfile
sed -n '1,220p' frontend/Dockerfile
sed -n '1,180p' e2e/Dockerfile
```

For each stage, state its input, output, installed dependencies, user, command, and intended environment.

### 2. Build production images without Compose

```bash
docker build --target production -t workboard-backend:module04 backend
docker build --target production -t workboard-frontend:module04 frontend
```

Inspect:

```bash
docker image ls workboard-backend:module04 workboard-frontend:module04
docker history workboard-backend:module04
docker history workboard-frontend:module04
```

Look for copied source, package installation layers, large unexpected content, and secret-like arguments. Build logs must not contain real secrets.

### 3. Prove the runtime identity

Start a temporary backend container command:

```bash
docker run --rm --entrypoint whoami workboard-backend:module04
docker run --rm --entrypoint id workboard-backend:module04
docker run --rm --entrypoint whoami workboard-frontend:module04
```

Expected application identity is non-root. Explain why non-root reduces impact but is not a complete sandbox.

### 4. Run an isolated liveness process

The backend readiness endpoint requires a database; run the liveness path with local environment values and a published port, or use Compose for full readiness. For frontend, run the production server and query `/api/health`.

Use `docker inspect` to locate process, user, environment names, port configuration, and health status. Do not print secret values in evidence.

### 5. Explore build cache deliberately

Build the same image twice, then change:

1. a late source file;
2. the dependency manifest.

Compare which layers rebuild. Explain why copying `package.json` or `pyproject.toml` before the full source improves dependency-layer reuse.

### 6. Inspect build context and exclusions

Read root and service `.dockerignore` files. Measure context with build output and verify that `.git`, `.env`, test artifacts, node modules, caches, and Terraform state are excluded.

Run the basic secret pattern check:

```bash
./scripts/check-secrets.sh
```

### 7. Failure drills

Perform at least two:

- use a wrong `CMD` executable and interpret exit code/logs;
- publish a port already in use;
- remove a required runtime environment variable;
- make a health path incorrect and inspect health state;
- attempt to write to a root-owned path as the app user.

Restore the file after each drill and record the smallest diagnostic commands.

### 8. Explain signal and shutdown behavior

Identify PID 1 in each production image and discuss graceful termination. Use `docker stop` and logs to observe shutdown. A mature extension would add explicit lifespan/connection cleanup tests.

## Validation checklist

- [ ] Both production images build from their final target.
- [ ] The final backend and frontend processes run as non-root.
- [ ] I can explain every Dockerfile stage and why dependency files are copied early.
- [ ] No environment secrets are baked into image history or context.
- [ ] I performed two failure drills and used focused diagnostics.
- [ ] I can distinguish EXPOSE, published ports, and Compose service networking.

## Independent challenge

Create a tiny throwaway Dockerfile with an intentionally poor layer order and root process. Improve it, compare rebuild behavior and image history, and document three changes. Do not add the throwaway image to production Compose.

## Common failure modes

- Assuming `EXPOSE` publishes a host port.
- Copying the entire repository before installing dependencies.
- Using root because a permission problem is easier to hide.
- Passing production secrets as Docker build arguments.
- Using container deletion as a database backup strategy.

## Evidence to submit

- Image tags, sizes, and relevant history excerpts.
- Non-root `whoami/id` output.
- Cache comparison.
- Two failure-drill symptoms, diagnostics, root causes, and prevention.

## Commit checkpoint

```text
chore(docker): document and validate production image fundamentals
```

Update the learning log before requesting review. The reviewer records the module or gate decision in the linked issue.

## Official references

- [security.md](../docs/security.md)
- [https://docs.docker.com/reference/dockerfile/](https://docs.docker.com/reference/dockerfile/)
- [https://docs.docker.com/build/building/multi-stage/](https://docs.docker.com/build/building/multi-stage/)
- [https://docs.docker.com/build/building/best-practices/](https://docs.docker.com/build/building/best-practices/)
