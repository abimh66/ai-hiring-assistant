import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'

import { getReport, triggerReport } from '@/features/reports/api'
import { ReportDocument } from '@/features/reports/ReportDocument'
import { ApiError } from '@/lib/api-client'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'

export function ReportCard({ projectId }: { projectId: number }) {
  const queryClient = useQueryClient()

  const { data: report, error } = useQuery({
    queryKey: ['hiring-projects', projectId, 'report'],
    queryFn: () => getReport(projectId),
    retry: false,
    refetchInterval: (query) => (query.state.data?.status === 'pending' ? 2500 : false),
  })

  const triggerMutation = useMutation({
    mutationFn: () => triggerReport(projectId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['hiring-projects', projectId, 'report'] })
    },
  })

  const is404 = error instanceof ApiError && error.status === 404
  const isPending = report?.status === 'pending' || triggerMutation.isPending
  const isFailed = report?.status === 'failed'
  const isCompleted = report?.status === 'completed'

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between">
        <CardTitle>Hiring report</CardTitle>
        <Button
          onClick={() => triggerMutation.mutate()}
          disabled={isPending}
        >
          {isPending ? 'Generating…' : isCompleted ? 'Regenerate' : 'Generate report'}
        </Button>
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
        {isCompleted && report?.content && <ReportDocument content={report.content} />}
      </CardContent>
    </Card>
  )
}
