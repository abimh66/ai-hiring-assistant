export type ApplicationStatus = 'new' | 'reviewing' | 'rejected' | 'shortlisted'

export interface Application {
  id: number
  candidate_id: number
  hiring_project_id: number
  resume_file_key: string
  interview_notes_file_key: string | null
  status: ApplicationStatus
  created_at: string
}

export interface ApplicationCreateInput {
  candidateEmail: string
  candidateFullName: string
  candidatePhone?: string
  resume: File
}

export interface ApplicationUpdateInput {
  status?: ApplicationStatus
}
