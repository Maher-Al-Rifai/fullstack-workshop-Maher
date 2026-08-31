<script setup lang="ts">
definePageMeta({
  title: 'Sign in',
  middleware: [
    // Redirect authenticated users away from the login page.
    () => {
      if (import.meta.server) return
      const auth = useAuthStore()
      if (auth.isAuthenticated) return navigateTo('/dashboard')
    },
  ],
})

useSeoMeta({ title: 'Sign in — Workboard', robots: 'noindex' })

const route = useRoute()
const auth = useAuthStore()

const email = ref('')
const password = ref('')
const error = ref<string | null>(null)
const pending = ref(false)

async function handleSubmit() {
  error.value = null
  pending.value = true
  try {
    await auth.login({ email: email.value, password: password.value })
    const redirect = typeof route.query.redirect === 'string' ? route.query.redirect : '/dashboard'
    await navigateTo(redirect)
  }
  catch (err: unknown) {
    error.value = (err as { message?: string })?.message ?? 'Invalid email or password.'
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
        <h1 class="auth-title">Sign in to Workboard</h1>
        <p class="auth-sub">
          Don't have an account?
          <NuxtLink to="/register">Register</NuxtLink>
        </p>
      </header>

      <UiErrorAlert v-if="error" :message="error" />

      <form class="auth-form" novalidate @submit.prevent="handleSubmit">
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
            aria-describedby="email-hint"
          >
          <span id="email-hint" class="form-hint">We'll never share your email.</span>
        </div>

        <div class="form-group">
          <label for="password" class="form-label">Password</label>
          <input
            id="password"
            v-model="password"
            type="password"
            class="form-input"
            autocomplete="current-password"
            required
            :disabled="pending"
          >
        </div>

        <button type="submit" class="btn btn-primary btn-full" :disabled="pending">
          {{ pending ? 'Signing in…' : 'Sign in' }}
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
