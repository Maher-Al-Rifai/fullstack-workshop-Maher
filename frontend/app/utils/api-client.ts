export interface ApiError {
  message: string
  status: number
  code?: string
}

type FetchOptions = {
  method?: string
  body?: unknown
  headers?: Record<string, string>
  credentials?: string
  query?: Record<string, unknown>
  _retried?: boolean
}

// Minimal fetcher signature: enough for $fetch and test doubles.
type Fetcher = (url: string, opts: Record<string, unknown>) => Promise<unknown>

export function normalizeError(err: unknown): ApiError {
  const e = err as { data?: { detail?: string; code?: string }; status?: number; message?: string }
  return {
    message: e.data?.detail ?? e.message ?? 'An unexpected error occurred.',
    status: e.status ?? 500,
    code: e.data?.code,
  }
}

export function createApiFetch({
  baseURL,
  getToken,
  onRefresh,
  onUnauthenticated,
  fetcher,
}: {
  baseURL: string
  getToken: () => string | null
  onRefresh: () => Promise<boolean>
  onUnauthenticated: () => Promise<void>
  fetcher: Fetcher
}) {
  async function apiFetch<T>(path: string, options: FetchOptions = {}): Promise<T> {
    const { _retried, ...fetchOptions } = options
    const token = getToken()

    try {
      return await fetcher(path, {
        baseURL,
        ...fetchOptions,
        headers: {
          ...(token ? { Authorization: `Bearer ${token}` } : {}),
          ...(fetchOptions.headers ?? {}),
        },
        credentials: 'include',
      }) as T
    }
    catch (err: unknown) {
      const status = (err as { status?: number })?.status
      if (status === 401 && !_retried) {
        const ok = await onRefresh()
        if (ok) {
          return apiFetch<T>(path, { ...options, _retried: true })
        }
        await onUnauthenticated()
      }
      throw normalizeError(err)
    }
  }

  return { apiFetch }
}
