'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { motion } from 'framer-motion'
import { AuthForm } from '@/components/auth-form'
import { signUp } from '@/lib/auth-client'
import { Rocket, Star, Zap, Sparkles } from 'lucide-react'

export default function RegisterPage() {
  const router = useRouter()
  const [error, setError] = useState<string | null>(null)
  const [isLoading, setIsLoading] = useState(false)

  const handleRegister = async (email: string, password: string, name?: string) => {
    setError(null)
    setIsLoading(true)

    try {
      const result = await signUp(email, password, name)

      if (result.error) {
        const errorMessage = result.error.message || 'Registration failed'
        if (errorMessage.toLowerCase().includes('exist')) {
          setError('An account with this email already exists')
        } else {
          setError(errorMessage)
        }
        return
      }

      router.push('/tasks')
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred during registration')
    } finally {
      setIsLoading(false)
    }
  }

  const benefits = [
    { icon: Rocket, text: 'Get started in seconds', color: 'from-pink-500 to-rose-500' },
    { icon: Star, text: 'Unlimited tasks & projects', color: 'from-amber-500 to-orange-500' },
    { icon: Zap, text: 'Sync across all devices', color: 'from-cyan-500 to-blue-500' },
  ]

  return (
    <div className="min-h-screen bg-black flex">
      {/* Left side - Registration form */}
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
              <h2 className="text-3xl font-bold text-white mb-2">Create account</h2>
              <p className="text-gray-400">
                Start organizing your tasks today
              </p>
            </div>

            <div className="relative z-10">
              <AuthForm
                mode="register"
                onSubmit={handleRegister}
                error={error}
                isLoading={isLoading}
              />
            </div>

            <div className="relative z-10 mt-8 text-center">
              <p className="text-gray-400">
                Already have an account?{' '}
                <Link
                  href="/login"
                  className="text-fuchsia-400 hover:text-fuchsia-300 font-medium transition-colors"
                >
                  Sign in
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
            By creating an account, you agree to our Terms of Service
          </motion.p>
        </div>
      </div>

      {/* Right side - Branding */}
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
              Start your
              <br />
              <span className="text-brand-gradient">
                productivity journey
              </span>
            </h1>

            <p className="text-xl text-gray-400 mb-12 max-w-md">
              Join thousands of users who have transformed the way they manage tasks.
            </p>

            <div className="space-y-6">
              {benefits.map((benefit, index) => (
                <motion.div
                  key={index}
                  className="flex items-center gap-4"
                  initial={{ opacity: 0, x: 20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 0.5 + index * 0.15 }}
                >
                  <div className={`w-12 h-12 bg-gradient-to-br ${benefit.color} rounded-xl flex items-center justify-center shadow-lg shadow-fuchsia-500/20 ring-2 ring-white/10`}>
                    <benefit.icon className="w-6 h-6 text-white" />
                  </div>
                  <span className="text-lg text-gray-300">{benefit.text}</span>
                </motion.div>
              ))}
            </div>

            {/* Social proof */}
            <motion.div
              className="mt-12 flex items-center gap-4 bg-white/5 backdrop-blur-sm rounded-2xl p-4 border border-white/10"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 1 }}
            >
              <div className="flex -space-x-3">
                {[...Array(4)].map((_, i) => (
                  <div
                    key={i}
                    className="w-10 h-10 rounded-full bg-gradient-to-br from-fuchsia-500/30 to-blue-700/30 border-2 border-fuchsia-500/30 flex items-center justify-center text-xs text-white font-medium shadow-lg"
                  >
                    {String.fromCharCode(65 + i)}
                  </div>
                ))}
              </div>
              <p className="text-gray-400">
                <span className="text-fuchsia-400 font-semibold">1,000+</span> happy users
              </p>
            </motion.div>
          </motion.div>
        </div>
      </div>
    </div>
  )
}
