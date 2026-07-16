import { createFileRoute, Link } from '@tanstack/react-router'
import { useQuery } from '@tanstack/react-query'
import { listCandidates } from '@/features/candidates/api'
import { Card, CardContent } from '@/components/ui/card'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'

export const Route = createFileRoute('/_authenticated/candidates/')({
  component: CandidatesPage,
})

function CandidatesPage() {
  const { data: candidates, isLoading } = useQuery({
    queryKey: ['candidates'],
    queryFn: listCandidates,
  })

  return (
    <div className="flex flex-col gap-6">
      <h1 className="text-2xl font-semibold">Candidates</h1>

      <Card>
        <CardContent>
          {isLoading && <p className="text-muted-foreground">Loading…</p>}
          {candidates && candidates.length === 0 && (
            <p className="text-sm text-muted-foreground">
              No candidates yet. They appear here once resumes are uploaded to a hiring project.
            </p>
          )}
          {candidates && candidates.length > 0 && (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Name</TableHead>
                  <TableHead>Email</TableHead>
                  <TableHead>Phone</TableHead>
                  <TableHead>Added</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {candidates.map((candidate) => (
                  <TableRow key={candidate.id}>
                    <TableCell>
                      <Link
                        className="font-medium underline underline-offset-4"
                        to="/candidates/$candidateId"
                        params={{ candidateId: String(candidate.id) }}
                      >
                        {candidate.full_name}
                      </Link>
                    </TableCell>
                    <TableCell className="text-muted-foreground">{candidate.email}</TableCell>
                    <TableCell className="text-muted-foreground">
                      {candidate.phone ?? '—'}
                    </TableCell>
                    <TableCell className="text-muted-foreground">
                      {new Date(candidate.created_at).toLocaleDateString()}
                    </TableCell>
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
