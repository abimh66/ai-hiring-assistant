import { cn } from '@/lib/utils'

/**
 * Renders job-description HTML produced by {@link RichTextEditor}.
 * Content is authored in-app (not user-to-user), so the stored HTML is trusted.
 */
export function RichTextContent({
  html,
  className,
}: {
  html: string
  className?: string
}) {
  return (
    <div
      className={cn('prose prose-sm max-w-none dark:prose-invert', className)}
      dangerouslySetInnerHTML={{ __html: html }}
    />
  )
}
