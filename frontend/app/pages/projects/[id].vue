<script setup lang="ts">
import type { Task, TaskStatus } from '~/types'

definePageMeta({ title: 'Project detail', middleware: ['auth'] })
useSeoMeta({ robots: 'noindex' })

const route = useRoute()
const projectId = Number(route.params.id)

const { getProject } = useProjects()
const { listTasks, createTask, advanceTask, deleteTask } = useTasks(projectId)

const project = ref<Awaited<ReturnType<typeof getProject>> | null>(null)
const tasks = ref<Task[]>([])
const pending = ref(true)
const fetchError = ref<string | null>(null)

// Create task form
const showTaskForm = ref(false)
const creatingTask = ref(false)
const taskError = ref<string | null>(null)
const newTaskTitle = ref('')

useSeoMeta({ title: () => project.value ? `${project.value.name} — Workboard` : 'Project detail' })

onMounted(async () => {
  try {
    ;[project.value, tasks.value] = await Promise.all([
      getProject(projectId),
      listTasks(),
    ])
  }
  catch (err: unknown) {
    fetchError.value = (err as { message?: string })?.message ?? 'Project not found or access denied.'
  }
  finally {
    pending.value = false
  }
})

async function handleAdvance(taskId: number, toStatus: TaskStatus) {
  taskError.value = null
  try {
    const updated = await advanceTask(taskId, toStatus)
    const idx = tasks.value.findIndex(t => t.id === taskId)
    if (idx !== -1) tasks.value[idx] = updated
  }
  catch (err: unknown) {
    taskError.value = (err as { message?: string })?.message ?? 'Could not update task.'
  }
}

async function handleDelete(taskId: number) {
  taskError.value = null
  try {
    await deleteTask(taskId)
    tasks.value = tasks.value.filter(t => t.id !== taskId)
  }
  catch (err: unknown) {
    taskError.value = (err as { message?: string })?.message ?? 'Could not delete task.'
  }
}

async function handleCreateTask() {
  if (creatingTask.value) return
  taskError.value = null
  creatingTask.value = true
  try {
    const task = await createTask({ title: newTaskTitle.value })
    tasks.value.push(task)
    newTaskTitle.value = ''
    showTaskForm.value = false
  }
  catch (err: unknown) {
    taskError.value = (err as { message?: string })?.message ?? 'Failed to create task.'
  }
  finally {
    creatingTask.value = false
  }
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
          <button type="button" class="btn btn-primary btn-sm" @click="showTaskForm = !showTaskForm">
            {{ showTaskForm ? 'Cancel' : 'Add task' }}
          </button>
        </div>

        <div v-if="showTaskForm" class="task-form">
          <form @submit.prevent="handleCreateTask">
            <div class="form-group">
              <label for="task-title" class="form-label">Task title</label>
              <input
                id="task-title"
                v-model="newTaskTitle"
                type="text"
                class="form-input"
                required
                :disabled="creatingTask"
              >
            </div>
            <button type="submit" class="btn btn-primary btn-sm" :disabled="creatingTask">
              {{ creatingTask ? 'Adding…' : 'Add task' }}
            </button>
          </form>
        </div>

        <UiErrorAlert v-if="taskError" :message="taskError" />

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

    <!-- Loading / error / project-not-found states handled above -->
    <div v-else class="empty-state">
      <p>Project #{{ projectId }} not found or access denied.</p>
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
.task-form {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: 8px;
  padding: var(--space-4);
  margin-bottom: var(--space-4);
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
}
.empty-state {
  padding: var(--space-8);
  text-align: center;
  border: 1px dashed var(--color-border);
  border-radius: 10px;
  color: var(--color-text-muted);
}
</style>
