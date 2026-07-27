# Learner start here

Welcome to the Full-Stack Intern Workshop. You will deliver one small product through the same engineering stages used by a professional team: clarify behavior, design contracts, implement backend and frontend code, persist data, write several kinds of tests, package containers, protect changes in CI, deploy to Google Cloud, observe a failure, and roll back safely.

## Your product

Workboard allows a user to register, sign in, create projects, create tasks, move tasks through a constrained workflow, and publish a server-rendered project summary. The product is intentionally simple. The engineering path is the assignment.

## Rules of engagement

1. Work on one numbered module at a time.
2. Create the branch named by the module.
3. Read the acceptance criteria before writing code.
4. Make the smallest change that demonstrates the objective.
5. Write or update tests while implementing behavior.
6. Record commands, failures, decisions, and questions in your learning log.
7. Open a pull request with the required evidence.
8. Address review feedback before starting the next gate unless your mentor explicitly permits parallel work.
9. Never commit credentials, `.env`, cloud keys, Terraform state, or personal information.
10. Explain code in your own words. A working result you cannot explain is not complete.

## First session

1. Copy [SETUP_CHECKLIST.md](SETUP_CHECKLIST.md) into your notes and complete it.
2. Create your own copy of [LEARNING_LOG.md](LEARNING_LOG.md).
3. Read [../COURSE_MAP.md](../COURSE_MAP.md).
4. Begin [Module 00](../workshop/00-orientation-and-definition-of-done.md).
5. Ask your mentor which delivery mode is being used:
   - starter branch with restricted reference solution;
   - complete reference repository with investigation challenges.

## Evidence standard

Good evidence is reproducible and directly supports an acceptance criterion. Examples:

- exact command and successful output;
- a test that first fails for the intended reason and then passes;
- a focused screenshot with the URL and relevant state visible;
- a `curl` request and response status/body;
- a migration upgrade and downgrade transcript;
- a pull-request discussion showing how feedback was resolved;
- Cloud Run revision, log query, alert, or rollback output;
- a brief explanation of a tradeoff and the alternative rejected.

A screenshot of a green screen without commands, context, or an explanation is weak evidence.

## How to use the reference solution

Try the task first. When blocked:

1. reduce the problem to the smallest failing behavior;
2. read the error and relevant official documentation;
3. inspect adjacent code and tests;
4. state a hypothesis and test it;
5. ask a focused question with evidence;
6. inspect the reference implementation only according to the mentor's publishing rules.

Do not copy an entire file and then reverse-engineer an explanation. The workshop assesses engineering reasoning, not typing speed.

## Completion

You finish when you can perform [FINAL_DEMO.md](FINAL_DEMO.md) from a clean checkout, pass the rubric, and hand over an accurate runbook. Module checkboxes alone are not completion.
