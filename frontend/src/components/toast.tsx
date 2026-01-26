'use client'

import { createContext, useContext, useState, useCallback, ReactNode } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { CheckCircle2, XCircle, AlertCircle, Info, X } from 'lucide-react'
import { cn } from '@/lib/utils'

type ToastType = 'success' | 'error' | 'warning' | 'info'

interface Toast {
  id: string
  type: ToastType
  message: string
  duration?: number
}

interface ToastContextType {
  showToast: (type: ToastType, message: string, duration?: number) => void
  success: (message: string) => void
  error: (message: string) => void
  warning: (message: string) => void
  info: (message: string) => void
}

const ToastContext = createContext<ToastContextType | undefined>(undefined)

export function useToast() {
  const context = useContext(ToastContext)
  if (!context) {
    throw new Error('useToast must be used within a ToastProvider')
  }
  return context
}

const toastIcons = {
  success: CheckCircle2,
  error: XCircle,
  warning: AlertCircle,
  info: Info,
}

const toastStyles = {
  success: {
    bg: 'bg-success/10',
    border: 'border-success/50',
    text: 'text-success',
    icon: 'text-success',
  },
  error: {
    bg: 'bg-destructive/10',
    border: 'border-destructive/50',
    text: 'text-destructive',
    icon: 'text-destructive',
  },
  warning: {
    bg: 'bg-warning/10',
    border: 'border-warning/50',
    text: 'text-warning',
    icon: 'text-warning',
  },
  info: {
    bg: 'bg-primary/10',
    border: 'border-primary/50',
    text: 'text-primary',
    icon: 'text-primary',
  },
}

export function ToastProvider({ children }: { children: ReactNode }) {
  const [toasts, setToasts] = useState<Toast[]>([])

  const removeToast = useCallback((id: string) => {
    setToasts((prev) => prev.filter((toast) => toast.id !== id))
  }, [])

  const showToast = useCallback(
    (type: ToastType, message: string, duration = 3000) => {
      const id = Math.random().toString(36).substring(7)
      const toast: Toast = { id, type, message, duration }

      setToasts((prev) => [...prev, toast])

      if (duration > 0) {
        setTimeout(() => {
          removeToast(id)
        }, duration)
      }
    },
    [removeToast]
  )

  const success = useCallback((message: string) => showToast('success', message), [showToast])
  const error = useCallback((message: string) => showToast('error', message), [showToast])
  const warning = useCallback((message: string) => showToast('warning', message), [showToast])
  const info = useCallback((message: string) => showToast('info', message), [showToast])

  return (
    <ToastContext.Provider value={{ showToast, success, error, warning, info }}>
      {children}

      {/* Toast container */}
      <div className="fixed bottom-4 right-4 z-[100] space-y-2 pointer-events-none">
        <AnimatePresence>
          {toasts.map((toast) => {
            const Icon = toastIcons[toast.type]
            const styles = toastStyles[toast.type]

            return (
              <motion.div
                key={toast.id}
                initial={{ opacity: 0, y: 20, scale: 0.95 }}
                animate={{ opacity: 1, y: 0, scale: 1 }}
                exit={{ opacity: 0, y: -20, scale: 0.95 }}
                className={cn(
                  'flex items-start gap-3 p-4 rounded-xl border glass-card shadow-lg max-w-md pointer-events-auto',
                  styles.bg,
                  styles.border
                )}
              >
                <Icon className={cn('h-5 w-5 mt-0.5 flex-shrink-0', styles.icon)} />
                <p className={cn('text-sm font-medium flex-1', styles.text)}>{toast.message}</p>
                <button
                  onClick={() => removeToast(toast.id)}
                  className={cn(
                    'flex-shrink-0 transition-opacity hover:opacity-70',
                    styles.text
                  )}
                >
                  <X className="h-4 w-4" />
                </button>
              </motion.div>
            )
          })}
        </AnimatePresence>
      </div>
    </ToastContext.Provider>
  )
}
