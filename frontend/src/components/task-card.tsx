'use client'

import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Check, Pencil, Trash2, X } from 'lucide-react'
import { cn } from '@/lib/utils'
import type { Task } from '@/types/task'

interface TaskCardProps {
  task: Task
  onComplete?: (task: Task) => Promise<void>
  onUncomplete?: (task: Task) => Promise<void>
  onEdit?: (task: Task) => void
  onDelete?: (task: Task) => Promise<void>
}

export function TaskCard({
  task,
  onComplete,
  onUncomplete,
  onEdit,
  onDelete,
}: TaskCardProps) {
  const [isLoading, setIsLoading] = useState(false)
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false)
  const [isHovered, setIsHovered] = useState(false)

  const handleToggleComplete = async () => {
    setIsLoading(true)
    try {
      if (task.completed) {
        await onUncomplete?.(task)
      } else {
        await onComplete?.(task)
      }
    } finally {
      setIsLoading(false)
    }
  }

  const handleDelete = async () => {
    setIsLoading(true)
    try {
      await onDelete?.(task)
    } finally {
      setIsLoading(false)
      setShowDeleteConfirm(false)
    }
  }

  return (
    <motion.div
      layout
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, scale: 0.95 }}
      transition={{ duration: 0.2 }}
      onHoverStart={() => setIsHovered(true)}
      onHoverEnd={() => setIsHovered(false)}
      className={cn(
        "group relative overflow-hidden rounded-xl border bg-card p-5 shadow-sm transition-all duration-200",
        "hover:shadow-lg hover:shadow-primary/5 hover:border-primary/20",
        task.completed && "opacity-60"
      )}
    >
      {/* Animated gradient background on hover */}
      <motion.div
        className="absolute inset-0 bg-gradient-to-br from-primary/5 via-transparent to-transparent opacity-0 pointer-events-none"
        animate={{ opacity: isHovered ? 1 : 0 }}
        transition={{ duration: 0.3 }}
      />

      <div className="relative flex items-start gap-4">
        {/* Checkbox */}
        <motion.button
          onClick={handleToggleComplete}
          disabled={isLoading}
          whileHover={{ scale: 1.1 }}
          whileTap={{ scale: 0.95 }}
          className={cn(
            "mt-0.5 flex h-6 w-6 items-center justify-center rounded-md border-2 transition-all duration-200 flex-shrink-0",
            task.completed
              ? "border-primary bg-primary text-primary-foreground"
              : "border-muted-foreground/30 hover:border-primary/50 hover:bg-primary/10",
            isLoading && "opacity-50 cursor-not-allowed"
          )}
          aria-label={task.completed ? 'Mark as incomplete' : 'Mark as complete'}
        >
          <AnimatePresence mode="wait">
            {task.completed && (
              <motion.div
                initial={{ scale: 0, rotate: -180 }}
                animate={{ scale: 1, rotate: 0 }}
                exit={{ scale: 0, rotate: 180 }}
                transition={{ type: "spring", stiffness: 200, damping: 15 }}
              >
                <Check className="h-4 w-4" />
              </motion.div>
            )}
          </AnimatePresence>
        </motion.button>

        {/* Content */}
        <div className="flex-1 min-w-0 space-y-1">
          <motion.h3
            className={cn(
              "font-semibold text-lg transition-all duration-200",
              task.completed
                ? "text-muted-foreground line-through"
                : "text-foreground"
            )}
            animate={{
              x: task.completed ? 4 : 0,
            }}
          >
            {task.title}
          </motion.h3>

          <AnimatePresence>
            {task.description && (
              <motion.p
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: "auto" }}
                exit={{ opacity: 0, height: 0 }}
                className={cn(
                  "text-sm transition-colors duration-200",
                  task.completed ? "text-muted-foreground/70" : "text-muted-foreground"
                )}
              >
                {task.description}
              </motion.p>
            )}
          </AnimatePresence>

          <p className="text-xs text-muted-foreground/50 pt-1">
            {new Date(task.created_at).toLocaleDateString('en-US', {
              month: 'short',
              day: 'numeric',
              year: 'numeric'
            })}
          </p>
        </div>

        {/* Actions */}
        <AnimatePresence>
          {!showDeleteConfirm && (
            <motion.div
              initial={{ opacity: 0, x: 10 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: 10 }}
              className="flex gap-1"
            >
              {onEdit && (
                <motion.button
                  onClick={() => onEdit(task)}
                  disabled={isLoading}
                  whileHover={{ scale: 1.1, rotate: 5 }}
                  whileTap={{ scale: 0.9 }}
                  className={cn(
                    "rounded-lg p-2 transition-colors duration-200",
                    "text-muted-foreground hover:text-foreground hover:bg-accent",
                    "disabled:opacity-50 disabled:cursor-not-allowed"
                  )}
                  aria-label="Edit task"
                >
                  <Pencil className="h-4 w-4" />
                </motion.button>
              )}

              {onDelete && (
                <motion.button
                  onClick={() => setShowDeleteConfirm(true)}
                  disabled={isLoading}
                  whileHover={{ scale: 1.1, rotate: -5 }}
                  whileTap={{ scale: 0.9 }}
                  className={cn(
                    "rounded-lg p-2 transition-colors duration-200",
                    "text-muted-foreground hover:text-destructive hover:bg-destructive/10",
                    "disabled:opacity-50 disabled:cursor-not-allowed"
                  )}
                  aria-label="Delete task"
                >
                  <Trash2 className="h-4 w-4" />
                </motion.button>
              )}
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      {/* Delete confirmation */}
      <AnimatePresence>
        {showDeleteConfirm && (
          <motion.div
            initial={{ opacity: 0, height: 0, marginTop: 0 }}
            animate={{ opacity: 1, height: "auto", marginTop: 16 }}
            exit={{ opacity: 0, height: 0, marginTop: 0 }}
            className="overflow-hidden"
          >
            <div className="border-t border-border pt-4 space-y-3">
              <p className="text-sm text-muted-foreground flex items-center gap-2">
                <Trash2 className="h-4 w-4 text-destructive" />
                Are you sure you want to delete this task?
              </p>
              <div className="flex gap-2">
                <motion.button
                  onClick={handleDelete}
                  disabled={isLoading}
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  className={cn(
                    "flex-1 rounded-lg bg-destructive px-4 py-2 text-sm font-medium text-destructive-foreground",
                    "transition-colors hover:bg-destructive/90",
                    "disabled:opacity-50 disabled:cursor-not-allowed"
                  )}
                >
                  {isLoading ? 'Deleting...' : 'Delete'}
                </motion.button>
                <motion.button
                  onClick={() => setShowDeleteConfirm(false)}
                  disabled={isLoading}
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  className={cn(
                    "flex-1 rounded-lg bg-secondary px-4 py-2 text-sm font-medium text-secondary-foreground",
                    "transition-colors hover:bg-secondary/80",
                    "disabled:opacity-50 disabled:cursor-not-allowed"
                  )}
                >
                  Cancel
                </motion.button>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  )
}
