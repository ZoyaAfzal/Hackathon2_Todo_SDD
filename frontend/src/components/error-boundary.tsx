'use client'

import { Component, type ReactNode, type ErrorInfo } from 'react'

interface ErrorBoundaryProps {
  children: ReactNode
  fallback?: ReactNode
  onError?: (error: Error, errorInfo: ErrorInfo) => void
}

interface ErrorBoundaryState {
  hasError: boolean
  error: Error | null
}

/**
 * Error boundary component that catches JavaScript errors in child components.
 *
 * Displays a fallback UI instead of crashing the entire application.
 * Optionally reports errors to an error tracking service.
 *
 * @example
 * ```tsx
 * <ErrorBoundary
 *   fallback={<ErrorFallback />}
 *   onError={(error) => reportError(error)}
 * >
 *   <MyComponent />
 * </ErrorBoundary>
 * ```
 */
export class ErrorBoundary extends Component<
  ErrorBoundaryProps,
  ErrorBoundaryState
> {
  constructor(props: ErrorBoundaryProps) {
    super(props)
    this.state = { hasError: false, error: null }
  }

  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    return { hasError: true, error }
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo): void {
    // Log error to console in development
    console.error('ErrorBoundary caught an error:', error, errorInfo)

    // Call optional error handler
    this.props.onError?.(error, errorInfo)
  }

  handleRetry = (): void => {
    this.setState({ hasError: false, error: null })
  }

  render(): ReactNode {
    if (this.state.hasError) {
      if (this.props.fallback) {
        return this.props.fallback
      }

      return (
        <DefaultErrorFallback
          error={this.state.error}
          onRetry={this.handleRetry}
        />
      )
    }

    return this.props.children
  }
}

interface DefaultErrorFallbackProps {
  error: Error | null
  onRetry: () => void
}

/**
 * Default error fallback UI.
 */
function DefaultErrorFallback({ error, onRetry }: DefaultErrorFallbackProps) {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 px-4">
      <div className="max-w-md w-full bg-white rounded-lg shadow-lg p-6 text-center">
        <div className="w-12 h-12 rounded-full bg-red-100 mx-auto flex items-center justify-center">
          <svg
            className="w-6 h-6 text-red-600"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
            />
          </svg>
        </div>

        <h2 className="mt-4 text-lg font-semibold text-gray-900">
          Something went wrong
        </h2>

        <p className="mt-2 text-sm text-gray-600">
          An unexpected error occurred. Please try again.
        </p>

        {error && process.env.NODE_ENV === 'development' && (
          <div className="mt-4 p-3 bg-gray-100 rounded text-left">
            <p className="text-xs font-mono text-gray-700 break-all">
              {error.message}
            </p>
          </div>
        )}

        <div className="mt-6 flex gap-3 justify-center">
          <button
            onClick={onRetry}
            className="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
          >
            Try Again
          </button>
          <button
            onClick={() => window.location.reload()}
            className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-200 rounded-md hover:bg-gray-300 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gray-500"
          >
            Refresh Page
          </button>
        </div>
      </div>
    </div>
  )
}

/**
 * Hook-friendly error boundary wrapper using React 18+ features.
 *
 * Note: This is a simplified version. For production, consider
 * using react-error-boundary library for more features.
 */
export function withErrorBoundary<P extends object>(
  Component: React.ComponentType<P>,
  options?: {
    fallback?: ReactNode
    onError?: (error: Error, errorInfo: ErrorInfo) => void
  }
) {
  return function WithErrorBoundary(props: P) {
    return (
      <ErrorBoundary
        fallback={options?.fallback}
        onError={options?.onError}
      >
        <Component {...props} />
      </ErrorBoundary>
    )
  }
}
