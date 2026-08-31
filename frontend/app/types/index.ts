// API types aligned with the FastAPI backend schemas.
// TypeScript types describe the shape; runtime validation is the backend's responsibility.

export type TaskStatus = 'backlog' | 'in_progress' | 'done' | 'cancelled'
export type TaskPriority = 'low' | 'medium' | 'high' | 'critical'

export interface User {
  id: number
  email: string
  full_name: string
  is_active: boolean
  created_at: string
}

export interface Project {
  id: number
  name: string
  description: string | null
  slug: string
  is_public: boolean
  owner_id: number
  created_at: string
}

export interface Task {
  id: number
  title: string
  description: string | null
  status: TaskStatus
  priority: TaskPriority
  project_id: number
  assignee_id: number | null
  due_date: string | null
  estimate_hours: number | null
  created_at: string
}

export interface PublicProject {
  id: number
  name: string
  description: string | null
  slug: string
  task_count: number
  done_count: number
}

export interface TokenResponse {
  access_token: string
  token_type: string
  expires_in: number
}

export interface RegisterRequest {
  email: string
  full_name: string
  password: string
}

export interface LoginRequest {
  email: string
  password: string
}
