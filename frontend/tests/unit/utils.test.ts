import { describe, expect, it } from 'vitest'
import { STATUS_LABELS, PRIORITY_LABELS } from '~/utils/labels'
import { formatDate } from '~/utils/formatDate'
import { normalizeError } from '~/utils/api-client'

// ---------------------------------------------------------------------------
// Status labels
// ---------------------------------------------------------------------------

describe('STATUS_LABELS', () => {
  it.each([
    ['backlog', 'Backlog'],
    ['in_progress', 'In Progress'],
    ['done', 'Done'],
    ['cancelled', 'Cancelled'],
  ] as const)('maps %s → %s', (status, expected) => {
    expect(STATUS_LABELS[status]).toBe(expected)
  })
})

// ---------------------------------------------------------------------------
// Priority labels
// ---------------------------------------------------------------------------

describe('PRIORITY_LABELS', () => {
  it.each([
    ['low', 'Low'],
    ['medium', 'Medium'],
    ['high', 'High'],
    ['critical', 'Critical'],
  ] as const)('maps %s → %s', (priority, expected) => {
    expect(PRIORITY_LABELS[priority]).toBe(expected)
  })
})

// ---------------------------------------------------------------------------
// formatDate
// ---------------------------------------------------------------------------

describe('formatDate', () => {
  it('returns em dash for null', () => {
    expect(formatDate(null)).toBe('—')
  })

  it('returns em dash for undefined', () => {
    expect(formatDate(undefined)).toBe('—')
  })

  it('returns em dash for empty string', () => {
    expect(formatDate('')).toBe('—')
  })

  it('returns em dash for invalid date string', () => {
    expect(formatDate('not-a-date')).toBe('—')
  })

  it('formats a valid ISO date string', () => {
    const result = formatDate('2026-01-15')
    // Result contains the year and day as numbers regardless of locale specifics
    expect(result).toContain('2026')
    expect(result).toContain('15')
  })
})

// ---------------------------------------------------------------------------
// normalizeError
// ---------------------------------------------------------------------------

describe('normalizeError', () => {
  it('uses data.detail as message when present', () => {
    const err = { data: { detail: 'Not found', code: 'not_found' }, status: 404 }
    expect(normalizeError(err)).toEqual({ message: 'Not found', status: 404, code: 'not_found' })
  })

  it('falls back to err.message when no data.detail', () => {
    const err = { message: 'Network error', status: 503 }
    expect(normalizeError(err)).toEqual({ message: 'Network error', status: 503, code: undefined })
  })

  it('uses fallback message when both are absent', () => {
    expect(normalizeError({})).toEqual({
      message: 'Server error. Please try again later.',
      status: 500,
      code: undefined,
    })
  })

  it('defaults status to 500 when absent', () => {
    const err = { message: 'oops' }
    expect(normalizeError(err).status).toBe(500)
  })
})
