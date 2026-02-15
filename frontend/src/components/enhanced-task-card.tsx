'use client'

import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  Check,
  Pencil,
  Trash2,
  X,
  AlertCircle,
  Zap,
  CheckCircle,
  Calendar,
  GripVertical
} from 'lucide-react'
import { cn } from '@/lib/utils'
import type { EnhancedTask, Priority } from '@/types/enhanced-task'
import { celebrateTaskCompletion } from '@/lib/confetti'
import type { SyntheticListenerMap } from '@dnd-kit/core/dist/hooks/utilities'

interface EnhancedTaskCardProps {
  task: EnhancedTask
  onComplete?: (task: EnhancedTask) => Promise<void>
  onUncomplete?: (task: EnhancedTask) => Promise<void>
  onEdit?: (task: EnhancedTask) => void
  onDelete?: (task: EnhancedTask) => Promise<void>
  onPriorityChange?: (taskId: string, priority: Priority) => void
  isDragging?: boolean
  dragHandleProps?: SyntheticListenerMap
}

const priorityConfig = {
  high: {
    label: 'High',
    icon: AlertCircle,
    color: 'text-priority-high',
    bgColor: 'bg-priority-high/10',
    borderColor: 'border-priority-high/50',
    glowColor: 'shadow-priority-high/20',
  },
  medium: {
    label: 'Medium',
    icon: Zap,
    color: 'text-priority-medium',
    bgColor: 'bg-priority-medium/10',
    borderColor: 'border-priority-medium/50',
    glowColor: 'shadow-priority-medium/20',
  },
  low: {
    label: 'Low',
    icon: CheckCircle,
    color: 'text-priority-low',
    bgColor: 'bg-priority-low/10',
    borderColor: 'border-priority-low/50',
    glowColor: 'shadow-priority-low/20',
  },
}

