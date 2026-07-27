# Module 10: Nuxt, Vue, and TypeScript foundation

**Guided effort:** 10 hours  
**Required branch:** `learning/10-nuxt-foundation`  
**Phase:** Frontend

## Objectives

- Explain Nuxt application structure, Vue Composition API, reactive state, props/events, pages, layouts, and runtime configuration.
- Create typed, semantic, reusable UI components and route-level pages.
- Handle loading, empty, error, and success states explicitly.
- Use accessibility-first HTML and responsive CSS without making styling the primary objective.

## Prerequisites

- Backend gate passed.
- Basic HTML, CSS, JavaScript, and TypeScript reading ability.

## Concepts and context

Vue components combine a rendered template, reactive state, and behavior. Nuxt adds application conventions: file-based routes, layouts, plugins, middleware, server routes, universal rendering, and deployment output. TypeScript improves contracts but cannot validate untrusted network data by itself.

Pages coordinate route-level data; components should have focused prop/event contracts; reusable request behavior belongs in composables/services. Start with semantic HTML. A visually styled `div` is not automatically a button, label, heading, or navigation landmark.

## Step-by-step lab

### 1. Inspect or initialize Nuxt

From `frontend/`, inspect `package.json`, `nuxt.config.ts`, `app/app.vue`, and the `app/` directories. Identify what runs on both server and browser versus `.client`-only code.

Run:

```bash
cd frontend
npm install
npm run dev -- --host 0.0.0.0
```

The Docker path remains canonical for the shared environment; host execution is useful for fast frontend iteration.

### 2. Configure TypeScript and runtime settings

Keep strict TypeScript enabled. Define:

- private `apiInternalBase` for server-side Nuxt requests;
- public `apiBase` for browser requests.

Explain why any value under public runtime configuration is visible to the browser and must never contain a secret.

### 3. Build the application shell

Create or inspect:

- `app.vue` with header/main/footer structure;
- `AppHeader` using navigation landmarks and real links/buttons;
- global design tokens and responsive layout rules;
- home page describing the capstone.

Check heading hierarchy, link purpose, focus visibility, and viewport behavior.

### 4. Define TypeScript API contracts

Create explicit `User`, `Project`, `Task`, status, priority, auth response, and public project types. Keep fields aligned with the documented API. Discuss the limitation: a TypeScript interface does not prove runtime JSON conforms; backend schemas and optional runtime validation protect that boundary.

### 5. Create reusable display components

Implement:

- loading indicator with understandable text;
- error alert;
- status badge containing text;
- project card;
- task card with emitted advance/delete actions.

Use typed `defineProps`/`defineEmits`. Keep network calls out of presentational components.

### 6. Build route pages

Baseline routes:

```text
/
/login
/register
/dashboard
/projects
/projects/[id]
/public/projects/[slug]
```

At this stage, use temporary local data for authenticated pages if the API client is not yet wired. Include loading/empty/error placeholders so page structure does not assume success.

### 7. Accessibility walkthrough

Using keyboard only:

- move through header navigation;
- reach and activate forms/buttons/links;
- see focus clearly;
- associate every input with a label;
- identify errors without relying only on color.

Use browser accessibility inspection to confirm names and roles for key controls.

### 8. Run frontend quality

```bash
npm run lint
npm run typecheck
npm run build
```

Treat build as important because universal rendering can expose server-only errors not visible during a client navigation.

## Validation checklist

- [ ] Nuxt application builds with strict TypeScript.
- [ ] Private and public runtime configuration are correctly separated.
- [ ] Pages and components have clear responsibilities.
- [ ] Core display components use typed props/events.
- [ ] Every form input has a label and controls work by keyboard.
- [ ] Loading, empty, error, and success states are represented.
- [ ] No API secret or token is placed in public runtime configuration.

## Independent challenge

Create a reusable pagination component with accessible previous/next controls, current page announcement, typed props/events, disabled boundary states, and a component test plan. It may remain unused until task filtering/pagination is implemented.

## Common failure modes

- Using `any` to bypass API contract mismatches.
- Putting every state value in Pinia before it is shared.
- Calling the backend directly from presentational components.
- Using clickable `div` elements without keyboard/role behavior.
- Accessing `window` during server rendering.

## Evidence to submit

- Annotated frontend directory map.
- Screenshot or recording of responsive page states.
- Accessibility inspection for one form and navigation.
- Lint/typecheck/build output.
- One explanation of page versus component versus composable responsibility.

## Commit checkpoint

```text
feat(web): establish typed Nuxt application foundation
```

Update the learning log before requesting review. The reviewer records the module or gate decision in the linked issue.

## Official references

- [architecture.md](../docs/architecture.md)
- [accessibility-and-seo.md](../docs/accessibility-and-seo.md)
- [introduction](https://nuxt.com/docs/getting-started/introduction)
- [overview.html](https://vuejs.org/guide/typescript/overview.html)
- [accessibility.html](https://vuejs.org/guide/best-practices/accessibility.html)
