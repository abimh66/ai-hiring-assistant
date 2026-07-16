export type ReportStatus = 'pending' | 'completed' | 'failed'
export type ReportVersionSource = 'ai_generated' | 'edited' | 'restored'

export interface HiringReport {
  id: number
  hiring_project_id: number
  status: ReportStatus
  error_message: string | null
  current_version_id: number | null
  content: string | null
  created_at: string
  updated_at: string
}

export interface ReportVersionSummary {
  id: number
  version_number: number
  source: ReportVersionSource
  created_by: number
  created_at: string
}

export interface ReportVersionDetail extends ReportVersionSummary {
  report_id: number
  content: string
}
