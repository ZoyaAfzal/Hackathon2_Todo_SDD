'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { motion } from 'framer-motion'
import { AuthForm } from '@/components/auth-form'
import { signIn } from '@/lib/auth-client'
import { Zap, CheckCircle2, Shield, Sparkles } from 'lucide-react'

export default function LoginPage() {
  const router = useRouter()
  const [error, setError] = useState<string | null>(null)
  const [isLoading, setIsLoading] = useState(false)

  const handleLogin = async (email: string, password: string) => {
    setError(null)
    setIsLoading(true)

    try {
      const result = await signIn(email, password)

      if (result.error) {
        setError(result.error.message || 'Invalid email or password')
        return
      }

      router.push('/tasks')
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred during login')
    } finally {
      setIsLoading(false)
    }
  }

  const features = [
    { icon: CheckCircle2, text: 'Track your tasks effortlessly' },
    { icon: Zap, text: 'Lightning fast performance' },
    { icon: Shield, text: 'Secure & private' },
  ]

  return (
    <div className="min-h-screen bg-black flex">
      {/* Left side - Branding */}
      <div className="hidden lg:flex lg:w-1/2 relative overflow-hidden">
        {/* Animated gradient background */}
        <div className="absolute inset-0 bg-gradient-to-bl from-fuchsia-600/20 via-blue-800/20 to-cyan-400/20" />

        {/* Animated orbs */}
        <motion.div
          className="absolute top-1/3 right-1/4 w-96 h-96 bg-fuchsia-500/30 rounded-full blur-3xl"
          animate={{
            scale: [1, 1.3, 1],
            opacity: [0.3, 0.5, 0.3],
          }}
          transition={{ duration: 10, repeat: Infinity }}
        />
        <motion.div
          className="absolute bottom-1/3 left-1/4 w-96 h-96 bg-blue-700/30 rounded-full blur-3xl"
          animate={{
            scale: [1.3, 1, 1.3],
            opacity: [0.5, 0.3, 0.5],
          }}
          transition={{ duration: 10, repeat: Infinity }}
        />

        {/* Content */}
        <div className="relative z-10 flex flex-col justify-center px-12 xl:px-20">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
          >
            <div className="flex items-center gap-3 mb-8">
              <div className="w-12 h-12 brand-gradient rounded-xl flex items-center justify-center shadow-brand-sm">
                <Sparkles className="w-7 h-7 text-white" />
              </div>
              <span className="text-3xl font-bold text-white">TaskFlow</span>
            </div>

            <h1 className="text-5xl xl:text-6xl font-bold text-white mb-6 leading-tight">
              Organize your life,
              <br />
              <span className="text-brand-gradient">
                one task at a time
              </span>
            </h1>

            <p className="text-xl text-gray-400 mb-12 max-w-md">
              The modern task management app that helps you stay focused and get things done.
            </p>

            <div className="space-y-4">
              {features.map((feature, index) => (
                <motion.div
                  key={index}
                  className="flex items-center gap-4"
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 0.5 + index * 0.1 }}
                >
                  <div className="w-12 h-12 bg-gradient-to-br from-fuchsia-500/20 to-blue-700/20 rounded-xl flex items-center justify-center border border-fuchsia-500/30 shadow-lg shadow-fuchsia-500/10">
                    <feature.icon className="w-6 h-6 text-fuchsia-400" />
                  </div>
                  <span className="text-gray-300">{feature.text}</span>
                </motion.div>
              ))}
            </div>
          </motion.div>
        </div>
      </div>

      {/* Right side - Login form */}
      <div className="w-full lg:w-1/2 flex items-center justify-center p-8">
        <div className="w-full max-w-md">
          {/* Mobile logo */}
          <motion.div
            className="flex items-center gap-3 mb-8 lg:hidden"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
          >
            <div className="w-10 h-10 brand-gradient rounded-xl flex items-center justify-center shadow-brand-sm">
              <Sparkles className="w-6 h-6 text-white" />
            </div>
            <span className="text-2xl font-bold text-white">TaskFlow</span>
          </motion.div>

          {/* Enhanced Glassmorphism card */}
          <motion.div
            className="relative bg-gradient-to-br from-white/10 via-blue-900/10 to-fuchsia-900/10 backdrop-blur-xl border border-fuchsia-500/20 rounded-3xl p-8 shadow-2xl overflow-hidden"
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.5 }}
          >
            {/* Card glow effect */}
            <div className="absolute -inset-1 bg-gradient-to-br from-fuchsia-500/10 via-transparent to-cyan-400/10 rounded-3xl blur-xl" />
            <div className="relative z-10 mb-8">
              <h2 className="text-3xl font-bold text-white mb-2">Welcome back</h2>
              <p className="text-gray-400">
                Sign in to continue to your tasks
              </p>
            </div>

            <div className="relative z-10">
              <AuthForm
                mode="login"
                onSubmit={handleLogin}
                error={error}
                isLoading={isLoading}
              />
            </div>

            <div className="relative z-10 mt-8 text-center">
              <p className="text-gray-400">
                Don't have an account?{' '}
                <Link
                  href="/register"
                  className="text-fuchsia-400 hover:text-fuchsia-300 font-medium transition-colors"
                >
                  Create one
                </Link>
              </p>
            </div>
          </motion.div>

          {/* Footer */}
          <motion.p
            className="text-center text-gray-600 text-sm mt-8"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.8 }}
          >
            By signing in, you agree to our Terms of Service
          </motion.p>
        </div>
      </div>
    </div>
  )
}
