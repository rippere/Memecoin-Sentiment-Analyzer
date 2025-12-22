/**
 * SENTIMENT HEATMAP COMPONENT
 * ============================
 * Visual heatmap showing sentiment across multiple coins
 * Color-coded grid for quick sentiment overview
 */

'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'

interface HeatmapCoin {
  symbol: string
  name: string
  sentiment_score: number
  hype_score: number
  post_count: number
  price_change_24h: number | null
}

export function SentimentHeatmap() {
  const [coins, setCoins] = useState<HeatmapCoin[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

  useEffect(() => {
    async function fetchHeatmap() {
      try {
        setLoading(true)
        const res = await fetch(`${API_URL}/api/sentiment/heatmap`)

        if (!res.ok) {
          // If heatmap endpoint doesn't exist, fall back to coins endpoint
          const coinsRes = await fetch(`${API_URL}/api/coins`)
          if (!coinsRes.ok) throw new Error('Failed to fetch data')

          const coinsData = await coinsRes.json()
          const heatmapData = (coinsData.coins || [])
            .filter((c: any) => c.sentiment !== null)
            .map((c: any) => ({
              symbol: c.symbol,
              name: c.name,
              sentiment_score: c.sentiment || 0,
              hype_score: c.hype_score || 0,
              post_count: 0,
              price_change_24h: c.change_24h
            }))
          setCoins(heatmapData)
        } else {
          const data = await res.json()
          setCoins(data.coins || [])
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Unknown error')
      } finally {
        setLoading(false)
      }
    }

    fetchHeatmap()

    // Refresh every 2 minutes
    const interval = setInterval(fetchHeatmap, 120000)
    return () => clearInterval(interval)
  }, [API_URL])

  // Get color based on sentiment score
  const getSentimentColor = (score: number) => {
    // Score ranges from -1 to 1
    if (score > 0.5) return 'bg-green-500/80 hover:bg-green-500'
    if (score > 0.2) return 'bg-green-600/60 hover:bg-green-600/80'
    if (score > 0) return 'bg-green-700/40 hover:bg-green-700/60'
    if (score > -0.2) return 'bg-gray-700/40 hover:bg-gray-700/60'
    if (score > -0.5) return 'bg-red-700/40 hover:bg-red-700/60'
    return 'bg-red-500/80 hover:bg-red-500'
  }

  // Get sentiment label
  const getSentimentLabel = (score: number) => {
    if (score > 0.3) return 'Very Bullish'
    if (score > 0.1) return 'Bullish'
    if (score > -0.1) return 'Neutral'
    if (score > -0.3) return 'Bearish'
    return 'Very Bearish'
  }

  // Get size based on hype score
  const getHypeSize = (hype: number) => {
    // Hype ranges from 0 to 100
    if (hype > 75) return 'font-bold text-lg'
    if (hype > 50) return 'font-semibold'
    if (hype > 25) return 'font-medium text-sm'
    return 'text-sm'
  }

  if (loading && coins.length === 0) {
    return (
      <div className="h-64 flex items-center justify-center">
        <div className="text-center">
          <div className="text-2xl mb-2 loading">🗺️</div>
          <p className="text-sm text-text-secondary">Loading heatmap...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="h-64 flex items-center justify-center">
        <p className="text-sm text-red-400">Error: {error}</p>
      </div>
    )
  }

  if (coins.length === 0) {
    return (
      <div className="h-64 flex items-center justify-center text-center">
        <div>
          <div className="text-4xl mb-2">🗺️</div>
          <p className="text-text-secondary">No sentiment data yet</p>
          <p className="text-xs text-text-secondary mt-1">
            Heatmap will appear once sentiment is analyzed
          </p>
        </div>
      </div>
    )
  }

  // Sort by absolute sentiment (most extreme first)
  const sortedCoins = [...coins].sort((a, b) =>
    Math.abs(b.sentiment_score) - Math.abs(a.sentiment_score)
  )

  return (
    <div className="space-y-4">
      {/* Legend */}
      <div className="flex items-center justify-between text-xs">
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 bg-red-500/80 rounded"></div>
          <span className="text-text-secondary">Very Bearish</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 bg-gray-700/40 rounded"></div>
          <span className="text-text-secondary">Neutral</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 bg-green-500/80 rounded"></div>
          <span className="text-text-secondary">Very Bullish</span>
        </div>
      </div>

      {/* Heatmap Grid */}
      <div className="grid grid-cols-4 sm:grid-cols-6 md:grid-cols-8 gap-2">
        {sortedCoins.map((coin) => (
          <Link
            key={coin.symbol}
            href={`/coins/${coin.symbol}`}
            className={`
              ${getSentimentColor(coin.sentiment_score)}
              ${getHypeSize(coin.hype_score)}
              rounded-lg p-3 text-center transition-all
              border border-transparent hover:border-accent
              cursor-pointer group
            `}
            title={`${coin.name}\nSentiment: ${coin.sentiment_score.toFixed(2)}\nHype: ${coin.hype_score.toFixed(0)}\n${getSentimentLabel(coin.sentiment_score)}`}
          >
            <div className="text-white font-bold mb-1">{coin.symbol}</div>
            <div className="text-xs opacity-90">{coin.sentiment_score.toFixed(2)}</div>
            {coin.price_change_24h !== null && (
              <div className={`text-xs mt-1 ${coin.price_change_24h >= 0 ? 'text-green-300' : 'text-red-300'}`}>
                {coin.price_change_24h >= 0 ? '+' : ''}{coin.price_change_24h.toFixed(1)}%
              </div>
            )}
          </Link>
        ))}
      </div>

      {/* Stats Summary */}
      <div className="grid grid-cols-3 gap-4 pt-2 border-t border-gray-800">
        <div className="text-center">
          <div className="text-sm text-text-secondary">Bullish</div>
          <div className="text-lg font-bold text-green-400">
            {coins.filter(c => c.sentiment_score > 0.1).length}
          </div>
        </div>
        <div className="text-center">
          <div className="text-sm text-text-secondary">Neutral</div>
          <div className="text-lg font-bold text-gray-400">
            {coins.filter(c => c.sentiment_score >= -0.1 && c.sentiment_score <= 0.1).length}
          </div>
        </div>
        <div className="text-center">
          <div className="text-sm text-text-secondary">Bearish</div>
          <div className="text-lg font-bold text-red-400">
            {coins.filter(c => c.sentiment_score < -0.1).length}
          </div>
        </div>
      </div>
    </div>
  )
}
