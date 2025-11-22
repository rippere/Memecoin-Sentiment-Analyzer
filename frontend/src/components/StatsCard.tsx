/**
 * STATS CARD COMPONENT
 * ====================
 * A simple card that displays a single statistic.
 * Used in the dashboard to show key metrics.
 */

interface StatsCardProps {
  title: string          // What metric this is (e.g., "Coins Tracked")
  value: string | number // The actual value to display
  icon: string           // Emoji icon for visual interest
  subtitle?: string      // Optional context (e.g., "Last 24h")
  sentiment?: 'positive' | 'negative' | 'neutral'  // Colors the value
}

export function StatsCard({ title, value, icon, subtitle, sentiment }: StatsCardProps) {
  // Determine the color based on sentiment
  const valueColor = sentiment === 'positive'
    ? 'text-bullish'
    : sentiment === 'negative'
      ? 'text-bearish'
      : 'text-text-primary'

  return (
    <div className="card hover:border-accent/50 transition-colors">
      {/* Top row: Icon and Title */}
      <div className="flex items-center gap-2 mb-2">
        <span className="text-2xl">{icon}</span>
        <span className="text-text-secondary text-sm">{title}</span>
      </div>

      {/* Main value - big and bold */}
      <div className={`text-2xl font-bold ${valueColor}`}>
        {value}
      </div>

      {/* Subtitle - small context */}
      {subtitle && (
        <div className="text-text-secondary text-xs mt-1">
          {subtitle}
        </div>
      )}
    </div>
  )
}
