<script setup lang="ts">
import type { Task, TaskStatus } from '~/types'

const props = defineProps<{ task: Task }>()

const emit = defineEmits<{
  advance: [taskId: number, toStatus: TaskStatus]
  delete: [taskId: number]
}>()

// Only forward transitions are supported by the state machine.
const NEXT_STATUS: Partial<Record<TaskStatus, TaskStatus>> = {
  backlog: 'in_progress',
  in_progress: 'done',
}

const nextStatus = computed(() => NEXT_STATUS[props.task.status] ?? null)
const nextLabel = computed(() =>
  nextStatus.value ? nextStatus.value.replace('_', ' ') : null,
)
</script>

<template>
  <article class="task-card">
    <header class="task-header">
      <StatusBadge :status="task.status" />
      <span class="task-priority" :data-priority="task.priority">
        {{ task.priority }}
      </span>
    </header>

    <h3 class="task-title">{{ task.title }}</h3>
    <p v-if="task.description" class="task-desc">{{ task.description }}</p>

    <div v-if="task.due_date" class="task-meta">
      Due <time :datetime="task.due_date">{{ task.due_date }}</time>
    </div>

    <footer class="task-actions">
      <button
        v-if="nextStatus"
        type="button"
        class="btn btn-sm btn-primary"
        :aria-label="`Move task to ${nextLabel}`"
        @click="emit('advance', task.id, nextStatus!)"
      >
        Move to {{ nextLabel }}
      </button>
      <button
        type="button"
        class="btn btn-sm btn-danger"
        :aria-label="`Delete task ${task.title}`"
        @click="emit('delete', task.id)"
      >
        Delete
      </button>
    </footer>
  </article>
</template>

<style scoped>
.task-card {
  background: white;
  border: 1px solid var(--color-border);
  border-radius: 8px;
  padding: var(--space-4);
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}
.task-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.task-priority {
  font-size: 0.7rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}
.task-priority[data-priority="high"]   { color: #dc2626; }
.task-priority[data-priority="medium"] { color: #d97706; }
.task-priority[data-priority="low"]    { color: #16a34a; }
.task-title {
  font-size: 0.95rem;
  font-weight: 600;
  margin: 0;
}
.task-desc {
  font-size: 0.85rem;
  color: var(--color-text-muted);
  margin: 0;
  line-height: 1.5;
}
.task-meta {
  font-size: 0.8rem;
  color: var(--color-text-muted);
}
.task-actions {
  display: flex;
  gap: var(--space-2);
  margin-top: var(--space-1);
}
</style>
