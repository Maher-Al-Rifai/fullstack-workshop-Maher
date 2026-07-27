# ADR 002: Use Nuxt universal rendering instead of a Vue SPA only

- Status: Accepted
- Date: 2026-07-22

## Context

The frontend objective includes Vue/TypeScript application development and an SEO-friendly public page. A client-only SPA can render interactive UI but does not inherently deliver meaningful public content and metadata in the initial HTML.

## Decision

Use Nuxt 4 with universal rendering, route rules, Vue 3, TypeScript, and Pinia for shared authentication state.

## Consequences

Positive:

- learner can compare SSR, prerendering, and client rendering;
- public project content and metadata are server-rendered;
- file-based routing and deployment output support a coherent app framework;
- same project teaches browser/server runtime differences.

Negative:

- hydration and dual-runtime behavior add complexity;
- internal versus public API base URLs require explicit configuration;
- frontend tests need Nuxt-aware utilities.

## Revisit when

The product is entirely authenticated with no server-rendered/public requirement, or the target organization uses a different Vue meta-framework.
