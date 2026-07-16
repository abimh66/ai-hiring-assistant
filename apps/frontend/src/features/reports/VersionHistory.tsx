import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'

import { listReportVersions, restoreReportVersion } from '@/features/reports/api'
import { Button } from '@/components/ui/button'

export function VersionHistory({ projectId }: { projectId: number }) {
  const queryClient = useQueryClient()

  const { data: versions } = useQuery({
    queryKey: ['hiring-projects', projectId, 'report', 'versions'],
    queryFn: () => listReportVersions(projectId),
  })

  const restoreMutation = useMutation({
    mutationFn: (versionId: number) => restoreReportVersion(projectId, versionId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['hiring-projects', projectId, 'report'] })
      queryClient.invalidateQueries({
        queryKey: ['hiring-projects', projectId, 'report', 'versions'],
      })
    },
  })

  if (!versions || versions.length === 0) return null

  return (
    <div className="space-y-2">
      <p className="text-sm font-medium">Version history</p>
      <ul className="space-y-1">
        {versions.map((v) => (
          <li key={v.id} className="flex items-center justify-between text-sm">
            <span>
              v{v.version_number} · {v.source} · {new Date(v.created_at).toLocaleString()}
            </span>
            <Button
              variant="outline"
              size="sm"
              onClick={() => restoreMutation.mutate(v.id)}
              disabled={restoreMutation.isPending}
            >
              Restore
            </Button>
          </li>
        ))}
      </ul>
    </div>
  )
}
