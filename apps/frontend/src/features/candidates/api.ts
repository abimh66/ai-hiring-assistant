import { apiGet } from '@/lib/api-client'
import type { Candidate } from '@/features/candidates/types'
import type { Application } from '@/features/applications/types'

export function listCandidates(): Promise<Candidate[]> {
  return apiGet<Candidate[]>('/candidates')
}

export function getCandidate(id: number): Promise<Candidate> {
  return apiGet<Candidate>(`/candidates/${id}`)
}

export function listCandidateApplications(id: number): Promise<Application[]> {
  return apiGet<Application[]>(`/candidates/${id}/applications`)
}