export function EnhancedTaskCard({
  task,
  onComplete,
  onUncomplete,
  onEdit,
  onDelete,
  onPriorityChange,
  isDragging = false,
  dragHandleProps,
}: EnhancedTaskCardProps) {
  const [isLoading, setIsLoading] = useState(false)
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false)
  const [isHovered, setIsHovered] = useState(false)

  const priority = task.priority || 'low'
  const priorityData = priorityConfig[priority]
  const PriorityIcon = priorityData.icon

  const handleToggleComplete = async () => {
    setIsLoading(true)
    try {
      if (task.completed) {
        await onUncomplete?.(task)
      } else {
        await onComplete?.(task)
        celebrateTaskCompletion()
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

  const isOverdue = task.dueDate && new Date(task.dueDate) < new Date() && !task.completed

  return (
    <motion.div
      layout
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0, scale: isDragging ? 1.05 : 1 }}
      exit={{ opacity: 0, scale: 0.95 }}
      transition={{ duration: 0.2 }}
      onHoverStart={() => setIsHovered(true)}
      onHoverEnd={() => setIsHovered(false)}
      className={cn(
        'group relative overflow-hidden rounded-xl border glass-card transition-all duration-300',
        task.completed && 'opacity-60',
        isOverdue && 'border-destructive/50',
        isDragging && 'shadow-2xl ring-2 ring-primary/50',
        !isDragging && 'hover:shadow-xl hover:border-primary/30',
        priorityData.borderColor
      )}
    >
      {/* Animated gradient background */}
      <motion.div
        className={cn(
          'absolute inset-0 bg-gradient-to-br opacity-0 pointer-events-none',
          priority === 'high' && 'from-priority-high/10 via-transparent to-transparent',
          priority === 'medium' && 'from-priority-medium/10 via-transparent to-transparent',
          priority === 'low' && 'from-priority-low/10 via-transparent to-transparent'
        )}
        animate={{ opacity: isHovered ? 1 : 0 }}
        transition={{ duration: 0.3 }}
      />

      {/* Priority indicator bar */}
      <div
        className={cn(
          'absolute left-0 top-0 bottom-0 w-1 transition-all duration-300',
          priorityData.bgColor.replace('/10', '')
        )}
      />

      <div className="relative p-5 pl-6">
        <div className="flex items-start gap-4">
          {/* Drag handle (visible on hover) */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: isHovered ? 0.5 : 0 }}
            className="flex-shrink-0 cursor-grab active:cursor-grabbing mt-1 touch-none"
            {...dragHandleProps}
          >
            <GripVertical className="h-5 w-5 text-muted-foreground" />
          </motion.div>

          {/* Checkbox */}
          <motion.button
            onClick={handleToggleComplete}
            disabled={isLoading}
            whileHover={{ scale: 1.1 }}
            whileTap={{ scale: 0.95 }}
            className={cn(
              'mt-0.5 flex h-6 w-6 items-center justify-center rounded-md border-2 transition-all duration-200 flex-shrink-0',
              task.completed
                ? 'border-primary bg-primary text-primary-foreground shadow-lg glow-primary'
                : 'border-muted-foreground/30 hover:border-primary/50 hover:bg-primary/10',
              isLoading && 'opacity-50 cursor-not-allowed'
            )}
            aria-label={task.completed ? 'Mark as incomplete' : 'Mark as complete'}
          >
            <AnimatePresence mode="wait">
              {task.completed && (
                <motion.div
                  initial={{ scale: 0, rotate: -180 }}
                  animate={{ scale: 1, rotate: 0 }}
                  exit={{ scale: 0, rotate: 180 }}
                  transition={{ type: 'spring', stiffness: 200, damping: 15 }}
                >
                  <Check className="h-4 w-4" />
                </motion.div>
              )}
            </AnimatePresence>
          </motion.button>

          {/* Content */}
          <div className="flex-1 min-w-0 space-y-2">
            {/* Title and badges */}
            <div className="space-y-2">
              <motion.h3
                className={cn(
                  'font-semibold text-lg transition-all duration-200',
                  task.completed
                    ? 'text-muted-foreground line-through'
                    : 'text-foreground'
                )}
                animate={{ x: task.completed ? 4 : 0 }}
              >
                {task.title}
              </motion.h3>

              {/* Badges row */}
              <div className="flex flex-wrap gap-2">
                {/* Priority badge */}
                <motion.div
                  whileHover={{ scale: 1.05 }}
                  className={cn(
                    'flex items-center gap-1.5 px-2.5 py-1 rounded-lg text-xs font-medium',
                    priorityData.bgColor,
                    priorityData.color
                  )}
                >
                  <PriorityIcon className="h-3.5 w-3.5" />
                  {priorityData.label}
                </motion.div>

                {/* Due date badge */}
                {task.dueDate && (
                  <motion.div
                    whileHover={{ scale: 1.05 }}
                    className={cn(
                      'flex items-center gap-1.5 px-2.5 py-1 rounded-lg text-xs font-medium',
                      isOverdue
                        ? 'bg-destructive/20 text-destructive'
                        : 'bg-accent/20 text-accent'
                    )}
                  >
                    <Calendar className="h-3.5 w-3.5" />
                    {new Date(task.dueDate).toLocaleDateString('en-US', {
                      month: 'short',
                      day: 'numeric',
                    })}
                  </motion.div>
                )}

                {/* Category badge */}
                {task.category && (
                  <motion.div
                    whileHover={{ scale: 1.05 }}
                    className="px-2.5 py-1 rounded-lg text-xs font-medium bg-secondary/50 text-secondary-foreground"
                  >
                    {task.category}
                  </motion.div>
                )}
              </div>
            </div>

            {/* Description */}
            <AnimatePresence>
              {task.description && (
                <motion.p
                  initial={{ opacity: 0, height: 0 }}
                  animate={{ opacity: 1, height: 'auto' }}
                  exit={{ opacity: 0, height: 0 }}
                  className={cn(
                    'text-sm transition-colors duration-200',
                    task.completed ? 'text-muted-foreground/70' : 'text-muted-foreground'
                  )}
                >
                  {task.description}
                </motion.p>
              )}
            </AnimatePresence>

            {/* Timestamp */}
            <p className="text-xs text-muted-foreground/50 pt-1">
              {new Date(task.created_at).toLocaleDateString('en-US', {
                month: 'short',
                day: 'numeric',
                year: 'numeric',
                hour: '2-digit',
                minute: '2-digit',
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
                      'rounded-lg p-2 transition-colors duration-200',
                      'text-muted-foreground hover:text-primary hover:bg-primary/10',
                      'disabled:opacity-50 disabled:cursor-not-allowed'
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
                      'rounded-lg p-2 transition-colors duration-200',
                      'text-muted-foreground hover:text-destructive hover:bg-destructive/10',
                      'disabled:opacity-50 disabled:cursor-not-allowed'
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
              animate={{ opacity: 1, height: 'auto', marginTop: 16 }}
              exit={{ opacity: 0, height: 0, marginTop: 0 }}
              className="overflow-hidden"
            >
              <div className="border-t border-border pt-4 space-y-3">
                <p className="text-sm text-muted-foreground flex items-center gap-2">
                  <Trash2 className="h-4 w-4 text-destructive" />
                  Delete this task permanently?
                </p>
                <div className="flex gap-2">
                  <motion.button
                    onClick={handleDelete}
                    disabled={isLoading}
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                    className={cn(
                      'flex-1 rounded-lg bg-destructive px-4 py-2 text-sm font-medium text-destructive-foreground',
                      'transition-colors hover:bg-destructive/90 shadow-lg',
                      'disabled:opacity-50 disabled:cursor-not-allowed'
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
                      'flex-1 rounded-lg bg-secondary px-4 py-2 text-sm font-medium text-secondary-foreground',
                      'transition-colors hover:bg-secondary/80',
                      'disabled:opacity-50 disabled:cursor-not-allowed'
                    )}
                  >
                    Cancel
                  </motion.button>
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      {/* Shine effect */}
      <motion.div
        className="absolute inset-0 bg-gradient-to-r from-transparent via-white/5 to-transparent pointer-events-none"
        initial={{ x: '-100%' }}
        whileHover={{ x: '100%' }}
        transition={{ duration: 0.6 }}
      />
    </motion.div>
  )
}
