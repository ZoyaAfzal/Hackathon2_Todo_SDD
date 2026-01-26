'use client'

import { motion } from 'framer-motion'
import { CheckCircle2, Circle, Clock, TrendingUp } from 'lucide-react'
import { cn } from '@/lib/utils'
import type { EnhancedTask } from '@/types/enhanced-task'

interface DashboardStatsProps {
  tasks: EnhancedTask[]
}

export function DashboardStats({ tasks }: DashboardStatsProps) {
  const total = tasks.length
  const completed = tasks.filter((t) => t.completed).length
  const active = total - completed
  const completionRate = total > 0 ? Math.round((completed / total) * 100) : 0

  const stats = [
    {
      label: 'Total Tasks',
      value: total,
      icon: Clock,
      color: 'text-primary',
      bgColor: 'bg-primary/10',
      glowColor: 'glow-primary',
    },
    {
      label: 'Active',
      value: active,
      icon: Circle,
      color: 'text-accent',
      bgColor: 'bg-accent/10',
      glowColor: 'glow-accent',
    },
    {
      label: 'Completed',
      value: completed,
      icon: CheckCircle2,
      color: 'text-success',
      bgColor: 'bg-success/10',
      glowColor: 'glow-success',
    },
    {
      label: 'Completion',
      value: `${completionRate}%`,
      icon: TrendingUp,
      color: 'text-warning',
      bgColor: 'bg-warning/10',
      glowColor: '',
    },
  ]

  return (
    <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
      {stats.map((stat, index) => {
        const Icon = stat.icon
        return (
          <motion.div
            key={stat.label}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1 }}
            whileHover={{ y: -4, scale: 1.02 }}
            className={cn(
              'relative overflow-hidden rounded-xl border border-border/50 p-6',
              'glass-card transition-all duration-300',
              'hover:border-primary/50',
              stat.glowColor && `hover:${stat.glowColor}`
            )}
          >
            {/* Gradient background */}
            <div className="absolute inset-0 bg-gradient-to-br from-primary/5 via-transparent to-accent/5 opacity-50" />

            {/* Content */}
            <div className="relative space-y-3">
              <div className="flex items-center justify-between">
                <div
                  className={cn(
                    'flex h-12 w-12 items-center justify-center rounded-lg',
                    stat.bgColor
                  )}
                >
                  <Icon className={cn('h-6 w-6', stat.color)} />
                </div>
              </div>

              <div className="space-y-1">
                <p className="text-sm text-muted-foreground font-medium">
                  {stat.label}
                </p>
                <p className={cn('text-3xl font-bold', stat.color)}>
                  {stat.value}
                </p>
              </div>
            </div>

            {/* Shine effect on hover */}
            <motion.div
              className="absolute inset-0 bg-gradient-to-r from-transparent via-white/5 to-transparent"
              initial={{ x: '-100%' }}
              whileHover={{ x: '100%' }}
              transition={{ duration: 0.6 }}
            />
          </motion.div>
        )
      })}
    </div>
  )
}
