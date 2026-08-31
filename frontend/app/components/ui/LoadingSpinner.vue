<script setup lang="ts">
withDefaults(defineProps<{ label?: string }>(), { label: 'Loading…' })
</script>

<template>
  <div class="loading" role="status" aria-live="polite">
    <span class="spinner" aria-hidden="true" />
    <span class="loading-label">{{ label }}</span>
  </div>
</template>

<style scoped>
.loading {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  padding: var(--space-6);
  color: var(--color-text-muted);
}
.spinner {
  display: inline-block;
  width: 20px;
  height: 20px;
  border: 2px solid var(--color-border);
  border-top-color: var(--color-brand);
  border-radius: 50%;
  animation: spin 0.7s linear infinite;
  flex-shrink: 0;
}
.loading-label {
  font-size: 0.9rem;
}
@keyframes spin {
  to { transform: rotate(360deg); }
}
</style>
