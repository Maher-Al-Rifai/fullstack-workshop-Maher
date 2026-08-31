import { describe, expect, it } from 'vitest'
import { mount } from '@vue/test-utils'
import TaskCard from '~/components/TaskCard.vue'
import StatusBadge from '~/components/ui/StatusBadge.vue'
import type { Task } from '~/types'

const base: Task = {
  id: 1,
  title: 'Fix login bug',
  description: null,
  status: 'backlog',
  priority: 'medium',
  project_id: 10,
  assignee_id: null,
  due_date: null,
  estimate_hours: null,
  created_at: '2026-01-01T00:00:00Z',
}

function mountCard(task: Partial<Task> = {}) {
  return mount(TaskCard, {
    props: { task: { ...base, ...task } },
    global: { components: { StatusBadge } },
  })
}

// ---------------------------------------------------------------------------
// Rendering
// ---------------------------------------------------------------------------

describe('TaskCard rendering', () => {
  it('renders the task title', () => {
    expect(mountCard().find('h3').text()).toBe('Fix login bug')
  })

  it('renders description when present', () => {
    const w = mountCard({ description: 'Needs auth fix' })
    expect(w.text()).toContain('Needs auth fix')
  })

  it('does not render description paragraph when absent', () => {
    expect(mountCard().find('p.task-desc').exists()).toBe(false)
  })

  it('renders the status badge with the correct label', () => {
    const w = mountCard({ status: 'in_progress' })
    expect(w.find('.badge').text()).toBe('In Progress')
  })

  it('renders the priority text', () => {
    const w = mountCard({ priority: 'high' })
    expect(w.find('.task-priority').text()).toBe('high')
  })

  it('renders due date in a time element when present', () => {
    const w = mountCard({ due_date: '2026-12-31' })
    expect(w.find('time').attributes('datetime')).toBe('2026-12-31')
  })
})

// ---------------------------------------------------------------------------
// Advance button visibility (state machine)
// ---------------------------------------------------------------------------

describe('TaskCard advance button', () => {
  it('shows "Move to in progress" for backlog task', () => {
    const w = mountCard({ status: 'backlog' })
    expect(w.find('[aria-label="Move task to in progress"]').exists()).toBe(true)
  })

  it('shows "Move to done" for in_progress task', () => {
    const w = mountCard({ status: 'in_progress' })
    expect(w.find('[aria-label="Move task to done"]').exists()).toBe(true)
  })

  it('has no advance button for done task', () => {
    const w = mountCard({ status: 'done' })
    const buttons = w.findAll('button').filter(b => b.text().startsWith('Move'))
    expect(buttons).toHaveLength(0)
  })

  it('has no advance button for cancelled task', () => {
    const w = mountCard({ status: 'cancelled' })
    const buttons = w.findAll('button').filter(b => b.text().startsWith('Move'))
    expect(buttons).toHaveLength(0)
  })
})

// ---------------------------------------------------------------------------
// Events
// ---------------------------------------------------------------------------

describe('TaskCard events', () => {
  it('emits advance with taskId and next status', async () => {
    const w = mountCard({ id: 42, status: 'backlog' })
    await w.find('[aria-label="Move task to in progress"]').trigger('click')
    expect(w.emitted('advance')).toEqual([[42, 'in_progress']])
  })

  it('emits advance with done when task is in_progress', async () => {
    const w = mountCard({ id: 5, status: 'in_progress' })
    await w.find('[aria-label="Move task to done"]').trigger('click')
    expect(w.emitted('advance')).toEqual([[5, 'done']])
  })

  it('emits delete with taskId', async () => {
    const w = mountCard({ id: 99 })
    await w.find('[aria-label="Delete task Fix login bug"]').trigger('click')
    expect(w.emitted('delete')).toEqual([[99]])
  })
})
