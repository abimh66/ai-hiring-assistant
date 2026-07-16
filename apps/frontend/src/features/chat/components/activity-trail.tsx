import { Search, Sparkles, Wrench } from 'lucide-react'
import type { ActivityData } from '@/features/chat/types'

const TOOL_LABELS: Record<string, string> = {
  list_candidates: 'Listing candidates',
  get_candidate: 'Reading candidate',
  get_match: 'Reading match analysis',
  get_shortlist: 'Reading shortlist',
  search_resumes: 'Searching resumes',
}

function toolLabel(tool: string): string {
  return TOOL_LABELS[tool] ?? `Using ${tool}`
}

function describe(activity: ActivityData): { icon: typeof Wrench; text: string } {
  switch (activity.kind) {
    case 'tool_call':
      return { icon: activity.tool === 'search_resumes' ? Search : Wrench, text: toolLabel(activity.tool) }
    case 'specialist':
      return { icon: Sparkles, text: `Spawned specialist: ${activity.topic}` }
    case 'tool_result':
      return { icon: Wrench, text: `${toolLabel(activity.tool)} — done` }
  }
}

export function ActivityTrail({ items }: { items: ActivityData[] }) {
  if (items.length === 0) return null
  return (
    <ul className="mb-2 flex flex-col gap-1 border-l-2 border-border pl-3">
      {items.map((activity, index) => {
        const { icon: Icon, text } = describe(activity)
        return (
          <li key={index} className="flex items-center gap-2 text-xs text-muted-foreground">
            <Icon className="size-3.5 shrink-0" />
            <span>{text}</span>
          </li>
        )
      })}
    </ul>
  )
}
