/**
 * API SERVICE
 * ===========
 * Centralized API client with typed fetch functions.
 * All API calls should go through this service.
 */

import type {
  Coin,
  CoinDetail,
  Stats,
  Event,
  HeatmapData,
  PricePoint,
  TimeRange,
} from '@/types'

// API base URL - configurable via environment variable
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

// ============================================
// GENERIC FETCH WRAPPER
// ============================================

interface FetchOptions {
  method?: 'GET' | 'POST' | 'PUT' | 'DELETE'
  body?: unknown
  headers?: Record<string, string>
}

async function fetchApi<T>(endpoint: string, options: FetchOptions = {}): Promise<T> {
  const { method = 'GET', body, headers = {} } = options

  const config: RequestInit = {
    method,
    headers: {
      'Content-Type': 'application/json',
      ...headers,
    },
  }

  if (body) {
    config.body = JSON.stringify(body)
  }

  const response = await fetch(`${API_URL}${endpoint}`, config)

  if (!response.ok) {
    const error = await response.text()
    throw new Error(error || `API Error: ${response.status}`)
  }

  return response.json()
}

// ============================================
// COINS API
// ============================================

export async function getCoins(): Promise<Coin[]> {
  const data = await fetchApi<{ coins: Coin[] }>('/api/coins')
  return data.coins || []
}

export async function getCoin(symbol: string): Promise<CoinDetail | null> {
  try {
    const data = await fetchApi<CoinDetail>(`/api/coins/${symbol}`)
    return data
  } catch {
    return null
  }
}

export async function getPriceHistory(
  symbol: string,
  timeRange: TimeRange = '24h'
): Promise<PricePoint[]> {
  try {
    const data = await fetchApi<{ prices: PricePoint[] }>(
      `/api/coins/${symbol}/history?timeframe=${timeRange}`
    )
    return data.prices || []
  } catch {
    return []
  }
}

// ============================================
// STATS API
// ============================================

export async function getStats(): Promise<Stats | null> {
  try {
    return await fetchApi<Stats>('/api/stats')
  } catch {
    return null
  }
}

// ============================================
// SENTIMENT API
// ============================================

export async function getSentimentHeatmap(): Promise<HeatmapData[]> {
  try {
    const data = await fetchApi<{ data: HeatmapData[] }>('/api/sentiment/heatmap')
    return data.data || []
  } catch {
    return []
  }
}

export async function getTopMovers(limit: number = 5): Promise<{
  gainers: Coin[]
  losers: Coin[]
}> {
  try {
    return await fetchApi<{ gainers: Coin[]; losers: Coin[] }>(
      `/api/sentiment/top-movers?limit=${limit}`
    )
  } catch {
    return { gainers: [], losers: [] }
  }
}

// ============================================
// EVENTS API
// ============================================

export async function getEvents(limit: number = 100): Promise<Event[]> {
  try {
    const data = await fetchApi<{ events: Event[] }>(`/api/events?limit=${limit}`)
    return data.events || []
  } catch {
    return []
  }
}

// ============================================
// UTILITY EXPORTS
// ============================================

export { API_URL }
