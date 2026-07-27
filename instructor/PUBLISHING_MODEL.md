# Repository publishing model

The ZIP contains a complete solution and a minimal starter. Do not hand the unrestricted solution to a beginner and then assess whether they can recreate it from memory.

## Recommended branch model

After creating a new GitHub repository:

```bash
unzip fullstack-intern-workshop.zip
cd fullstack-intern-workshop
git init
git add .
git commit -m "chore: publish complete workshop reference"
git branch -M reference
git remote add origin <repository-url>
git push -u origin reference
```

Export and publish the learner starter:

```bash
./scripts/export-starter.sh ../fullstack-intern-workshop-starter
cd ../fullstack-intern-workshop-starter
git init
git add .
git commit -m "chore: initialize learner starter"
git branch -M main
git remote add origin <same-or-separate-repository-url>
git push -u origin main
```

### Same repository

Use `main` for the learner starter and protect `reference` so only instructors can view or merge it. This is simple but repository permissions may not conceal a branch from users who can read the repository.

### Separate repositories — strongest solution control

Use a learner repository containing the starter and workshop materials, plus a private instructor repository containing the complete reference. This prevents accidental browsing and lets the instructor cherry-pick fixes between them.

## Checkpoint strategy

Create one GitHub milestone per major gate and one issue per module. The issue should contain only the module objective, acceptance criteria, and evidence link; the detailed instructions remain in `workshop/`.

Recommended labels:

```text
learning
foundation
backend
frontend
integration
cloud
blocked
needs-review
gate
```

Recommended branch per module:

```text
learning/00-orientation
learning/01-setup
learning/02-git-workflow
...
learning/19-final-readiness
```

Require a pull request for modules 02 onward. A reviewer records `Pass`, `Pass with follow-up`, `Repeat evidence`, or `Rework` in the issue.

## Revealing solutions

Use one of these policies and publish it before the workshop:

- reveal the relevant reference files only after the module PR is approved;
- allow reference access after the learner submits a failing attempt and focused question;
- keep reference closed until the end of each major gate;
- allow open reference exploration but assess through novel change requests and failure diagnosis.

Do not change the policy silently after the learner begins.

## Cohort reset

Before a new cohort:

1. archive learner branches and cloud evidence;
2. update dependencies and official references in a maintenance PR;
3. run the complete verification and deployment path;
4. export a fresh starter;
5. recreate issues/milestones from the updated module set;
6. confirm cloud project, budget, IAM, and cleanup ownership;
7. calibrate reviewers with one sample PR.
