import type { ResumeAnalysisStatus } from '@/features/applications/types'

export type HiringProjectStatus = 'open' | 'closed'

export interface HiringProject {
  id: number
  title: string
  job_description: string
  status: HiringProjectStatus
  created_by: number
  created_at: string
}

export interface HiringProjectCreateInput {
  title: string
  job_description: string
}

export interface HiringProjectUpdateInput {
  title?: string
  job_description?: string
  status?: HiringProjectStatus
}

export interface ShortlistEntry {
  application_id: number
  rank: number
  match_score: number
  recommendation_reasoning: string
  risks: string[]
}

export interface ShortlistRecommendation {
  id: number
  hiring_project_id: number
  status: ResumeAnalysisStatus
  recommendations: ShortlistEntry[] | null
  overall_summary: string | null
  error_message: string | null
  created_at: string
  updated_at: string
}
