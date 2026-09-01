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
  routeRules: {
    // Static home page — prerendered at build time
    '/': { prerender: true },
    // Public project pages — SSR + 60 s stale-while-revalidate
    '/public/projects/**': { swr: 60 },
    // Authenticated pages — client-only; no SSR (auth state is in memory)
    '/dashboard': { ssr: false },
    '/projects': { ssr: false },
    '/projects/**': { ssr: false },
    '/login': { ssr: false },
    '/register': { ssr: false },
  },
  typescript: {
    strict: true,
    // run `npm run typecheck` explicitly; vite-plugin-checker misfires on happy-dom/vitest types
    typeCheck: false,
  },
})
