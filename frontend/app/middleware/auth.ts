// Protects /dashboard and /projects/* — client-only to avoid SSR hydration mismatch.
export default defineNuxtRouteMiddleware((to) => {
  if (import.meta.server) return

  const auth = useAuthStore()

  // Plugin hasn't finished yet — let the page mount and re-evaluate.
  if (!auth.initialized) return

  if (!auth.isAuthenticated) {
    const redirect = encodeURIComponent(to.fullPath)
    return navigateTo(`/login?redirect=${redirect}`)
  }
})
