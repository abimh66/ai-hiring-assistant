import { createFileRoute, Link } from '@tanstack/react-router'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { getApplication, getResumeAnalysis, retryResumeAnalysis } from '@/features/applications/api'
import { getCandidate } from '@/features/candidates/api'
import { getHiringProject } from '@/features/hiring-projects/api'
import type {
  ResumeEducationEntry,
  ResumeExperienceEntry,
} from '@/features/applications/types'
import { ApiError } from '@/lib/api-client'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Separator } from '@/components/ui/separator'
import { Skeleton } from '@/components/ui/skeleton'

export const Route = createFileRoute('/_authenticated/applications/$applicationId')({
  component: ApplicationAnalysisPage,
})

function ApplicationAnalysisPage() {
  const { applicationId } = Route.useParams()
  const id = Number(applicationId)

  const { data: application } = useQuery({
    queryKey: ['applications', id],
    queryFn: () => getApplication(id),
  })

  const { data: hiringProject } = useQuery({
    queryKey: ['hiring-projects', application?.hiring_project_id],
    queryFn: () => getHiringProject(application!.hiring_project_id),
    enabled: !!application,
  })

  const { data: candidate } = useQuery({
    queryKey: ['candidates', application?.candidate_id],
    queryFn: () => getCandidate(application!.candidate_id!),
    enabled: !!application?.candidate_id,
  })

  const {
    data: analysis,
    error: analysisError,
    isLoading: isAnalysisLoading,
  } = useQuery({
    queryKey: ['applications', id, 'resume-analysis'],
    queryFn: () => getResumeAnalysis(id),
    retry: false,
    refetchInterval: (query) => {
      const status = query.state.data?.status
      const is404 = query.state.error instanceof ApiError && query.state.error.status === 404
      return status === 'pending' || is404 ? 2500 : false
    },
  })

  const isPending =
    analysis?.status === 'pending' || (analysisError instanceof ApiError && analysisError.status === 404)
  const isFailed = analysis?.status === 'failed'
  const isCompleted = analysis?.status === 'completed'

  return (
    <div className="mx-auto flex max-w-3xl flex-col gap-6">
      <div className="animate-in fade-in slide-in-from-bottom-1 flex flex-col gap-3 duration-500">
        {candidate && (
          <Link
            to="/candidates/$candidateId"
            params={{ candidateId: String(candidate.id) }}
            className="w-fit text-sm text-muted-foreground underline-offset-4 hover:text-foreground hover:underline"
          >
            ← {candidate.full_name}
          </Link>
        )}
        <div className="flex flex-wrap items-start justify-between gap-3">
          <div>
            <h1 className="text-2xl font-semibold tracking-tight">
              {application?.resume_original_filename ?? 'Application'}
            </h1>
            <p className="text-sm text-muted-foreground">
              {hiringProject?.title ?? 'Hiring project'}
              {application && (
                <>
                  {' '}
                  · Submitted{' '}
                  {new Date(application.created_at).toLocaleDateString(undefined, {
                    year: 'numeric',
                    month: 'short',
                    day: 'numeric',
                  })}
                </>
              )}
            </p>
          </div>
          {application && <Badge variant="secondary">{application.status}</Badge>}
        </div>
      </div>

      <Card className="animate-in fade-in slide-in-from-bottom-1 delay-100 fill-mode-both duration-500">
        <CardHeader>
          <CardTitle>Resume analysis</CardTitle>
        </CardHeader>
        <CardContent>
          {isAnalysisLoading && <AnalysisSkeleton />}
          {!isAnalysisLoading && isPending && <PendingState />}
          {!isAnalysisLoading && isFailed && (
            <FailedState applicationId={id} errorMessage={analysis?.error_message ?? null} />
          )}
          {!isAnalysisLoading && isCompleted && analysis && <CompletedState analysis={analysis} />}
        </CardContent>
      </Card>
    </div>
  )
}

function AnalysisSkeleton() {
  return (
    <div className="flex flex-col gap-4">
      <Skeleton className="h-4 w-3/4" />
      <Skeleton className="h-4 w-1/2" />
      <div className="flex gap-2 pt-2">
        <Skeleton className="h-5 w-16" />
        <Skeleton className="h-5 w-20" />
        <Skeleton className="h-5 w-14" />
      </div>
    </div>
  )
}

function PendingState() {
  return (
    <div className="flex flex-col items-center gap-3 py-8 text-center">
      <span className="relative flex size-3">
        <span className="absolute inline-flex size-full animate-ping rounded-full bg-foreground/40" />
        <span className="relative inline-flex size-3 rounded-full bg-foreground/70" />
      </span>
      <p className="text-sm text-muted-foreground">
        Analyzing resume… this usually takes a few seconds.
      </p>
    </div>
  )
}

