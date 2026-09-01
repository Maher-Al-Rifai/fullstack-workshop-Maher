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
  const e = err as {
    data?: { detail?: string | Array<{ msg?: string }>; code?: string }
    status?: number
    message?: string
  }
  const status = e.status ?? 500
  const detail = e.data?.detail

  let message: string
  if (typeof detail === 'string' && detail) {
    message = detail
  } else if (Array.isArray(detail) && detail.length > 0) {
    // Pydantic validation error list — surface the first human-readable message
    message = detail[0]?.msg ?? 'Please check your input and try again.'
  } else {
    switch (status) {
      case 400: message = 'Bad request. Please check your input.'; break
      case 401: message = 'Invalid email or password.'; break
      case 403: message = 'You don\'t have permission to do that.'; break
      case 404: message = 'Not found.'; break
      case 409: message = 'A conflict occurred — that record may already exist.'; break
      case 422: message = 'Please check your input and try again.'; break
      case 429: message = 'Too many requests. Please slow down.'; break
      case 500: message = 'Server error. Please try again later.'; break
      default:  message = e.message?.includes('fetch') ? 'Could not reach the server. Check your connection.' : (e.message ?? 'An unexpected error occurred.')
    }
  }

  return { message, status, code: e.data?.code }
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
