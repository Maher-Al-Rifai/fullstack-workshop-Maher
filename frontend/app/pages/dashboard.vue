<script setup lang="ts">
definePageMeta({ title: 'Dashboard', middleware: ['auth'] })
useSeoMeta({ title: 'Dashboard — Workboard' })

const auth = useAuthStore()
const { listProjects } = useProjects()

const projects = ref<Awaited<ReturnType<typeof listProjects>>>([])
const pending = ref(true)
const fetchError = ref<string | null>(null)

onMounted(async () => {
  try {
    projects.value = await listProjects()
  }
  catch (err: unknown) {
    fetchError.value = (err as { message?: string })?.message ?? 'Failed to load projects.'
  }
  finally {
    pending.value = false
  }
})
</script>

<template>
  <div>
    <div class="page-header">
      <h1 class="page-title">Dashboard</h1>
      <p class="page-subtitle">Welcome back, {{ auth.user?.full_name }}.</p>
    </div>

    <section aria-label="Your projects">
      <div class="section-header">
        <h2 class="section-title">Projects</h2>
        <NuxtLink to="/projects" class="btn btn-primary btn-sm">New project</NuxtLink>
      </div>

      <!-- Loading state -->
      <UiLoadingSpinner v-if="pending" label="Loading projects…" />

      <!-- Error state -->
      <UiErrorAlert v-else-if="fetchError" :message="fetchError" />

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
