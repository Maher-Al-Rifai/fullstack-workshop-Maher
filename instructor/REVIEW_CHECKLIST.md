# Pull-request review checklist

Use selectively; do not turn review into a mechanical checkbox exercise.

## Intent and scope

- Is the desired behavior and acceptance criterion clear?
- Is the change small enough to reason about?
- Is unrelated formatting, refactoring, or dependency churn separated?

## API and domain

- Are HTTP method, path, status, request, and response contracts correct?
- Is validation at the appropriate boundary?
- Are business invariants in a testable service/domain function?
- Are errors consistent and safe for clients?
- Are authorization checks based on the actual resource?

## Data

- Are keys, constraints, nullability, indexes, and cascade behavior intentional?
- Is the transaction boundary correct?
- Is there a migration, and can an empty database reach the new state?
- Is rollout compatible with old/new application revisions when required?

## Frontend

- Are TypeScript contracts explicit?
- Are loading, error, empty, unauthorized, and success states handled?
- Is state local unless genuinely shared?
- Are labels, headings, focus behavior, and keyboard operation sound?
- Does SSR code avoid browser-only dependencies?

## Tests

- Does each test protect behavior rather than implementation trivia?
- Is the lowest useful test layer used?
- Are failure and authorization cases represented?
- Would the test fail after a realistic regression?
- Is nondeterminism controlled without arbitrary sleeps?

## Docker and delivery

- Are build context and layers efficient and explainable?
- Does the production process run as non-root?
- Is configuration supplied at runtime and secrets excluded?
- Are health checks meaningful?
- Do CI permissions and credentials follow least privilege?
- Are deployment image tags immutable and rollback notes present?

## Documentation and learning

- Are commands and expected output updated?
- Does the learner explain a decision and alternative?
- Is evidence sufficient to repeat the result?
- Does the change preserve module objectives and starter/reference alignment?
