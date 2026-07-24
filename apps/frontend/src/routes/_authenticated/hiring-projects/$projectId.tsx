import { useState } from 'react'
import { createFileRoute, Link } from '@tanstack/react-router'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { useDropzone } from 'react-dropzone'
import { getHiringProject, getShortlist, triggerShortlist } from '@/features/hiring-projects/api'
import type { ShortlistEntry } from '@/features/hiring-projects/types'
import { createApplications, getMatch, listApplicationsForProject } from '@/features/applications/api'
import type { Application } from '@/features/applications/types'
import { ReportCard } from '@/features/reports/ReportCard'
import { RichTextContent } from '@/components/rich-text-content'
import { ApiError } from '@/lib/api-client'
import { cn, scoreTone } from '@/lib/utils'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog'

export const Route = createFileRoute('/_authenticated/hiring-projects/$projectId')({
  component: HiringProjectDetailPage,
})

function HiringProjectDetailPage() {
  const { projectId } = Route.useParams()
  const id = Number(projectId)

  const { data: project } = useQuery({
    queryKey: ['hiring-projects', id],
    queryFn: () => getHiringProject(id),
  })

  const { data: applications, isLoading } = useQuery({
    queryKey: ['hiring-projects', id, 'applications'],
    queryFn: () => listApplicationsForProject(id),
    refetchInterval: (query) => {
      const apps = query.state.data
      const hasPending = apps?.some((application) => application.candidate_id == null)
      return hasPending ? 3000 : false
    },
  })

  return (
    <div className="flex flex-col gap-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold">{project?.title}</h1>
          {project && (
            <Badge className="mt-1" variant={project.status === 'open' ? 'default' : 'secondary'}>
              {project.status}
            </Badge>
          )}
        </div>
        <UploadResumeDialog projectId={id} />
      </div>

      {project && (
        <Card>
          <CardHeader>
            <CardTitle>Job description</CardTitle>
          </CardHeader>
          <CardContent>
            <RichTextContent html={project.job_description} className="text-muted-foreground" />
          </CardContent>
        </Card>
      )}

      <ShortlistCard projectId={id} applications={applications ?? []} />

      <ReportCard projectId={id} />

      <Card>
        <CardHeader>
          <CardTitle>Applications</CardTitle>
        </CardHeader>
        <CardContent>
          {isLoading && <p className="text-muted-foreground">Loading…</p>}
          {applications && applications.length === 0 && (
            <p className="text-sm text-muted-foreground">No applications yet.</p>
          )}
          {applications && applications.length > 0 && (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Application</TableHead>
                  <TableHead>Fit</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Submitted</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {applications.map((application) => (
                  <TableRow key={application.id}>
                    <TableCell>
                      {application.candidate_id == null ? (
                        <span className="text-muted-foreground">
                          {application.resume_original_filename} (processing…)
                        </span>
                      ) : (
                        <Link
                          className="underline"
                          to="/applications/$applicationId"
                          params={{ applicationId: String(application.id) }}
                        >
                          {application.resume_original_filename}
                        </Link>
                      )}
                    </TableCell>
                    <TableCell>
                      <MatchScoreCell applicationId={application.id} />
                    </TableCell>
                    <TableCell>
                      <Badge variant="secondary">{application.status}</Badge>
                    </TableCell>
                    <TableCell>{new Date(application.created_at).toLocaleDateString()}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>
    </div>
  )
}

function MatchScoreCell({ applicationId }: { applicationId: number }) {
  const { data: match, error } = useQuery({
    queryKey: ['applications', applicationId, 'match'],
    queryFn: () => getMatch(applicationId),
    retry: false,
    refetchInterval: (query) => (query.state.data?.status === 'pending' ? 2500 : false),
  })

  const is404 = error instanceof ApiError && error.status === 404

  if (is404) return <span className="text-muted-foreground">—</span>
  if (match?.status === 'completed' && match.match_score != null) {
    return (
      <span
        className={cn(
          'inline-flex min-w-9 items-center justify-center rounded-md px-2 py-0.5 text-xs font-semibold',
          scoreTone(match.match_score),
        )}
      >
        {match.match_score}
      </span>
    )
  }
  if (match?.status === 'failed') return <span className="text-destructive">failed</span>
  return <span className="text-muted-foreground">…</span>
}

function ShortlistCard({
  projectId,
  applications,
}: {
  projectId: number
  applications: Application[]
}) {
  const queryClient = useQueryClient()

  const { data: shortlist, error } = useQuery({
    queryKey: ['hiring-projects', projectId, 'shortlist'],
    queryFn: () => getShortlist(projectId),
    retry: false,
    refetchInterval: (query) => (query.state.data?.status === 'pending' ? 2500 : false),
  })

  const triggerMutation = useMutation({
    mutationFn: () => triggerShortlist(projectId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['hiring-projects', projectId, 'shortlist'] })
    },
  })

  const is404 = error instanceof ApiError && error.status === 404
  const isPending = shortlist?.status === 'pending' || triggerMutation.isPending
  const isFailed = shortlist?.status === 'failed'
  const isCompleted = shortlist?.status === 'completed'
  const hasResult = isCompleted || isFailed

  const buttonLabel = triggerMutation.isPending
    ? 'Generating…'
    : isFailed
      ? 'Try again'
      : isCompleted
        ? 'Regenerate'
        : 'Generate shortlist'

  const filenameFor = (applicationId: number) =>
    applications.find((a) => a.id === applicationId)?.resume_original_filename ??
    `Application #${applicationId}`

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between">
        <CardTitle>Shortlist</CardTitle>
        <Button
          variant={hasResult ? 'outline' : 'default'}
          size="sm"
          onClick={() => triggerMutation.mutate()}
          disabled={isPending}
        >
          {buttonLabel}
        </Button>
      </CardHeader>
      <CardContent>
        {(is404 || (!shortlist && !isPending)) && !triggerMutation.isPending && (
          <p className="text-sm text-muted-foreground">
            No shortlist yet. Generate one from the completed matches.
          </p>
        )}

        {isPending && (
          <div className="flex flex-col items-center gap-3 py-6 text-center">
            <span className="relative flex size-3">
              <span className="absolute inline-flex size-full animate-ping rounded-full bg-foreground/40" />
              <span className="relative inline-flex size-3 rounded-full bg-foreground/70" />
            </span>
            <p className="text-sm text-muted-foreground">Reviewing the candidate pool…</p>
          </div>
        )}

        {!isPending && isFailed && (
          <div className="flex flex-col gap-1 rounded-md border border-destructive/20 bg-destructive/5 p-4">
            <p className="text-sm font-medium text-destructive">Shortlist generation failed</p>
            {shortlist?.error_message && (
              <p className="text-sm text-muted-foreground">{shortlist.error_message}</p>
            )}
          </div>
        )}

        {!isPending && isCompleted && shortlist && (
          <div className="flex flex-col gap-5">
            {shortlist.overall_summary && (
              <p className="text-sm leading-relaxed text-foreground">{shortlist.overall_summary}</p>
            )}

            {(!shortlist.recommendations || shortlist.recommendations.length === 0) && (
              <p className="text-sm text-muted-foreground">
                No candidates met the bar for a recommendation.
              </p>
            )}

            {shortlist.recommendations && shortlist.recommendations.length > 0 && (
              <div className="flex flex-col gap-3">
                {[...shortlist.recommendations]
                  .sort((a, b) => a.rank - b.rank)
                  .map((entry) => (
                    <ShortlistRow key={entry.application_id} entry={entry} filename={filenameFor(entry.application_id)} />
                  ))}
              </div>
            )}

            <p className="text-xs text-muted-foreground">
              Not auto-refreshed — regenerate after uploading more candidates or editing the job
              description. Updated {new Date(shortlist.updated_at).toLocaleString()}.
            </p>
          </div>
        )}
      </CardContent>
    </Card>
  )
}

function ShortlistRow({ entry, filename }: { entry: ShortlistEntry; filename: string }) {
  return (
    <div className="flex flex-col gap-2 rounded-md border p-4">
      <div className="flex flex-wrap items-center gap-2">
        <Badge variant="secondary">#{entry.rank}</Badge>
        <Link
          className="font-medium underline underline-offset-4"
          to="/applications/$applicationId"
          params={{ applicationId: String(entry.application_id) }}
        >
          {filename}
        </Link>
        <span
          className={cn(
            'ml-auto inline-flex min-w-9 items-center justify-center rounded-md px-2 py-0.5 text-xs font-semibold',
            scoreTone(entry.match_score),
          )}
        >
          {entry.match_score}
        </span>
      </div>
      <p className="text-sm leading-relaxed text-foreground">{entry.recommendation_reasoning}</p>
      {entry.risks && entry.risks.length > 0 && (
        <div className="flex flex-col gap-1">
          <h4 className="text-xs font-semibold tracking-wide text-muted-foreground uppercase">
            Risks to probe
          </h4>
          <ul className="flex flex-col gap-1">
            {entry.risks.map((risk, index) => (
              <li key={index} className="flex gap-2 text-sm">
                <span className="text-muted-foreground">–</span>
                <span>{risk}</span>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  )
}

const MAX_BULK_FILES = 20

function UploadResumeDialog({ projectId }: { projectId: number }) {
  const queryClient = useQueryClient()
  const [open, setOpen] = useState(false)
  const [files, setFiles] = useState<File[]>([])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    accept: {
      'application/pdf': ['.pdf'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
      'text/plain': ['.txt'],
      'text/markdown': ['.md'],
    },
    maxFiles: MAX_BULK_FILES,
    onDrop: (accepted) => setFiles((prev) => [...prev, ...accepted].slice(0, MAX_BULK_FILES)),
  })

  const mutation = useMutation({
    mutationFn: () => {
      if (files.length === 0) throw new Error('At least one resume file is required')
      return createApplications(projectId, files)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['hiring-projects', projectId, 'applications'] })
      setOpen(false)
      setFiles([])
    },
  })

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger render={<Button>Upload resumes</Button>} />
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Upload candidate resumes</DialogTitle>
        </DialogHeader>
        <form
          className="flex flex-col gap-4"
          onSubmit={(e) => {
            e.preventDefault()
            mutation.mutate()
          }}
        >
          <div
            {...getRootProps()}
            className={`flex flex-col items-center justify-center gap-2 rounded-md border-2 border-dashed p-8 text-center text-sm ${
              isDragActive ? 'border-primary bg-muted' : 'border-muted-foreground/25'
            }`}
          >
            <input {...getInputProps()} />
            <p className="text-muted-foreground">
              Drag and drop resumes here, or click to browse (PDF/DOCX/TXT/MD, up to{' '}
              {MAX_BULK_FILES})
            </p>
          </div>
          {files.length > 0 && (
            <ul className="flex flex-col gap-1 text-sm">
              {files.map((file, index) => (
                <li key={`${file.name}-${index}`} className="flex items-center justify-between">
                  <span>{file.name}</span>
                  <button
                    type="button"
                    className="text-muted-foreground underline"
                    onClick={() => setFiles((prev) => prev.filter((_, i) => i !== index))}
                  >
                    Remove
                  </button>
                </li>
              ))}
            </ul>
          )}
          {mutation.isError && (
            <p className="text-sm text-destructive">{(mutation.error as Error).message}</p>
          )}
          <Button type="submit" disabled={mutation.isPending || files.length === 0}>
            {mutation.isPending ? 'Uploading…' : `Upload ${files.length || ''}`.trim()}
          </Button>
        </form>
      </DialogContent>
    </Dialog>
  )
}
