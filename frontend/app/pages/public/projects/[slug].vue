<script setup lang="ts">
import type { PublicProject } from '~/types'

const route = useRoute()
const slug = route.params.slug as string

const { data: project, status } = useFetch<PublicProject>(
  () => `/api/v1/projects/public/${slug}`,
  {
    baseURL: useRuntimeConfig().public.apiBase,
    ignoreResponseError: true,
  },
)

useSeoMeta({
  title: () => project.value ? `${project.value.name} — Workboard` : 'Project not found',
  description: () => project.value?.description ?? undefined,
})
</script>

<template>
  <div>
    <UiLoadingSpinner v-if="status === 'pending'" label="Loading project…" />

    <UiErrorAlert
      v-else-if="status === 'error' || !project"
      message="This project is private or does not exist."
    />

    <template v-else>
      <div class="page-header">
        <h1 class="page-title">{{ project.name }}</h1>
        <p v-if="project.description" class="page-desc">{{ project.description }}</p>
      </div>

      <section class="stats-row" aria-label="Project statistics">
        <div class="stat-card">
          <span class="stat-value">{{ project.task_count }}</span>
          <span class="stat-label">Total tasks</span>
        </div>
        <div class="stat-card">
          <span class="stat-value">{{ project.done_count }}</span>
          <span class="stat-label">Completed</span>
        </div>
        <div class="stat-card">
          <span class="stat-value">
            {{ project.task_count ? Math.round((project.done_count / project.task_count) * 100) : 0 }}%
          </span>
          <span class="stat-label">Progress</span>
        </div>
      </section>

      <p class="slug-note">Public URL: /public/projects/{{ project.slug }}</p>
    </template>
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
