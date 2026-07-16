import { clsx, type ClassValue } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

/**
 * Tailwind classes for a 0-100 candidate fit score, used consistently across the
 * application "Job fit" card, the shortlist rows, and the applications table cell.
 */
export function scoreTone(score: number): string {
  if (score >= 70) return 'bg-emerald-500/10 text-emerald-600 dark:text-emerald-400'
  if (score >= 40) return 'bg-amber-500/10 text-amber-600 dark:text-amber-400'
  return 'bg-destructive/10 text-destructive'
}
