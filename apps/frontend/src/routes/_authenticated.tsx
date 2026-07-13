import { createFileRoute, Link, Outlet, redirect, useNavigate } from '@tanstack/react-router'
import { clearTokens, isAuthenticated } from '@/lib/auth'
import { Button } from '@/components/ui/button'

export const Route = createFileRoute('/_authenticated')({
  beforeLoad: () => {
    if (!isAuthenticated()) {
      throw redirect({ to: '/login' })
    }
  },
  component: AuthenticatedLayout,
})

function AuthenticatedLayout() {
  const navigate = useNavigate()

  function handleLogout() {
    clearTokens()
    navigate({ to: '/login' })
  }

  return (
    <div className="min-h-screen bg-muted/20">
      <header className="flex items-center justify-between border-b bg-background px-6 py-3">
        <Link to="/hiring-projects" className="font-semibold">
          AI Hiring Assistant
        </Link>
        <Button variant="ghost" onClick={handleLogout}>
          Log out
        </Button>
      </header>
      <main className="mx-auto max-w-5xl p-6">
        <Outlet />
      </main>
    </div>
  )
}
