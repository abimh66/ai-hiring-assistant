import { useState } from 'react'
import { createFileRoute } from '@tanstack/react-router'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { deactivateUser, inviteUser, listUsers } from '@/features/users/api'
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

export const Route = createFileRoute('/_authenticated/users/')({
  component: UsersPage,
})

function UsersPage() {
  const { data: users, isLoading } = useQuery({
    queryKey: ['users'],
    queryFn: listUsers,
  })
  const queryClient = useQueryClient()

  const deactivateMutation = useMutation({
    mutationFn: deactivateUser,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['users'] }),
  })

  return (
    <div className="flex flex-col gap-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-semibold">Team</h1>
        <InviteUserDialog />
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Members</CardTitle>
        </CardHeader>
        <CardContent>
          {isLoading && <p className="text-muted-foreground">Loading…</p>}
          {users && (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Name</TableHead>
                  <TableHead>Email</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead />
                </TableRow>
              </TableHeader>
              <TableBody>
                {users.map((user) => (
                  <TableRow key={user.id}>
                    <TableCell>{user.full_name}</TableCell>
                    <TableCell>{user.email}</TableCell>
                    <TableCell>
                      {!user.is_active ? (
                        <Badge variant="destructive">deactivated</Badge>
                      ) : user.is_pending ? (
                        <Badge variant="secondary">invite pending</Badge>
                      ) : (
                        <Badge>active</Badge>
                      )}
                    </TableCell>
                    <TableCell className="text-right">
                      {user.is_active && (
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => deactivateMutation.mutate(user.id)}
                          disabled={deactivateMutation.isPending}
                        >
                          Deactivate
                        </Button>
                      )}
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

function InviteUserDialog() {
  const queryClient = useQueryClient()
  const [open, setOpen] = useState(false)
  const [email, setEmail] = useState('')
  const [fullName, setFullName] = useState('')
  const [inviteLink, setInviteLink] = useState<string | null>(null)

  const mutation = useMutation({
    mutationFn: () => inviteUser({ email, full_name: fullName }),
    onSuccess: (response) => {
      queryClient.invalidateQueries({ queryKey: ['users'] })
      setInviteLink(`${window.location.origin}/accept-invite?token=${response.invite_token}`)
    },
  })

  function handleOpenChange(nextOpen: boolean) {
    setOpen(nextOpen)
    if (!nextOpen) {
      setEmail('')
      setFullName('')
      setInviteLink(null)
      mutation.reset()
    }
  }

  return (
    <Dialog open={open} onOpenChange={handleOpenChange}>
      <DialogTrigger render={<Button>Invite teammate</Button>} />
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Invite teammate</DialogTitle>
        </DialogHeader>

        {inviteLink ? (
          <div className="flex flex-col gap-3">
            <p className="text-sm text-muted-foreground">
              Share this link with your teammate so they can set their password. No email is sent
              automatically yet.
            </p>
            <Input readOnly value={inviteLink} onFocus={(e) => e.currentTarget.select()} />
            <Button variant="outline" onClick={() => navigator.clipboard.writeText(inviteLink)}>
              Copy link
            </Button>
          </div>
        ) : (
          <form
            className="flex flex-col gap-4"
            onSubmit={(e) => {
              e.preventDefault()
              mutation.mutate()
            }}
          >
            <div className="flex flex-col gap-2">
              <Label htmlFor="invite-name">Full name</Label>
              <Input id="invite-name" required value={fullName} onChange={(e) => setFullName(e.target.value)} />
            </div>
            <div className="flex flex-col gap-2">
              <Label htmlFor="invite-email">Email</Label>
              <Input
                id="invite-email"
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
              />
            </div>
            {mutation.isError && (
              <p className="text-sm text-destructive">{(mutation.error as Error).message}</p>
            )}
            <Button type="submit" disabled={mutation.isPending}>
              {mutation.isPending ? 'Sending invite…' : 'Send invite'}
            </Button>
          </form>
        )}
      </DialogContent>
    </Dialog>
  )
}
