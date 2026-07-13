import { apiGet, apiPatch, apiPostForm } from '@/lib/api-client'
import type {
  Application,
  ApplicationCreateInput,
  ApplicationUpdateInput,
} from '@/features/applications/types'

export function listApplicationsForProject(hiringProjectId: number): Promise<Application[]> {
  return apiGet<Application[]>(`/hiring-projects/${hiringProjectId}/applications`)
}

export function createApplication(
  hiringProjectId: number,
  input: ApplicationCreateInput,
): Promise<Application> {
  const formData = new FormData()
  formData.set('candidate_email', input.candidateEmail)
  formData.set('candidate_full_name', input.candidateFullName)
  if (input.candidatePhone) formData.set('candidate_phone', input.candidatePhone)
  formData.set('resume', input.resume)

  return apiPostForm<Application>(`/hiring-projects/${hiringProjectId}/applications`, formData)
}

export function getApplication(id: number): Promise<Application> {
  return apiGet<Application>(`/applications/${id}`)
}

export function updateApplication(id: number, input: ApplicationUpdateInput): Promise<Application> {
  return apiPatch<Application>(`/applications/${id}`, input)
}

export function uploadInterviewNotes(id: number, notes: File): Promise<Application> {
  const formData = new FormData()
  formData.set('notes', notes)
  return apiPostForm<Application>(`/applications/${id}/interview-notes`, formData)
}

export function getResumeUrl(id: number): Promise<{ url: string }> {
  return apiGet<{ url: string }>(`/applications/${id}/resume-url`)
}

export function getInterviewNotesUrl(id: number): Promise<{ url: string }> {
  return apiGet<{ url: string }>(`/applications/${id}/interview-notes-url`)
}
