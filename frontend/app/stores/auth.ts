import { defineStore } from 'pinia'
import type { User, TokenResponse, LoginRequest, RegisterRequest } from '~/types'

export const useAuthStore = defineStore('auth', () => {
  const user = ref<User | null>(null)
  const accessToken = ref<string | null>(null)
  const initialized = ref(false)

  const isAuthenticated = computed(() => !!user.value)

  async function login(credentials: LoginRequest): Promise<void> {
    const config = useRuntimeConfig()
    const data = await $fetch<TokenResponse>('/auth/login', {
      baseURL: config.public.apiBase,
      method: 'POST',
      body: { email: credentials.email, password: credentials.password },
      credentials: 'include',
    })
    accessToken.value = data.access_token
    await loadMe()
  }

  async function register(payload: RegisterRequest): Promise<void> {
    const config = useRuntimeConfig()
    await $fetch<User>('/auth/register', {
      baseURL: config.public.apiBase,
      method: 'POST',
      body: payload,
    })
    await login({ email: payload.email, password: payload.password })
  }

  async function refresh(): Promise<boolean> {
    try {
      const config = useRuntimeConfig()
      const data = await $fetch<TokenResponse>('/auth/refresh', {
        baseURL: config.public.apiBase,
        method: 'POST',
        credentials: 'include',
      })
      accessToken.value = data.access_token
      return true
    }
    catch {
      return false
    }
  }

  async function loadMe(): Promise<void> {
    const config = useRuntimeConfig()
    user.value = await $fetch<User>('/auth/me', {
      baseURL: config.public.apiBase,
      headers: accessToken.value
        ? { Authorization: `Bearer ${accessToken.value}` }
        : {},
    })
  }

  // Called once by auth.client.ts plugin on first browser load.
  async function initialize(): Promise<void> {
    if (initialized.value) return
    const ok = await refresh()
    if (ok) {
      try { await loadMe() }
      catch { user.value = null; accessToken.value = null }
    }
    initialized.value = true
  }

  async function logout(): Promise<void> {
    try {
      const config = useRuntimeConfig()
      await $fetch('/auth/logout', {
        baseURL: config.public.apiBase,
        method: 'POST',
        credentials: 'include',
      })
    }
    finally {
      user.value = null
      accessToken.value = null
    }
  }

  return {
    user,
    accessToken,
    initialized,
    isAuthenticated,
    login,
    register,
    refresh,
    loadMe,
    initialize,
    logout,
  }
})
