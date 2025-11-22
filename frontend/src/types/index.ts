/**
 * SHARED TYPES
 * ============
 * Centralized TypeScript interfaces for the application.
 * Import from '@/types' in any component or page.
 */

// ============================================
// COIN TYPES
// ============================================

export interface Coin {
  symbol: string
  name: string
  price: number | null
  change_24h: number | null
  sentiment: number | null
  hype_score: number | null
}

export interface CoinDetail extends Coin {
  market_cap: number | null
  volume_24h: number | null
  high_24h: number | null
  low_24h: number | null
  price_history: PricePoint[]
  sentiment_history: SentimentPoint[]
}

// ============================================
// PRICE & CHART TYPES
// ============================================

export interface PricePoint {
  timestamp: string
  price: number
}

export interface SentimentPoint {
  timestamp: string
  sentiment: number
  hype_score: number
}

export interface ChartDataPoint {
  timestamp: string
  label: string
  price?: number
  sentiment?: number
  hype?: number
  volume?: number
}

// ============================================
// STATS TYPES
// ============================================

export interface Stats {
  total_coins: number
  avg_sentiment_24h: number | null
  avg_hype_24h: number | null
  record_counts: {
    prices: number
    reddit_posts: number
    tiktok_videos: number
  }
}

// ============================================
// EVENT TYPES
// ============================================

export interface Event {
  id: number
  timestamp: string
  event_type: EventType
  coin_symbol: string
  description: string
  magnitude: number | null
  metadata: Record<string, unknown> | null
}

export type EventType =
  | 'price_spike'
  | 'price_drop'
  | 'sentiment_shift'
  | 'volume_spike'
  | 'social_surge'
  | 'anomaly'

// ============================================
// SENTIMENT TYPES
// ============================================

export interface HeatmapData {
  symbol: string
  sentiment: number
}

export interface SentimentBreakdown {
  source: 'reddit' | 'tiktok' | 'twitter' | 'overall'
  sentiment: number
  volume: number
  change_24h: number
}

// ============================================
// API RESPONSE TYPES
// ============================================

export interface ApiResponse<T> {
  data?: T
  error?: string
  status: number
}

export interface CoinsResponse {
  coins: Coin[]
}

export interface StatsResponse extends Stats {}

export interface EventsResponse {
  events: Event[]
}

export interface HeatmapResponse {
  data: HeatmapData[]
}

export interface PriceHistoryResponse {
  symbol: string
  prices: PricePoint[]
  timeframe: TimeRange
}

// ============================================
// FILTER & UI TYPES
// ============================================

export type TimeRange = '1h' | '24h' | '7d' | '30d' | 'all'

export type SortDirection = 'asc' | 'desc'

export interface SortConfig {
  key: string
  direction: SortDirection
}

export type SentimentStatus = 'bullish' | 'bearish' | 'neutral'

// ============================================
// COMPONENT PROP TYPES
// ============================================

export interface StatsCardProps {
  title: string
  value: string | number
  icon: string
  subtitle?: string
  sentiment?: 'positive' | 'negative' | 'neutral'
}

export interface CoinTableProps {
  coins: Coin[]
  onCoinClick?: (symbol: string) => void
}

export interface SentimentChartProps {
  coins: Coin[]
  timeRange?: TimeRange
}

export interface SentimentGaugeProps {
  value: number
  label?: string
}

export interface PriceChartProps {
  symbol: string
  data: PricePoint[]
  sentimentData?: SentimentPoint[]
  timeRange: TimeRange
  onTimeRangeChange?: (range: TimeRange) => void
}
