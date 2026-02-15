'use client'

import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { X, Save, Loader2, AlertCircle } from 'lucide-react'
import { cn } from '@/lib/utils'
import type { Task, TaskUpdate } from '@/types/task'

interface EditTaskFormProps {
  task: Task
  onSave: (taskId: string, data: TaskUpdate) => Promise<void>
  onCancel: () => void
  isLoading?: boolean
}

export function EditTaskForm({
  task,
  onSave,
  onCancel,
  isLoading = false,
}: EditTaskFormProps) {
  const [title, setTitle] = useState(task.title)
  const [description, setDescription] = useState(task.description || '')
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    setTitle(task.title)
    setDescription(task.description || '')
  }, [task])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError(null)

    if (!title.trim()) {
      setError('Title is required')
      return
    }

    try {
      await onSave(task.id, {
        title: title.trim(),
        description: description.trim() || undefined,
        version: task.version,
      })
    } catch (err) {
      if (err instanceof Error) {
        if (err.message.includes('409')) {
          setError('This task was modified by another session. Please refresh and try again.')
        } else {
          setError(err.message)
        }
      } else {
        setError('Failed to save changes')
      }
    }
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      {/* Backdrop */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        onClick={onCancel}
        className="absolute inset-0 bg-black/60 backdrop-blur-sm"
      />

      {/* Modal */}
      <motion.div
        initial={{ opacity: 0, scale: 0.95, y: 20 }}
        animate={{ opacity: 1, scale: 1, y: 0 }}
        exit={{ opacity: 0, scale: 0.95, y: 20 }}
        transition={{ type: "spring", duration: 0.3 }}
        className="relative w-full max-w-lg"
      >
        <form onSubmit={handleSubmit} className="bg-card rounded-2xl shadow-2xl border border-border overflow-hidden">
          {/* Header */}
          <div className="flex items-center justify-between px-6 py-5 border-b border-border">
            <div className="flex items-center gap-3">
              <div className="h-10 w-10 rounded-lg bg-primary/10 flex items-center justify-center">
                <Save className="h-5 w-5 text-primary" />
              </div>
              <h2 className="text-xl font-bold text-foreground">Edit Task</h2>
            </div>
            <motion.button
              type="button"
              onClick={onCancel}
              whileHover={{ scale: 1.1, rotate: 90 }}
              whileTap={{ scale: 0.9 }}
              className="rounded-lg p-2 text-muted-foreground hover:text-foreground hover:bg-accent transition-colors"
            >
              <X className="h-5 w-5" />
            </motion.button>
          </div>

          {/* Body */}
          <div className="p-6 space-y-5">
            {/* Error message */}
            <AnimatePresence>
              {error && (
                <motion.div
                  initial={{ opacity: 0, height: 0 }}
                  animate={{ opacity: 1, height: "auto" }}
                  exit={{ opacity: 0, height: 0 }}
                  className="overflow-hidden"
                >
                  <div className="rounded-lg bg-destructive/10 border border-destructive/20 px-4 py-3 flex items-start gap-2">
                    <AlertCircle className="h-4 w-4 text-destructive mt-0.5 flex-shrink-0" />
                    <p className="text-sm text-destructive flex-1">{error}</p>
                  </div>
                </motion.div>
              )}
            </AnimatePresence>

            {/* Title input */}
            <div className="space-y-2">
              <label
                htmlFor="edit-title"
                className="block text-sm font-medium text-foreground"
              >
                Title
              </label>
              <input
                id="edit-title"
                type="text"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                disabled={isLoading}
                className={cn(
                  "w-full rounded-lg border bg-background px-4 py-3 text-base transition-all duration-200",
                  "placeholder:text-muted-foreground/50",
                  "focus:outline-none focus:ring-2 focus:ring-primary/20",
                  "disabled:opacity-50 disabled:cursor-not-allowed"
                )}
                placeholder="Task title"
                maxLength={255}
                autoFocus
              />
            </div>

            {/* Description textarea */}
            <div className="space-y-2">
              <label
                htmlFor="edit-description"
                className="block text-sm font-medium text-foreground"
              >
                Description <span className="text-muted-foreground font-normal">(optional)</span>
              </label>
              <textarea
                id="edit-description"
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                disabled={isLoading}
                rows={4}
                className={cn(
                  "w-full rounded-lg border bg-background px-4 py-3 text-sm transition-all duration-200",
                  "placeholder:text-muted-foreground/50",
                  "focus:outline-none focus:ring-2 focus:ring-primary/20",
                  "resize-none disabled:opacity-50 disabled:cursor-not-allowed"
                )}
                placeholder="Add more details..."
              />
            </div>
          </div>

          {/* Footer */}
          <div className="px-6 py-4 bg-muted/30 border-t border-border flex justify-end gap-3">
            <motion.button
              type="button"
              onClick={onCancel}
              disabled={isLoading}
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              className={cn(
                "rounded-lg px-5 py-2.5 text-sm font-medium transition-colors",
                "bg-secondary text-secondary-foreground hover:bg-secondary/80",
                "disabled:opacity-50 disabled:cursor-not-allowed"
              )}
            >
              Cancel
            </motion.button>
            <motion.button
              type="submit"
              disabled={isLoading || !title.trim()}
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              className={cn(
                "rounded-lg px-5 py-2.5 text-sm font-medium transition-colors flex items-center gap-2",
                "bg-primary text-primary-foreground hover:bg-primary/90 shadow-lg shadow-primary/25",
                "disabled:opacity-50 disabled:cursor-not-allowed disabled:shadow-none"
              )}
            >
              {isLoading ? (
                <>
                  <Loader2 className="h-4 w-4 animate-spin" />
                  Saving...
                </>
              ) : (
                <>
                  <Save className="h-4 w-4" />
                  Save Changes
                </>
              )}
            </motion.button>
          </div>
        </form>
      </motion.div>
    </div>
  )
}
