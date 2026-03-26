'use client'

import { motion } from 'framer-motion'
import { Search, SlidersHorizontal, X, Zap, AlertCircle, CheckCircle } from 'lucide-react'
import { cn } from '@/lib/utils'
import type { Priority } from '@/types/enhanced-task'

export type FilterStatus = 'all' | 'active' | 'completed'
export type SortBy = 'created' | 'title' | 'priority' | 'dueDate'

interface TaskFiltersProps {
  searchQuery: string
  onSearchChange: (query: string) => void
  filterStatus: FilterStatus
  onFilterStatusChange: (status: FilterStatus) => void
  filterPriority: Priority | 'all'
  onFilterPriorityChange: (priority: Priority | 'all') => void
  sortBy: SortBy
  onSortByChange: (sortBy: SortBy) => void
}

export function TaskFilters({
  searchQuery,
  onSearchChange,
  filterStatus,
  onFilterStatusChange,
  filterPriority,
  onFilterPriorityChange,
  sortBy,
  onSortByChange,
}: TaskFiltersProps) {
  const statusFilters: { value: FilterStatus; label: string }[] = [
    { value: 'all', label: 'All' },
    { value: 'active', label: 'Active' },
    { value: 'completed', label: 'Completed' },
  ]

  const priorityFilters: { value: Priority | 'all'; label: string; icon: any }[] = [
    { value: 'all', label: 'All', icon: SlidersHorizontal },
    { value: 'high', label: 'High', icon: AlertCircle },
    { value: 'medium', label: 'Medium', icon: Zap },
    { value: 'low', label: 'Low', icon: CheckCircle },
  ]

  const sortOptions: { value: SortBy; label: string }[] = [
    { value: 'created', label: 'Created Date' },
    { value: 'title', label: 'Title' },
    { value: 'priority', label: 'Priority' },
    { value: 'dueDate', label: 'Due Date' },
  ]

  return (
    <motion.div
      initial={{ opacity: 0, y: -20 }}
      animate={{ opacity: 1, y: 0 }}
      className="space-y-4"
    >
      {/* Search bar */}
      <div className="relative">
        <Search className="absolute left-4 top-1/2 -translate-y-1/2 h-5 w-5 text-muted-foreground pointer-events-none" />
        <input
          type="text"
          value={searchQuery}
          onChange={(e) => onSearchChange(e.target.value)}
          placeholder="Search tasks..."
          className={cn(
            'w-full rounded-xl border bg-card/50 pl-12 pr-12 py-4 text-base',
            'glass-card transition-all duration-200',
            'placeholder:text-muted-foreground/50',
            'focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary/50',
            'hover:border-primary/30'
          )}
        />
        {searchQuery && (
          <button
            onClick={() => onSearchChange('')}
            className="absolute right-4 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground transition-colors"
          >
            <X className="h-5 w-5" />
          </button>
        )}
      </div>

      {/* Filters */}
      <div className="flex flex-wrap gap-3">
        {/* Status filter */}
        <div className="flex gap-1 rounded-xl border border-border/50 p-1 glass-card">
          {statusFilters.map((filter) => (
            <button
              key={filter.value}
              onClick={() => onFilterStatusChange(filter.value)}
              className={cn(
                'px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200',
                filterStatus === filter.value
                  ? 'bg-primary text-primary-foreground shadow-lg'
                  : 'text-muted-foreground hover:text-foreground hover:bg-accent/50'
              )}
            >
              {filter.label}
            </button>
          ))}
        </div>

        {/* Priority filter */}
        <div className="flex gap-1 rounded-xl border border-border/50 p-1 glass-card">
          {priorityFilters.map((filter) => {
            const Icon = filter.icon
            return (
              <button
                key={filter.value}
                onClick={() => onFilterPriorityChange(filter.value)}
                className={cn(
                  'flex items-center gap-2 px-3 py-2 rounded-lg text-sm font-medium transition-all duration-200',
                  filterPriority === filter.value
                    ? filter.value === 'high'
                      ? 'bg-priority-high text-white shadow-lg'
                      : filter.value === 'medium'
                      ? 'bg-priority-medium text-black shadow-lg'
                      : filter.value === 'low'
                      ? 'bg-priority-low text-white shadow-lg'
                      : 'bg-primary text-primary-foreground shadow-lg'
                    : 'text-muted-foreground hover:text-foreground hover:bg-accent/50'
                )}
              >
                <Icon className="h-4 w-4" />
                <span className="hidden sm:inline">{filter.label}</span>
              </button>
            )
          })}
        </div>

        {/* Sort */}
        <select
          value={sortBy}
          onChange={(e) => onSortByChange(e.target.value as SortBy)}
          className={cn(
            'px-4 py-2 rounded-xl border border-border/50 glass-card',
            'text-sm font-medium text-foreground',
            'focus:outline-none focus:ring-2 focus:ring-primary/50',
            'hover:border-primary/30 transition-all duration-200',
            'cursor-pointer'
          )}
        >
          {sortOptions.map((option) => (
            <option key={option.value} value={option.value} className="bg-card">
              Sort: {option.label}
            </option>
          ))}
        </select>
      </div>
    </motion.div>
  )
}
