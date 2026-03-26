'use client'

import { useCallback, useEffect, useRef, useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Send, Bot, Sparkles, MessageCircle } from 'lucide-react'
import { ChatMessage } from './chat-message'
import { sendMessage, type ChatResponse } from '@/lib/chat-client'

interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
}

const SUGGESTIONS = [
  'Add a task to buy groceries',
  'Show my pending tasks',
  'Mark my first task as done',
  'What tasks do I have?',
]

export function ChatInterface() {
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [conversationId, setConversationId] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLTextAreaElement>(null)

  const scrollToBottom = useCallback(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [])

  useEffect(() => {
    scrollToBottom()
  }, [messages, loading, scrollToBottom])

  // Auto-focus input
  useEffect(() => {
    inputRef.current?.focus()
  }, [])

  const handleSend = async (text?: string) => {
    const msg = (text || input).trim()
    if (!msg || loading) return

    setInput('')
    setError(null)

    // Reset textarea height
    if (inputRef.current) {
      inputRef.current.style.height = 'auto'
    }

    const userMsg: Message = {
      id: `user-${Date.now()}`,
      role: 'user',
      content: msg,
    }
    setMessages((prev) => [...prev, userMsg])
    setLoading(true)

    try {
      const response: ChatResponse = await sendMessage(msg, conversationId)

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

  // Auto-resize textarea
  const handleInputChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setInput(e.target.value)
    e.target.style.height = 'auto'
    e.target.style.height = Math.min(e.target.scrollHeight, 120) + 'px'
  }

  return (
    <div className="flex flex-col h-[calc(100vh-4rem)] max-w-3xl mx-auto">
      {/* Messages area */}
      <div className="flex-1 overflow-y-auto px-4 py-6 space-y-4 scrollbar-thin">
        {/* Empty state */}
        <AnimatePresence>
          {messages.length === 0 && !loading && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              className="flex flex-col items-center justify-center h-full pt-12"
            >
              <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-cyan-500 to-blue-600 flex items-center justify-center mb-6 shadow-lg shadow-blue-500/20">
                <Bot className="w-8 h-8 text-white" />
              </div>
              <h2 className="text-2xl font-bold text-white mb-2">Todo Chat Assistant</h2>
              <p className="text-gray-400 text-sm mb-8 text-center max-w-md">
                Manage your tasks with natural language. Add, list, update, complete, or delete tasks just by chatting.
              </p>

              {/* Suggestion chips */}
              <div className="flex flex-wrap gap-2 justify-center max-w-lg">
                {SUGGESTIONS.map((suggestion) => (
                  <motion.button
                    key={suggestion}
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                    onClick={() => handleSend(suggestion)}
                    className="px-4 py-2 rounded-full bg-white/5 border border-white/10 text-sm text-gray-300 hover:bg-white/10 hover:border-white/20 hover:text-white transition-all"
                  >
                    <Sparkles className="w-3 h-3 inline-block mr-1.5 text-fuchsia-400" />
                    {suggestion}
                  </motion.button>
                ))}
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Messages */}
        {messages.map((msg) => (
          <ChatMessage key={msg.id} role={msg.role} content={msg.content} />
        ))}

        {/* Typing indicator */}
        <AnimatePresence>
          {loading && (
            <motion.div
              initial={{ opacity: 0, y: 12 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -12 }}
              className="flex gap-3 items-start"
            >
              <div className="shrink-0 w-8 h-8 rounded-full bg-gradient-to-br from-cyan-500 to-blue-500 flex items-center justify-center">
                <Bot className="w-4 h-4 text-white" />
              </div>
              <div className="bg-white/10 border border-white/10 rounded-2xl px-4 py-3">
                <div className="flex gap-1.5 items-center">
                  <motion.span
                    className="w-2 h-2 bg-cyan-400 rounded-full"
                    animate={{ scale: [1, 1.3, 1], opacity: [0.5, 1, 0.5] }}
                    transition={{ duration: 1, repeat: Infinity, delay: 0 }}
                  />
                  <motion.span
                    className="w-2 h-2 bg-cyan-400 rounded-full"
                    animate={{ scale: [1, 1.3, 1], opacity: [0.5, 1, 0.5] }}
                    transition={{ duration: 1, repeat: Infinity, delay: 0.2 }}
                  />
                  <motion.span
                    className="w-2 h-2 bg-cyan-400 rounded-full"
                    animate={{ scale: [1, 1.3, 1], opacity: [0.5, 1, 0.5] }}
                    transition={{ duration: 1, repeat: Infinity, delay: 0.4 }}
                  />
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        <div ref={messagesEndRef} />
      </div>

      {/* Error banner */}
      <AnimatePresence>
        {error && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            className="mx-4 mb-2 px-4 py-2 rounded-xl bg-red-500/10 border border-red-500/20 text-red-400 text-sm"
          >
            {error}
          </motion.div>
        )}
      </AnimatePresence>

      {/* Input area */}
      <div className="px-4 pb-4 pt-2">
        <div className="relative flex items-end gap-2 bg-white/5 border border-white/10 rounded-2xl px-4 py-3 focus-within:border-fuchsia-500/50 focus-within:bg-white/[0.07] transition-all">
          <MessageCircle className="w-5 h-5 text-gray-500 shrink-0 mb-0.5" />
          <textarea
            ref={inputRef}
            value={input}
            onChange={handleInputChange}
            onKeyDown={handleKeyDown}
            placeholder="Ask me to manage your tasks..."
            disabled={loading}
            rows={1}
            className="flex-1 bg-transparent text-sm text-white placeholder-gray-500 resize-none focus:outline-none disabled:opacity-50 max-h-[120px]"
          />
          <motion.button
            onClick={() => handleSend()}
            disabled={loading || !input.trim()}
            whileHover={{ scale: 1.1 }}
            whileTap={{ scale: 0.9 }}
            className="shrink-0 w-8 h-8 rounded-xl bg-gradient-to-r from-fuchsia-600 to-blue-600 flex items-center justify-center text-white disabled:opacity-30 disabled:cursor-not-allowed transition-opacity"
          >
            <Send className="w-4 h-4" />
          </motion.button>
        </div>
        <p className="text-[11px] text-gray-600 text-center mt-2">
          Press Enter to send, Shift+Enter for new line
        </p>
      </div>
    </div>
  )
}
