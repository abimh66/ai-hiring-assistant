import { useRef } from 'react'
import { createFileRoute } from '@tanstack/react-router'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { getCandidate, listCandidateApplications } from '@/features/candidates/api'
import {
  getInterviewNotesUrl,
  getResumeUrl,
  updateApplication,
  uploadInterviewNotes,
} from '@/features/applications/api'
import type { Application, ApplicationStatus } from '@/features/applications/types'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'

export const Route = createFileRoute('/_authenticated/candidates/$candidateId')({
  component: CandidateProfilePage,
})

const STATUS_OPTIONS: ApplicationStatus[] = ['new', 'reviewing', 'shortlisted', 'rejected']

function CandidateProfilePage() {
  const { candidateId } = Route.useParams()
  const id = Number(candidateId)

  const { data: candidate } = useQuery({
    queryKey: ['candidates', id],
    queryFn: () => getCandidate(id),
  })

  const { data: applications, isLoading } = useQuery({
    queryKey: ['candidates', id, 'applications'],
    queryFn: () => listCandidateApplications(id),
  })

  return (
    <div className="flex flex-col gap-6">
      <div>
        <h1 className="text-2xl font-semibold">{candidate?.full_name}</h1>
        <p className="text-muted-foreground">{candidate?.email}</p>
        {candidate?.phone && <p className="text-muted-foreground">{candidate.phone}</p>}
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Applications across hiring projects</CardTitle>
        </CardHeader>
        <CardContent className="flex flex-col gap-4">
          {isLoading && <p className="text-muted-foreground">Loading…</p>}
          {applications?.map((application) => (
            <ApplicationRow key={application.id} application={application} candidateId={id} />
          ))}
        </CardContent>
      </Card>
    </div>
  )
}

function ApplicationRow({
  application,
  candidateId,
}: {
  application: Application
  candidateId: number
}) {
  const queryClient = useQueryClient()
  const notesInputRef = useRef<HTMLInputElement>(null)

  const statusMutation = useMutation({
    mutationFn: (status: ApplicationStatus) => updateApplication(application.id, { status }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['candidates', candidateId, 'applications'] })
    },
  })

  const uploadNotesMutation = useMutation({
    mutationFn: (file: File) => uploadInterviewNotes(application.id, file),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['candidates', candidateId, 'applications'] })
    },
  })

  async function openResume() {
    const { url } = await getResumeUrl(application.id)
    window.open(url, '_blank')
  }

  async function openInterviewNotes() {
    const { url } = await getInterviewNotesUrl(application.id)
    window.open(url, '_blank')
  }

  return (
    <div className="flex flex-col gap-3 rounded-md border p-4">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <span className="font-medium">Hiring project #{application.hiring_project_id}</span>
        <Select
          value={application.status}
          onValueChange={(value) => statusMutation.mutate(value as ApplicationStatus)}
        >
          <SelectTrigger className="w-40">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            {STATUS_OPTIONS.map((status) => (
              <SelectItem key={status} value={status}>
                {status}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      <div className="flex flex-wrap items-center gap-2">
        <Button variant="outline" size="sm" onClick={openResume}>
          View resume
        </Button>

        {application.interview_notes_file_key ? (
          <Button variant="outline" size="sm" onClick={openInterviewNotes}>
            View interview notes
          </Button>
        ) : (
          <span className="text-sm text-muted-foreground">No interview notes yet</span>
        )}

        <input
          ref={notesInputRef}
          type="file"
          className="hidden"
          onChange={(e) => {
            const file = e.target.files?.[0]
            if (file) uploadNotesMutation.mutate(file)
          }}
        />
        <Button
          variant="ghost"
          size="sm"
          onClick={() => notesInputRef.current?.click()}
          disabled={uploadNotesMutation.isPending}
        >
          {uploadNotesMutation.isPending ? 'Uploading…' : 'Upload interview notes'}
        </Button>
      </div>
    </div>
  )
}
