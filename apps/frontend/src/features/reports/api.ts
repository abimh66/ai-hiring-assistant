import { apiGet, apiPost } from '@/lib/api-client'
import type {
  HiringReport,
  ReportVersionDetail,
  ReportVersionSummary,
} from '@/features/reports/types'

export function getReport(projectId: number): Promise<HiringReport> {
  return apiGet<HiringReport>(`/hiring-projects/${projectId}/report`)
}

export function triggerReport(projectId: number): Promise<HiringReport> {
  return apiPost<HiringReport>(`/hiring-projects/${projectId}/report`)
}

export function saveReportVersion(projectId: number, content: string): Promise<HiringReport> {
  return apiPost<HiringReport>(`/hiring-projects/${projectId}/report/versions`, { content })
}

export function restoreReportVersion(
  projectId: number,
  versionId: number,
): Promise<HiringReport> {
  return apiPost<HiringReport>(
    `/hiring-projects/${projectId}/report/versions/${versionId}/restore`,
  )
}

export function listReportVersions(projectId: number): Promise<ReportVersionSummary[]> {
  return apiGet<ReportVersionSummary[]>(`/hiring-projects/${projectId}/report/versions`)
}

export function getReportVersion(
  projectId: number,
  versionId: number,
): Promise<ReportVersionDetail> {
  return apiGet<ReportVersionDetail>(
    `/hiring-projects/${projectId}/report/versions/${versionId}`,
  )
}
