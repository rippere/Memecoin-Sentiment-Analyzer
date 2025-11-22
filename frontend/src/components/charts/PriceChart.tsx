/**
 * PRICE CHART COMPONENT
 * =====================
 * Displays price history with optional sentiment overlay.
 * Features time range selector and responsive design.
 */

'use client'

import { useState, useMemo } from 'react'
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Area,
  ComposedChart,
  Legend,
} from 'recharts'
import type { TimeRange, PricePoint, SentimentPoint } from '@/types'

interface PriceChartProps {
  prices: PricePoint[]
  sentimentData?: SentimentPoint[]
  timeRange: TimeRange
  onTimeRangeChange: (range: TimeRange) => void
  showSentiment?: boolean
  height?: number
}

const TIME_RANGES: { value: TimeRange; label: string }[] = [
  { value: '1h', label: '1H' },
  { value: '24h', label: '24H' },
  { value: '7d', label: '7D' },
  { value: '30d', label: '30D' },
  { value: 'all', label: 'ALL' },
]

export function PriceChart({
  prices,
  sentimentData,
  timeRange,
  onTimeRangeChange,
  showSentiment = false,
  height = 400,
}: PriceChartProps) {
  const [hoveredData, setHoveredData] = useState<{
    price: number
    sentiment?: number
    timestamp: string
  } | null>(null)

  // Combine price and sentiment data
  const chartData = useMemo(() => {
    if (!prices.length) return []

    // Create a map of sentiment by timestamp for quick lookup
    const sentimentMap = new Map<string, number>()
    if (sentimentData) {
      sentimentData.forEach((s) => {
        sentimentMap.set(s.timestamp, s.sentiment)
      })
    }

    return prices.map((p) => ({
      timestamp: p.timestamp,
      price: p.price,
      sentiment: sentimentMap.get(p.timestamp) ?? null,
      // Format timestamp for display
      label: formatTimestamp(p.timestamp, timeRange),
    }))
  }, [prices, sentimentData, timeRange])

  // Calculate price change
  const priceChange = useMemo(() => {
    if (chartData.length < 2) return { value: 0, percent: 0 }
    const first = chartData[0].price
    const last = chartData[chartData.length - 1].price
    const change = last - first
    const percent = (change / first) * 100
    return { value: change, percent }
  }, [chartData])

  // Format timestamp based on time range
  function formatTimestamp(timestamp: string, range: TimeRange): string {
    const date = new Date(timestamp)
    switch (range) {
      case '1h':
        return date.toLocaleTimeString('en-US', {
          hour: '2-digit',
          minute: '2-digit',
        })
      case '24h':
        return date.toLocaleTimeString('en-US', {
          hour: '2-digit',
          minute: '2-digit',
        })
      case '7d':
        return date.toLocaleDateString('en-US', {
          weekday: 'short',
          hour: '2-digit',
        })
      case '30d':
        return date.toLocaleDateString('en-US', {
          month: 'short',
          day: 'numeric',
        })
      default:
        return date.toLocaleDateString('en-US', {
          month: 'short',
          day: 'numeric',
        })
    }
  }

  // Format price for display
  function formatPrice(price: number): string {
    if (price < 0.0001) return `$${price.toExponential(2)}`
    if (price < 1) return `$${price.toFixed(6)}`
    if (price < 100) return `$${price.toFixed(4)}`
    return `$${price.toLocaleString('en-US', { maximumFractionDigits: 2 })}`
  }

  // Custom tooltip
  const CustomTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload
      return (
        <div className="bg-bg-secondary border border-gray-700 rounded-lg p-3 shadow-lg">
          <p className="text-text-secondary text-xs mb-1">{data.label}</p>
          <p className="text-text-primary font-bold">
            {formatPrice(data.price)}
          </p>
          {showSentiment && data.sentiment !== null && (
            <p
              className={`text-sm ${
                data.sentiment > 0 ? 'text-bullish' : 'text-bearish'
              }`}
            >
              Sentiment: {(data.sentiment * 100).toFixed(1)}%
            </p>
          )}
        </div>
      )
    }
    return null
  }

  if (!prices.length) {
    return (
      <div className="flex items-center justify-center h-64 bg-bg-secondary rounded-lg">
        <p className="text-text-secondary">No price data available</p>
      </div>
    )
  }

  return (
    <div className="space-y-4">
      {/* Header with time range selector */}
      <div className="flex items-center justify-between">
        <div>
          <span
            className={`text-lg font-bold ${
              priceChange.percent >= 0 ? 'text-bullish' : 'text-bearish'
            }`}
          >
            {priceChange.percent >= 0 ? '+' : ''}
            {priceChange.percent.toFixed(2)}%
          </span>
          <span className="text-text-secondary text-sm ml-2">
            {timeRange === 'all' ? 'All time' : `Last ${timeRange}`}
          </span>
        </div>

        {/* Time range buttons */}
        <div className="flex gap-1 bg-bg-secondary rounded-lg p-1">
          {TIME_RANGES.map((range) => (
            <button
              key={range.value}
              onClick={() => onTimeRangeChange(range.value)}
              className={`px-3 py-1 rounded text-sm font-medium transition-colors ${
                timeRange === range.value
                  ? 'bg-accent text-white'
                  : 'text-text-secondary hover:text-text-primary hover:bg-bg-primary'
              }`}
            >
              {range.label}
            </button>
          ))}
        </div>
      </div>

      {/* Chart */}
      <div style={{ height }}>
        <ResponsiveContainer width="100%" height="100%">
          {showSentiment && sentimentData ? (
            <ComposedChart data={chartData}>
              <defs>
                <linearGradient id="priceGradient" x1="0" y1="0" x2="0" y2="1">
                  <stop
                    offset="5%"
                    stopColor={priceChange.percent >= 0 ? '#16c784' : '#ea3943'}
                    stopOpacity={0.3}
                  />
                  <stop
                    offset="95%"
                    stopColor={priceChange.percent >= 0 ? '#16c784' : '#ea3943'}
                    stopOpacity={0}
                  />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#2d3748" />
              <XAxis
                dataKey="label"
                stroke="#8b93b6"
                fontSize={12}
                tickLine={false}
                axisLine={false}
              />
              <YAxis
                yAxisId="price"
                orientation="left"
                stroke="#8b93b6"
                fontSize={12}
                tickLine={false}
                axisLine={false}
                tickFormatter={(v) => formatPrice(v)}
                domain={['auto', 'auto']}
              />
              <YAxis
                yAxisId="sentiment"
                orientation="right"
                stroke="#936df8"
                fontSize={12}
                tickLine={false}
                axisLine={false}
                tickFormatter={(v) => `${(v * 100).toFixed(0)}%`}
                domain={[-1, 1]}
              />
              <Tooltip content={<CustomTooltip />} />
              <Legend />
              <Area
                yAxisId="price"
                type="monotone"
                dataKey="price"
                stroke={priceChange.percent >= 0 ? '#16c784' : '#ea3943'}
                fill="url(#priceGradient)"
                strokeWidth={2}
                name="Price"
              />
              <Line
                yAxisId="sentiment"
                type="monotone"
                dataKey="sentiment"
                stroke="#936df8"
                strokeWidth={2}
                dot={false}
                strokeDasharray="5 5"
                name="Sentiment"
              />
            </ComposedChart>
          ) : (
            <LineChart data={chartData}>
              <defs>
                <linearGradient id="priceGradient" x1="0" y1="0" x2="0" y2="1">
                  <stop
                    offset="5%"
                    stopColor={priceChange.percent >= 0 ? '#16c784' : '#ea3943'}
                    stopOpacity={0.3}
                  />
                  <stop
                    offset="95%"
                    stopColor={priceChange.percent >= 0 ? '#16c784' : '#ea3943'}
                    stopOpacity={0}
                  />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#2d3748" />
              <XAxis
                dataKey="label"
                stroke="#8b93b6"
                fontSize={12}
                tickLine={false}
                axisLine={false}
              />
              <YAxis
                stroke="#8b93b6"
                fontSize={12}
                tickLine={false}
                axisLine={false}
                tickFormatter={(v) => formatPrice(v)}
                domain={['auto', 'auto']}
              />
              <Tooltip content={<CustomTooltip />} />
              <Line
                type="monotone"
                dataKey="price"
                stroke={priceChange.percent >= 0 ? '#16c784' : '#ea3943'}
                strokeWidth={2}
                dot={false}
                activeDot={{ r: 6, strokeWidth: 0 }}
              />
            </LineChart>
          )}
        </ResponsiveContainer>
      </div>
    </div>
  )
}

export default PriceChart
