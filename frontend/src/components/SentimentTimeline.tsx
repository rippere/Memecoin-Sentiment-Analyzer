/**
 * SENTIMENT TIMELINE COMPONENT
 * ============================
 * Shows sentiment and price over time
 * Dual-axis chart with sentiment and price correlation
 */

'use client'

import { useState, useEffect } from 'react'
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  ReferenceLine
} from 'recharts'

interface TimelineData {
  timestamp: string
  sentiment_score: number
  hype_score: number
  post_count: number
  price_usd: number | null
}

interface SentimentTimelineProps {
  symbol?: string
  hours?: number
}

export function SentimentTimeline({ symbol, hours = 168 }: SentimentTimelineProps) {
  const [data, setData] = useState<TimelineData[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

  useEffect(() => {
    async function fetchTimeline() {
      try {
        setLoading(true)
        const params = new URLSearchParams({
          hours: hours.toString()
        })
        if (symbol) {
          params.append('symbol', symbol)
        }

        const res = await fetch(`${API_URL}/api/sentiment/timeline?${params}`)

        if (!res.ok) {
          throw new Error('Failed to fetch timeline')
        }

        const result = await res.json()
        setData(result.timeline || [])
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Unknown error')
      } finally {
        setLoading(false)
      }
    }

    fetchTimeline()

    // Refresh every 5 minutes
    const interval = setInterval(fetchTimeline, 300000)
    return () => clearInterval(interval)
  }, [API_URL, symbol, hours])

  // Format timestamp for display
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
            <span className="text-green-400">Sentiment:</span>{' '}
            <span className="font-bold">{data.sentiment_score?.toFixed(3)}</span>
          </p>
          <p className="text-sm">
            <span className="text-orange-400">Hype:</span>{' '}
            <span className="font-bold">{data.hype_score?.toFixed(1)}</span>
          </p>
          {data.price_usd && (
            <p className="text-sm">
              <span className="text-blue-400">Price:</span>{' '}
              <span className="font-bold">${data.price_usd?.toFixed(6)}</span>
            </p>
          )}
          <p className="text-xs text-text-secondary">
            {data.post_count} posts
          </p>
        </div>
      </div>
    )
  }

  if (loading && data.length === 0) {
    return (
      <div className="h-64 flex items-center justify-center">
        <div className="text-center">
          <div className="text-2xl mb-2 loading">📊</div>
          <p className="text-sm text-text-secondary">Loading timeline...</p>
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

  if (data.length === 0) {
    return (
      <div className="h-64 flex items-center justify-center text-center">
        <div>
          <div className="text-4xl mb-2">📈</div>
          <p className="text-text-secondary">No timeline data yet</p>
          <p className="text-xs text-text-secondary mt-1">
            Data will appear once collection starts
          </p>
        </div>
      </div>
    )
  }

  // Reverse data to show oldest first
  const chartData = [...data].reverse()

  return (
    <div className="w-full h-64">
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={chartData} margin={{ top: 5, right: 30, left: 0, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#333" />
          <XAxis
            dataKey="timestamp"
            tickFormatter={formatTime}
            stroke="#666"
            style={{ fontSize: '12px' }}
          />
          <YAxis
            yAxisId="left"
            stroke="#10b981"
            domain={[-1, 1]}
            label={{ value: 'Sentiment', angle: -90, position: 'insideLeft', style: { fill: '#10b981' } }}
          />
          <YAxis
            yAxisId="right"
            orientation="right"
            stroke="#f97316"
            label={{ value: 'Hype', angle: 90, position: 'insideRight', style: { fill: '#f97316' } }}
          />
          <Tooltip content={<CustomTooltip />} />
          <Legend />

          {/* Reference line at 0 for sentiment */}
          <ReferenceLine yAxisId="left" y={0} stroke="#666" strokeDasharray="3 3" />

          {/* Sentiment line */}
          <Line
            yAxisId="left"
            type="monotone"
            dataKey="sentiment_score"
            stroke="#10b981"
            strokeWidth={2}
            dot={false}
            name="Sentiment"
          />

          {/* Hype line */}
          <Line
            yAxisId="right"
            type="monotone"
            dataKey="hype_score"
            stroke="#f97316"
            strokeWidth={2}
            dot={false}
            name="Hype Score"
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  )
}
