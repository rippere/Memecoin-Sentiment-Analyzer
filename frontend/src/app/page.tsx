/**
 * DASHBOARD PAGE
 * ==============
 * This is the main page users see at "/"
 * It shows an overview of all sentiment data.
 */

'use client'  // Required for components that use React hooks

import { useState, useEffect } from 'react'
import { StatsCard } from '@/components/StatsCard'
import { CoinTable } from '@/components/CoinTable'
import { SentimentChart } from '@/components/SentimentChart'
import { SentimentGauge } from '@/components/SentimentGauge'

// Define what our API data looks like
interface Stats {
  total_coins: number
  avg_sentiment_24h: number | null
  avg_hype_24h: number | null
  record_counts: {
    prices: number
    reddit_posts: number
    tiktok_videos: number
  }
}

interface Coin {
  symbol: string
  name: string
  price: number | null
  change_24h: number | null
  sentiment: number | null
  hype_score: number | null
}

export default function Dashboard() {
  // State variables - these hold our data
  const [stats, setStats] = useState<Stats | null>(null)
  const [coins, setCoins] = useState<Coin[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  // API base URL - change this when deploying
  const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

  // Fetch data when component loads
  useEffect(() => {
    async function fetchData() {
      try {
        setLoading(true)

        // Fetch stats and coins in parallel
        const [statsRes, coinsRes] = await Promise.all([
          fetch(`${API_URL}/api/stats`),
          fetch(`${API_URL}/api/coins`)
        ])

        if (!statsRes.ok || !coinsRes.ok) {
          throw new Error('Failed to fetch data')
        }

        const statsData = await statsRes.json()
        const coinsData = await coinsRes.json()

        setStats(statsData)
        setCoins(coinsData.coins || [])
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Unknown error')
      } finally {
        setLoading(false)
      }
    }

    fetchData()

    // Refresh data every 60 seconds
    const interval = setInterval(fetchData, 60000)
    return () => clearInterval(interval)
  }, [API_URL])

  // Show loading state
  if (loading && !stats) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="text-4xl mb-4 loading">🔄</div>
          <p className="text-text-secondary">Loading dashboard...</p>
        </div>
      </div>
    )
  }

  // Show error state
  if (error) {
    return (
      <div className="card bg-red-900/20 border-red-500">
        <h2 className="text-xl font-bold text-red-400 mb-2">Error Loading Data</h2>
        <p className="text-text-secondary mb-4">{error}</p>
        <p className="text-sm text-text-secondary">
          Make sure the API is running: <code className="bg-bg-secondary px-2 py-1 rounded">python api/main.py</code>
        </p>
      </div>
    )
  }

  // Calculate sentiment status
  const avgSentiment = stats?.avg_sentiment_24h || 0
  const sentimentStatus = avgSentiment > 0.1 ? 'Bullish' : avgSentiment < -0.1 ? 'Bearish' : 'Neutral'

  return (
    <div className="space-y-8">
      {/* Page Title */}
      <div>
        <h1 className="text-3xl font-bold mb-2">Sentiment Dashboard</h1>
        <p className="text-text-secondary">Real-time memecoin sentiment analysis</p>
      </div>

      {/* Stats Row - 4 cards showing key metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatsCard
          title="Coins Tracked"
          value={stats?.total_coins || 0}
          icon="📊"
          subtitle="Active tracking"
        />
        <StatsCard
          title="Avg Sentiment"
          value={avgSentiment.toFixed(2)}
          icon={avgSentiment >= 0 ? '📈' : '📉'}
          subtitle={sentimentStatus}
          sentiment={avgSentiment >= 0 ? 'positive' : 'negative'}
        />
        <StatsCard
          title="Hype Index"
          value={`${Math.round(stats?.avg_hype_24h || 0)}/100`}
          icon="🔥"
          subtitle={(stats?.avg_hype_24h || 0) > 50 ? 'Elevated' : 'Normal'}
        />
        <StatsCard
          title="Social Posts"
          value={(stats?.record_counts?.reddit_posts || 0) + (stats?.record_counts?.tiktok_videos || 0)}
          icon="💬"
          subtitle="Last 24h"
        />
      </div>

      {/* Main Content - Chart and Gauge side by side */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Sentiment Chart - Takes 2/3 width */}
        <div className="lg:col-span-2 card">
          <h2 className="text-xl font-bold mb-4">Sentiment Overview</h2>
          <SentimentChart coins={coins} />
        </div>

        {/* Gauge - Takes 1/3 width */}
        <div className="card">
          <h2 className="text-xl font-bold mb-4">Market Sentiment</h2>
          <SentimentGauge value={avgSentiment} />
        </div>
      </div>

      {/* Coin Table */}
      <div className="card">
        <h2 className="text-xl font-bold mb-4">All Coins</h2>
        <CoinTable coins={coins} />
      </div>
    </div>
  )
}
