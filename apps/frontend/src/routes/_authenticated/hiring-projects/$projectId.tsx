import { useRef, useState } from 'react'
import { createFileRoute, Link } from '@tanstack/react-router'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { getHiringProject } from '@/features/hiring-projects/api'
import { createApplication, listApplicationsForProject } from '@/features/applications/api'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
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
            <p className="whitespace-pre-wrap text-sm text-muted-foreground">
              {project.job_description}
            </p>
          </CardContent>
        </Card>
      )}

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
                  <TableHead>Status</TableHead>
                  <TableHead>Submitted</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {applications.map((application) => (
                  <TableRow key={application.id}>
                    <TableCell>
                      <Link
                        className="underline"
                        to="/candidates/$candidateId"
                        params={{ candidateId: String(application.candidate_id) }}
                      >
                        Application #{application.id}
                      </Link>
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

function UploadResumeDialog({ projectId }: { projectId: number }) {
  const queryClient = useQueryClient()
  const [open, setOpen] = useState(false)
  const [candidateEmail, setCandidateEmail] = useState('')
  const [candidateFullName, setCandidateFullName] = useState('')
  const [candidatePhone, setCandidatePhone] = useState('')
  const fileInputRef = useRef<HTMLInputElement>(null)

  const mutation = useMutation({
    mutationFn: () => {
      const resume = fileInputRef.current?.files?.[0]
      if (!resume) throw new Error('Resume file is required')
      return createApplication(projectId, {
        candidateEmail,
        candidateFullName,
        candidatePhone: candidatePhone || undefined,
        resume,
      })
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['hiring-projects', projectId, 'applications'] })
      setOpen(false)
      setCandidateEmail('')
      setCandidateFullName('')
      setCandidatePhone('')
      if (fileInputRef.current) fileInputRef.current.value = ''
    },
  })

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger render={<Button>Upload candidate</Button>} />
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Upload candidate resume</DialogTitle>
        </DialogHeader>
        <form
          className="flex flex-col gap-4"
          onSubmit={(e) => {
            e.preventDefault()
            mutation.mutate()
          }}
        >
          <div className="flex flex-col gap-2">
            <Label htmlFor="candidate-name">Full name</Label>
            <Input
              id="candidate-name"
              required
              value={candidateFullName}
              onChange={(e) => setCandidateFullName(e.target.value)}
            />
          </div>
          <div className="flex flex-col gap-2">
            <Label htmlFor="candidate-email">Email</Label>
            <Input
              id="candidate-email"
              type="email"
              required
              value={candidateEmail}
              onChange={(e) => setCandidateEmail(e.target.value)}
            />
          </div>
          <div className="flex flex-col gap-2">
            <Label htmlFor="candidate-phone">Phone (optional)</Label>
            <Input
              id="candidate-phone"
              value={candidatePhone}
              onChange={(e) => setCandidatePhone(e.target.value)}
            />
          </div>
          <div className="flex flex-col gap-2">
            <Label htmlFor="resume">Resume</Label>
            <Input id="resume" type="file" required ref={fileInputRef} />
          </div>
          {mutation.isError && (
            <p className="text-sm text-destructive">{(mutation.error as Error).message}</p>
          )}
          <Button type="submit" disabled={mutation.isPending}>
            {mutation.isPending ? 'Uploading…' : 'Upload'}
          </Button>
        </form>
      </DialogContent>
    </Dialog>
  )
}
