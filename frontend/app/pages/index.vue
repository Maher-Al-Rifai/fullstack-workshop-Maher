<script setup lang="ts">
useSeoMeta({
  title: 'Workboard — Full-Stack Workshop',
  description: 'A team task board built across 19 workshop modules with FastAPI, PostgreSQL, and Nuxt.',
  ogTitle: 'Workboard — Full-Stack Workshop',
  ogDescription: 'A team task board built across 19 workshop modules with FastAPI, PostgreSQL, and Nuxt.',
  ogType: 'website',
})
</script>

<template>
  <div>
    <section class="hero">
      <p class="eyebrow">Full-Stack Intern Workshop</p>
      <h1 class="hero-title">Build a real product, end to end.</h1>
      <p class="hero-lead">
        Workboard is the capstone application connecting all 19 modules — from
        Docker fundamentals to Google Cloud deployment. You build the API, the
        database, the frontend, and the CI/CD pipeline.
      </p>
      <div class="hero-actions">
        <NuxtLink to="/register" class="btn btn-primary">Get started</NuxtLink>
        <NuxtLink to="/login" class="btn btn-ghost">Sign in</NuxtLink>
      </div>
    </section>

    <section class="features" aria-label="Key features">
      <article class="feature-card">
        <h2 class="feature-title">Projects</h2>
        <p>Create public or private projects with auto-generated slugs and team membership.</p>
      </article>
      <article class="feature-card">
        <h2 class="feature-title">Tasks</h2>
        <p>Move tasks through a defined lifecycle: backlog → in progress → done.</p>
      </article>
      <article class="feature-card">
        <h2 class="feature-title">Teams</h2>
        <p>Invite members to collaborate. Access control enforced at every API endpoint.</p>
      </article>
    </section>
  </div>
</template>

<style scoped>
.hero {
  padding: var(--space-10) 0;
  max-width: 640px;
}
.eyebrow {
  font-size: 0.8rem;
  font-weight: 700;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: var(--color-brand);
  margin-bottom: var(--space-3);
}
.hero-title {
  font-size: clamp(2rem, 6vw, 3.25rem);
  font-weight: 800;
  line-height: 1.1;
  margin-bottom: var(--space-5);
}
.hero-lead {
  font-size: 1.1rem;
  color: var(--color-text-muted);
  max-width: 520px;
}
.hero-actions {
  display: flex;
  gap: var(--space-3);
  flex-wrap: wrap;
  margin-top: var(--space-6);
}
.features {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
  gap: var(--space-5);
  padding-top: var(--space-8);
  border-top: 1px solid var(--color-border);
}
.feature-card {
  padding: var(--space-5);
  background: white;
  border: 1px solid var(--color-border);
  border-radius: 10px;
}
.feature-title {
  font-size: 1.05rem;
  font-weight: 700;
  margin-bottom: var(--space-2);
}
.feature-card p {
  color: var(--color-text-muted);
  font-size: 0.9rem;
  margin: 0;
}
</style>
