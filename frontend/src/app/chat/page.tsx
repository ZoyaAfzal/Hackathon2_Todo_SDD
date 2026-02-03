'use client'

import { ProtectedRoute } from '@/components/protected-route'
import { ChatKitProvider } from '@/components/chatkit-provider'

export default function ChatPage() {
  return (
    <ProtectedRoute>
      <div className="min-h-screen bg-white dark:bg-gray-900 flex flex-col">
        <header className="border-b px-4 py-3 flex items-center justify-between shrink-0">
          <h1 className="text-lg font-semibold text-gray-900 dark:text-white">
            Todo Chat
          </h1>
          <a
            href="/tasks"
            className="text-sm text-blue-600 hover:underline"
          >
            Task List
          </a>
        </header>
        <main className="flex-1 overflow-hidden">
          <ChatKitProvider className="h-full" />
        </main>
      </div>
    </ProtectedRoute>
  )
}
