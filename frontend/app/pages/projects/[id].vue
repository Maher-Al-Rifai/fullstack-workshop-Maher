<script setup lang="ts">
import type { Task, TaskStatus } from '~/types'

const route = useRoute()
const projectId = Number(route.params.id)

useSeoMeta({ title: 'Project detail — Workboard' })

// Placeholder until Module 11 wires the API client.
const project = ref<{ id: number; name: string; description: string | null } | null>(null)
const tasks = ref<Task[]>([])
const pending = ref(false)
const fetchError = ref<string | null>(null)

function handleAdvance(taskId: number, toStatus: TaskStatus) {
  // Module 11 will call PATCH /api/v1/projects/{id}/tasks/{taskId}
  console.log('advance', taskId, toStatus)
}

function handleDelete(taskId: number) {
  // Module 11 will call DELETE /api/v1/projects/{id}/tasks/{taskId}
  console.log('delete', taskId)
}
</script>

<template>
  <div>
    <UiLoadingSpinner v-if="pending" label="Loading project…" />
    <UiErrorAlert v-else-if="fetchError" :message="fetchError" />

    <template v-else-if="project">
      <div class="page-header">
        <NuxtLink to="/projects" class="back-link">← Projects</NuxtLink>
        <h1 class="page-title">{{ project.name }}</h1>
        <p v-if="project.description" class="page-desc">{{ project.description }}</p>
      </div>

      <section aria-label="Tasks">
        <div class="section-header">
          <h2 class="section-title">Tasks</h2>
          <button type="button" class="btn btn-primary btn-sm">Add task</button>
        </div>

        <div v-if="tasks.length === 0" class="empty-state">
          <p>No tasks yet. Add the first one.</p>
        </div>
        <div v-else class="task-list">
          <TaskCard
            v-for="task in tasks"
            :key="task.id"
            :task="task"
            @advance="handleAdvance"
            @delete="handleDelete"
          />
        </div>
      </section>
    </template>

    <!-- Empty placeholder when project ID is not yet resolved -->
    <div v-else class="empty-state">
      <p>Project #{{ projectId }} — connect the API in Module 11 to load data.</p>
    </div>
  </div>
</template>

<style scoped>
.back-link {
  display: inline-block;
  margin-bottom: var(--space-3);
  color: var(--color-text-muted);
  font-size: 0.85rem;
  text-decoration: none;
}
.back-link:hover { color: var(--color-text); }
.page-desc { color: var(--color-text-muted); }
.section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: var(--space-5);
}
.section-title { font-size: 1.1rem; font-weight: 600; margin: 0; }
.task-list { display: flex; flex-direction: column; gap: var(--space-3); }
.empty-state {
  padding: var(--space-8);
  text-align: center;
  border: 1px dashed var(--color-border);
  border-radius: 10px;
  color: var(--color-text-muted);
}
</style>
