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

      {/* Sentiment Heatmap (if data available) */}
      {heatmapData.length > 0 && (
        <div className="card">
          <h2 className="text-xl font-bold mb-4">Sentiment Heatmap</h2>
          <div className="grid grid-cols-6 md:grid-cols-8 lg:grid-cols-12 gap-2">
            {heatmapData.map((item) => {
              const bgColor = item.sentiment > 0.1
                ? 'bg-bullish'
                : item.sentiment < -0.1
                  ? 'bg-bearish'
                  : 'bg-neutral'
              const opacity = Math.min(Math.abs(item.sentiment) + 0.3, 1)

              return (
                <div
                  key={item.symbol}
                  className={`${bgColor} rounded p-2 text-center cursor-pointer hover:scale-105 transition-transform`}
                  style={{ opacity }}
                  title={`${item.symbol}: ${item.sentiment.toFixed(3)}`}
                >
                  <div className="text-xs font-bold text-white">{item.symbol}</div>
                </div>
              )
            })}
          </div>
        </div>
      )}
    </div>
  )
}
