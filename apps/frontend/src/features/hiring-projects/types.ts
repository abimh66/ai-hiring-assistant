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
