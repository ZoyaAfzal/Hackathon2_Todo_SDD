'use client'

import { useEffect, useState, useCallback, useMemo } from 'react'
import { useRouter } from 'next/navigation'
import { motion, AnimatePresence } from 'framer-motion'
import {
  LogOut,
  Loader2,
  CheckCircle2,
  Circle,
  Sparkles,
  Command,
  Info,
  MessageCircle
} from 'lucide-react'
import {
  DndContext,
  closestCenter,
  KeyboardSensor,
  PointerSensor,
  useSensor,
  useSensors,
  DragEndEvent,
} from '@dnd-kit/core'
import {
  arrayMove,
  SortableContext,
  sortableKeyboardCoordinates,
  verticalListSortingStrategy,
  useSortable,
} from '@dnd-kit/sortable'
import { CSS } from '@dnd-kit/utilities'

import { EnhancedTaskCard } from '@/components/enhanced-task-card'
import { AddTaskForm } from '@/components/add-task-form'
import { EditTaskForm } from '@/components/edit-task-form'
import { DashboardStats } from '@/components/dashboard-stats'
import { TaskFilters, FilterStatus, SortBy } from '@/components/task-filters'
import { get, post, put, del } from '@/lib/api-client'
import { getSession, signOut } from '@/lib/auth-client'
import { cn } from '@/lib/utils'
import {
  getTaskMetadata,
  saveTaskMetadata,
  deleteTaskMetadata,
  updateTaskMetadata,
} from '@/lib/task-metadata'
import type { Task, TaskCreate, TaskUpdate, TaskListResponse } from '@/types/task'
import type { EnhancedTask, Priority } from '@/types/enhanced-task'

// Sortable task wrapper
function SortableTask({
  task,
  onComplete,
  onUncomplete,
  onEdit,
  onDelete,
  onPriorityChange,
}: {
  task: EnhancedTask
  onComplete: (task: EnhancedTask) => Promise<void>
  onUncomplete: (task: EnhancedTask) => Promise<void>
  onEdit: (task: EnhancedTask) => void
  onDelete: (task: EnhancedTask) => Promise<void>
  onPriorityChange: (taskId: string, priority: Priority) => void
}) {
  const { attributes, listeners, setNodeRef, transform, transition, isDragging } = useSortable({
    id: task.id,
  })

  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
  }

  return (
    <div ref={setNodeRef} style={style} {...attributes}>
      <EnhancedTaskCard
        task={task}
        onComplete={onComplete}
        onUncomplete={onUncomplete}
        onEdit={onEdit}
        onDelete={onDelete}
        onPriorityChange={onPriorityChange}
        isDragging={isDragging}
        dragHandleProps={listeners}
      />
    </div>
  )
}

