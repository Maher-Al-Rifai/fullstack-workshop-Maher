// Runs only in the browser — initializes auth state from the refresh cookie.
export default defineNuxtPlugin(async () => {
  const auth = useAuthStore()
  await auth.initialize()
})
