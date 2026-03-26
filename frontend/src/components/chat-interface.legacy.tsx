'use client'

import { useCallback, useEffect, useRef, useState } from 'react'
import { ChatMessage } from './chat-message.legacy'
import { sendMessage, type ChatResponse } from '@/lib/chat-client.legacy'

interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
}

export function ChatInterface() {
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [conversationId, setConversationId] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const scrollToBottom = useCallback(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [])

  useEffect(() => {
    scrollToBottom()
  }, [messages, scrollToBottom])

  const handleSend = async () => {
    const text = input.trim()
    if (!text || loading) return

    setInput('')
    setError(null)

    const userMsg: Message = {
      id: `user-${Date.now()}`,
      role: 'user',
      content: text,
    }
    setMessages((prev) => [...prev, userMsg])
    setLoading(true)

    try {
      const response: ChatResponse = await sendMessage(text, conversationId)

      if (!conversationId) {
        setConversationId(response.conversation_id)
      }

      const assistantMsg: Message = {
        id: `assistant-${Date.now()}`,
        role: 'assistant',
        content: response.reply,
      }
      setMessages((prev) => [...prev, assistantMsg])
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Something went wrong'
      setError(message)
    } finally {
      setLoading(false)
    }
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  return (
    <div className="flex flex-col h-[calc(100vh-8rem)] max-w-3xl mx-auto">
      <div className="flex-1 overflow-y-auto p-4 space-y-2">
        {messages.length === 0 && (
          <div className="text-center text-gray-500 mt-20">
            <p className="text-lg font-medium">Todo Chat Assistant</p>
            <p className="text-sm mt-2">
              Try: &quot;Add a task to buy groceries&quot; or &quot;Show my pending tasks&quot;
            </p>
          </div>
        )}
        {messages.map((msg) => (
          <ChatMessage key={msg.id} role={msg.role} content={msg.content} />
        ))}
        {loading && (
          <div className="flex justify-start mb-3">
            <div className="bg-gray-100 dark:bg-gray-800 rounded-lg px-4 py-2">
              <p className="text-sm text-gray-500 animate-pulse">Thinking...</p>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {error && (
        <div className="px-4 py-2 bg-red-50 dark:bg-red-900/20 text-red-600 dark:text-red-400 text-sm">
          {error}
        </div>
      )}

      <div className="border-t p-4">
        <div className="flex gap-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Type a message..."
            disabled={loading}
            className="flex-1 rounded-lg border border-gray-300 dark:border-gray-600 px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-800 dark:text-white disabled:opacity-50"
          />
          <button
            onClick={handleSend}
            disabled={loading || !input.trim()}
            className="rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Send
          </button>
        </div>
      </div>
    </div>
  )
}
