import type { Task, TaskPriority, TaskStatus } from '~/types'

export function useTasks(projectId: number) {
  const { apiFetch } = useApi()
  const base = `/projects/${projectId}/tasks`

  function listTasks(): Promise<Task[]> {
    return apiFetch<Task[]>(base)
  }

  function createTask(data: {
    title: string
    description?: string
    priority?: TaskPriority
    due_date?: string
  }): Promise<Task> {
    return apiFetch<Task>(base, { method: 'POST', body: data })
  }

  function updateTask(
    taskId: number,
    data: Partial<Pick<Task, 'title' | 'description' | 'status' | 'priority' | 'due_date' | 'estimate_hours'>>,
  ): Promise<Task> {
    return apiFetch<Task>(`${base}/${taskId}`, { method: 'PATCH', body: data })
  }

  function advanceTask(taskId: number, toStatus: TaskStatus): Promise<Task> {
    return updateTask(taskId, { status: toStatus })
  }

  function deleteTask(taskId: number): Promise<void> {
    return apiFetch(`${base}/${taskId}`, { method: 'DELETE' })
  }

  return { listTasks, createTask, updateTask, advanceTask, deleteTask }
}
