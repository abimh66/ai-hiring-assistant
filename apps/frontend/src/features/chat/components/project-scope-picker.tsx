import { useQuery } from '@tanstack/react-query'
import { listHiringProjects } from '@/features/hiring-projects/api'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'

const ALL = 'all'

export function ProjectScopePicker({
  value,
  onChange,
}: {
  value: number | null
  onChange: (hiringProjectId: number | null) => void
}) {
  const { data: projects } = useQuery({
    queryKey: ['hiring-projects'],
    queryFn: listHiringProjects,
  })

  return (
    <Select
      value={value == null ? ALL : String(value)}
      onValueChange={(next) => onChange(next === ALL ? null : Number(next))}
    >
      <SelectTrigger size="sm" className="w-48">
        <SelectValue />
      </SelectTrigger>
      <SelectContent>
        <SelectItem value={ALL}>All projects</SelectItem>
        {projects?.map((project) => (
          <SelectItem key={project.id} value={String(project.id)}>
            {project.title}
          </SelectItem>
        ))}
      </SelectContent>
    </Select>
  )
}
