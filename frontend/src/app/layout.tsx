import type { Metadata } from 'next'
import Script from 'next/script'
import { ToastProvider } from '@/components/toast'
import './globals.css'

export const metadata: Metadata = {
  title: 'TaskFlow - Modern Task Management',
  description: 'A beautiful, interactive task management application with priority levels, drag-and-drop, and real-time updates',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" className="dark">
      <body className="antialiased">
        {/* ChatKit CDN script for widget styling */}
        <Script
          src="https://cdn.platform.openai.com/deployments/chatkit/chatkit.js"
          strategy="afterInteractive"
        />
        <ToastProvider>{children}</ToastProvider>
      </body>
    </html>
  )
}
