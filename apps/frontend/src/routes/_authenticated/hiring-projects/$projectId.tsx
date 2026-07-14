import { useState } from 'react'
import { createFileRoute, Link } from '@tanstack/react-router'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { useDropzone } from 'react-dropzone'
import { getHiringProject } from '@/features/hiring-projects/api'
import { createApplications, listApplicationsForProject } from '@/features/applications/api'
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

const MAX_BULK_FILES = 20

function UploadResumeDialog({ projectId }: { projectId: number }) {
  const queryClient = useQueryClient()
  const [open, setOpen] = useState(false)
  const [files, setFiles] = useState<File[]>([])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    accept: {
      'application/pdf': ['.pdf'],
      'application/msword': ['.doc'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
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
              Drag and drop resumes here, or click to browse (PDF/DOC/DOCX, up to {MAX_BULK_FILES})
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
