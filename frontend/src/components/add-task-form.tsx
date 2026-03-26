'use client'

import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Plus, Loader2, X } from 'lucide-react'
import { cn } from '@/lib/utils'
import type { TaskCreate } from '@/types/task'

interface AddTaskFormProps {
  onSubmit: (data: TaskCreate) => Promise<void>
  isLoading?: boolean
}

export function AddTaskForm({ onSubmit, isLoading = false }: AddTaskFormProps) {
  const [title, setTitle] = useState('')
  const [description, setDescription] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [isExpanded, setIsExpanded] = useState(false)
  const [isFocused, setIsFocused] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError(null)

    if (!title.trim()) {
      setError('Title is required')
      return
    }

    if (title.length > 255) {
      setError('Title must be 255 characters or less')
      return
    }

    try {
      await onSubmit({
        title: title.trim(),
        description: description.trim() || undefined,
      })

      // Clear form on success
      setTitle('')
      setDescription('')
      setIsExpanded(false)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create task')
    }
  }

  return (
    <motion.form
      onSubmit={handleSubmit}
      initial={{ opacity: 0, y: -20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      className={cn(
        "relative overflow-hidden rounded-xl border bg-card p-5 shadow-sm transition-all duration-200",
        isFocused && "border-primary/50 shadow-lg shadow-primary/10"
      )}
    >
      {/* Animated error message */}
      <AnimatePresence>
        {error && (
          <motion.div
            initial={{ opacity: 0, height: 0, marginBottom: 0 }}
            animate={{ opacity: 1, height: "auto", marginBottom: 16 }}
            exit={{ opacity: 0, height: 0, marginBottom: 0 }}
            className="overflow-hidden"
          >
            <div className="rounded-lg bg-destructive/10 border border-destructive/20 px-4 py-3 flex items-start gap-2">
              <X className="h-4 w-4 text-destructive mt-0.5 flex-shrink-0" />
              <p className="text-sm text-destructive flex-1">{error}</p>
              <button
                type="button"
                onClick={() => setError(null)}
                className="text-destructive/70 hover:text-destructive transition-colors"
              >
                <X className="h-4 w-4" />
              </button>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      <div className="flex gap-3">
        <div className="flex-1 space-y-3">
          <motion.input
            type="text"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            onFocus={() => {
              setIsExpanded(true)
              setIsFocused(true)
            }}
            onBlur={() => setIsFocused(false)}
            placeholder="What needs to be done?"
            className={cn(
              "w-full rounded-lg border bg-background px-4 py-3 text-base transition-all duration-200",
              "placeholder:text-muted-foreground/50",
              "focus:outline-none focus:ring-2 focus:ring-primary/20",
              "disabled:opacity-50 disabled:cursor-not-allowed"
            )}
            disabled={isLoading}
            maxLength={255}
            whileFocus={{ scale: 1.01 }}
          />

          <AnimatePresence>
            {isExpanded && (
              <motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: "auto" }}
                exit={{ opacity: 0, height: 0 }}
                transition={{ duration: 0.2 }}
                className="overflow-hidden space-y-3"
              >
                <textarea
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  placeholder="Add details... (optional)"
                  rows={3}
                  className={cn(
                    "w-full rounded-lg border bg-background px-4 py-3 text-sm transition-all duration-200",
                    "placeholder:text-muted-foreground/50",
                    "focus:outline-none focus:ring-2 focus:ring-primary/20",
                    "resize-none disabled:opacity-50 disabled:cursor-not-allowed"
                  )}
                  disabled={isLoading}
                />

                <div className="flex justify-end gap-2">
                  <motion.button
                    type="button"
                    onClick={() => {
                      setIsExpanded(false)
                      setDescription('')
                    }}
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                    className={cn(
                      "rounded-lg px-4 py-2 text-sm font-medium transition-colors",
                      "text-muted-foreground hover:text-foreground hover:bg-accent"
                    )}
                  >
                    Collapse
                  </motion.button>
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>

        <motion.button
          type="submit"
          disabled={isLoading || !title.trim()}
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          className={cn(
            "h-12 w-12 flex items-center justify-center rounded-lg",
            "bg-primary text-primary-foreground shadow-lg shadow-primary/25",
            "transition-all duration-200 hover:shadow-xl hover:shadow-primary/30",
            "disabled:opacity-50 disabled:cursor-not-allowed disabled:shadow-none",
            "flex-shrink-0"
          )}
        >
          <AnimatePresence mode="wait">
            {isLoading ? (
              <motion.div
                key="loading"
                initial={{ rotate: 0, scale: 0 }}
                animate={{ rotate: 360, scale: 1 }}
                exit={{ rotate: 0, scale: 0 }}
                transition={{ duration: 0.2 }}
              >
                <Loader2 className="h-5 w-5 animate-spin" />
              </motion.div>
            ) : (
              <motion.div
                key="plus"
                initial={{ rotate: -90, scale: 0 }}
                animate={{ rotate: 0, scale: 1 }}
                exit={{ rotate: 90, scale: 0 }}
                transition={{ type: "spring", stiffness: 200, damping: 15 }}
              >
                <Plus className="h-5 w-5" />
              </motion.div>
            )}
          </AnimatePresence>
        </motion.button>
      </div>

      {/* Character count */}
      <AnimatePresence>
        {title.length > 200 && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="mt-2 text-right"
          >
            <span
              className={cn(
                "text-xs",
                title.length > 255
                  ? "text-destructive font-medium"
                  : title.length > 240
                  ? "text-yellow-500"
                  : "text-muted-foreground"
              )}
            >
              {title.length}/255
            </span>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.form>
  )
}
