import { describe, expect, it, vi } from 'vitest'
import { createApiFetch } from '~/utils/api-client'

function makeClient(overrides: Partial<Parameters<typeof createApiFetch>[0]> = {}) {
  return createApiFetch({
    baseURL: 'http://api.test',
    getToken: () => 'test-token',
    onRefresh: vi.fn().mockResolvedValue(false),
    onUnauthenticated: vi.fn().mockResolvedValue(undefined),
    fetcher: vi.fn().mockResolvedValue({ ok: true }),
    ...overrides,
  })
}

// ---------------------------------------------------------------------------
// Request shaping
// ---------------------------------------------------------------------------

describe('apiFetch request shaping', () => {
  it('sends bearer token from getToken', async () => {
    const fetcher = vi.fn().mockResolvedValue({})
    const { apiFetch } = makeClient({ fetcher, getToken: () => 'abc123' })
    await apiFetch('/projects')
    expect(fetcher).toHaveBeenCalledWith(
      '/projects',
      expect.objectContaining({
        headers: expect.objectContaining({ Authorization: 'Bearer abc123' }),
      }),
    )
  })

  it('sends no Authorization header when token is null', async () => {
    const fetcher = vi.fn().mockResolvedValue({})
    const { apiFetch } = makeClient({ fetcher, getToken: () => null })
    await apiFetch('/public')
    const opts = fetcher.mock.calls[0][1] as Record<string, unknown>
    expect((opts.headers as Record<string, string>).Authorization).toBeUndefined()
  })

  it('uses the configured baseURL', async () => {
    const fetcher = vi.fn().mockResolvedValue({})
    const { apiFetch } = makeClient({ fetcher, baseURL: 'http://custom.api' })
    await apiFetch('/health')
    expect(fetcher).toHaveBeenCalledWith('/health', expect.objectContaining({ baseURL: 'http://custom.api' }))
  })

  it('forwards method and body', async () => {
    const fetcher = vi.fn().mockResolvedValue({})
    const { apiFetch } = makeClient({ fetcher })
    await apiFetch('/tasks', { method: 'POST', body: { title: 'Fix bug' } })
    expect(fetcher).toHaveBeenCalledWith(
      '/tasks',
      expect.objectContaining({ method: 'POST', body: { title: 'Fix bug' } }),
    )
  })

  it('returns the fetcher response', async () => {
    const fetcher = vi.fn().mockResolvedValue({ id: 7 })
    const { apiFetch } = makeClient({ fetcher })
    const result = await apiFetch<{ id: number }>('/x')
    expect(result).toEqual({ id: 7 })
  })
})

// ---------------------------------------------------------------------------
// 401 retry / refresh
// ---------------------------------------------------------------------------

describe('apiFetch 401 handling', () => {
  it('calls onRefresh on first 401', async () => {
    const onRefresh = vi.fn().mockResolvedValue(false)
    const fetcher = vi.fn().mockRejectedValue({ status: 401 })
    const { apiFetch } = makeClient({ fetcher, onRefresh })
    await expect(apiFetch('/protected')).rejects.toBeDefined()
    expect(onRefresh).toHaveBeenCalledOnce()
  })

  it('retries with new token after successful refresh', async () => {
    const onRefresh = vi.fn().mockResolvedValue(true)
    const fetcher = vi.fn()
      .mockRejectedValueOnce({ status: 401 })
      .mockResolvedValueOnce({ data: 'ok' })
    const { apiFetch } = makeClient({ fetcher, onRefresh })
    const result = await apiFetch('/protected')
    expect(fetcher).toHaveBeenCalledTimes(2)
    expect(result).toEqual({ data: 'ok' })
  })

  it('does NOT retry a second time (no infinite loop)', async () => {
    const onRefresh = vi.fn().mockResolvedValue(true)
    // Both calls fail with 401
    const fetcher = vi.fn().mockRejectedValue({ status: 401 })
    const { apiFetch } = makeClient({ fetcher, onRefresh })
    await expect(apiFetch('/protected')).rejects.toBeDefined()
    expect(fetcher).toHaveBeenCalledTimes(2)   // original + one retry
    expect(onRefresh).toHaveBeenCalledOnce()   // refresh attempted once only
  })

  it('calls onUnauthenticated when refresh fails', async () => {
    const onUnauthenticated = vi.fn().mockResolvedValue(undefined)
    const fetcher = vi.fn().mockRejectedValue({ status: 401 })
    const { apiFetch } = makeClient({
      fetcher,
      onRefresh: vi.fn().mockResolvedValue(false),
      onUnauthenticated,
    })
    await expect(apiFetch('/protected')).rejects.toBeDefined()
    expect(onUnauthenticated).toHaveBeenCalledOnce()
  })

  it('does NOT call onRefresh for non-401 errors', async () => {
    const onRefresh = vi.fn()
    const fetcher = vi.fn().mockRejectedValue({ status: 500, message: 'Server error' })
    const { apiFetch } = makeClient({ fetcher, onRefresh })
    await expect(apiFetch('/x')).rejects.toBeDefined()
    expect(onRefresh).not.toHaveBeenCalled()
  })

  it('normalizes non-401 errors', async () => {
    const fetcher = vi.fn().mockRejectedValue({ data: { detail: 'Not found' }, status: 404 })
    const { apiFetch } = makeClient({ fetcher })
    const err = await apiFetch('/x').catch(e => e)
    expect(err).toMatchObject({ message: 'Not found', status: 404 })
  })
})
