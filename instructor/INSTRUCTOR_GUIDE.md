# Instructor guide

## Purpose

This workshop evaluates whether an intern can integrate several engineering disciplines into one repeatable delivery system. It is not designed to maximize the number of frameworks encountered. Keep the project scope stable and use review, failures, and explanation to deepen understanding.

## Instructor responsibilities

Before the cohort:

- run the full repository validation on a clean machine;
- choose guided-build or reference-exploration mode;
- create starter/reference branches and module issues;
- establish review service levels and escalation contacts;
- provision or schedule a disposable Google Cloud project;
- set a budget alert and cleanup date;
- verify that required GitHub Actions and cloud APIs are allowed by organizational policy;
- define what AI assistance is permitted and how use must be disclosed;
- calibrate the rubric with all reviewers.

During the cohort:

- review evidence, not only final code;
- ask the learner to predict outcomes before running commands;
- require small reproductions for defects;
- distinguish a knowledge gap from an environment problem;
- avoid taking over the keyboard unless demonstrating a narrowly scoped technique;
- record gate decisions and unresolved risks;
- provide fast feedback on architecture and security errors that would cause later rework.

After the cohort:

- conduct the final demonstration and defense;
- score the rubric with concrete evidence;
- remove cloud resources and access;
- collect curriculum defects separately from learner defects;
- update versions, commands, and instructor notes before reuse.

## Recommended review cadence

- 15-minute daily learner check-in: objective, evidence, blocker, next experiment;
- two scheduled code-review sessions per week;
- one gate review at the end of each major phase;
- one architecture/operations oral review before cloud deployment;
- final demonstration of 75–120 minutes.

Do not convert every daily check-in into a status meeting. The learner should bring a branch, failing test, log, diagram, or precise question.

## Teaching method

Use a four-stage loop:

1. **Predict** — learner explains expected behavior and failure modes.
2. **Implement** — learner makes a focused change and test.
3. **Observe** — learner uses logs, HTTP responses, SQL, browser tools, or CI evidence.
4. **Explain** — learner states the root cause, boundary, and tradeoff in their own words.

A correct change without stages three and four should not receive full credit.

## Appropriate hints

Prefer progressively stronger hints:

1. point to the acceptance criterion;
2. ask which layer owns the behavior;
3. ask for the smallest reproduction;
4. point to an official documentation section;
5. identify the failing contract;
6. show a minimal unrelated example;
7. reveal the reference implementation only according to the publishing model.

Avoid giving a completed file. It removes the reasoning the module is meant to assess.

## Common learner patterns

### “It works in the browser”

Ask for a repeatable request, status code, test, and behavior under failure. The lesson is that an unrecorded happy path is not a delivery guarantee.

### “Docker is broken”

Ask the learner to identify whether the problem is build context, layer cache, process exit, port binding, DNS, health, volume state, permissions, or runtime configuration. Require `docker compose ps`, logs, and one targeted inspection command.

### “The test needs a sleep”

Ask what observable readiness condition should replace time. Fixed sleeps usually hide nondeterministic state, asynchronous UI behavior, or missing service health.

### “I put it in the store”

Ask whether the state is genuinely shared, durable, and client-owned. Server data does not automatically belong in global state.

### “The endpoint is authenticated”

Ask whether the current user is authorized for this exact project/task. Authentication identifies; authorization decides.

### “Coverage is high”

Mutate a business rule and ask which test fails. Coverage without assertion quality is weak evidence.

## Gate decisions

Use [MODULE_GATES.md](MODULE_GATES.md). Record one of:

- **Pass** — objectives demonstrated independently;
- **Pass with follow-up** — safe to continue, with a specific correction deadline;
- **Repeat evidence** — implementation may be correct but demonstration is insufficient;
- **Rework** — a core contract, security boundary, migration, or quality gate is incorrect.

Do not average away a critical security or data-integrity failure with strong styling or documentation.

## Final assessment

Use [RUBRIC.md](RUBRIC.md) and [../learner/FINAL_DEMO.md](../learner/FINAL_DEMO.md). Ask counterfactual questions:

- What fails when the database is unavailable?
- What changes when two backend instances serve traffic?
- How is a stale access token handled?
- What happens when a migration succeeds but the new revision fails?
- Which content is present in initial HTML?
- Which test would catch an authorization regression?
- Which identity reads the secret?
- How would traffic return to the last good revision?

The learner should know where uncertainty remains. Overconfident guessing is a production risk.
