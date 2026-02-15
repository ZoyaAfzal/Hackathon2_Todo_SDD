'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'
import { motion, useScroll, useTransform, AnimatePresence } from 'framer-motion'
import {
  Sparkles,
  CheckCircle2,
  Zap,
  Shield,
  ArrowRight,
  LayoutDashboard,
  Bell,
  Calendar,
  Users,
  Star,
  ChevronDown,
  ChevronUp,
  Target,
  TrendingUp,
  Mail,
  Check,
  Quote
} from 'lucide-react'

export default function HomePage() {
  const [activeTestimonial, setActiveTestimonial] = useState(0)
  const [openFaq, setOpenFaq] = useState<number | null>(null)
  const [mousePosition, setMousePosition] = useState({ x: 0, y: 0 })
  const [email, setEmail] = useState('')
  const [isSubmitted, setIsSubmitted] = useState(false)

  const { scrollYProgress } = useScroll()
  const backgroundY = useTransform(scrollYProgress, [0, 1], ['0%', '100%'])

  // Mouse parallax effect
  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      setMousePosition({ x: e.clientX, y: e.clientY })
    }
    window.addEventListener('mousemove', handleMouseMove)
    return () => window.removeEventListener('mousemove', handleMouseMove)
  }, [])

  // Auto-rotate testimonials
  useEffect(() => {
    const interval = setInterval(() => {
      setActiveTestimonial((prev) => (prev + 1) % testimonials.length)
    }, 5000)
    return () => clearInterval(interval)
  }, [])

  const features = [
    {
      icon: LayoutDashboard,
      title: 'Beautiful Dashboard',
      description: 'Track all your tasks with an intuitive, modern interface',
      color: 'from-cyan-500 to-blue-600'
    },
    {
      icon: Zap,
      title: 'Lightning Fast',
      description: 'Optimized performance for instant task management',
      color: 'from-yellow-500 to-orange-500'
    },
    {
      icon: Shield,
      title: 'Secure & Private',
      description: 'Your data is encrypted and always protected',
      color: 'from-green-500 to-emerald-600'
    },
    {
      icon: Bell,
      title: 'Smart Notifications',
      description: 'Never miss a deadline with intelligent reminders',
      color: 'from-purple-500 to-pink-600'
    },
    {
      icon: Calendar,
      title: 'Smart Scheduling',
      description: 'AI-powered task scheduling and prioritization',
      color: 'from-indigo-500 to-purple-600'
    },
    {
      icon: Users,
      title: 'Team Collaboration',
      description: 'Work together seamlessly with your team',
      color: 'from-pink-500 to-rose-600'
    },
  ]

  const howItWorks = [
    {
      step: '01',
      icon: Target,
      title: 'Create Your Tasks',
      description: 'Add tasks with descriptions, deadlines, and priorities in seconds'
    },
    {
      step: '02',
      icon: TrendingUp,
      title: 'Organize & Prioritize',
      description: 'Let AI help you organize and prioritize your workload automatically'
    },
    {
      step: '03',
      icon: CheckCircle2,
      title: 'Get Things Done',
      description: 'Track progress, celebrate achievements, and stay motivated'
    },
  ]

  const testimonials = [
    {
      name: 'Sarah Johnson',
      role: 'Product Manager',
      company: 'TechCorp',
      content: 'TaskFlow transformed how our team manages projects. The interface is intuitive and the AI suggestions are incredibly helpful.',
      rating: 5,
      avatar: 'SJ'
    },
    {
      name: 'Michael Chen',
      role: 'Founder',
      company: 'StartupXYZ',
      content: 'Best task management tool I\'ve used. Clean design, powerful features, and the mobile app is perfect.',
      rating: 5,
      avatar: 'MC'
    },
    {
      name: 'Emily Rodriguez',
      role: 'Designer',
      company: 'Creative Studios',
      content: 'Finally, a todo app that\'s both beautiful and functional. The dark mode is gorgeous!',
      rating: 5,
      avatar: 'ER'
    },
  ]

  const faqs = [
    {
      question: 'Is TaskFlow free to use?',
      answer: 'Yes! TaskFlow offers a generous free tier with all core features. Premium plans are available for teams and advanced features.'
    },
    {
      question: 'Can I collaborate with my team?',
      answer: 'Absolutely! TaskFlow supports team collaboration with shared workspaces, task assignments, and real-time updates.'
    },
    {
      question: 'Is my data secure?',
      answer: 'Your data is encrypted end-to-end and stored securely. We never share your information with third parties.'
    },
    {
      question: 'What platforms are supported?',
      answer: 'TaskFlow works on all modern web browsers, with native iOS and Android apps coming soon.'
    },
    {
      question: 'Can I import my existing tasks?',
      answer: 'Yes! We support importing from popular task management tools like Todoist, Trello, and Asana.'
    },
  ]

  const handleNewsletterSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    setIsSubmitted(true)
    setTimeout(() => {
      setIsSubmitted(false)
      setEmail('')
    }, 3000)
  }

  return (
    <div className="min-h-screen bg-black overflow-hidden">
      {/* Animated floating orbs that follow mouse */}
      <div className="fixed inset-0 pointer-events-none">
        <motion.div
          className="absolute w-[600px] h-[600px] bg-gradient-to-br from-fuchsia-500/30 to-blue-800/25 rounded-full blur-[120px]"
          animate={{
            x: mousePosition.x * 0.02,
            y: mousePosition.y * 0.02,
            scale: [1, 1.2, 1],
            opacity: [0.4, 0.6, 0.4],
          }}
          transition={{ duration: 8, repeat: Infinity }}
          style={{
            top: '20%',
            left: '20%',
          }}
        />
        <motion.div
          className="absolute w-[600px] h-[600px] bg-gradient-to-br from-blue-700/30 to-cyan-300/25 rounded-full blur-[120px]"
          animate={{
            x: -mousePosition.x * 0.015,
            y: -mousePosition.y * 0.015,
            scale: [1.2, 1, 1.2],
            opacity: [0.5, 0.3, 0.5],
          }}
          transition={{ duration: 10, repeat: Infinity }}
          style={{
            bottom: '20%',
            right: '20%',
          }}
        />
        <motion.div
          className="absolute w-[800px] h-[800px] bg-gradient-to-br from-fuchsia-500/20 via-blue-800/15 to-cyan-300/20 rounded-full blur-[150px]"
          animate={{
            rotate: [0, 360],
            scale: [1, 1.1, 1],
          }}
          transition={{ duration: 60, repeat: Infinity, ease: 'linear' }}
          style={{
            top: '50%',
            left: '50%',
            transform: 'translate(-50%, -50%)',
          }}
        />
      </div>

      {/* Navigation */}
      <nav className="fixed top-0 left-0 right-0 z-50 bg-transparent backdrop-blur-2xl border-b border-white/10 shadow-lg">
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          <motion.div
            className="flex items-center gap-3"
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
          >
            <div className="w-11 h-11 brand-gradient rounded-xl flex items-center justify-center shadow-brand-sm">
              <Sparkles className="w-6 h-6 text-white" />
            </div>
            <span className="text-xl font-bold bg-gradient-to-r from-white to-gray-300 bg-clip-text text-transparent">TaskFlow</span>
          </motion.div>

          <motion.div
            className="flex items-center gap-3"
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
          >
            <Link href="/login">
              <motion.button
                className="text-gray-300 hover:text-white transition-colors px-5 py-2.5 rounded-lg hover:bg-white/5"
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
              >
                Sign in
              </motion.button>
            </Link>
            <Link href="/register">
              <motion.button
                className="brand-gradient text-white px-6 py-2.5 rounded-xl font-semibold shadow-brand-sm hover:shadow-brand transition-all duration-300"
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
              >
                Get Started
              </motion.button>
            </Link>
          </motion.div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="relative pt-32 pb-20 px-6">
        <div className="relative max-w-7xl mx-auto text-center">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
          >
            <div className="inline-flex items-center gap-2 bg-white/5 border border-white/10 rounded-full px-4 py-2 mb-8">
              <span className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
              <span className="text-sm text-gray-400">Now with AI-powered task suggestions</span>
            </div>

            {/* Typing animation for headline */}
            <h1 className="text-5xl md:text-7xl lg:text-8xl font-bold text-white mb-8 leading-tight">
              <TypewriterText text="Manage tasks" delay={0} />
              <br />
              <span className="text-brand-gradient">
                <TypewriterText text="like never before" delay={1000} />
              </span>
            </h1>

            <p className="text-xl md:text-2xl text-gray-400 mb-12 max-w-3xl mx-auto">
              The modern task management app that helps you stay organized,
              focused, and productive. Built for individuals and teams.
            </p>

            <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
              <Link href="/register">
                <motion.button
                  className="group relative px-10 py-5 brand-gradient text-white font-bold rounded-xl overflow-hidden shadow-brand hover:glow-brand"
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                >
                  <div className="absolute inset-0 bg-gradient-to-r from-fuchsia-400 via-blue-600 to-cyan-300 opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
                  <span className="relative flex items-center gap-2 text-lg">
                    Get Started Free
                    <ArrowRight className="w-6 h-6 group-hover:translate-x-1 transition-transform" />
                  </span>
                </motion.button>
              </Link>

              <Link href="/login">
                <motion.button
                  className="px-10 py-5 bg-white/10 border-2 border-white/20 text-white font-bold rounded-xl hover:bg-white/15 hover:border-white/30 transition-all duration-300 shadow-lg text-lg backdrop-blur-sm"
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                >
                  Sign In
                </motion.button>
              </Link>
            </div>
          </motion.div>

          {/* Animated Stats with Counter */}
          <motion.div
            className="mt-24 grid grid-cols-2 md:grid-cols-4 gap-8"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.5 }}
          >
            {[
              { value: 10000, suffix: '+', label: 'Active Users' },
              { value: 1000000, suffix: '+', label: 'Tasks Completed' },
              { value: 99.9, suffix: '%', label: 'Uptime' },
              { value: 4.9, suffix: '/5', label: 'User Rating' },
            ].map((stat, index) => (
              <motion.div
                key={index}
                className="group relative text-center p-6 rounded-2xl bg-gradient-to-br from-white/10 via-blue-900/10 to-fuchsia-900/10 border border-white/10 hover:border-fuchsia-500/50 transition-all duration-500 backdrop-blur-xl overflow-hidden"
                initial={{ opacity: 0, scale: 0.5 }}
                whileInView={{ opacity: 1, scale: 1 }}
                viewport={{ once: true }}
                transition={{ delay: index * 0.1 }}
                whileHover={{ y: -8, scale: 1.05 }}
              >
                {/* Animated gradient border */}
                <div className="absolute inset-0 rounded-2xl bg-gradient-to-r from-fuchsia-500/20 via-blue-700/20 to-cyan-400/20 opacity-0 group-hover:opacity-100 transition-opacity duration-500" />

                {/* Inner glow */}
                <div className="absolute -inset-1 bg-gradient-to-br from-fuchsia-500/10 via-transparent to-cyan-400/10 rounded-2xl blur-xl opacity-0 group-hover:opacity-100 transition-opacity duration-500" />

                <div className="relative z-10">
                  <div className="text-3xl md:text-5xl font-bold text-brand-gradient mb-3">
                    <CountUp end={stat.value} suffix={stat.suffix} />
                  </div>
                  <div className="text-gray-400 font-medium group-hover:text-white transition-colors">{stat.label}</div>
                </div>
              </motion.div>
            ))}
          </motion.div>
        </div>
      </section>

      {/* How It Works Section */}
      <section className="py-20 px-6">
        <div className="max-w-7xl mx-auto">
          <motion.div
            className="text-center mb-16"
            initial={{ opacity: 0 }}
            whileInView={{ opacity: 1 }}
            viewport={{ once: true }}
          >
            <h2 className="text-4xl md:text-5xl font-bold text-white mb-4">
              How it works
            </h2>
            <p className="text-xl text-gray-400">
              Get started in three simple steps
            </p>
          </motion.div>

          <div className="grid md:grid-cols-3 gap-8">
            {howItWorks.map((item, index) => (
              <motion.div
                key={index}
                className="relative"
                initial={{ opacity: 0, y: 30 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: index * 0.2 }}
              >
                {/* Connecting line */}
                {index < howItWorks.length - 1 && (
                  <div className="hidden md:block absolute top-20 left-[60%] w-full h-0.5 bg-gradient-to-r from-cyan-500/50 to-transparent z-0" />
                )}

                <div className="relative group bg-gradient-to-br from-white/10 via-blue-900/10 to-fuchsia-900/10 backdrop-blur-xl border border-white/20 rounded-3xl p-8 hover:border-fuchsia-500/50 transition-all duration-500 shadow-xl hover:shadow-2xl hover:shadow-fuchsia-500/20 overflow-hidden">
                  {/* Animated background gradient */}
                  <div className="absolute inset-0 bg-gradient-to-br from-fuchsia-500/5 via-blue-700/10 to-cyan-400/5 rounded-3xl opacity-0 group-hover:opacity-100 transition-opacity duration-500" />

                  {/* Glowing orb effect */}
                  <div className="absolute -top-20 -right-20 w-40 h-40 bg-fuchsia-500/20 rounded-full blur-3xl opacity-0 group-hover:opacity-100 transition-opacity duration-500" />

                  <div className="relative z-10">
                    <div className="text-7xl font-bold bg-gradient-to-br from-fuchsia-500/40 to-blue-700/40 bg-clip-text text-transparent mb-6">
                      {item.step}
                    </div>

                    <div className="w-20 h-20 brand-gradient rounded-2xl flex items-center justify-center mb-6 shadow-brand-sm group-hover:shadow-brand group-hover:scale-110 transition-all duration-300">
                      <item.icon className="w-10 h-10 text-white" />
                    </div>

                    <h3 className="text-2xl font-bold text-white mb-4 group-hover:text-fuchsia-400 transition-colors">{item.title}</h3>
                    <p className="text-gray-400 leading-relaxed group-hover:text-gray-300 transition-colors">{item.description}</p>
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20 px-6">
        <div className="max-w-7xl mx-auto">
          <motion.div
            className="text-center mb-16"
            initial={{ opacity: 0 }}
            whileInView={{ opacity: 1 }}
            viewport={{ once: true }}
          >
            <h2 className="text-4xl md:text-5xl font-bold text-white mb-4">
              Everything you need
            </h2>
            <p className="text-xl text-gray-400">
              Powerful features to supercharge your productivity
            </p>
          </motion.div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {features.map((feature, index) => (
              <motion.div
                key={index}
                className="group relative p-8 bg-gradient-to-br from-white/10 via-blue-900/5 to-fuchsia-900/10 backdrop-blur-xl border border-white/15 rounded-3xl overflow-hidden hover:border-fuchsia-500/50 transition-all duration-500 shadow-xl hover:shadow-2xl hover:shadow-fuchsia-500/20"
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: index * 0.1 }}
                whileHover={{ y: -10, scale: 1.02 }}
              >
                {/* Animated gradient background */}
                <div className="absolute inset-0 bg-gradient-to-br from-fuchsia-500/10 via-blue-700/10 to-cyan-400/10 opacity-0 group-hover:opacity-100 transition-opacity duration-500" />

                {/* Corner glow effects */}
                <div className="absolute -top-10 -right-10 w-32 h-32 bg-fuchsia-500/20 rounded-full blur-3xl opacity-0 group-hover:opacity-100 transition-opacity duration-500" />
                <div className="absolute -bottom-10 -left-10 w-32 h-32 bg-cyan-400/20 rounded-full blur-3xl opacity-0 group-hover:opacity-100 transition-opacity duration-500" />

                {/* Animated border glow */}
                <div className="absolute inset-0 rounded-3xl opacity-0 group-hover:opacity-100 transition-opacity duration-500">
                  <div className="absolute inset-0 rounded-3xl bg-gradient-to-br from-fuchsia-500/20 via-blue-700/20 to-cyan-400/20 blur-xl" />
                </div>

                <div className="relative z-10">
                  <motion.div
                    className={`w-16 h-16 bg-gradient-to-br ${feature.color} rounded-2xl flex items-center justify-center mb-6 shadow-lg group-hover:shadow-2xl group-hover:shadow-fuchsia-500/40 ring-2 ring-white/10 group-hover:ring-fuchsia-500/30 transition-all duration-300`}
                    whileHover={{ rotate: 360, scale: 1.15 }}
                    transition={{ duration: 0.6, type: "spring", stiffness: 200 }}
                  >
                    <feature.icon className="w-8 h-8 text-white" />
                  </motion.div>
                  <h3 className="text-xl font-bold text-white mb-3 group-hover:text-fuchsia-400 transition-colors">{feature.title}</h3>
                  <p className="text-gray-400 leading-relaxed group-hover:text-gray-200 transition-colors">{feature.description}</p>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Testimonials Carousel */}
      <section className="py-20 px-6">
        <div className="max-w-5xl mx-auto">
          <motion.div
            className="text-center mb-16"
            initial={{ opacity: 0 }}
            whileInView={{ opacity: 1 }}
            viewport={{ once: true }}
          >
            <h2 className="text-4xl md:text-5xl font-bold text-white mb-4">
              Loved by thousands
            </h2>
            <p className="text-xl text-gray-400">
              See what our users have to say
            </p>
          </motion.div>

          <div className="relative">
            <AnimatePresence mode="wait">
              <motion.div
                key={activeTestimonial}
                initial={{ opacity: 0, x: 100 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -100 }}
                transition={{ duration: 0.5 }}
                className="relative group bg-gradient-to-br from-white/10 via-blue-900/10 to-fuchsia-900/10 backdrop-blur-xl border-2 border-white/20 rounded-3xl p-10 md:p-14 shadow-2xl hover:border-fuchsia-500/50 transition-all duration-500 overflow-hidden"
              >
                {/* Animated ambient glow effect */}
                <div className="absolute -inset-2 bg-gradient-to-r from-fuchsia-500/20 via-blue-700/25 to-cyan-400/20 rounded-3xl blur-3xl opacity-40 group-hover:opacity-70 transition-opacity duration-500" />

                {/* Corner decorations */}
                <div className="absolute top-0 right-0 w-40 h-40 bg-gradient-to-br from-fuchsia-500/20 to-transparent rounded-full blur-2xl" />
                <div className="absolute bottom-0 left-0 w-40 h-40 bg-gradient-to-tr from-cyan-400/20 to-transparent rounded-full blur-2xl" />

                <div className="relative z-10">
                  {/* Quote icon with gradient background */}
                  <div className="w-16 h-16 bg-gradient-to-br from-fuchsia-500/20 to-blue-700/20 rounded-2xl flex items-center justify-center mb-8 border border-fuchsia-500/30 shadow-lg shadow-fuchsia-500/20">
                    <Quote className="w-10 h-10 text-fuchsia-400" />
                  </div>

                  {/* Star rating with glow */}
                  <div className="flex gap-1.5 mb-8">
                    {Array.from({ length: testimonials[activeTestimonial].rating }).map((_, i) => (
                      <motion.div
                        key={i}
                        initial={{ opacity: 0, scale: 0 }}
                        animate={{ opacity: 1, scale: 1 }}
                        transition={{ delay: i * 0.1 }}
                      >
                        <Star className="w-6 h-6 fill-yellow-400 text-yellow-400 drop-shadow-lg" />
                      </motion.div>
                    ))}
                  </div>

                  <p className="text-xl md:text-2xl text-gray-200 mb-10 leading-relaxed font-light">
                    "{testimonials[activeTestimonial].content}"
                  </p>

                  <div className="flex items-center gap-5">
                    <div className="w-16 h-16 brand-gradient rounded-full flex items-center justify-center text-white font-bold text-xl shadow-brand-sm ring-2 ring-white/20">
                      {testimonials[activeTestimonial].avatar}
                    </div>
                    <div>
                      <div className="text-white font-bold text-lg mb-1">
                        {testimonials[activeTestimonial].name}
                      </div>
                      <div className="text-gray-400">
                        {testimonials[activeTestimonial].role} at {testimonials[activeTestimonial].company}
                      </div>
                    </div>
                  </div>
                </div>
              </motion.div>
            </AnimatePresence>

            {/* Enhanced navigation dots */}
            <div className="flex justify-center gap-3 mt-10">
              {testimonials.map((_, index) => (
                <motion.button
                  key={index}
                  onClick={() => setActiveTestimonial(index)}
                  className={`h-3 rounded-full transition-all duration-300 ${
                    index === activeTestimonial
                      ? 'brand-gradient w-12 shadow-lg shadow-fuchsia-500/50'
                      : 'bg-gray-600 w-3 hover:bg-fuchsia-400'
                  }`}
                  whileHover={{ scale: 1.2 }}
                  whileTap={{ scale: 0.9 }}
                />
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* FAQ Section */}
      <section className="py-20 px-6">
        <div className="max-w-3xl mx-auto">
          <motion.div
            className="text-center mb-16"
            initial={{ opacity: 0 }}
            whileInView={{ opacity: 1 }}
            viewport={{ once: true }}
          >
            <h2 className="text-4xl md:text-5xl font-bold text-white mb-4">
              Frequently asked questions
            </h2>
            <p className="text-xl text-gray-400">
              Everything you need to know
            </p>
          </motion.div>

          <div className="space-y-4">
            {faqs.map((faq, index) => (
              <motion.div
                key={index}
                className="group bg-gradient-to-br from-white/10 via-blue-900/5 to-fuchsia-900/10 backdrop-blur-xl border border-white/15 rounded-2xl overflow-hidden hover:border-fuchsia-500/50 transition-all duration-500 shadow-lg hover:shadow-xl hover:shadow-fuchsia-500/10"
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: index * 0.1 }}
              >
                <button
                  onClick={() => setOpenFaq(openFaq === index ? null : index)}
                  className="w-full flex items-center justify-between p-6 text-left hover:bg-white/5 transition-colors"
                >
                  <span className="text-lg font-semibold text-white pr-4 group-hover:text-fuchsia-400 transition-colors">{faq.question}</span>
                  <motion.div
                    animate={{ rotate: openFaq === index ? 180 : 0 }}
                    transition={{ duration: 0.3, type: "spring", stiffness: 200 }}
                    className="flex-shrink-0"
                  >
                    <div className={`w-10 h-10 rounded-xl flex items-center justify-center transition-all duration-300 ${
                      openFaq === index
                        ? 'bg-gradient-to-br from-fuchsia-500/30 to-blue-700/30 border border-fuchsia-500/50 shadow-lg shadow-fuchsia-500/20'
                        : 'bg-white/5 border border-white/10 group-hover:border-fuchsia-500/30 group-hover:bg-fuchsia-500/10'
                    }`}>
                      <ChevronDown className={`w-5 h-5 transition-colors ${
                        openFaq === index ? 'text-fuchsia-400' : 'text-gray-400 group-hover:text-fuchsia-400'
                      }`} />
                    </div>
                  </motion.div>
                </button>

                <AnimatePresence>
                  {openFaq === index && (
                    <motion.div
                      initial={{ height: 0, opacity: 0 }}
                      animate={{ height: 'auto', opacity: 1 }}
                      exit={{ height: 0, opacity: 0 }}
                      transition={{ duration: 0.3, ease: "easeInOut" }}
                      className="overflow-hidden"
                    >
                      <div className="px-6 pb-6 text-gray-300 leading-relaxed border-t border-fuchsia-500/20 pt-4 mx-6 bg-gradient-to-b from-fuchsia-500/5 to-transparent">
                        {faq.answer}
                      </div>
                    </motion.div>
                  )}
                </AnimatePresence>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Newsletter Section */}
      <section className="py-20 px-6">
        <motion.div
          className="relative max-w-4xl mx-auto text-center bg-gradient-to-br from-fuchsia-500/15 via-blue-800/15 to-cyan-400/20 backdrop-blur-xl border-2 border-fuchsia-500/40 rounded-3xl p-12 md:p-16 shadow-2xl overflow-hidden"
          initial={{ opacity: 0, scale: 0.95 }}
          whileInView={{ opacity: 1, scale: 1 }}
          viewport={{ once: true }}
        >
          {/* Animated ambient glow */}
          <div className="absolute -inset-2 bg-gradient-to-r from-fuchsia-500/25 via-blue-700/30 to-cyan-400/25 rounded-3xl blur-3xl opacity-60" />

          {/* Decorative corners */}
          <div className="absolute top-0 left-0 w-32 h-32 bg-gradient-to-br from-fuchsia-500/30 to-transparent rounded-full blur-2xl" />
          <div className="absolute bottom-0 right-0 w-32 h-32 bg-gradient-to-tl from-cyan-400/30 to-transparent rounded-full blur-2xl" />

          <div className="relative z-10">
            <div className="w-20 h-20 brand-gradient rounded-2xl flex items-center justify-center mx-auto mb-8 shadow-brand ring-2 ring-white/20">
              <Mail className="w-10 h-10 text-white" />
            </div>

            <h2 className="text-3xl md:text-4xl font-bold text-white mb-4">
              Stay in the loop
            </h2>
            <p className="text-xl text-gray-300 mb-10 max-w-2xl mx-auto leading-relaxed">
              Get updates on new features, tips, and productivity insights.
            </p>

            <form onSubmit={handleNewsletterSubmit} className="max-w-md mx-auto">
              <div className="flex flex-col sm:flex-row gap-3">
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="Enter your email"
                  required
                  className="flex-1 px-5 py-4 bg-white/10 border-2 border-white/20 rounded-xl text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-cyan-500 focus:border-cyan-500/50 transition-all duration-300 backdrop-blur-sm"
                />
                <motion.button
                  type="submit"
                  className="px-8 py-4 bg-gradient-to-r from-cyan-500 to-blue-600 text-white font-bold rounded-xl shadow-lg shadow-cyan-500/40 hover:shadow-xl hover:shadow-cyan-500/60 transition-all duration-300"
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                >
                  Subscribe
                </motion.button>
              </div>

              <AnimatePresence>
                {isSubmitted && (
                  <motion.div
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -10 }}
                    className="mt-6 px-6 py-3 bg-green-500/20 border border-green-500/40 rounded-xl text-green-400 flex items-center justify-center gap-2 font-semibold"
                  >
                    <div className="w-6 h-6 rounded-full bg-green-500/30 flex items-center justify-center">
                      <Check className="w-4 h-4" />
                    </div>
                    Thanks for subscribing!
                  </motion.div>
                )}
              </AnimatePresence>
            </form>
          </div>
        </motion.div>
      </section>

      {/* Final CTA Section */}
      <section className="py-20 px-6">
        <motion.div
          className="max-w-4xl mx-auto text-center"
          initial={{ opacity: 0, scale: 0.95 }}
          whileInView={{ opacity: 1, scale: 1 }}
          viewport={{ once: true }}
        >
          <h2 className="text-4xl md:text-6xl font-bold text-white mb-6 leading-tight">
            Ready to get started?
          </h2>
          <p className="text-xl md:text-2xl text-gray-300 mb-10 max-w-2xl mx-auto leading-relaxed">
            Join thousands of users and start managing your tasks today.
          </p>
          <Link href="/register">
            <motion.button
              className="group relative px-12 py-5 brand-gradient text-white font-bold rounded-xl text-lg overflow-hidden shadow-brand hover:glow-brand transition-all duration-300 ring-2 ring-white/10 hover:ring-fuchsia-500/30"
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              <div className="absolute inset-0 bg-gradient-to-r from-fuchsia-400 via-blue-600 to-cyan-300 opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
              <span className="relative flex items-center gap-3">
                Create Free Account
                <ArrowRight className="w-6 h-6 group-hover:translate-x-1 transition-transform" />
              </span>
            </motion.button>
          </Link>
        </motion.div>
      </section>

      {/* Footer */}
      <footer className="py-8 px-6 border-t border-white/5">
        <div className="max-w-7xl mx-auto flex flex-col md:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 brand-gradient rounded-lg flex items-center justify-center shadow-brand-sm">
              <Sparkles className="w-4 h-4 text-white" />
            </div>
            <span className="text-white font-semibold">TaskFlow</span>
          </div>
          <p className="text-gray-500 text-sm">
            © 2024 TaskFlow. All rights reserved.
          </p>
        </div>
      </footer>
    </div>
  )
}

// Typewriter effect component
function TypewriterText({ text, delay = 0 }: { text: string; delay?: number }) {
  const [displayText, setDisplayText] = useState('')
  const [currentIndex, setCurrentIndex] = useState(0)
  const [hasStarted, setHasStarted] = useState(false)

  useEffect(() => {
    const startTimeout = setTimeout(() => setHasStarted(true), delay)
    return () => clearTimeout(startTimeout)
  }, [delay])

  useEffect(() => {
    if (!hasStarted) return

    if (currentIndex < text.length) {
      const timeout = setTimeout(() => {
        setDisplayText(prev => prev + text[currentIndex])
        setCurrentIndex(prev => prev + 1)
      }, 50)
      return () => clearTimeout(timeout)
    }
  }, [currentIndex, text, hasStarted])

  return <span>{displayText}</span>
}

// Counter animation component
function CountUp({ end, suffix = '' }: { end: number; suffix?: string }) {
  const [count, setCount] = useState(0)
  const [hasStarted, setHasStarted] = useState(false)

  useEffect(() => {
    if (!hasStarted) return

    const duration = 2000
    const steps = 60
    const increment = end / steps
    const stepDuration = duration / steps

    let current = 0
    const timer = setInterval(() => {
      current += increment
      if (current >= end) {
        setCount(end)
        clearInterval(timer)
      } else {
        setCount(current)
      }
    }, stepDuration)

    return () => clearInterval(timer)
  }, [end, hasStarted])

  // Start counting when component comes into view
  useEffect(() => {
    const timeout = setTimeout(() => setHasStarted(true), 500)
    return () => clearTimeout(timeout)
  }, [])

  const displayValue = end > 1000
    ? Math.floor(count).toLocaleString()
    : count.toFixed(end % 1 !== 0 ? 1 : 0)

  return <>{displayValue}{suffix}</>
}
