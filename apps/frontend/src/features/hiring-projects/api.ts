import { apiDelete, apiGet, apiPatch, apiPost } from '@/lib/api-client'
import type {
  HiringProject,
  HiringProjectCreateInput,
  HiringProjectUpdateInput,
} from '@/features/hiring-projects/types'

export function listHiringProjects(): Promise<HiringProject[]> {
  return apiGet<HiringProject[]>('/hiring-projects')
}

export function getHiringProject(id: number): Promise<HiringProject> {
  return apiGet<HiringProject>(`/hiring-projects/${id}`)
}

export function createHiringProject(input: HiringProjectCreateInput): Promise<HiringProject> {
  return apiPost<HiringProject>('/hiring-projects', input)
}

export function updateHiringProject(
  id: number,
  input: HiringProjectUpdateInput,
): Promise<HiringProject> {
  return apiPatch<HiringProject>(`/hiring-projects/${id}`, input)
}

export function deleteHiringProject(id: number): Promise<void> {
  return apiDelete<void>(`/hiring-projects/${id}`)
}
