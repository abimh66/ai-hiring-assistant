import { useRef, useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { useReactToPrint } from 'react-to-print'

import { getReport, saveReportVersion, triggerReport } from '@/features/reports/api'
import { ReportDocument } from '@/features/reports/ReportDocument'
import { ReportEditor } from '@/features/reports/ReportEditor'
import { VersionHistory } from '@/features/reports/VersionHistory'
import { ApiError } from '@/lib/api-client'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'

export function ReportCard({ projectId }: { projectId: number }) {
  const queryClient = useQueryClient()
  const [editing, setEditing] = useState(false)
  const printRef = useRef<HTMLDivElement>(null)
  const handlePrint = useReactToPrint({
    contentRef: printRef,
    documentTitle: `hiring-report-project-${projectId}`,
  })

  const { data: report, error } = useQuery({
    queryKey: ['hiring-projects', projectId, 'report'],
    queryFn: () => getReport(projectId),
    retry: false,
    refetchInterval: (query) => (query.state.data?.status === 'pending' ? 2500 : false),
  })

  const invalidateReport = () => {
    queryClient.invalidateQueries({ queryKey: ['hiring-projects', projectId, 'report'] })
    queryClient.invalidateQueries({
      queryKey: ['hiring-projects', projectId, 'report', 'versions'],
    })
  }

  const triggerMutation = useMutation({
    mutationFn: () => triggerReport(projectId),
    onSuccess: invalidateReport,
  })

  const saveMutation = useMutation({
    mutationFn: (content: string) => saveReportVersion(projectId, content),
    onSuccess: () => {
      setEditing(false)
      invalidateReport()
    },
  })

  const is404 = error instanceof ApiError && error.status === 404
  const isPending = report?.status === 'pending' || triggerMutation.isPending
  const isFailed = report?.status === 'failed'
  const isCompleted = report?.status === 'completed'

  const handleRegenerate = () => {
    if (editing && !window.confirm('Discard your unsaved edits and regenerate the report?')) {
      return
    }
    setEditing(false)
    triggerMutation.mutate()
  }

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between">
        <CardTitle>Hiring report</CardTitle>
        <div className="flex gap-2">
          {isCompleted && !editing && (
            <Button variant="outline" onClick={handlePrint}>
              Export PDF
            </Button>
          )}
          {isCompleted && !editing && (
            <Button variant="outline" onClick={() => setEditing(true)}>
              Edit
            </Button>
          )}
          <Button onClick={handleRegenerate} disabled={isPending}>
            {isPending ? 'Generating…' : isCompleted ? 'Regenerate' : 'Generate report'}
          </Button>
        </div>
      </CardHeader>
      <CardContent className="space-y-3">
        {(is404 || (!report && !isPending)) && !triggerMutation.isPending && (
          <p className="text-sm text-muted-foreground">
            No report yet. Generate one from the shortlisted candidates.
          </p>
        )}
        {isPending && <p className="text-sm text-muted-foreground">Generating report…</p>}
        {isFailed && (
          <div>
            <p className="text-sm font-medium text-destructive">Report generation failed</p>
            {report?.error_message && (
              <p className="text-sm text-muted-foreground">{report.error_message}</p>
            )}
          </div>
        )}
        {isCompleted && report?.content && !editing && (
          <>
            <div ref={printRef} className="report-print-area">
              <ReportDocument content={report.content} />
            </div>
            <VersionHistory projectId={projectId} />
          </>
        )}
        {isCompleted && report?.content && editing && (
          <ReportEditor
            content={report.content}
            saving={saveMutation.isPending}
            onSave={(next) => saveMutation.mutate(next)}
            onCancel={() => setEditing(false)}
          />
        )}
      </CardContent>
    </Card>
  )
}
