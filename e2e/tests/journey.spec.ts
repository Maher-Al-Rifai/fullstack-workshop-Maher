import { test, expect } from '@playwright/test'

// Unique per run so parallel CI runs and reruns never share accounts or projects.
const ts = Date.now()
const email = `e2e-${ts}@workboard.test`
const password = 'Test1234!'
const projectName = `E2E Project ${ts}`
const taskTitle = 'E2E integration task'

test.describe('critical authenticated journey', () => {
  test('register → task lifecycle → public page → sign out', async ({ page }) => {
    // ── 1. Register ──────────────────────────────────────────────────────────
    await page.goto('/register')
    await page.getByLabel('Full name').fill('E2E User')
    await page.getByLabel('Email address').fill(email)
    await page.getByLabel('Password').fill(password)
    await page.getByRole('button', { name: 'Create account' }).click()

    await expect(page).toHaveURL('/dashboard')
    await expect(page.getByText('E2E User')).toBeVisible()

    // ── 2. Create a public project ────────────────────────────────────────────
    await page.goto('/projects')
    await page.getByRole('button', { name: 'New project' }).click()
    await page.getByLabel('Project name').fill(projectName)
    await page.getByLabel('Make this project public').check()
    await page.getByRole('button', { name: 'Create project' }).click()

    await expect(page.getByRole('link', { name: projectName })).toBeVisible()

    // Slug is displayed in the card footer — capture it for the public-page step.
    const slug = (await page.locator('.card-meta').first().textContent() ?? '').trim()
    expect(slug).toBeTruthy()

    // ── 3. Open project and create a task ─────────────────────────────────────
    await page.getByRole('link', { name: projectName }).click()
    await expect(page.getByRole('heading', { name: projectName })).toBeVisible()

    await page.getByRole('button', { name: 'Add task' }).click()   // opens form; button becomes "Cancel"
    await page.getByLabel('Task title').fill(taskTitle)
    await page.getByRole('button', { name: 'Add task' }).click()   // form submit

    await expect(page.getByText(taskTitle)).toBeVisible()
    await expect(page.getByText('Backlog')).toBeVisible()

    // ── 4. Advance: backlog → in progress ─────────────────────────────────────
    await page.getByRole('button', { name: 'Move task to in progress' }).click()
    await expect(page.getByText('In Progress')).toBeVisible()

    // ── 5. Advance: in progress → done ───────────────────────────────────────
    await page.getByRole('button', { name: 'Move task to done' }).click()
    await expect(page.getByText('Done')).toBeVisible()
    // No further advance button should be visible for a done task.
    await expect(page.getByRole('button', { name: /Move task to/ })).not.toBeVisible()

    // ── 6. Public page renders project name (SSR) ─────────────────────────────
    await page.goto(`/public/projects/${slug}`)
    await expect(page.getByRole('heading', { name: projectName })).toBeVisible()

    // ── 7. Sign out — verify protected navigation returns to home ─────────────
    await page.goto('/projects') // back to authenticated area first
    await page.getByRole('button', { name: 'Sign out' }).click()
    await expect(page).toHaveURL('/')
    await expect(page.getByRole('link', { name: 'Sign in' })).toBeVisible()
    await expect(page.getByRole('link', { name: 'Register' })).toBeVisible()

    // Confirm that navigating to a protected page redirects to login.
    await page.goto('/dashboard')
    await expect(page).toHaveURL(/\/login/)
  })
})
