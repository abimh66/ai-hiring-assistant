export type ApplicationStatus = 'new' | 'reviewing' | 'rejected' | 'shortlisted'

export interface Application {
  id: number
  candidate_id: number | null
  hiring_project_id: number
  resume_file_key: string
  resume_original_filename: string
  interview_notes_file_key: string | null
  status: ApplicationStatus
  created_at: string
}

export interface ApplicationUploadResult {
  filename: string
  application: Application | null
  error: string | null
}

export interface ApplicationUpdateInput {
  status?: ApplicationStatus
}
