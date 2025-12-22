/**
 * TRENDING COINS PAGE
 * ===================
 * Shows currently trending cryptocurrencies
 * with real-time ranking and sentiment data
 */

'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'

interface TrendingCoin {
  id: number
  symbol: string
  name: string
  coingecko_id: string
  is_trending: boolean
  trending_rank: number
  trending_since: string
  price_usd: number | null
  price_change_24h: number | null
  market_cap: number | null
  volume_24h: number | null
}

export default function TrendingPage() {
  const [coins, setCoins] = useState<TrendingCoin[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [lastUpdate, setLastUpdate] = useState<string>('')

  const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

  useEffect(() => {
    async function fetchTrending() {
      try {
        setLoading(true)
        const res = await fetch(`${API_URL}/api/trending`)

        if (!res.ok) {
          throw new Error('Failed to fetch trending coins')
        }

        const data = await res.json()
        setCoins(data.trending_coins || [])
        setLastUpdate(data.last_update)
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Unknown error')
      } finally {
        setLoading(false)
      }
    }

    fetchTrending()

    // Refresh every 5 minutes
    const interval = setInterval(fetchTrending, 300000)
    return () => clearInterval(interval)
  }, [API_URL])

  // Format market cap
  const formatMarketCap = (value: number | null) => {
    if (!value) return 'N/A'
    if (value >= 1e9) return `$${(value / 1e9).toFixed(2)}B`
    if (value >= 1e6) return `$${(value / 1e6).toFixed(2)}M`
    if (value >= 1e3) return `$${(value / 1e3).toFixed(2)}K`
    return `$${value.toFixed(2)}`
  }

  // Format time since trending
  const timeSinceTrending = (timestamp: string) => {
    if (!timestamp) return 'Unknown'
    const date = new Date(timestamp)
    const now = new Date()
    const diff = now.getTime() - date.getTime()
    const hours = Math.floor(diff / (1000 * 60 * 60))
    const days = Math.floor(hours / 24)

    if (days > 0) return `${days}d ago`
    if (hours > 0) return `${hours}h ago`
    return 'Just now'
  }

  if (loading && coins.length === 0) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="text-4xl mb-4 loading">🔥</div>
          <p className="text-text-secondary">Loading trending coins...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="card bg-red-900/20 border-red-500">
        <h2 className="text-xl font-bold text-red-400 mb-2">Error Loading Trending Data</h2>
        <p className="text-text-secondary">{error}</p>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold mb-2">🔥 Trending Coins</h1>
          <p className="text-text-secondary">
            {coins.length} coins currently trending on CoinGecko
          </p>
        </div>
        {lastUpdate && (
          <div className="text-sm text-text-secondary">
            Last updated: {new Date(lastUpdate).toLocaleTimeString()}
          </div>
        )}
      </div>

      {/* Trending Coins Grid */}
      {coins.length === 0 ? (
        <div className="card text-center py-12">
          <div className="text-6xl mb-4">📊</div>
          <h2 className="text-xl font-bold mb-2">No Trending Coins</h2>
          <p className="text-text-secondary">
            Trending data will appear here once collection starts.
          </p>
          <p className="text-sm text-text-secondary mt-2">
            Run: <code className="bg-bg-secondary px-2 py-1 rounded">python update_trending.py</code>
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {coins.map((coin) => (
            <Link
              key={coin.id}
              href={`/coins/${coin.symbol}`}
              className="card hover:border-accent transition-colors cursor-pointer group"
            >
              {/* Rank Badge */}
              <div className="flex items-start justify-between mb-3">
                <div className="flex items-center gap-3">
                  <div className="bg-accent/20 text-accent px-3 py-1 rounded-full font-bold text-sm">
                    #{coin.trending_rank}
                  </div>
                  <div>
                    <div className="font-bold text-lg group-hover:text-accent transition-colors">
                      {coin.symbol}
                    </div>
                    <div className="text-sm text-text-secondary">{coin.name}</div>
                  </div>
                </div>
              </div>

              {/* Price Info */}
              <div className="grid grid-cols-2 gap-4 mb-3">
                <div>
                  <div className="text-xs text-text-secondary mb-1">Price</div>
                  <div className="font-bold">
                    {coin.price_usd ? `$${coin.price_usd.toFixed(8)}` : 'N/A'}
                  </div>
                </div>
                <div>
                  <div className="text-xs text-text-secondary mb-1">24h Change</div>
                  <div className={`font-bold ${
                    (coin.price_change_24h || 0) >= 0 ? 'text-green-400' : 'text-red-400'
                  }`}>
                    {coin.price_change_24h
                      ? `${coin.price_change_24h >= 0 ? '+' : ''}${coin.price_change_24h.toFixed(2)}%`
                      : 'N/A'
                    }
                  </div>
                </div>
              </div>

              {/* Market Stats */}
              <div className="grid grid-cols-2 gap-4 mb-3 pb-3 border-b border-gray-800">
                <div>
                  <div className="text-xs text-text-secondary mb-1">Market Cap</div>
                  <div className="text-sm">{formatMarketCap(coin.market_cap)}</div>
                </div>
                <div>
                  <div className="text-xs text-text-secondary mb-1">Volume 24h</div>
                  <div className="text-sm">{formatMarketCap(coin.volume_24h)}</div>
                </div>
              </div>

              {/* Trending Info */}
              <div className="flex items-center justify-between text-xs">
                <span className="text-text-secondary">
                  Trending since: {timeSinceTrending(coin.trending_since)}
                </span>
                <span className="text-accent group-hover:underline">View Details →</span>
              </div>
            </Link>
          ))}
        </div>
      )}

      {/* Info Card */}
      <div className="card bg-bg-secondary/50">
        <h3 className="font-bold mb-2">ℹ️ About Trending Coins</h3>
        <p className="text-sm text-text-secondary mb-2">
          Trending coins are automatically tracked from CoinGecko's trending API. The system updates every 3 hours via GitHub Actions.
        </p>
        <p className="text-sm text-text-secondary">
          Coins are ranked by trending score and social media activity. Reddit posts and sentiment data are collected for each trending coin.
        </p>
      </div>
    </div>
  )
}
