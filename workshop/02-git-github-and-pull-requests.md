# Module 02: Git, GitHub, and pull requests

**Guided effort:** 5 hours  
**Required branch:** `learning/02-git-workflow`  
**Phase:** Foundation

## Objectives

- Use branches, commits, remotes, pull requests, and reviews as a controlled change workflow.
- Write focused commits and useful pull-request evidence.
- Resolve a simple merge conflict without losing another change.
- Explain required checks, protected branches, and why force-push policy matters.

## Prerequisites

- Modules 00–01 complete.
- Repository push and pull-request permission.

## Concepts and context

Git records a directed history of snapshots; GitHub adds collaboration, review, policy, and automation. A branch is not a folder or copy of the repository. A pull request is a proposal and evidence packet, not merely a merge button.

The workshop uses short-lived branches and conventional commit prefixes. Keep changes small enough that a reviewer can reason about behavior and rollback. A green check does not replace review, and review does not replace automated checks.

## Step-by-step lab

### 1. Configure and inspect identity

```bash
git config user.name
git config user.email
git status
git log --oneline --decorate -n 8
git remote -v
```

Correct identity before committing. Do not use a shared generic identity.

### 2. Create a focused branch

```bash
git switch -c learning/02-git-workflow
```

Add a short note to your personal learning log explaining the difference between working tree, staging area, local commit, and remote branch.

### 3. Practice selective staging

Make two small documentation edits in different files. Inspect and stage only one:

```bash
git diff
git add -p
git diff --staged
git commit -m "docs(learning): explain Git state model"
```

Then stage and commit the second change separately. Explain why `git add .` can hide accidental scope.

### 4. Push and open a draft pull request

```bash
git push -u origin learning/02-git-workflow
```

Open a draft PR using `.github/pull_request_template.md`. Include purpose, scope, commands/evidence, risk, rollback, and module number. Link the learning issue if one exists.

### 5. Read checks and review comments

For each check, identify:

- trigger;
- job responsibility;
- evidence/artifact;
- whether failure blocks merge;
- where to find logs.

Request review. Respond to feedback with a new commit rather than editing history while the reviewer is inspecting it, unless the repository policy says otherwise.

### 6. Resolve a deliberate conflict

The instructor changes the same training sentence on the base branch, or you simulate with a second branch. Update your branch:

```bash
git fetch origin
git rebase origin/main
# or the team's approved merge approach
```

Open conflict markers, understand both intentions, create the correct combined result, stage, and continue. Run validation after resolution. Never choose “ours” or “theirs” without understanding content.

### 7. Inspect history and restore safely

Practice on a disposable file:

```bash
git log --oneline --graph --decorate --all -n 20
git show <commit>
git restore --staged <file>
git restore <file>
```

Discuss when `git revert` is safer than rewriting shared history.

### 8. Complete review

Update the PR evidence, resolve discussions only after changes/explanation are present, convert from draft, and merge according to policy. Delete the remote branch after merge if permitted.

## Validation checklist

- [ ] The PR contains two coherent commits rather than one mixed snapshot.
- [ ] No generated files, `.env`, credentials, or unrelated formatting are included.
- [ ] I can explain working tree, index, commit, branch, remote, and PR.
- [ ] I resolved a content conflict by preserving intent and reran validation.
- [ ] I can identify which GitHub checks are required and where their evidence appears.
- [ ] Review feedback is reflected in code or a reasoned response.

## Independent challenge

Use `git bisect` on an instructor-provided three-to-ten commit practice history to identify the commit that changes an expected text assertion. Record the commands and result.

## Common failure modes

- Committing all local changes because they happen to be present.
- Using force push on a shared branch without policy/coordination.
- Treating conflict resolution as choosing one side wholesale.
- Marking review conversations resolved before the concern is addressed.

## Evidence to submit

- Pull-request link.
- Before/after commit graph.
- Conflict-resolution explanation.
- One review comment and the correction it caused.
- `git bisect` transcript or equivalent investigation.

## Commit checkpoint

```text
docs(learning): demonstrate reviewed Git workflow
```

Update the learning log before requesting review. The reviewer records the module or gate decision in the linked issue.

## Official references

- [CONTRIBUTING.md](../CONTRIBUTING.md)
- [pull_request_template.md](../.github/pull_request_template.md)
- [v2](https://git-scm.com/book/en/v2)
- [pull-requests](https://docs.github.com/en/pull-requests)
