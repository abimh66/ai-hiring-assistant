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

export type ResumeAnalysisStatus = 'pending' | 'completed' | 'failed'

export interface ResumeExperienceEntry {
  company: string
  title: string
  start_date: string | null
  end_date: string | null
  description: string | null
}

export interface ResumeEducationEntry {
  institution: string
  degree: string | null
  field: string | null
  start_date: string | null
  end_date: string | null
}

export interface ResumeAnalysis {
  id: number
  application_id: number
  status: ResumeAnalysisStatus
  summary: string | null
  skills: string[] | null
  experience: ResumeExperienceEntry[] | null
  education: ResumeEducationEntry[] | null
  strengths: string[] | null
  concerns: string[] | null
  suggested_interview_topics: string[] | null
  extraction_method: string | null
  error_message: string | null
  created_at: string
  updated_at: string
}
