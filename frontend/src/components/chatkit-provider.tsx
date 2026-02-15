'use client'

import { useCallback, useEffect, useState } from 'react'
import { useChatKit, ChatKit } from '@openai/chatkit-react'
import { authClient } from '@/lib/auth-client'

const API_BASE_URL = '/api/proxy'

interface ChatKitProviderProps {
  className?: string
}

export function ChatKitProvider({ className }: ChatKitProviderProps) {
  const [userId, setUserId] = useState<string | null>(null)
  const [isReady, setIsReady] = useState(false)

  // Get user ID on mount
  useEffect(() => {
    async function loadUser() {
      try {
        const session = await authClient.getSession()
        if (session.data?.user?.id) {
          setUserId(session.data.user.id)
          setIsReady(true)
        }
      } catch (err) {
        console.error('Failed to load user session:', err)
      }
    }
    loadUser()
  }, [])

  // Custom fetch with auth headers
  const customFetch = useCallback(
    async (url: string | URL | Request, options?: RequestInit) => {
      const session = await authClient.getSession()
      const token = session.data?.session?.token

      const headers = new Headers(options?.headers)
      if (token) {
        headers.set('Authorization', `Bearer ${token}`)
      }
      headers.set('Content-Type', 'application/json')

      return fetch(url, {
        ...options,
        headers,
      })
    },
    []
  )

  const chatkit = useChatKit({
    api: {
      url: userId ? `${API_BASE_URL}/api/${userId}/chat/stream` : '',
      fetch: customFetch,
      domainKey: process.env.NEXT_PUBLIC_CHATKIT_DOMAIN_KEY || 'localhost',
    },
    onError: ({ error }) => {
      console.error('ChatKit error:', error)
    },
  })

  if (!isReady || !userId) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-gray-500 animate-pulse">Loading chat...</div>
      </div>
    )
  }

  return (
    <div className={className}>
      <ChatKit control={chatkit.control} />
    </div>
  )
}
