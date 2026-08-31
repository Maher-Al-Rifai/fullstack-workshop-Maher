export default defineNuxtConfig({
  compatibilityDate: '2026-07-01',
  devtools: { enabled: false },
  modules: ['@pinia/nuxt', '@nuxt/eslint'],
  css: ['~/assets/css/main.css'],
  runtimeConfig: {
    // server-side only — never exposed to the browser
    apiInternalBase: process.env.NUXT_API_INTERNAL_BASE || 'http://localhost:8000/api/v1',
    public: {
      // exposed to the browser — must never contain secrets
      apiBase: process.env.NUXT_PUBLIC_API_BASE || 'http://localhost:8000/api/v1',
    },
  },
  typescript: {
    strict: true,
    typeCheck: true,
  },
})
