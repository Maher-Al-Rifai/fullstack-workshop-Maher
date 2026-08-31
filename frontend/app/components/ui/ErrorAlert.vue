<script setup lang="ts">
defineProps<{ message: string }>()
</script>

<template>
  <div class="error-alert" role="alert">
    <strong class="error-label">Error:</strong>
    <span class="error-message">{{ message }}</span>
  </div>
</template>

<style scoped>
.error-alert {
  display: flex;
  gap: var(--space-2);
  padding: var(--space-3) var(--space-4);
  background: #fef2f2;
  border: 1px solid #fecaca;
  border-radius: 8px;
  color: #991b1b;
  font-size: 0.9rem;
}
.error-label {
  flex-shrink: 0;
}
</style>
