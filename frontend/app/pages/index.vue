<script setup lang="ts">
const { data, error } = await useFetch<{ status: string }>('/api/health')

useSeoMeta({
  title: 'Workboard workshop starter',
  description: 'A verified starting point for the full-stack intern workshop.'
})
</script>

<template>
  <main class="shell">
    <p class="eyebrow">Full-stack intern workshop</p>
    <h1>Workboard starter is running</h1>
    <p>
      Nuxt rendered this page. The next modules introduce the API contract, domain,
      tests, Docker quality gates, continuous integration, and Google Cloud delivery.
    </p>
    <p v-if="data" class="success">Nuxt server health: {{ data.status }}</p>
    <p v-else class="error">Nuxt health failed: {{ error?.message }}</p>
  </main>
</template>
