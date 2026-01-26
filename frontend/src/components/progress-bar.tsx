'use client'

import { motion } from 'framer-motion'
import { cn } from '@/lib/utils'

interface ProgressBarProps {
  value: number
  max: number
  className?: string
  showLabel?: boolean
}

export function ProgressBar({ value, max, className, showLabel = true }: ProgressBarProps) {
  const percentage = max > 0 ? Math.round((value / max) * 100) : 0

  return (
    <div className={cn('space-y-2', className)}>
      {showLabel && (
        <div className="flex items-center justify-between text-sm">
          <span className="text-muted-foreground">Progress</span>
          <span className="font-semibold text-primary">{percentage}%</span>
        </div>
      )}

      <div className="h-2 w-full rounded-full bg-secondary/50 overflow-hidden">
        <motion.div
          className="h-full bg-gradient-to-r from-primary via-accent to-primary rounded-full animate-gradient"
          initial={{ width: 0 }}
          animate={{ width: `${percentage}%` }}
          transition={{ duration: 0.5, ease: 'easeOut' }}
        />
      </div>
    </div>
  )
}
