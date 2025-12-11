/**
 * COIN DETAIL PAGE
 * ================
 * Shows detailed information for a single cryptocurrency.
 * Includes price chart, sentiment analysis, and key metrics.
 */

'use client'

import { useState, useEffect } from 'react'
import { useParams } from 'next/navigation'
import Link from 'next/link'
import { PriceChart } from '@/components/charts/PriceChart'
import { SentimentGauge } from '@/components/SentimentGauge'
import { AnalysisPanel } from '@/components/AnalysisPanel'
import type { TimeRange, PricePoint, Coin } from '@/types'

// Coin metadata for display
const COIN_INFO: Record<string, { name: string; icon: string; color: string }> = {
  DOGE: { name: 'Dogecoin', icon: '🐕', color: '#C3A634' },
  SHIB: { name: 'Shiba Inu', icon: '🐕‍🦺', color: '#FFA409' },
  PEPE: { name: 'Pepe', icon: '🐸', color: '#3D9942' },
  BONK: { name: 'Bonk', icon: '🦴', color: '#F9A825' },
  FLOKI: { name: 'Floki', icon: '⚔️', color: '#D4A84B' },
  WIF: { name: 'Dogwifhat', icon: '🎩', color: '#A855F7' },
}

export default function CoinDetailPage() {
  const params = useParams()
  const symbol = (params.symbol as string)?.toUpperCase()

  const [coin, setCoin] = useState<Coin | null>(null)
  const [priceHistory, setPriceHistory] = useState<PricePoint[]>([])
  const [timeRange, setTimeRange] = useState<TimeRange>('24h')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

  // Fetch coin data
  useEffect(() => {
    async function fetchCoinData() {
      if (!symbol) return

      try {
        setLoading(true)
        setError(null)

        // Fetch coin info and price history in parallel
        const [coinRes, historyRes] = await Promise.all([
          fetch(`${API_URL}/api/coins/${symbol.toLowerCase()}`),
          fetch(`${API_URL}/api/coins/${symbol.toLowerCase()}/history?timeframe=${timeRange}`),
        ])

        if (!coinRes.ok) {
          throw new Error(`Coin ${symbol} not found`)
        }

        const coinData = await coinRes.json()
        setCoin(coinData)

        // Price history might not exist yet
        if (historyRes.ok) {
          const historyData = await historyRes.json()
          setPriceHistory(historyData.prices || [])
        } else {
          // Generate mock data for demo if no history
          setPriceHistory(generateMockPriceHistory(coinData.price || 0.001, timeRange))
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load coin data')
      } finally {
        setLoading(false)
      }
    }

    fetchCoinData()
  }, [symbol, timeRange, API_URL])

  // Generate mock price data for demo purposes
  function generateMockPriceHistory(currentPrice: number, range: TimeRange): PricePoint[] {
    const points: PricePoint[] = []
    const now = Date.now()

    let numPoints: number
    let intervalMs: number

    switch (range) {
      case '1h':
        numPoints = 60
        intervalMs = 60 * 1000 // 1 minute
        break
      case '24h':
        numPoints = 96
        intervalMs = 15 * 60 * 1000 // 15 minutes
        break
      case '7d':
        numPoints = 168
        intervalMs = 60 * 60 * 1000 // 1 hour
        break
      case '30d':
        numPoints = 120
        intervalMs = 6 * 60 * 60 * 1000 // 6 hours
        break
      default:
        numPoints = 180
        intervalMs = 24 * 60 * 60 * 1000 // 1 day
    }

    // Random walk from a starting price
    let price = currentPrice * (0.85 + Math.random() * 0.3) // Start 85-115% of current

    for (let i = numPoints - 1; i >= 0; i--) {
      const timestamp = new Date(now - i * intervalMs).toISOString()
      points.push({ timestamp, price })

      // Random walk: -3% to +3% change
      const change = (Math.random() - 0.5) * 0.06
      price = price * (1 + change)
    }

    // Ensure last point is close to current price
    if (points.length > 0) {
      points[points.length - 1].price = currentPrice
    }

    return points
  }

  // Get coin metadata
  const coinMeta = COIN_INFO[symbol] || {
    name: symbol,
    icon: '🪙',
    color: '#3861FB',
  }

  // Loading state
  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="text-4xl mb-4 loading">{coinMeta.icon}</div>
          <p className="text-text-secondary">Loading {symbol} data...</p>
        </div>
      </div>
    )
  }

  // Error state
  if (error || !coin) {
    return (
      <div className="space-y-4">
        <Link
          href="/coins"
          className="inline-flex items-center gap-2 text-text-secondary hover:text-accent transition-colors"
        >
          ← Back to Coins
        </Link>
        <div className="card bg-red-900/20 border-red-500">
          <h2 className="text-xl font-bold text-red-400 mb-2">Error</h2>
          <p className="text-text-secondary">{error || 'Coin not found'}</p>
        </div>
      </div>
    )
  }

  // Format price
  function formatPrice(price: number | null): string {
    if (!price) return 'N/A'
    if (price < 0.0001) return `$${price.toExponential(2)}`
    if (price < 1) return `$${price.toFixed(6)}`
    if (price < 100) return `$${price.toFixed(4)}`
    return `$${price.toLocaleString('en-US', { maximumFractionDigits: 2 })}`
  }

  // Format percentage
  function formatPercent(value: number | null): string {
    if (value === null) return 'N/A'
    const prefix = value >= 0 ? '+' : ''
    return `${prefix}${value.toFixed(2)}%`
  }

  return (
    <div className="space-y-6">
      {/* Back link */}
      <Link
        href="/coins"
        className="inline-flex items-center gap-2 text-text-secondary hover:text-accent transition-colors"
      >
        ← Back to Coins
      </Link>

      {/* Header */}
      <div className="flex items-center gap-4">
        <span className="text-5xl">{coinMeta.icon}</span>
        <div>
          <h1 className="text-3xl font-bold">{coinMeta.name}</h1>
          <p className="text-text-secondary text-lg">{symbol}</p>
        </div>
      </div>

      {/* Key Metrics Row */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {/* Current Price */}
        <div className="card">
          <p className="text-text-secondary text-sm mb-1">Price</p>
          <p className="text-2xl font-bold">{formatPrice(coin.price)}</p>
        </div>

        {/* 24h Change */}
        <div className="card">
          <p className="text-text-secondary text-sm mb-1">24h Change</p>
          <p
            className={`text-2xl font-bold ${
              (coin.change_24h || 0) >= 0 ? 'text-bullish' : 'text-bearish'
            }`}
          >
            {formatPercent(coin.change_24h)}
          </p>
        </div>

        {/* Sentiment */}
        <div className="card">
          <p className="text-text-secondary text-sm mb-1">Sentiment</p>
          <p
            className={`text-2xl font-bold ${
              (coin.sentiment || 0) >= 0 ? 'text-bullish' : 'text-bearish'
            }`}
          >
            {coin.sentiment !== null
              ? `${((coin.sentiment + 1) * 50).toFixed(0)}%`
              : 'N/A'}
          </p>
        </div>

        {/* Hype Score */}
        <div className="card">
          <p className="text-text-secondary text-sm mb-1">Hype Score</p>
          <p className="text-2xl font-bold text-accent">
            {coin.hype_score !== null ? `${Math.round(coin.hype_score)}/100` : 'N/A'}
          </p>
        </div>
      </div>

      {/* Main Content - Chart and Sentiment */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Price Chart - 2/3 width */}
        <div className="lg:col-span-2 card">
          <h2 className="text-xl font-bold mb-4">Price History</h2>
          <PriceChart
            prices={priceHistory}
            timeRange={timeRange}
            onTimeRangeChange={setTimeRange}
            height={350}
          />
        </div>

        {/* Sentiment Gauge - 1/3 width */}
        <div className="card">
          <h2 className="text-xl font-bold mb-4">Market Sentiment</h2>
          <SentimentGauge value={coin.sentiment || 0} />
          <div className="mt-4 space-y-2 text-sm">
            <div className="flex justify-between">
              <span className="text-text-secondary">Sentiment Score</span>
              <span
                className={
                  (coin.sentiment || 0) >= 0 ? 'text-bullish' : 'text-bearish'
                }
              >
                {coin.sentiment?.toFixed(3) || 'N/A'}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-text-secondary">Hype Level</span>
              <span className="text-accent">
                {coin.hype_score !== null
                  ? coin.hype_score > 70
                    ? 'High 🔥'
                    : coin.hype_score > 40
                    ? 'Medium'
                    : 'Low'
                  : 'N/A'}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-text-secondary">Status</span>
              <span>
                {(coin.sentiment || 0) > 0.1
                  ? '📈 Bullish'
                  : (coin.sentiment || 0) < -0.1
                  ? '📉 Bearish'
                  : '➡️ Neutral'}
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* AI Analysis Panel */}
      <AnalysisPanel symbol={symbol} />
    </div>
  )
}
