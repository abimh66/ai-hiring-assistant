import { useState } from 'react'

import { ReportDocument } from '@/features/reports/ReportDocument'
import { Button } from '@/components/ui/button'

export function ReportEditor({
  content,
  onSave,
  onCancel,
  saving,
}: {
  content: string
  onSave: (next: string) => void
  onCancel: () => void
  saving: boolean
}) {
  const [draft, setDraft] = useState(content)

  return (
    <div className="space-y-3">
      <div className="grid grid-cols-2 gap-4">
        <textarea
          className="min-h-[400px] w-full rounded-md border bg-background p-3 font-mono text-sm"
          value={draft}
          onChange={(e) => setDraft(e.target.value)}
        />
        <div className="min-h-[400px] overflow-auto rounded-md border p-3">
          <ReportDocument content={draft} />
        </div>
      </div>
      <div className="flex gap-2">
        <Button onClick={() => onSave(draft)} disabled={saving}>
          {saving ? 'Saving…' : 'Save'}
        </Button>
        <Button variant="outline" onClick={onCancel} disabled={saving}>
          Cancel
        </Button>
      </div>
    </div>
  )
}
