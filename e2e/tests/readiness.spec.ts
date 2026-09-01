import { test, expect } from '@playwright/test'

const backendUrl = process.env.BACKEND_URL ?? 'http://localhost:8000'

test.describe('service readiness', () => {
  test('backend /health/ready reports ready database', async ({ request }) => {
    const res = await request.get(`${backendUrl}/health/ready`)
    expect(res.status()).toBe(200)
    expect((await res.json()).status).toBe('ready')
  })

  test('frontend home page serves HTML', async ({ request }) => {
    const res = await request.get('/')
    expect(res.status()).toBe(200)
    expect(res.headers()['content-type']).toContain('text/html')
  })
})
