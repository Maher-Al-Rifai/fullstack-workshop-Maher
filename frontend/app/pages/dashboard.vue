<script setup lang="ts">
import type { Project } from '~/types'

definePageMeta({ title: 'Dashboard' })

useSeoMeta({ title: 'Dashboard — Workboard' })

// Placeholder data until Module 11 wires the auth composable and API client.
const projects: Project[] = [
  {
    id: 1,
    name: 'Capstone delivery plan',
    description: 'All 19 workshop modules tracked as tasks.',
    slug: 'capstone-delivery-plan',
    is_public: true,
    owner_id: 1,
    created_at: '2026-01-01T00:00:00.000Z',
    updated_at: '2026-01-01T00:00:00.000Z',
  },
]
</script>

<template>
  <div>
    <div class="page-header">
      <h1 class="page-title">Dashboard</h1>
      <p class="page-subtitle">Your projects and recent activity.</p>
    </div>

    <section aria-label="Your projects">
      <div class="section-header">
        <h2 class="section-title">Projects</h2>
        <NuxtLink to="/projects" class="btn btn-primary btn-sm">New project</NuxtLink>
      </div>

      <!-- Loading state -->
      <!-- <UiLoadingSpinner label="Loading projects…" /> -->

      <!-- Error state -->
      <!-- <UiErrorAlert message="Could not load projects." /> -->

      <!-- Empty state -->
      <div v-if="projects.length === 0" class="empty-state">
        <p>No projects yet.</p>
        <NuxtLink to="/projects" class="btn btn-primary">Create your first project</NuxtLink>
      </div>

      <!-- Success state -->
      <div v-else class="card-grid">
        <ProjectCard
          v-for="project in projects"
          :key="project.id"
          :project="project"
        />
      </div>
    </section>
  </div>
</template>

<style scoped>
.page-subtitle { color: var(--color-text-muted); margin-top: calc(-1 * var(--space-2)); }
.section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: var(--space-5);
}
.section-title { font-size: 1.1rem; font-weight: 600; margin: 0; }
.empty-state {
  padding: var(--space-10) var(--space-6);
  text-align: center;
  border: 1px dashed var(--color-border);
  border-radius: 10px;
  color: var(--color-text-muted);
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--space-4);
}
</style>
