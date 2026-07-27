# Learner setup checklist

Record versions and evidence; do not mark an item complete from memory.

## Accounts and access

- [ ] GitHub account uses multi-factor authentication.
- [ ] I can access the assigned repository and issue/project board.
- [ ] I know the mentor, reviewer, escalation contact, and expected review cadence.
- [ ] I have access to a disposable Google Cloud project or understand when access will be provided.
- [ ] Billing and budget ownership for cloud exercises is clear.

## Local tools

Run and record:

```bash
git --version
docker --version
docker compose version
```

For cloud modules later:

```bash
gcloud --version
terraform version
gh --version
```

- [ ] Docker has at least 8 GB memory available.
- [ ] Line endings are configured appropriately for my operating system.
- [ ] My editor can format Python, TypeScript, Vue, Markdown, YAML, and Terraform.
- [ ] I can open an integrated terminal and locate the repository root.

## Repository

```bash
git clone <assigned-url>
cd <repository>
make setup
make up
make ps
```

- [ ] `.env` was created locally and is not tracked by Git.
- [ ] PostgreSQL reports healthy.
- [ ] Backend reports healthy.
- [ ] Frontend reports healthy.
- [ ] `http://localhost:3000` loads.
- [ ] `http://localhost:8000/docs` loads.
- [ ] I can sign in with the local demonstration account.
- [ ] I can view the public project page.

## Git identity and workflow

```bash
git config user.name
git config user.email
git status
git remote -v
```

- [ ] My commit identity is correct.
- [ ] I can create and push a branch.
- [ ] I can open a draft pull request.
- [ ] I know which checks are required before review.

## Evidence to submit

- operating system and architecture;
- tool versions;
- `docker compose ps` output;
- frontend and API documentation URLs;
- one paragraph describing any setup issue and how it was resolved.
