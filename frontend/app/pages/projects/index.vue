<script setup lang="ts">
import type { Project } from '~/types'
import { normalizeError } from '~/utils/api-client'

definePageMeta({ title: 'Projects', middleware: ['auth'] })
useSeoMeta({ title: 'Projects — Workboard', robots: 'noindex' })

const { listProjects, createProject } = useProjects()

const projects = ref<Project[]>([])
const pending = ref(true)
const fetchError = ref<string | null>(null)

// Create form state
const showForm = ref(false)
const creating = ref(false)
const createError = ref<string | null>(null)
const newName = ref('')
const newDescription = ref('')
const newIsPublic = ref(false)

onMounted(async () => {
  try {
    projects.value = await listProjects()
  }
  catch (err: unknown) {
    fetchError.value = normalizeError(err).message
  }
  finally {
    pending.value = false
  }
})

async function handleCreate() {
  if (creating.value) return
  createError.value = null
  creating.value = true
  try {
    const project = await createProject({
      name: newName.value,
      description: newDescription.value || undefined,
      is_public: newIsPublic.value,
    })
    projects.value.unshift(project)
    showForm.value = false
    newName.value = ''
    newDescription.value = ''
    newIsPublic.value = false
  }
  catch (err: unknown) {
    createError.value = normalizeError(err).message
  }
  finally {
    creating.value = false
  }
}
</script>

<template>
  <div>
    <div class="page-header">
      <div class="header-row">
        <h1 class="page-title">Projects</h1>
        <button type="button" class="btn btn-primary" @click="showForm = !showForm">
          {{ showForm ? 'Cancel' : 'New project' }}
        </button>
      </div>
    </div>

    <div v-if="showForm" class="create-form">
      <h2 class="form-title">New project</h2>
      <UiErrorAlert v-if="createError" :message="createError" />
      <form @submit.prevent="handleCreate">
        <div class="form-group">
          <label for="proj-name" class="form-label">Project name</label>
          <input id="proj-name" v-model="newName" type="text" class="form-input" required :disabled="creating">
        </div>
        <div class="form-group">
          <label for="proj-desc" class="form-label">Description <span class="optional">(optional)</span></label>
          <input id="proj-desc" v-model="newDescription" type="text" class="form-input" :disabled="creating">
        </div>
        <div class="form-check">
          <input id="proj-public" v-model="newIsPublic" type="checkbox" :disabled="creating">
          <label for="proj-public">Make this project public</label>
        </div>
        <button type="submit" class="btn btn-primary" :disabled="creating">
          {{ creating ? 'Creating…' : 'Create project' }}
        </button>
      </form>
    </div>

    <UiLoadingSpinner v-if="pending" label="Loading projects…" />
    <UiErrorAlert v-else-if="fetchError" :message="fetchError" />

    <template v-else>
      <div v-if="projects.length === 0" class="empty-state">
        <p>No projects yet. Create one to get started.</p>
        <button type="button" class="btn btn-primary" @click="showForm = true">
          Create project
        </button>
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
.create-form {
  background: white;
  border: 1px solid var(--color-border);
  border-radius: 10px;
  padding: var(--space-5);
  margin-bottom: var(--space-6);
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
}
.form-title { font-size: 1rem; font-weight: 600; margin: 0; }
.optional { font-weight: 400; color: var(--color-text-muted); font-size: 0.8rem; }
.form-check {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  font-size: 0.9rem;
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
