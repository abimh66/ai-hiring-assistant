import { useState } from 'react'
import { ArrowUp, Square } from 'lucide-react'
import { Button } from '@/components/ui/button'

export function Composer({
  onSend,
  onStop,
  isBusy,
}: {
  onSend: (text: string) => void
  onStop: () => void
  isBusy: boolean
}) {
  const [value, setValue] = useState('')

  function submit() {
    const trimmed = value.trim()
    if (!trimmed || isBusy) return
    onSend(trimmed)
    setValue('')
  }

  function handleKeyDown(event: React.KeyboardEvent<HTMLTextAreaElement>) {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault()
      submit()
    }
  }

  return (
    <div className="flex items-end gap-2 rounded-lg border border-input bg-background p-2">
      <textarea
        value={value}
        onChange={(event) => setValue(event.target.value)}
        onKeyDown={handleKeyDown}
        rows={1}
        placeholder="Ask about candidates, matches, or the shortlist…"
        className="max-h-40 flex-1 resize-none bg-transparent px-2 py-1.5 text-sm outline-none placeholder:text-muted-foreground"
      />
      {isBusy ? (
        <Button size="icon" variant="secondary" onClick={onStop} aria-label="Stop">
          <Square />
        </Button>
      ) : (
        <Button size="icon" onClick={submit} disabled={!value.trim()} aria-label="Send">
          <ArrowUp />
        </Button>
      )}
    </div>
  )
}
