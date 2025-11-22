/**
 * SENTIMENT GAUGE COMPONENT
 * =========================
 * A visual gauge that shows overall market sentiment.
 * Goes from -1 (extremely bearish) to +1 (extremely bullish).
 */

'use client'

interface SentimentGaugeProps {
  value: number  // -1 to 1
}

export function SentimentGauge({ value }: SentimentGaugeProps) {
  // Clamp value between -1 and 1
  const clampedValue = Math.max(-1, Math.min(1, value))

  // Convert to 0-100 scale for positioning (0 = -1, 50 = 0, 100 = +1)
  const percentage = ((clampedValue + 1) / 2) * 100

  // Determine the sentiment label
  const getLabel = () => {
    if (clampedValue >= 0.5) return 'Very Bullish'
    if (clampedValue >= 0.2) return 'Bullish'
    if (clampedValue >= 0.05) return 'Slightly Bullish'
    if (clampedValue > -0.05) return 'Neutral'
    if (clampedValue > -0.2) return 'Slightly Bearish'
    if (clampedValue > -0.5) return 'Bearish'
    return 'Very Bearish'
  }

  // Get color based on value
  const getColor = () => {
    if (clampedValue >= 0.2) return '#16c784'  // Green
    if (clampedValue > -0.2) return '#8b93b6'  // Gray
    return '#ea3943'  // Red
  }

  return (
    <div className="flex flex-col items-center py-4">
      {/* Gauge Container */}
      <div className="relative w-full max-w-xs">
        {/* Background arc (semi-circle) */}
        <svg viewBox="0 0 200 110" className="w-full">
          {/* Background track */}
          <path
            d="M 20 100 A 80 80 0 0 1 180 100"
            fill="none"
            stroke="#374151"
            strokeWidth="16"
            strokeLinecap="round"
          />

          {/* Gradient arc showing the scale */}
          <defs>
            <linearGradient id="gaugeGradient" x1="0%" y1="0%" x2="100%" y2="0%">
              <stop offset="0%" stopColor="#ea3943" />
              <stop offset="50%" stopColor="#8b93b6" />
              <stop offset="100%" stopColor="#16c784" />
            </linearGradient>
          </defs>
          <path
            d="M 20 100 A 80 80 0 0 1 180 100"
            fill="none"
            stroke="url(#gaugeGradient)"
            strokeWidth="12"
            strokeLinecap="round"
            opacity="0.3"
          />

          {/* Needle */}
          <g transform={`rotate(${-90 + (percentage * 1.8)}, 100, 100)`}>
            <line
              x1="100"
              y1="100"
              x2="100"
              y2="35"
              stroke={getColor()}
              strokeWidth="3"
              strokeLinecap="round"
            />
            <circle cx="100" cy="100" r="8" fill={getColor()} />
          </g>

          {/* Labels */}
          <text x="15" y="108" fill="#ea3943" fontSize="10" fontWeight="bold">-1</text>
          <text x="95" y="25" fill="#8b93b6" fontSize="10" textAnchor="middle">0</text>
          <text x="180" y="108" fill="#16c784" fontSize="10" fontWeight="bold">+1</text>
        </svg>
      </div>

      {/* Value display */}
      <div className="text-center mt-4">
        <div
          className="text-4xl font-bold font-mono"
          style={{ color: getColor() }}
        >
          {clampedValue >= 0 ? '+' : ''}{clampedValue.toFixed(2)}
        </div>
        <div className="text-text-secondary mt-1">
          {getLabel()}
        </div>
      </div>

      {/* Legend */}
      <div className="flex justify-between w-full max-w-xs mt-6 text-xs text-text-secondary">
        <div className="flex items-center gap-1">
          <div className="w-3 h-3 rounded-full bg-bearish" />
          <span>Bearish</span>
        </div>
        <div className="flex items-center gap-1">
          <div className="w-3 h-3 rounded-full bg-neutral" />
          <span>Neutral</span>
        </div>
        <div className="flex items-center gap-1">
          <div className="w-3 h-3 rounded-full bg-bullish" />
          <span>Bullish</span>
        </div>
      </div>
    </div>
  )
}
