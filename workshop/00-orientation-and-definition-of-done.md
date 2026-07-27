# Module 00: Orientation and definition of done

**Guided effort:** 2 hours  
**Required branch:** `learning/00-orientation`  
**Phase:** Foundation

## Objectives

- Describe the product, architecture, course gates, and final demonstration in your own words.
- Distinguish a feature that appears to work from a reproducible, tested, deployable definition of done.
- Create a baseline self-assessment and a learning log that records evidence and uncertainty.
- Identify the permitted use of reference solutions and AI assistance for the cohort.

## Prerequisites

- Access to the assigned repository and mentor expectations.
- Ability to read Markdown and run basic terminal commands.

## Concepts and context

A professional delivery is a chain of evidence. Source code is one link; contracts, migrations, tests, images, runtime configuration, deployment identity, logs, rollback, and handover are others. The course is therefore assessed through behavior and explanation rather than completed checkboxes.

The reference application is Workboard: users register, authenticate, create projects, create tasks, move tasks through a constrained status workflow, and publish a server-rendered project summary. The small product scope lets you spend time on engineering quality instead of feature volume.

Read the distinction between the **learner starter** and **reference solution** in `../instructor/PUBLISHING_MODEL.md`. Your mentor must state which mode applies. Disclose AI-assisted changes according to organizational policy, verify every generated claim, and never paste credentials, private data, or proprietary material into an unapproved system.

## Step-by-step lab

### 1. Inspect the course map and repository

From the repository root:

```bash
pwd
find . -maxdepth 2 -type f | sort | sed -n '1,160p'
```

Read `../README.md`, `../COURSE_MAP.md`, `../docs/architecture.md`, and `../learner/FINAL_DEMO.md`. Draw the system from memory using five boxes: browser, Nuxt, FastAPI, PostgreSQL, Google Cloud delivery. Add arrows and state what travels over each boundary.

### 2. Translate the final result into evidence

Create an issue or note called `Workshop definition of done`. For each statement below, write how it will be proven:

- a clean machine can run the application;
- a user cannot read another user's private project;
- a database schema can be reproduced from zero;
- public project content exists in initial HTML;
- a failed pull request cannot merge;
- a known-good cloud revision can receive traffic again.

Avoid evidence such as “I looked at it” or “the code seems correct.” Prefer commands, test failures/passes, HTTP responses, logs, revision names, and repeatable demonstrations.

### 3. Create your learning log

Copy the template without overwriting the shared file:

```bash
cp learner/LEARNING_LOG.md learner/LEARNING_LOG-<your-name>.md
```

Record prior experience honestly. A low baseline score is useful; it changes mentoring and lets you demonstrate growth.

### 4. Establish the work agreement

Confirm with the mentor:

- core hours and review response expectations;
- branch and pull-request rules;
- when a module may proceed while review is open;
- reference-solution access policy;
- AI/tool use and disclosure policy;
- cloud billing owner and cleanup date;
- escalation path for security or credential exposure.

Write the agreement in the learning log or assigned issue.

### 5. Baseline explanation

Without opening source files, explain for five minutes:

1. why frontend and backend are separate production services;
2. why PostgreSQL data is not stored in a container filesystem;
3. why a migration job is different from application startup;
4. why one green browser path is insufficient;
5. why rollback may fail after an incompatible database migration.

Record which answers were uncertain. These become explicit learning targets.

## Validation checklist

- [ ] I can state the complete product journey without reading the README.
- [ ] I can name every major course gate and the evidence required to pass it.
- [ ] My personal learning log exists and is not a vague status diary.
- [ ] The mentor agreement covers solution access, AI use, reviews, cloud cost, and escalation.
- [ ] I can explain at least three differences between “works locally” and “ready to deliver.”

## Independent challenge

Choose one ordinary feature—such as deleting a project—and write a miniature definition of done covering API contract, authorization, persistence, migration impact, frontend states, tests, logs, and rollback. Do not implement it.

## Common failure modes

- Treating the course as a sequence of files to copy rather than capabilities to demonstrate.
- Writing goals such as “learn Docker” that have no observable completion condition.
- Hiding uncertainty to appear advanced; this delays effective mentoring.

## Evidence to submit

- Link to the baseline self-assessment and learning log.
- Architecture sketch with boundary explanations.
- Definition-of-done evidence table.
- One paragraph identifying the largest current knowledge risk.

## Commit checkpoint

```text
docs(learning): record workshop baseline and definition of done
```

Update the learning log before requesting review. The reviewer records the module or gate decision in the linked issue.

## Official references

- [README.md](../README.md)
- [COURSE_MAP.md](../COURSE_MAP.md)
- [architecture.md](../docs/architecture.md)
- [FINAL_DEMO.md](../learner/FINAL_DEMO.md)
- [ssdf](https://csrc.nist.gov/Projects/ssdf)
