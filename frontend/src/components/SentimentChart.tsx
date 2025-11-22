/**
 * SENTIMENT CHART COMPONENT
 * =========================
 * Displays a bar chart showing sentiment for each coin.
 * Uses Recharts library for the visualization.
 */

'use client'

import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Cell,
  ReferenceLine
} from 'recharts'

interface Coin {
  symbol: string
  name: string
  sentiment: number | null
}

interface SentimentChartProps {
  coins: Coin[]
}

export function SentimentChart({ coins }: SentimentChartProps) {
  // Filter coins with sentiment data and sort by sentiment
  const chartData = coins
    .filter(coin => coin.sentiment !== null)
    .map(coin => ({
      symbol: coin.symbol,
      name: coin.name,
      sentiment: coin.sentiment as number,
    }))
    .sort((a, b) => b.sentiment - a.sentiment)
    .slice(0, 15)  // Show top 15 coins

  // Colors for the bars
  const BULLISH = '#16c784'
  const BEARISH = '#ea3943'

  // Show message if no data
  if (chartData.length === 0) {
    return (
      <div className="flex items-center justify-center h-64 text-text-secondary">
        No sentiment data available yet. Run social media collection first.
      </div>
    )
  }

  // Custom tooltip
  const CustomTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload
      return (
        <div className="bg-bg-secondary border border-gray-700 rounded-lg p-3 shadow-lg">
          <p className="font-bold text-text-primary">{data.symbol}</p>
          <p className="text-text-secondary text-sm">{data.name}</p>
          <p className={`font-mono ${data.sentiment >= 0 ? 'text-bullish' : 'text-bearish'}`}>
            Sentiment: {data.sentiment.toFixed(3)}
          </p>
        </div>
      )
    }
    return null
  }

  return (
    <div className="h-80">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart
          data={chartData}
          layout="vertical"
          margin={{ top: 10, right: 30, left: 60, bottom: 10 }}
        >
          <CartesianGrid strokeDasharray="3 3" stroke="#374151" horizontal={false} />

          {/* X-axis (sentiment values) */}
          <XAxis
            type="number"
            domain={[-1, 1]}
            tickFormatter={(value) => value.toFixed(1)}
            tick={{ fill: '#8b93b6', fontSize: 12 }}
            axisLine={{ stroke: '#374151' }}
          />

          {/* Y-axis (coin symbols) */}
          <YAxis
            type="category"
            dataKey="symbol"
            tick={{ fill: '#e6e9f0', fontSize: 12, fontFamily: 'monospace' }}
            axisLine={{ stroke: '#374151' }}
            width={50}
          />

          <Tooltip content={<CustomTooltip />} cursor={{ fill: 'rgba(56, 97, 251, 0.1)' }} />

          {/* Zero reference line */}
          <ReferenceLine x={0} stroke="#8b93b6" strokeDasharray="3 3" />

          {/* Bars with conditional colors */}
          <Bar dataKey="sentiment" radius={[0, 4, 4, 0]}>
            {chartData.map((entry, index) => (
              <Cell
                key={`cell-${index}`}
                fill={entry.sentiment >= 0 ? BULLISH : BEARISH}
              />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  )
}