function FailedState({
  applicationId,
  errorMessage,
}: {
  applicationId: number
  errorMessage: string | null
}) {
  const queryClient = useQueryClient()

  const retryMutation = useMutation({
    mutationFn: () => retryResumeAnalysis(applicationId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['applications', applicationId, 'resume-analysis'] })
    },
  })

  return (
    <div className="flex flex-col gap-3 rounded-md border border-destructive/20 bg-destructive/5 p-4">
      <p className="text-sm font-medium text-destructive">Resume analysis failed</p>
      {errorMessage && <p className="text-sm text-muted-foreground">{errorMessage}</p>}
      <Button
        variant="outline"
        size="sm"
        className="w-fit"
        onClick={() => retryMutation.mutate()}
        disabled={retryMutation.isPending}
      >
        {retryMutation.isPending ? 'Retrying…' : 'Retry analysis'}
      </Button>
    </div>
  )
}

function CompletedState({
  analysis,
}: {
  analysis: {
    summary: string | null
    skills: string[] | null
    experience: ResumeExperienceEntry[] | null
    education: ResumeEducationEntry[] | null
    strengths: string[] | null
    concerns: string[] | null
    suggested_interview_topics: string[] | null
    extraction_method: string | null
    updated_at: string
  }
}) {
  return (
    <div className="flex flex-col gap-6">
      {analysis.summary && (
        <p className="text-sm leading-relaxed text-foreground">{analysis.summary}</p>
      )}

      {analysis.skills && analysis.skills.length > 0 && (
        <div className="flex flex-wrap gap-1.5">
          {analysis.skills.map((skill) => (
            <Badge key={skill} variant="outline">
              {skill}
            </Badge>
          ))}
        </div>
      )}

      {analysis.experience && analysis.experience.length > 0 && (
        <>
          <Separator />
          <Section title="Experience">
            <div className="flex flex-col gap-4">
              {analysis.experience.map((entry, index) => (
                <div key={index} className="flex flex-col gap-0.5">
                  <div className="flex flex-wrap items-baseline justify-between gap-x-3">
                    <span className="font-medium">
                      {entry.title} · {entry.company}
                    </span>
                    <span className="text-xs text-muted-foreground">
                      {entry.start_date ?? '—'} – {entry.end_date ?? 'Present'}
                    </span>
                  </div>
                  {entry.description && (
                    <p className="text-sm text-muted-foreground">{entry.description}</p>
                  )}
                </div>
              ))}
            </div>
          </Section>
        </>
      )}

      {analysis.education && analysis.education.length > 0 && (
        <>
          <Separator />
          <Section title="Education">
            <div className="flex flex-col gap-2">
              {analysis.education.map((entry, index) => (
                <div key={index} className="flex flex-wrap items-baseline justify-between gap-x-3">
                  <span className="font-medium">
                    {entry.degree ? `${entry.degree}, ` : ''}
                    {entry.institution}
                  </span>
                  <span className="text-xs text-muted-foreground">
                    {entry.start_date ?? '—'} – {entry.end_date ?? '—'}
                  </span>
                </div>
              ))}
            </div>
          </Section>
        </>
      )}

      {((analysis.strengths && analysis.strengths.length > 0) ||
        (analysis.concerns && analysis.concerns.length > 0)) && (
        <>
          <Separator />
          <div className="grid gap-6 sm:grid-cols-2">
            {analysis.strengths && analysis.strengths.length > 0 && (
              <Section title="Strengths">
                <BulletList items={analysis.strengths} />
              </Section>
            )}
            {analysis.concerns && analysis.concerns.length > 0 && (
              <Section title="Concerns">
                <BulletList items={analysis.concerns} />
              </Section>
            )}
          </div>
        </>
      )}

      {analysis.suggested_interview_topics && analysis.suggested_interview_topics.length > 0 && (
        <>
          <Separator />
          <Section title="Suggested interview topics">
            <BulletList items={analysis.suggested_interview_topics} />
          </Section>
        </>
      )}

      <p className="text-xs text-muted-foreground">
        Extracted via {analysis.extraction_method ?? 'unknown method'} ·{' '}
        {new Date(analysis.updated_at).toLocaleString()}
      </p>
    </div>
  )
}

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div className="flex flex-col gap-2">
      <h3 className="text-xs font-semibold tracking-wide text-muted-foreground uppercase">{title}</h3>
      {children}
    </div>
  )
}

function BulletList({ items }: { items: string[] }) {
  return (
    <ul className="flex flex-col gap-1.5">
      {items.map((item, index) => (
        <li key={index} className="flex gap-2 text-sm">
          <span className="text-muted-foreground">–</span>
          <span>{item}</span>
        </li>
      ))}
    </ul>
  )
}
