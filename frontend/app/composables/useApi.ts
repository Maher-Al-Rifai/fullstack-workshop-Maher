import { createApiFetch } from '~/utils/api-client'
import type { ApiError } from '~/utils/api-client'

export type { ApiError }

export function useApi() {
  const auth = useAuthStore()
  const config = useRuntimeConfig()

  return createApiFetch({
    baseURL: config.public.apiBase,
    getToken: () => auth.accessToken,
    onRefresh: () => auth.refresh(),
    onUnauthenticated: async () => {
      auth.user = null
      auth.accessToken = null
      await navigateTo('/login')
    },
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    fetcher: ($fetch as any),
  })
}