export default function TasksPage() {
  const router = useRouter()
  const [tasks, setTasks] = useState<EnhancedTask[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [isCreating, setIsCreating] = useState(false)
  const [isEditing, setIsEditing] = useState(false)
  const [editingTask, setEditingTask] = useState<EnhancedTask | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [hasMore, setHasMore] = useState(false)
  const [nextCursor, setNextCursor] = useState<string | null>(null)
  const [showKeyboardHints, setShowKeyboardHints] = useState(false)

  // Filter and sort state
  const [searchQuery, setSearchQuery] = useState('')
  const [filterStatus, setFilterStatus] = useState<FilterStatus>('all')
  const [filterPriority, setFilterPriority] = useState<Priority | 'all'>('all')
  const [sortBy, setSortBy] = useState<SortBy>('created')

  // Drag and drop sensors
  const sensors = useSensors(
    useSensor(PointerSensor),
    useSensor(KeyboardSensor, {
      coordinateGetter: sortableKeyboardCoordinates,
    })
  )

  // Enhance tasks with metadata
  const enhanceTasks = useCallback((apiTasks: Task[]): EnhancedTask[] => {
    return apiTasks.map((task) => {
      const metadata = getTaskMetadata(task.id)
      return {
        ...task,
        priority: metadata?.priority || 'low',
        category: metadata?.category,
        dueDate: metadata?.dueDate,
      }
    })
  }, [])

  const loadTasks = useCallback(
    async (cursor?: string) => {
      try {
        const endpoint = cursor ? `/tasks?after_id=${cursor}` : '/tasks'
        const response = await get<TaskListResponse>(endpoint)

        const enhanced = enhanceTasks(response.tasks)

        if (cursor) {
          setTasks((prev) => [...prev, ...enhanced])
        } else {
          setTasks(enhanced)
        }
        setHasMore(response.has_more)
        setNextCursor(response.next_cursor)
      } catch (err) {
        if (err instanceof Error && err.message.includes('401')) {
          router.push('/login')
          return
        }
        setError(err instanceof Error ? err.message : 'Failed to load tasks')
      } finally {
        setIsLoading(false)
      }
    },
    [router, enhanceTasks]
  )

  useEffect(() => {
    const checkAuth = async () => {
      const session = await getSession()
      if (!session) {
        router.push('/login')
        return
      }
      loadTasks()
    }

    checkAuth()
  }, [router, loadTasks])

  // Keyboard shortcuts
  useEffect(() => {
    const handleKeyPress = (e: KeyboardEvent) => {
      // Cmd/Ctrl + K for keyboard hints
      if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault()
        setShowKeyboardHints((prev) => !prev)
      }
    }

    window.addEventListener('keydown', handleKeyPress)
    return () => window.removeEventListener('keydown', handleKeyPress)
  }, [])

  const handleCreateTask = async (data: TaskCreate) => {
    setIsCreating(true)
    try {
      const newTask = await post<Task>('/tasks', data)
      const enhanced = enhanceTasks([newTask])[0]
      // Set default priority to medium for new tasks
      updateTaskMetadata(enhanced.id, { priority: 'medium' })
      enhanced.priority = 'medium'
      setTasks((prev) => [enhanced, ...prev])
    } finally {
      setIsCreating(false)
    }
  }

  const handleCompleteTask = async (task: EnhancedTask) => {
    const updated = await post<Task>(`/tasks/${task.id}/complete`, {
      version: task.version,
    })
    const enhanced = enhanceTasks([updated])[0]
    setTasks((prev) => prev.map((t) => (t.id === task.id ? enhanced : t)))
  }

  const handleUncompleteTask = async (task: EnhancedTask) => {
    const updated = await post<Task>(`/tasks/${task.id}/uncomplete`, {
      version: task.version,
    })
    const enhanced = enhanceTasks([updated])[0]
    setTasks((prev) => prev.map((t) => (t.id === task.id ? enhanced : t)))
  }

  const handleDeleteTask = async (task: EnhancedTask) => {
    await del(`/tasks/${task.id}`)
    deleteTaskMetadata(task.id)
    setTasks((prev) => prev.filter((t) => t.id !== task.id))
  }

  const handleEditTask = (task: EnhancedTask) => {
    setEditingTask(task)
  }

  const handleSaveEdit = async (taskId: string, data: TaskUpdate) => {
    setIsEditing(true)
    try {
      const updated = await put<Task>(`/tasks/${taskId}`, data)
      const enhanced = enhanceTasks([updated])[0]
      setTasks((prev) => prev.map((t) => (t.id === taskId ? enhanced : t)))
      setEditingTask(null)
    } finally {
      setIsEditing(false)
    }
  }

  const handleCancelEdit = () => {
    setEditingTask(null)
  }

  const handleLogout = async () => {
    await signOut()
    router.push('/login')
  }

  const handlePriorityChange = (taskId: string, priority: Priority) => {
    updateTaskMetadata(taskId, { priority })
    setTasks((prev) =>
      prev.map((t) => (t.id === taskId ? { ...t, priority } : t))
    )
  }

  const handleDragEnd = (event: DragEndEvent) => {
    const { active, over } = event

    if (over && active.id !== over.id) {
      setTasks((items) => {
        const oldIndex = items.findIndex((item) => item.id === active.id)
        const newIndex = items.findIndex((item) => item.id === over.id)
        return arrayMove(items, oldIndex, newIndex)
      })
    }
  }

  // Filter and sort tasks
  const filteredAndSortedTasks = useMemo(() => {
    let filtered = [...tasks]

    // Search filter
    if (searchQuery) {
      const query = searchQuery.toLowerCase()
      filtered = filtered.filter(
        (t) =>
          t.title.toLowerCase().includes(query) ||
          t.description?.toLowerCase().includes(query)
      )
    }

    // Status filter
    if (filterStatus === 'active') {
      filtered = filtered.filter((t) => !t.completed)
    } else if (filterStatus === 'completed') {
      filtered = filtered.filter((t) => t.completed)
    }

    // Priority filter
    if (filterPriority !== 'all') {
      filtered = filtered.filter((t) => t.priority === filterPriority)
    }

    // Sort
    filtered.sort((a, b) => {
      switch (sortBy) {
        case 'title':
          return a.title.localeCompare(b.title)
        case 'priority': {
          const priorityOrder = { high: 0, medium: 1, low: 2 }
          return (
            priorityOrder[a.priority || 'low'] - priorityOrder[b.priority || 'low']
          )
        }
        case 'dueDate':
          if (!a.dueDate && !b.dueDate) return 0
          if (!a.dueDate) return 1
          if (!b.dueDate) return -1
          return new Date(a.dueDate).getTime() - new Date(b.dueDate).getTime()
        case 'created':
        default:
          return new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
      }
    })

    return filtered
  }, [tasks, searchQuery, filterStatus, filterPriority, sortBy])

  const completedTasks = filteredAndSortedTasks.filter((t) => t.completed)
  const activeTasks = filteredAndSortedTasks.filter((t) => !t.completed)

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-background">
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          className="text-center space-y-4"
        >
          <Loader2 className="h-12 w-12 text-primary mx-auto animate-spin glow-primary" />
          <p className="text-muted-foreground">Loading your tasks...</p>
        </motion.div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-background">
      {/* Header with glassmorphism */}
      <header className="sticky top-0 z-50 border-b border-border/50 glass backdrop-blur-xl">
        <div className="max-w-6xl mx-auto px-6 py-6">
          <div className="flex items-center justify-between">
            <motion.div
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              className="flex items-center gap-4"
            >
              <div className="h-12 w-12 rounded-xl bg-gradient-to-br from-primary to-accent flex items-center justify-center glow-primary">
                <Sparkles className="h-6 w-6 text-primary-foreground" />
              </div>
              <div>
                <h1 className="text-3xl font-bold text-gradient">Task Dashboard</h1>
                <p className="text-sm text-muted-foreground">
                  Organize your work with style
                </p>
              </div>
            </motion.div>

            <div className="flex items-center gap-3">
              <motion.a
                href="/chat"
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                className={cn(
                  'flex items-center gap-2 rounded-xl px-4 py-2 glass-card',
                  'text-sm font-medium text-muted-foreground',
                  'hover:text-foreground hover:border-primary/50 transition-all duration-200'
                )}
              >
                <MessageCircle className="h-4 w-4" />
                <span className="hidden sm:inline">Chat</span>
              </motion.a>

              <motion.button
                onClick={() => setShowKeyboardHints((prev) => !prev)}
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                className={cn(
                  'flex items-center gap-2 rounded-xl px-4 py-2 glass-card',
                  'text-sm font-medium text-muted-foreground',
                  'hover:text-foreground hover:border-primary/50 transition-all duration-200'
                )}
              >
                <Command className="h-4 w-4" />
                <span className="hidden sm:inline">Shortcuts</span>
              </motion.button>

              <motion.button
                onClick={handleLogout}
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                className={cn(
                  'flex items-center gap-2 rounded-xl px-4 py-2 glass-card',
                  'text-sm font-medium text-muted-foreground',
                  'hover:text-foreground hover:border-destructive/50 transition-all duration-200'
                )}
              >
                <LogOut className="h-4 w-4" />
                <span className="hidden sm:inline">Sign out</span>
              </motion.button>
            </div>
          </div>
        </div>
      </header>

      {/* Main content */}
      <main className="max-w-6xl mx-auto px-6 py-8 space-y-8">
        {/* Dashboard Stats */}
        <DashboardStats tasks={tasks} />

        {/* Error message */}
        <AnimatePresence>
          {error && (
            <motion.div
              initial={{ opacity: 0, y: -20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              className="rounded-xl glass-card border-destructive/50 px-6 py-4 flex items-start gap-3"
            >
              <Circle className="h-5 w-5 text-destructive mt-0.5 flex-shrink-0" />
              <div className="flex-1">
                <p className="text-sm font-medium text-destructive">{error}</p>
              </div>
              <button
                onClick={() => setError(null)}
                className="text-destructive/70 hover:text-destructive transition-colors"
              >
                <motion.div whileHover={{ rotate: 90 }} transition={{ duration: 0.2 }}>
                  <LogOut className="h-4 w-4" />
                </motion.div>
              </button>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Keyboard hints */}
        <AnimatePresence>
          {showKeyboardHints && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              exit={{ opacity: 0, height: 0 }}
              className="overflow-hidden"
            >
              <div className="rounded-xl glass-card border-primary/50 p-6">
                <div className="flex items-center gap-2 mb-4">
                  <Info className="h-5 w-5 text-primary" />
                  <h3 className="font-semibold text-foreground">Keyboard Shortcuts</h3>
                </div>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-sm">
                  <div className="flex items-center justify-between">
                    <span className="text-muted-foreground">Toggle shortcuts</span>
                    <kbd className="px-2 py-1 rounded bg-muted text-muted-foreground font-mono text-xs">
                      ⌘K / Ctrl+K
                    </kbd>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-muted-foreground">Drag to reorder</span>
                    <kbd className="px-2 py-1 rounded bg-muted text-muted-foreground font-mono text-xs">
                      Click & Drag
                    </kbd>
                  </div>
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Add task form */}
        <AddTaskForm onSubmit={handleCreateTask} isLoading={isCreating} />

        {/* Filters */}
        <TaskFilters
          searchQuery={searchQuery}
          onSearchChange={setSearchQuery}
          filterStatus={filterStatus}
          onFilterStatusChange={setFilterStatus}
          filterPriority={filterPriority}
          onFilterPriorityChange={setFilterPriority}
          sortBy={sortBy}
          onSortByChange={setSortBy}
        />

        {/* Active Tasks Section with Drag & Drop */}
        <motion.div layout className="space-y-4">
          <div className="flex items-center gap-2 px-1">
            <Circle className="h-4 w-4 text-accent" />
            <h2 className="text-sm font-semibold uppercase tracking-wider text-accent">
              Active Tasks ({activeTasks.length})
            </h2>
            <div className="h-px flex-1 bg-gradient-to-r from-accent/50 to-transparent" />
          </div>

          <DndContext
            sensors={sensors}
            collisionDetection={closestCenter}
            onDragEnd={handleDragEnd}
          >
            <SortableContext items={activeTasks} strategy={verticalListSortingStrategy}>
              <AnimatePresence mode="popLayout">
                {activeTasks.length === 0 ? (
                  <motion.div
                    key="empty-active"
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    exit={{ opacity: 0 }}
                    className="text-center py-16 space-y-3"
                  >
                    <div className="h-20 w-20 rounded-full bg-gradient-to-br from-primary/20 to-accent/20 flex items-center justify-center mx-auto">
                      <CheckCircle2 className="h-10 w-10 text-primary" />
                    </div>
                    <p className="text-muted-foreground text-lg">All caught up!</p>
                    <p className="text-sm text-muted-foreground/70">
                      No active tasks. Add one above to get started.
                    </p>
                  </motion.div>
                ) : (
                  <div className="space-y-3">
                    {activeTasks.map((task) => (
                      <SortableTask
                        key={task.id}
                        task={task}
                        onComplete={handleCompleteTask}
                        onUncomplete={handleUncompleteTask}
                        onEdit={handleEditTask}
                        onDelete={handleDeleteTask}
                        onPriorityChange={handlePriorityChange}
                      />
                    ))}
                  </div>
                )}
              </AnimatePresence>
            </SortableContext>
          </DndContext>
        </motion.div>

        {/* Completed Tasks Section */}
        <AnimatePresence>
          {completedTasks.length > 0 && (
            <motion.div
              layout
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="space-y-4"
            >
              <div className="flex items-center gap-2 px-1">
                <CheckCircle2 className="h-4 w-4 text-success" />
                <h2 className="text-sm font-semibold uppercase tracking-wider text-success">
                  Completed ({completedTasks.length})
                </h2>
                <div className="h-px flex-1 bg-gradient-to-r from-success/50 to-transparent" />
              </div>

              <div className="space-y-3">
                {completedTasks.map((task, index) => (
                  <motion.div
                    key={task.id}
                    layout
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, scale: 0.95 }}
                    transition={{ delay: index * 0.05 }}
                  >
                    <EnhancedTaskCard
                      task={task}
                      onComplete={handleCompleteTask}
                      onUncomplete={handleUncompleteTask}
                      onEdit={handleEditTask}
                      onDelete={handleDeleteTask}
                      onPriorityChange={handlePriorityChange}
                    />
                  </motion.div>
                ))}
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Load more */}
        <AnimatePresence>
          {hasMore && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: 20 }}
              className="text-center pt-4"
            >
              <motion.button
                onClick={() => loadTasks(nextCursor || undefined)}
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                className={cn(
                  'rounded-xl glass-card px-6 py-3 glow-primary',
                  'text-sm font-medium text-foreground',
                  'hover:border-primary/50 transition-all duration-200 shadow-lg'
                )}
              >
                Load more tasks
              </motion.button>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Empty state */}
        {tasks.length === 0 && (
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            className="text-center py-20 space-y-4"
          >
            <div className="h-24 w-24 rounded-full bg-gradient-to-br from-primary/20 via-accent/20 to-primary/20 flex items-center justify-center mx-auto animate-gradient glow-primary">
              <Sparkles className="h-12 w-12 text-primary" />
            </div>
            <div className="space-y-2">
              <h3 className="text-2xl font-semibold text-gradient">Ready to get started?</h3>
              <p className="text-muted-foreground max-w-md mx-auto">
                Create your first task above and start organizing your work like a pro.
              </p>
            </div>
          </motion.div>
        )}
      </main>

      {/* Edit task modal */}
      {editingTask && (
        <EditTaskForm
          task={editingTask}
          onSave={handleSaveEdit}
          onCancel={handleCancelEdit}
          isLoading={isEditing}
        />
      )}
    </div>
  )
}
