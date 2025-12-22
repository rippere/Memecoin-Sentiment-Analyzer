/**
 * RECENT POSTS COMPONENT
 * ======================
 * Displays latest social media posts from Reddit
 * with sentiment indicators
 */

'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'

interface Post {
  id: number
  coin_id: number
  symbol: string
  coin_name: string
  platform: string
  post_id: string
  title: string | null
  content: string | null
  author: string
  source: string
  engagement: number
  comments: number
  created_at: number | string
  sentiment_score: number | null
  hype_score: number | null
}

interface RecentPostsProps {
  limit?: number
  showCoinFilter?: boolean
}

export function RecentPosts({ limit = 20, showCoinFilter = false }: RecentPostsProps) {
  const [posts, setPosts] = useState<Post[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

  useEffect(() => {
    async function fetchPosts() {
      try {
        setLoading(true)
        const res = await fetch(`${API_URL}/api/posts/recent?limit=${limit}`)

        if (!res.ok) {
          throw new Error('Failed to fetch posts')
        }

        const data = await res.json()
        setPosts(data.posts || [])
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Unknown error')
      } finally {
        setLoading(false)
      }
    }

    fetchPosts()

    // Refresh every 2 minutes
    const interval = setInterval(fetchPosts, 120000)
    return () => clearInterval(interval)
  }, [API_URL, limit])

  // Format timestamp
  const formatTime = (timestamp: number | string) => {
    const date = typeof timestamp === 'number'
      ? new Date(timestamp * 1000)  // Unix timestamp
      : new Date(timestamp)

    const now = new Date()
    const diff = now.getTime() - date.getTime()
    const minutes = Math.floor(diff / (1000 * 60))
    const hours = Math.floor(minutes / 60)
    const days = Math.floor(hours / 24)

    if (days > 0) return `${days}d ago`
    if (hours > 0) return `${hours}h ago`
    if (minutes > 0) return `${minutes}m ago`
    return 'Just now'
  }

  // Get sentiment color
  const getSentimentColor = (score: number | null) => {
    if (score === null) return 'text-gray-400'
    if (score > 0.3) return 'text-green-400'
    if (score < -0.3) return 'text-red-400'
    return 'text-yellow-400'
  }

  // Get sentiment label
  const getSentimentLabel = (score: number | null) => {
    if (score === null) return 'Unknown'
    if (score > 0.3) return 'Bullish'
    if (score < -0.3) return 'Bearish'
    return 'Neutral'
  }

  if (loading && posts.length === 0) {
    return (
      <div className="flex items-center justify-center h-32">
        <div className="text-center">
          <div className="text-2xl mb-2 loading">💬</div>
          <p className="text-text-secondary text-sm">Loading posts...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="bg-red-900/20 border border-red-500 rounded-lg p-4">
        <p className="text-red-400 text-sm">Error loading posts: {error}</p>
      </div>
    )
  }

  if (posts.length === 0) {
    return (
      <div className="text-center py-8">
        <div className="text-4xl mb-2">📭</div>
        <p className="text-text-secondary">No posts yet</p>
        <p className="text-sm text-text-secondary mt-1">
          Posts will appear once data collection starts
        </p>
      </div>
    )
  }

  return (
    <div className="space-y-3">
      {posts.map((post) => (
        <div
          key={post.id}
          className="bg-bg-secondary border border-gray-800 rounded-lg p-4 hover:border-gray-700 transition-colors"
        >
          {/* Post Header */}
          <div className="flex items-start justify-between mb-2">
            <div className="flex items-center gap-2">
              {/* Platform Badge */}
              <span className="text-xs bg-accent/20 text-accent px-2 py-1 rounded">
                {post.platform}
              </span>

              {/* Coin Link */}
              <Link
                href={`/coins/${post.symbol}`}
                className="text-sm font-bold hover:text-accent transition-colors"
              >
                ${post.symbol}
              </Link>

              {/* Source */}
              <span className="text-xs text-text-secondary">
                r/{post.source}
              </span>
            </div>

            {/* Time */}
            <span className="text-xs text-text-secondary">
              {formatTime(post.created_at)}
            </span>
          </div>

          {/* Post Title */}
          {post.title && (
            <h3 className="font-medium mb-1 line-clamp-2">
              {post.title}
            </h3>
          )}

          {/* Post Content Preview */}
          {post.content && (
            <p className="text-sm text-text-secondary line-clamp-2 mb-2">
              {post.content}
            </p>
          )}

          {/* Post Footer */}
          <div className="flex items-center justify-between text-xs">
            <div className="flex items-center gap-3 text-text-secondary">
              <span>👤 {post.author}</span>
              <span>⬆️ {post.engagement}</span>
              <span>💬 {post.comments}</span>
            </div>

            {/* Sentiment Indicator */}
            {post.sentiment_score !== null && (
              <div className={`font-medium ${getSentimentColor(post.sentiment_score)}`}>
                {getSentimentLabel(post.sentiment_score)}
              </div>
            )}
          </div>
        </div>
      ))}

      {/* View All Link */}
      {posts.length >= limit && (
        <div className="text-center pt-2">
          <Link
            href="/posts"
            className="text-sm text-accent hover:underline"
          >
            View all posts →
          </Link>
        </div>
      )}
    </div>
  )
}
