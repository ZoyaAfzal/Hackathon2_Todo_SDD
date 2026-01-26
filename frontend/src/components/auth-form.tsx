'use client'

import { useState } from 'react'
import { motion } from 'framer-motion'
import { Mail, Lock, User, Loader2, ArrowRight, Eye, EyeOff } from 'lucide-react'

interface AuthFormProps {
  mode: 'login' | 'register'
  onSubmit: (email: string, password: string, name?: string) => Promise<void>
  error?: string | null
  isLoading?: boolean
}

export function AuthForm({ mode, onSubmit, error, isLoading = false }: AuthFormProps) {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [name, setName] = useState('')
  const [localError, setLocalError] = useState<string | null>(null)
  const [showPassword, setShowPassword] = useState(false)
  const [focusedField, setFocusedField] = useState<string | null>(null)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLocalError(null)

    if (!email || !password) {
      setLocalError('Email and password are required')
      return
    }

    if (password.length < 8) {
      setLocalError('Password must be at least 8 characters')
      return
    }

    try {
      await onSubmit(email, password, mode === 'register' ? name : undefined)
    } catch (err) {
      setLocalError(err instanceof Error ? err.message : 'An error occurred')
    }
  }

  const displayError = error || localError

  const inputVariants = {
    focused: { scale: 1.02, boxShadow: '0 0 20px rgba(0, 191, 255, 0.3)' },
    unfocused: { scale: 1, boxShadow: '0 0 0px rgba(0, 191, 255, 0)' }
  }

  return (
    <motion.form
      onSubmit={handleSubmit}
      className="space-y-6 w-full"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay: 0.2 }}
    >
      {displayError && (
        <motion.div
          className="bg-red-500/10 border border-red-500/50 text-red-400 px-4 py-3 rounded-xl backdrop-blur-sm"
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ type: 'spring', stiffness: 500, damping: 30 }}
        >
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 bg-red-500 rounded-full animate-pulse" />
            {displayError}
          </div>
        </motion.div>
      )}

      {mode === 'register' && (
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
        >
          <label htmlFor="name" className="block text-sm font-medium text-gray-300 mb-2">
            Name (optional)
          </label>
          <motion.div
            className="relative"
            variants={inputVariants}
            animate={focusedField === 'name' ? 'focused' : 'unfocused'}
          >
            <User className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-500" />
            <input
              type="text"
              id="name"
              value={name}
              onChange={(e) => setName(e.target.value)}
              onFocus={() => setFocusedField('name')}
              onBlur={() => setFocusedField(null)}
              className="w-full pl-12 pr-4 py-4 bg-white/5 border border-white/10 rounded-xl text-white placeholder-gray-500 focus:outline-none focus:border-cyan-500/50 focus:bg-white/10 transition-all duration-300"
              placeholder="John Doe"
              disabled={isLoading}
            />
          </motion.div>
        </motion.div>
      )}

      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: mode === 'register' ? 0.2 : 0.1 }}
      >
        <label htmlFor="email" className="block text-sm font-medium text-gray-300 mb-2">
          Email
        </label>
        <motion.div
          className="relative"
          variants={inputVariants}
          animate={focusedField === 'email' ? 'focused' : 'unfocused'}
        >
          <Mail className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-500" />
          <input
            type="email"
            id="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            onFocus={() => setFocusedField('email')}
            onBlur={() => setFocusedField(null)}
            required
            className="w-full pl-12 pr-4 py-4 bg-white/5 border border-white/10 rounded-xl text-white placeholder-gray-500 focus:outline-none focus:border-cyan-500/50 focus:bg-white/10 transition-all duration-300"
            placeholder="you@example.com"
            disabled={isLoading}
          />
        </motion.div>
      </motion.div>

      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: mode === 'register' ? 0.3 : 0.2 }}
      >
        <label htmlFor="password" className="block text-sm font-medium text-gray-300 mb-2">
          Password
        </label>
        <motion.div
          className="relative"
          variants={inputVariants}
          animate={focusedField === 'password' ? 'focused' : 'unfocused'}
        >
          <Lock className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-500" />
          <input
            type={showPassword ? 'text' : 'password'}
            id="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            onFocus={() => setFocusedField('password')}
            onBlur={() => setFocusedField(null)}
            required
            minLength={8}
            className="w-full pl-12 pr-12 py-4 bg-white/5 border border-white/10 rounded-xl text-white placeholder-gray-500 focus:outline-none focus:border-cyan-500/50 focus:bg-white/10 transition-all duration-300"
            placeholder="Minimum 8 characters"
            disabled={isLoading}
          />
          <button
            type="button"
            onClick={() => setShowPassword(!showPassword)}
            className="absolute right-4 top-1/2 -translate-y-1/2 text-gray-500 hover:text-cyan-400 transition-colors"
          >
            {showPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
          </button>
        </motion.div>
        <p className="mt-2 text-xs text-gray-500">Must be at least 8 characters</p>
      </motion.div>

      <motion.button
        type="submit"
        disabled={isLoading}
        className="relative w-full py-4 px-6 bg-gradient-to-r from-cyan-500 to-blue-600 text-white font-semibold rounded-xl overflow-hidden group disabled:opacity-50 disabled:cursor-not-allowed"
        whileHover={{ scale: 1.02 }}
        whileTap={{ scale: 0.98 }}
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: mode === 'register' ? 0.4 : 0.3 }}
      >
        {/* Animated background */}
        <div className="absolute inset-0 bg-gradient-to-r from-cyan-400 to-blue-500 opacity-0 group-hover:opacity-100 transition-opacity duration-300" />

        {/* Shine effect */}
        <div className="absolute inset-0 opacity-0 group-hover:opacity-100">
          <div className="absolute inset-0 translate-x-[-100%] group-hover:translate-x-[100%] transition-transform duration-1000 bg-gradient-to-r from-transparent via-white/20 to-transparent" />
        </div>

        <span className="relative flex items-center justify-center gap-2">
          {isLoading ? (
            <>
              <Loader2 className="w-5 h-5 animate-spin" />
              {mode === 'login' ? 'Signing in...' : 'Creating account...'}
            </>
          ) : (
            <>
              {mode === 'login' ? 'Sign in' : 'Create account'}
              <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
            </>
          )}
        </span>
      </motion.button>
    </motion.form>
  )
}
