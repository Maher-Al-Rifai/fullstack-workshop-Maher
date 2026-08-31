<script setup lang="ts">
import type { PublicProject } from '~/types'

const route = useRoute()
const slug = route.params.slug as string
const config = useRuntimeConfig()

// Use the internal base on the server, public base on the client.
const { data: project, error } = await useAsyncData<PublicProject>(
  `public-project-${slug}`,
  () => $fetch(`/api/v1/projects/public/${slug}`, {
    baseURL: import.meta.server ? config.apiInternalBase : config.public.apiBase,
  }),
)

if (!project.value || error.value) {
  throw createError({ statusCode: 404, statusMessage: 'Project not found' })
}

const completion = computed(() =>
  project.value!.task_count
    ? Math.round((project.value!.done_count / project.value!.task_count) * 100)
    : 0,
)

useSeoMeta({
  title: () => `${project.value!.name} — Workboard`,
  description: () => project.value!.description ?? `A public project on Workboard with ${project.value!.task_count} tasks.`,
  ogTitle: () => project.value!.name,
  ogDescription: () => project.value!.description ?? undefined,
  ogType: 'website',
})
</script>

<template>
  <div>
    <div class="page-header">
      <h1 class="page-title">{{ project!.name }}</h1>
      <p v-if="project!.description" class="page-desc">{{ project!.description }}</p>
    </div>

    <section class="stats-row" aria-label="Project statistics">
      <div class="stat-card">
        <span class="stat-value" aria-label="{{ project!.task_count }} total tasks">{{ project!.task_count }}</span>
        <span class="stat-label">Total tasks</span>
      </div>
      <div class="stat-card">
        <span class="stat-value" aria-label="{{ project!.done_count }} completed">{{ project!.done_count }}</span>
        <span class="stat-label">Completed</span>
      </div>
      <div class="stat-card">
        <span class="stat-value" aria-label="{{ completion }}% complete">{{ completion }}%</span>
        <span class="stat-label">Progress</span>
      </div>
    </section>

    <p class="slug-note">Public URL: /public/projects/{{ project!.slug }}</p>
  </div>
</template>

<style scoped>
.page-desc { color: var(--color-text-muted); }
.stats-row {
  display: flex;
  gap: var(--space-5);
  flex-wrap: wrap;
  margin-top: var(--space-6);
}
.stat-card {
  background: white;
  border: 1px solid var(--color-border);
  border-radius: 10px;
  padding: var(--space-5) var(--space-6);
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--space-1);
  min-width: 120px;
}
.stat-value {
  font-size: 2rem;
  font-weight: 700;
  color: var(--color-brand);
}
.stat-label {
  font-size: 0.8rem;
  color: var(--color-text-muted);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}
.slug-note {
  font-size: 0.8rem;
  color: var(--color-text-muted);
  font-family: ui-monospace, monospace;
  margin-top: var(--space-6);
}
</style>
