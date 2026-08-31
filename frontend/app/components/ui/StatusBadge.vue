<script setup lang="ts">
import type { TaskStatus } from '~/types'
import { STATUS_LABELS } from '~/utils/labels'

const props = defineProps<{ status: TaskStatus }>()
</script>

<template>
  <span :class="['badge', `badge--${props.status.replace('_', '-')}`]">
    {{ STATUS_LABELS[props.status] }}
  </span>
</template>

<style scoped>
.badge {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 999px;
  font-size: 0.75rem;
  font-weight: 600;
  letter-spacing: 0.02em;
}
.badge--backlog      { background: #f1f5f9; color: #475569; }
.badge--in-progress  { background: #eff6ff; color: #1d4ed8; }
.badge--done         { background: #f0fdf4; color: #15803d; }
.badge--cancelled    { background: #fafafa; color: #737373; text-decoration: line-through; }
</style>
