/**
 * SENTIMENT PAGE
 * ==============
 * Detailed sentiment analysis view.
 * Shows heatmap and historical trends.
 */

'use client'

import { useState, useEffect } from 'react'
import { SentimentChart } from '@/components/SentimentChart'
import { SentimentGauge } from '@/components/SentimentGauge'
import { SentimentHeatmap } from '@/components/SentimentHeatmap'
import { SentimentTimeline } from '@/components/SentimentTimeline'

interface Coin {
  symbol: string
  name: string
  sentiment: number | null
  hype_score: number | null
}

interface HeatmapData {
  symbol: string
  sentiment: number
}

export default function SentimentPage() {
  const [coins, setCoins] = useState<Coin[]>([])
  const [heatmapData, setHeatmapData] = useState<HeatmapData[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

  useEffect(() => {
    async function fetchData() {
      try {
        const [coinsRes, heatmapRes] = await Promise.all([
          fetch(`${API_URL}/api/coins`),
          fetch(`${API_URL}/api/sentiment/heatmap`)
        ])

        if (!coinsRes.ok) throw new Error('Failed to fetch coins')

        const coinsData = await coinsRes.json()
        setCoins(coinsData.coins || [])

        if (heatmapRes.ok) {
          const heatmapJson = await heatmapRes.json()
          setHeatmapData(heatmapJson.data || [])
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Unknown error')
      } finally {
        setLoading(false)
      }
    }

    fetchData()
    const interval = setInterval(fetchData, 60000)
    return () => clearInterval(interval)
  }, [API_URL])

  // Calculate average sentiment
  const avgSentiment = coins.reduce((sum, coin) => {
    return sum + (coin.sentiment || 0)
  }, 0) / (coins.filter(c => c.sentiment !== null).length || 1)

  // Categorize coins by sentiment
  const bullishCoins = coins.filter(c => c.sentiment !== null && c.sentiment > 0.1)
  const bearishCoins = coins.filter(c => c.sentiment !== null && c.sentiment < -0.1)
  const neutralCoins = coins.filter(c => c.sentiment !== null && Math.abs(c.sentiment) <= 0.1)

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="text-4xl mb-4 loading">📊</div>
          <p className="text-text-secondary">Loading sentiment data...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="card bg-red-900/20 border-red-500">
        <h2 className="text-xl font-bold text-red-400 mb-2">Error</h2>
        <p className="text-text-secondary">{error}</p>
      </div>
    )
  }

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold mb-2">Sentiment Analysis</h1>
        <p className="text-text-secondary">Real-time social media sentiment tracking</p>
      </div>

      {/* Overview Row */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Main Gauge */}
        <div className="card">
          <h2 className="text-xl font-bold mb-4">Overall Market</h2>
          <SentimentGauge value={avgSentiment} />
        </div>

        {/* Sentiment Breakdown */}
        <div className="lg:col-span-2 card">
          <h2 className="text-xl font-bold mb-4">Sentiment Distribution</h2>
          <div className="grid grid-cols-3 gap-4 text-center">
            <div className="p-4 bg-bullish/10 rounded-lg border border-bullish/30">
              <div className="text-3xl font-bold text-bullish">{bullishCoins.length}</div>
              <div className="text-sm text-text-secondary mt-1">Bullish</div>
              <div className="text-xs text-bullish mt-2">
                {bullishCoins.slice(0, 3).map(c => c.symbol).join(', ')}
                {bullishCoins.length > 3 && '...'}
              </div>
            </div>
            <div className="p-4 bg-neutral/10 rounded-lg border border-neutral/30">
              <div className="text-3xl font-bold text-neutral">{neutralCoins.length}</div>
              <div className="text-sm text-text-secondary mt-1">Neutral</div>
              <div className="text-xs text-neutral mt-2">
                {neutralCoins.slice(0, 3).map(c => c.symbol).join(', ')}
                {neutralCoins.length > 3 && '...'}
              </div>
            </div>
            <div className="p-4 bg-bearish/10 rounded-lg border border-bearish/30">
              <div className="text-3xl font-bold text-bearish">{bearishCoins.length}</div>
              <div className="text-sm text-text-secondary mt-1">Bearish</div>
              <div className="text-xs text-bearish mt-2">
                {bearishCoins.slice(0, 3).map(c => c.symbol).join(', ')}
                {bearishCoins.length > 3 && '...'}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Chart */}
      <div className="card">
        <h2 className="text-xl font-bold mb-4">Sentiment by Coin</h2>
        <SentimentChart coins={coins} />
      </div>

      {/* Sentiment Heatmap */}
      <div className="card">
        <h2 className="text-xl font-bold mb-4">📊 Sentiment Heatmap</h2>
        <p className="text-sm text-text-secondary mb-4">
          Color-coded grid showing sentiment across all coins. Click any coin for detailed analysis.
        </p>
        <SentimentHeatmap />
      </div>

      {/* Sentiment Timeline */}
      <div className="card">
        <h2 className="text-xl font-bold mb-4">📈 Sentiment Over Time</h2>
        <p className="text-sm text-text-secondary mb-4">
          Aggregated sentiment and hype scores across all tracked coins (last 7 days).
        </p>
        <SentimentTimeline hours={168} />
      </div>

      {/* Info Box */}
      <div className="card bg-bg-secondary/50">
        <h3 className="font-bold mb-2">ℹ️ About Sentiment Analysis</h3>
        <div className="text-sm text-text-secondary space-y-2">
          <p>
            Sentiment scores range from -1 (very bearish) to +1 (very bullish), calculated using VADER sentiment analysis on social media posts.
          </p>
          <p>
            <span className="font-semibold text-accent">Hype Score:</span> Measures excitement level based on keywords, emojis, and engagement (0-100 scale).
          </p>
          <p>
            <span className="font-semibold text-accent">Correlation:</span> Statistical relationship between sentiment and price. Strong correlation (>0.7) suggests sentiment may predict price movements.
          </p>
        </div>
      </div>
    </div>
  )
}
