export interface ApiError {
  message: string
  status: number
  code?: string
}

type ApiFetchOptions = {
  method?: 'GET' | 'POST' | 'PUT' | 'PATCH' | 'DELETE'
  body?: Record<string, unknown> | BodyInit | URLSearchParams
  headers?: Record<string, string>
  credentials?: RequestCredentials
  query?: Record<string, string | number | boolean>
  _retried?: boolean
}

function normalizeError(err: unknown): ApiError {
  const e = err as { data?: { detail?: string; code?: string }; status?: number; message?: string }
  return {
    message: e.data?.detail ?? e.message ?? 'An unexpected error occurred.',
    status: e.status ?? 500,
    code: e.data?.code,
  }
}

export function useApi() {
  const auth = useAuthStore()
  const config = useRuntimeConfig()
  const baseURL = config.public.apiBase

  async function apiFetch<T>(path: string, options: ApiFetchOptions = {}): Promise<T> {
    const { _retried, ...fetchOptions } = options

    try {
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      return await ($fetch as any)(path, {
        baseURL,
        ...fetchOptions,
        headers: {
          ...(auth.accessToken ? { Authorization: `Bearer ${auth.accessToken}` } : {}),
          ...(fetchOptions.headers ?? {}),
        },
        credentials: 'include',
      }) as T
    }
    catch (err: unknown) {
      const status = (err as { status?: number })?.status
      if (status === 401 && !_retried) {
        const ok = await auth.refresh()
        if (ok) {
          return apiFetch<T>(path, { ...options, _retried: true })
        }
        auth.user = null
        auth.accessToken = null
        await navigateTo('/login')
      }
      throw normalizeError(err)
    }
  }

  return { apiFetch }
}
