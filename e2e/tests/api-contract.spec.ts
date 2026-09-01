import { test, expect, request as playwrightRequest, APIRequestContext } from '@playwright/test'

const backendUrl = process.env.BACKEND_URL ?? 'http://localhost:8000'
const ts = Date.now()
const email = `api-${ts}@workboard.test`
const password = 'Test1234!'
const projectName = `API Project ${ts}`

// Serial: each test depends on state created in beforeAll.
test.describe.serial('API contract', () => {
  let api: APIRequestContext
  let accessToken: string
  let projectId: number
  let projectSlug: string
  let taskId: number

  test.beforeAll(async () => {
    api = await playwrightRequest.newContext({ baseURL: backendUrl })

    // Register + login to get an access token.
    await api.post('/api/v1/auth/register', {
      data: { email, full_name: 'API Test User', password },
    })
    const loginRes = await api.post('/api/v1/auth/login', {
      data: { email, password },
    })
    expect(loginRes.status()).toBe(200)
    accessToken = (await loginRes.json()).access_token

    // Create a public project.
    const projectRes = await api.post('/api/v1/projects', {
      headers: { Authorization: `Bearer ${accessToken}` },
      data: { name: projectName, is_public: true },
    })
    expect(projectRes.status()).toBe(201)
    const project = await projectRes.json()
    projectId = project.id
    projectSlug = project.slug

    // Create a task — starts as backlog by default.
    const taskRes = await api.post(`/api/v1/projects/${projectId}/tasks`, {
      headers: { Authorization: `Bearer ${accessToken}` },
      data: { title: `API Task ${ts}` },
    })
    expect(taskRes.status()).toBe(201)
    taskId = (await taskRes.json()).id
  })

  test.afterAll(async () => {
    await api.dispose()
  })

  test('backlog → done transition is rejected with 409 and code invalid_transition', async () => {
    const res = await api.patch(`/api/v1/projects/${projectId}/tasks/${taskId}`, {
      headers: { Authorization: `Bearer ${accessToken}` },
      data: { status: 'done' },
    })
    expect(res.status()).toBe(409)
    const body = await res.json()
    // The API must include a machine-readable code, not just an HTTP status.
    expect(body.detail.code).toBe('invalid_transition')
  })

  test('public project page HTML contains project name (SSR not client-only)', async () => {
    // Request the page as raw HTTP — the content must be in the initial HTML,
    // proving the page is server-rendered and not deferred to the browser.
    const frontend = await playwrightRequest.newContext({
      baseURL: process.env.BASE_URL ?? 'http://localhost:3000',
    })
    const res = await frontend.get(`/public/projects/${projectSlug}`)
    expect(res.status()).toBe(200)
    const html = await res.text()
    expect(html).toContain(projectName)
    await frontend.dispose()
  })
})
