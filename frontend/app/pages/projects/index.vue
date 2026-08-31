<script setup lang="ts">
import type { Project } from '~/types'

definePageMeta({ title: 'Projects' })

useSeoMeta({ title: 'Projects — Workboard' })

// Placeholder — Module 11 replaces this with a real API call.
const projects: Project[] = []
const pending = false
const fetchError = null
</script>

<template>
  <div>
    <div class="page-header">
      <div class="header-row">
        <h1 class="page-title">Projects</h1>
        <button type="button" class="btn btn-primary">New project</button>
      </div>
    </div>

    <UiLoadingSpinner v-if="pending" label="Loading projects…" />
    <UiErrorAlert v-else-if="fetchError" message="Could not load projects. Try again." />

    <template v-else>
      <div v-if="projects.length === 0" class="empty-state">
        <p>No projects yet. Create one to get started.</p>
        <button type="button" class="btn btn-primary">Create project</button>
      </div>
      <div v-else class="card-grid">
        <ProjectCard
          v-for="project in projects"
          :key="project.id"
          :project="project"
        />
      </div>
    </template>
  </div>
</template>

<style scoped>
.header-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.empty-state {
  padding: var(--space-10);
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
