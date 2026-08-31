import { vi } from 'vitest'
import * as Vue from 'vue'
import { config } from '@vue/test-utils'

// Replicate Nuxt's Vue auto-imports in the test environment.
// Components under test use these without explicit imports.
Object.assign(globalThis, {
  ref: Vue.ref,
  computed: Vue.computed,
  reactive: Vue.reactive,
  readonly: Vue.readonly,
  watch: Vue.watch,
  watchEffect: Vue.watchEffect,
  onMounted: Vue.onMounted,
  onUnmounted: Vue.onUnmounted,
  nextTick: Vue.nextTick,
  toRef: Vue.toRef,
  toRefs: Vue.toRefs,
})

// Mock Nuxt router / navigation composables
;(globalThis as Record<string, unknown>).navigateTo = vi.fn()
;(globalThis as Record<string, unknown>).useRoute = () => ({ params: {}, query: {}, path: '/' })
;(globalThis as Record<string, unknown>).useRouter = () => ({ push: vi.fn(), replace: vi.fn() })
;(globalThis as Record<string, unknown>).useRuntimeConfig = () => ({
  public: { apiBase: 'http://localhost:8000/api/v1' },
  apiInternalBase: 'http://backend:8000/api/v1',
})
;(globalThis as Record<string, unknown>).definePageMeta = () => {}
;(globalThis as Record<string, unknown>).useSeoMeta = () => {}

// Stub Nuxt-specific global components
config.global.stubs = {
  NuxtLink: { props: ['to'], template: '<a :href="to"><slot /></a>' },
}
