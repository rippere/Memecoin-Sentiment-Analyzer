/**
 * ROOT LAYOUT
 * ===========
 * This file wraps ALL pages in your app.
 * It's where you put things that appear on every page (like navigation).
 */

import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'

// Load the Inter font (clean, modern look)
const inter = Inter({ subsets: ['latin'] })

// Page metadata (shows in browser tab)
export const metadata: Metadata = {
  title: 'Memecoin Sentiment Dashboard',
  description: 'Real-time cryptocurrency sentiment analysis',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className={`${inter.className} bg-bg-primary text-text-primary min-h-screen`}>
        {/* Navigation Header */}
        <nav className="bg-bg-secondary border-b border-gray-800 px-6 py-4">
          <div className="max-w-7xl mx-auto flex items-center justify-between">
            {/* Logo */}
            <div className="flex items-center gap-2">
              <span className="text-2xl">🪙</span>
              <span className="text-xl font-bold">MemeTracker</span>
            </div>

            {/* Navigation Links */}
            <div className="flex gap-6">
              <a href="/" className="hover:text-accent transition-colors">Dashboard</a>
              <a href="/coins" className="hover:text-accent transition-colors">Coins</a>
              <a href="/sentiment" className="hover:text-accent transition-colors">Sentiment</a>
              <a href="/events" className="hover:text-accent transition-colors">Events</a>
            </div>
          </div>
        </nav>

        {/* Main Content Area */}
        <main className="max-w-7xl mx-auto px-6 py-8">
          {children}
        </main>
      </body>
    </html>
  )
}
