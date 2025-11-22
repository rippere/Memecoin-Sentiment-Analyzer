/**
 * DATA HOOKS
 * ==========
 * Custom React hooks for fetching and managing data.
 * Provides loading states, error handling, and auto-refresh.
 */

import { useState, useEffect, useCallback } from 'react'
import type { Coin, CoinDetail, Stats, Event, HeatmapData, PricePoint, TimeRange } from '@/types'
import * as api from '@/services/api'

// ============================================
// GENERIC DATA HOOK
// ============================================

interface UseDataResult<T> {
  data: T | null
  loading: boolean
  error: string | null
  refetch: () => Promise<void>
}

function useData<T>(
  fetcher: () => Promise<T>,
  refreshInterval?: number
): UseDataResult<T> {
  const [data, setData] = useState<T | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const fetchData = useCallback(async () => {
    try {
      setLoading(true)
      const result = await fetcher()
      setData(result)
      setError(null)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error')
    } finally {
      setLoading(false)
    }
  }, [fetcher])

  useEffect(() => {
    fetchData()

    if (refreshInterval && refreshInterval > 0) {
      const interval = setInterval(fetchData, refreshInterval)
      return () => clearInterval(interval)
    }
  }, [fetchData, refreshInterval])

  return { data, loading, error, refetch: fetchData }
}

// ============================================
// SPECIFIC HOOKS
// ============================================

/**
 * Fetch all coins with auto-refresh
 */
export function useCoins(refreshInterval = 60000) {
  const [data, setData] = useState<Coin[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const fetchCoins = useCallback(async () => {
    try {
      setLoading(true)
      const coins = await api.getCoins()
      setData(coins)
      setError(null)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch coins')
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    fetchCoins()
    if (refreshInterval > 0) {
      const interval = setInterval(fetchCoins, refreshInterval)
      return () => clearInterval(interval)
    }
  }, [fetchCoins, refreshInterval])

  return { coins: data, loading, error, refetch: fetchCoins }
}

/**
 * Fetch single coin details
 */
export function useCoin(symbol: string) {
  const [data, setData] = useState<CoinDetail | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const fetchCoin = useCallback(async () => {
    if (!symbol) return
    try {
      setLoading(true)
      const coin = await api.getCoin(symbol)
      setData(coin)
      setError(null)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch coin')
    } finally {
      setLoading(false)
    }
  }, [symbol])

  useEffect(() => {
    fetchCoin()
  }, [fetchCoin])

  return { coin: data, loading, error, refetch: fetchCoin }
}

/**
 * Fetch price history for a coin
 */
export function usePriceHistory(symbol: string, timeRange: TimeRange = '24h') {
  const [data, setData] = useState<PricePoint[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const fetchHistory = useCallback(async () => {
    if (!symbol) return
    try {
      setLoading(true)
      const prices = await api.getPriceHistory(symbol, timeRange)
      setData(prices)
      setError(null)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch price history')
    } finally {
      setLoading(false)
    }
  }, [symbol, timeRange])

  useEffect(() => {
    fetchHistory()
  }, [fetchHistory])

  return { prices: data, loading, error, refetch: fetchHistory }
}

/**
 * Fetch dashboard stats
 */
export function useStats(refreshInterval = 60000) {
  const [data, setData] = useState<Stats | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const fetchStats = useCallback(async () => {
    try {
      setLoading(true)
      const stats = await api.getStats()
      setData(stats)
      setError(null)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch stats')
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    fetchStats()
    if (refreshInterval > 0) {
      const interval = setInterval(fetchStats, refreshInterval)
      return () => clearInterval(interval)
    }
  }, [fetchStats, refreshInterval])

  return { stats: data, loading, error, refetch: fetchStats }
}

/**
 * Fetch events log
 */
export function useEvents(limit = 100, refreshInterval = 30000) {
  const [data, setData] = useState<Event[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const fetchEvents = useCallback(async () => {
    try {
      setLoading(true)
      const events = await api.getEvents(limit)
      setData(events)
      setError(null)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch events')
    } finally {
      setLoading(false)
    }
  }, [limit])

  useEffect(() => {
    fetchEvents()
    if (refreshInterval > 0) {
      const interval = setInterval(fetchEvents, refreshInterval)
      return () => clearInterval(interval)
    }
  }, [fetchEvents, refreshInterval])

  return { events: data, loading, error, refetch: fetchEvents }
}

/**
 * Fetch sentiment heatmap
 */
export function useSentimentHeatmap(refreshInterval = 60000) {
  const [data, setData] = useState<HeatmapData[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const fetchHeatmap = useCallback(async () => {
    try {
      setLoading(true)
      const heatmap = await api.getSentimentHeatmap()
      setData(heatmap)
      setError(null)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch heatmap')
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    fetchHeatmap()
    if (refreshInterval > 0) {
      const interval = setInterval(fetchHeatmap, refreshInterval)
      return () => clearInterval(interval)
    }
  }, [fetchHeatmap, refreshInterval])

  return { heatmap: data, loading, error, refetch: fetchHeatmap }
}

/**
 * Combined dashboard data hook
 */
export function useDashboard(refreshInterval = 60000) {
  const { coins, loading: coinsLoading, error: coinsError } = useCoins(refreshInterval)
  const { stats, loading: statsLoading, error: statsError } = useStats(refreshInterval)

  return {
    coins,
    stats,
    loading: coinsLoading || statsLoading,
    error: coinsError || statsError,
  }
}
