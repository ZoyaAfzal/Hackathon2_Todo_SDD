'use client'

import { useEffect, useState, type ReactNode } from 'react'
import { useRouter } from 'next/navigation'
import { getSession } from '@/lib/auth-client'

interface ProtectedRouteProps {
  children: ReactNode
  fallback?: ReactNode
  redirectTo?: string
}

/**
 * Protected route wrapper that ensures user is authenticated.
 *
 * Redirects to login page if user is not authenticated.
 * Shows loading state while checking authentication.
 *
 * @example
 * ```tsx
 * export default function DashboardPage() {
 *   return (
 *     <ProtectedRoute>
 *       <Dashboard />
 *     </ProtectedRoute>
 *   )
 * }
 * ```
 */
export function ProtectedRoute({
  children,
  fallback,
  redirectTo = '/login',
}: ProtectedRouteProps) {
  const router = useRouter()
  const [isLoading, setIsLoading] = useState(true)
  const [isAuthenticated, setIsAuthenticated] = useState(false)

  useEffect(() => {
    const checkAuth = async () => {
      try {
        const session = await getSession()
        if (!session) {
          router.push(redirectTo)
          return
        }
        setIsAuthenticated(true)
      } catch {
        router.push(redirectTo)
      } finally {
        setIsLoading(false)
      }
    }

    checkAuth()
  }, [router, redirectTo])

  if (isLoading) {
    return fallback ?? <LoadingSpinner />
  }

  if (!isAuthenticated) {
    return null
  }

  return <>{children}</>
}

/**
 * Default loading spinner component.
 */
function LoadingSpinner() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="text-center">
        <svg
          className="animate-spin h-10 w-10 text-blue-600 mx-auto"
          xmlns="http://www.w3.org/2000/svg"
          fill="none"
          viewBox="0 0 24 24"
        >
          <circle
            className="opacity-25"
            cx="12"
            cy="12"
            r="10"
            stroke="currentColor"
            strokeWidth="4"
          ></circle>
          <path
            className="opacity-75"
            fill="currentColor"
            d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
          ></path>
        </svg>
        <p className="mt-2 text-gray-600">Loading...</p>
      </div>
    </div>
  )
}

/**
 * HOC version of protected route for convenience.
 *
 * @example
 * ```tsx
 * const ProtectedDashboard = withProtectedRoute(Dashboard)
 * export default ProtectedDashboard
 * ```
 */
export function withProtectedRoute<P extends object>(
  Component: React.ComponentType<P>,
  options?: { redirectTo?: string }
) {
  return function ProtectedComponent(props: P) {
    return (
      <ProtectedRoute redirectTo={options?.redirectTo}>
        <Component {...props} />
      </ProtectedRoute>
    )
  }
}
