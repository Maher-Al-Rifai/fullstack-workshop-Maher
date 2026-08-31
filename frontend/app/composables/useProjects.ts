import type { Project } from '~/types'

export function useProjects() {
  const { apiFetch } = useApi()

  function listProjects(): Promise<Project[]> {
    return apiFetch<Project[]>('/projects')
  }

  function getProject(id: number): Promise<Project> {
    return apiFetch<Project>(`/projects/${id}`)
  }

  function createProject(data: {
    name: string
    description?: string
    is_public?: boolean
  }): Promise<Project> {
    return apiFetch<Project>('/projects', { method: 'POST', body: data })
  }

  function updateProject(
    id: number,
    data: Partial<Pick<Project, 'name' | 'description' | 'is_public'>>,
  ): Promise<Project> {
    return apiFetch<Project>(`/projects/${id}`, { method: 'PATCH', body: data })
  }

  function deleteProject(id: number): Promise<void> {
    return apiFetch(`/projects/${id}`, { method: 'DELETE' })
  }

  return { listProjects, getProject, createProject, updateProject, deleteProject }
}
