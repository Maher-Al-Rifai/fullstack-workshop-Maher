<script setup lang="ts">
import { normalizeError } from '~/utils/api-client'

definePageMeta({
  title: 'Register',
  middleware: [
    () => {
      if (import.meta.server) return
      const auth = useAuthStore()
      if (auth.isAuthenticated) return navigateTo('/dashboard')
    },
  ],
})

useSeoMeta({ title: 'Create account — Workboard', robots: 'noindex' })

const auth = useAuthStore()

const fullName = ref('')
const email = ref('')
const password = ref('')
const error = ref<string | null>(null)
const pending = ref(false)

async function handleSubmit() {
  error.value = null
  pending.value = true
  try {
    await auth.register({ email: email.value, full_name: fullName.value, password: password.value })
    await navigateTo('/dashboard')
  }
  catch (err: unknown) {
    error.value = normalizeError(err).message
  }
  finally {
    pending.value = false
  }
}
</script>

<template>
  <div class="auth-page">
    <div class="auth-card">
      <header class="auth-header">
        <h1 class="auth-title">Create your account</h1>
        <p class="auth-sub">
          Already registered?
          <NuxtLink to="/login">Sign in</NuxtLink>
        </p>
      </header>

      <UiErrorAlert v-if="error" :message="error" />

      <form class="auth-form" novalidate @submit.prevent="handleSubmit">
        <div class="form-group">
          <label for="full-name" class="form-label">Full name</label>
          <input
            id="full-name"
            v-model="fullName"
            type="text"
            class="form-input"
            autocomplete="name"
            required
            :disabled="pending"
          >
        </div>

        <div class="form-group">
          <label for="email" class="form-label">Email address</label>
          <input
            id="email"
            v-model="email"
            type="email"
            class="form-input"
            autocomplete="email"
            required
            :disabled="pending"
          >
        </div>

        <div class="form-group">
          <label for="password" class="form-label">Password</label>
          <input
            id="password"
            v-model="password"
            type="password"
            class="form-input"
            autocomplete="new-password"
            minlength="8"
            required
            :disabled="pending"
            aria-describedby="password-hint"
          >
          <span id="password-hint" class="form-hint">Minimum 8 characters.</span>
        </div>

        <button type="submit" class="btn btn-primary btn-full" :disabled="pending">
          {{ pending ? 'Creating account…' : 'Create account' }}
        </button>
      </form>
    </div>
  </div>
</template>

<style scoped>
.auth-page {
  display: flex;
  justify-content: center;
  padding-top: var(--space-8);
}
.auth-card {
  background: white;
  border: 1px solid var(--color-border);
  border-radius: 12px;
  padding: var(--space-8);
  width: 100%;
  max-width: 420px;
  display: flex;
  flex-direction: column;
  gap: var(--space-5);
}
.auth-header { text-align: center; }
.auth-title { font-size: 1.5rem; font-weight: 700; margin-bottom: var(--space-2); }
.auth-sub { color: var(--color-text-muted); font-size: 0.9rem; margin: 0; }
.auth-sub a { color: var(--color-brand); }
.auth-form { display: flex; flex-direction: column; gap: var(--space-4); }
.form-hint { font-size: 0.75rem; color: var(--color-text-muted); }
.btn-full { width: 100%; justify-content: center; }
</style>
