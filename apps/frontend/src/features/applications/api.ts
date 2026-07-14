import { apiGet, apiPatch, apiPost, apiPostForm } from '@/lib/api-client'
import type {
  Application,
  ApplicationUpdateInput,
  ApplicationUploadResult,
  ResumeAnalysis,
} from '@/features/applications/types'

export function listApplicationsForProject(hiringProjectId: number): Promise<Application[]> {
  return apiGet<Application[]>(`/hiring-projects/${hiringProjectId}/applications`)
}

export function createApplications(
  hiringProjectId: number,
  files: File[],
): Promise<ApplicationUploadResult[]> {
  const formData = new FormData()
  files.forEach((file) => formData.append('resumes', file))

  return apiPostForm<ApplicationUploadResult[]>(
    `/hiring-projects/${hiringProjectId}/applications`,
    formData,
  )
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

export function getResumeAnalysis(id: number): Promise<ResumeAnalysis> {
  return apiGet<ResumeAnalysis>(`/applications/${id}/resume-analysis`)
}

export function retryResumeAnalysis(id: number): Promise<ResumeAnalysis> {
  return apiPost<ResumeAnalysis>(`/applications/${id}/resume-analysis/retry`)
}
