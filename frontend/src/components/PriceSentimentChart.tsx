/**
 * PRICE vs SENTIMENT CHART
 * =========================
 * Dual-axis chart showing price and sentiment correlation
 * Helps visualize if sentiment predicts price movements
 */

'use client'

import { useState, useEffect } from 'react'
import {
  ComposedChart,
  Line,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  ReferenceLine
} from 'recharts'

interface ChartData {
  timestamp: string
  price: number
  sentiment: number
  volume: number
}

interface PriceSentimentChartProps {
  symbol: string
  hours?: number
}

export function PriceSentimentChart({ symbol, hours = 168 }: PriceSentimentChartProps) {
  const [data, setData] = useState<ChartData[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [correlation, setCorrelation] = useState<number | null>(null)

  const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

  useEffect(() => {
    async function fetchData() {
      try {
        setLoading(true)

        // Fetch both price and sentiment data
        const [pricesRes, sentimentRes] = await Promise.all([
          fetch(`${API_URL}/api/coins/${symbol}/prices?hours=${hours}`),
          fetch(`${API_URL}/api/sentiment/timeline?symbol=${symbol}&hours=${hours}`)
        ])

        if (!pricesRes.ok || !sentimentRes.ok) {
          throw new Error('Failed to fetch data')
        }

        const pricesData = await pricesRes.json()
        const sentimentData = await sentimentRes.json()

        // Merge price and sentiment data by timestamp
        const priceMap = new Map(
          (pricesData.prices || []).map((p: any) => [
            new Date(p.timestamp).getTime(),
            { price: p.price_usd, volume: p.volume_24h || 0 }
          ])
        )

        const merged: ChartData[] = (sentimentData.timeline || [])
          .map((s: any) => {
            const time = new Date(s.timestamp).getTime()
            const priceData = priceMap.get(time)

            return {
              timestamp: s.timestamp,
              price: priceData?.price || 0,
              sentiment: s.sentiment_score || 0,
              volume: priceData?.volume || 0
            }
          })
          .filter((d: ChartData) => d.price > 0)
          .reverse() // Oldest first

        setData(merged)

        // Calculate correlation if we have data
        if (merged.length > 5) {
          const corr = calculateCorrelation(
            merged.map(d => d.sentiment),
            merged.map(d => d.price)
          )
          setCorrelation(corr)
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Unknown error')
      } finally {
        setLoading(false)
      }
    }

    fetchData()

    // Refresh every 5 minutes
    const interval = setInterval(fetchData, 300000)
    return () => clearInterval(interval)
  }, [API_URL, symbol, hours])

  // Calculate Pearson correlation coefficient
  const calculateCorrelation = (x: number[], y: number[]): number => {
    const n = Math.min(x.length, y.length)
    if (n < 2) return 0

    const sumX = x.reduce((a, b) => a + b, 0)
    const sumY = y.reduce((a, b) => a + b, 0)
    const sumXY = x.reduce((sum, xi, i) => sum + xi * y[i], 0)
    const sumX2 = x.reduce((sum, xi) => sum + xi * xi, 0)
    const sumY2 = y.reduce((sum, yi) => sum + yi * yi, 0)

    const numerator = n * sumXY - sumX * sumY
    const denominator = Math.sqrt((n * sumX2 - sumX * sumX) * (n * sumY2 - sumY * sumY))

    return denominator === 0 ? 0 : numerator / denominator
  }

  // Get correlation interpretation
  const getCorrelationLabel = (corr: number | null) => {
    if (corr === null) return { label: 'Unknown', color: 'text-gray-400' }
    const abs = Math.abs(corr)
    if (abs > 0.7) return { label: 'Strong', color: corr > 0 ? 'text-green-400' : 'text-red-400' }
    if (abs > 0.4) return { label: 'Moderate', color: corr > 0 ? 'text-green-400' : 'text-red-400' }
    if (abs > 0.2) return { label: 'Weak', color: 'text-yellow-400' }
    return { label: 'Very Weak', color: 'text-gray-400' }
  }

  // Format timestamp
  const formatTime = (timestamp: string) => {
    const date = new Date(timestamp)
    const now = new Date()
    const diffDays = Math.floor((now.getTime() - date.getTime()) / (1000 * 60 * 60 * 24))

    if (diffDays < 1) {
      return date.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' })
    }
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
  }

  // Custom tooltip
  const CustomTooltip = ({ active, payload }: any) => {
    if (!active || !payload || !payload.length) return null

    const data = payload[0].payload
    return (
      <div className="bg-bg-secondary border border-gray-700 rounded-lg p-3 shadow-lg">
        <p className="text-xs text-text-secondary mb-2">
          {new Date(data.timestamp).toLocaleString()}
        </p>
        <div className="space-y-1">
          <p className="text-sm">
            <span className="text-blue-400">Price:</span>{' '}
            <span className="font-bold">${data.price?.toFixed(6)}</span>
          </p>
          <p className="text-sm">
            <span className="text-green-400">Sentiment:</span>{' '}
            <span className="font-bold">{data.sentiment?.toFixed(3)}</span>
          </p>
        </div>
      </div>
    )
  }

  if (loading && data.length === 0) {
    return (
      <div className="h-80 flex items-center justify-center">
        <div className="text-center">
          <div className="text-2xl mb-2 loading">📊</div>
          <p className="text-sm text-text-secondary">Loading correlation data...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="h-80 flex items-center justify-center">
        <p className="text-sm text-red-400">Error: {error}</p>
      </div>
    )
  }

  if (data.length === 0) {
    return (
      <div className="h-80 flex items-center justify-center text-center">
        <div>
          <div className="text-4xl mb-2">📈</div>
          <p className="text-text-secondary">No correlation data yet</p>
          <p className="text-xs text-text-secondary mt-1">
            Need both price and sentiment data
          </p>
        </div>
      </div>
    )
  }

  const corrLabel = getCorrelationLabel(correlation)

  return (
    <div className="space-y-4">
      {/* Correlation Badge */}
      {correlation !== null && (
        <div className="flex items-center justify-between">
          <div>
            <div className="text-sm text-text-secondary">Correlation Coefficient</div>
            <div className={`text-2xl font-bold ${corrLabel.color}`}>
              {correlation.toFixed(3)}
            </div>
          </div>
          <div className="text-right">
            <div className="text-sm text-text-secondary">Strength</div>
            <div className={`text-lg font-semibold ${corrLabel.color}`}>
              {corrLabel.label}
            </div>
          </div>
        </div>
      )}

      {/* Chart */}
      <div className="w-full h-80">
        <ResponsiveContainer width="100%" height="100%">
          <ComposedChart data={data} margin={{ top: 5, right: 30, left: 0, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#333" />
            <XAxis
              dataKey="timestamp"
              tickFormatter={formatTime}
              stroke="#666"
              style={{ fontSize: '12px' }}
            />
            <YAxis
              yAxisId="price"
              stroke="#3b82f6"
              label={{ value: 'Price ($)', angle: -90, position: 'insideLeft', style: { fill: '#3b82f6' } }}
            />
            <YAxis
              yAxisId="sentiment"
              orientation="right"
              domain={[-1, 1]}
              stroke="#10b981"
              label={{ value: 'Sentiment', angle: 90, position: 'insideRight', style: { fill: '#10b981' } }}
            />
            <Tooltip content={<CustomTooltip />} />
            <Legend />

            {/* Sentiment area (background) */}
            <Area
              yAxisId="sentiment"
              type="monotone"
              dataKey="sentiment"
              fill="#10b981"
              fillOpacity={0.2}
              stroke="none"
              name="Sentiment (background)"
            />

            {/* Reference line at 0 for sentiment */}
            <ReferenceLine yAxisId="sentiment" y={0} stroke="#666" strokeDasharray="3 3" />

            {/* Price line */}
            <Line
              yAxisId="price"
              type="monotone"
              dataKey="price"
              stroke="#3b82f6"
              strokeWidth={3}
              dot={false}
              name="Price"
            />

            {/* Sentiment line */}
            <Line
              yAxisId="sentiment"
              type="monotone"
              dataKey="sentiment"
              stroke="#10b981"
              strokeWidth={2}
              dot={false}
              name="Sentiment"
            />
          </ComposedChart>
        </ResponsiveContainer>
      </div>

      {/* Interpretation */}
      <div className="bg-bg-secondary/50 rounded-lg p-3 text-sm">
        <p className="text-text-secondary">
          <span className="font-semibold">Interpretation:</span>{' '}
          {correlation !== null && (
            <>
              {Math.abs(correlation) > 0.4
                ? `There is a ${corrLabel.label.toLowerCase()} ${correlation > 0 ? 'positive' : 'negative'} correlation between sentiment and price. `
                : 'The correlation between sentiment and price is weak. '}
              {correlation > 0
                ? 'Positive sentiment tends to coincide with higher prices.'
                : correlation < -0.2
                ? 'Negative sentiment tends to coincide with higher prices (contrarian indicator).'
                : 'Sentiment and price move somewhat independently.'}
            </>
          )}
        </p>
      </div>
    </div>
  )
}
