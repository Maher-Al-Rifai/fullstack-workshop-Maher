<script setup lang="ts">
import type { Project } from '~/types'

defineProps<{ project: Project }>()
</script>

<template>
  <article class="project-card">
    <header class="card-header">
      <h2 class="card-title">
        <NuxtLink :to="`/projects/${project.id}`">{{ project.name }}</NuxtLink>
      </h2>
      <span
        class="visibility-badge"
        :aria-label="project.is_public ? 'Public project' : 'Private project'"
      >
        {{ project.is_public ? 'Public' : 'Private' }}
      </span>
    </header>
    <p v-if="project.description" class="card-description">
      {{ project.description }}
    </p>
    <footer class="card-footer">
      <span class="card-meta">{{ project.slug }}</span>
    </footer>
  </article>
</template>

<style scoped>
.project-card {
  background: white;
  border: 1px solid var(--color-border);
  border-radius: 10px;
  padding: var(--space-5);
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
  transition: box-shadow 0.15s;
}
.project-card:hover {
  box-shadow: 0 4px 12px rgb(0 0 0 / 8%);
}
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: var(--space-3);
}
.card-title {
  font-size: 1.05rem;
  font-weight: 600;
  margin: 0;
}
.card-title a {
  color: var(--color-text);
  text-decoration: none;
}
.card-title a:hover { text-decoration: underline; }
.card-title a:focus-visible {
  outline: 2px solid var(--color-brand);
  outline-offset: 2px;
  border-radius: 3px;
}
.visibility-badge {
  font-size: 0.7rem;
  font-weight: 600;
  padding: 2px 7px;
  border-radius: 999px;
  background: var(--color-surface);
  color: var(--color-text-muted);
  flex-shrink: 0;
}
.card-description {
  color: var(--color-text-muted);
  font-size: 0.9rem;
  margin: 0;
  line-height: 1.5;
}
.card-footer {
  margin-top: auto;
}
.card-meta {
  font-size: 0.75rem;
  color: var(--color-text-muted);
  font-family: ui-monospace, monospace;
}
</style>
