/**
 * Enhanced task types with priority, category, and due date support.
 * These extend the base Task type with frontend-only fields.
 */

import type { Task } from './task'

export type Priority = 'high' | 'medium' | 'low'
export type Category = 'work' | 'personal' | 'shopping' | 'health' | 'other'

/**
 * Enhanced task with additional frontend fields.
 * Priority, category, and dueDate are stored in localStorage.
 */
export interface EnhancedTask extends Task {
  priority?: Priority
  category?: Category
  dueDate?: string
}

export interface TaskMetadata {
  taskId: string
  priority?: Priority
  category?: Category
  dueDate?: string
}
