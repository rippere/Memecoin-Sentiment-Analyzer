/**
 * COINS PAGE
 * ==========
 * Shows detailed information for all tracked coins.
 * Includes filtering and search functionality.
 */

'use client'

import { useState, useEffect } from 'react'
import { CoinTable } from '@/components/CoinTable'

interface Coin {
  symbol: string
  name: string
  price: number | null
  change_24h: number | null
  sentiment: number | null
  hype_score: number | null
}

export default function CoinsPage() {
  const [coins, setCoins] = useState<Coin[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [search, setSearch] = useState('')

  const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

  useEffect(() => {
    async function fetchCoins() {
      try {
        const res = await fetch(`${API_URL}/api/coins`)
        if (!res.ok) throw new Error('Failed to fetch coins')
        const data = await res.json()
        setCoins(data.coins || [])
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Unknown error')
      } finally {
        setLoading(false)
      }
    }

    fetchCoins()
    const interval = setInterval(fetchCoins, 60000)
    return () => clearInterval(interval)
  }, [API_URL])

  // Filter coins based on search
  const filteredCoins = coins.filter(coin =>
    coin.symbol.toLowerCase().includes(search.toLowerCase()) ||
    coin.name.toLowerCase().includes(search.toLowerCase())
  )

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="text-4xl mb-4 loading">🪙</div>
          <p className="text-text-secondary">Loading coins...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="card bg-red-900/20 border-red-500">
        <h2 className="text-xl font-bold text-red-400 mb-2">Error</h2>
        <p className="text-text-secondary">{error}</p>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold mb-2">All Coins</h1>
          <p className="text-text-secondary">
            Tracking {coins.length} cryptocurrencies
          </p>
        </div>

        {/* Search box */}
        <div className="relative">
          <input
            type="text"
            placeholder="Search coins..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="bg-bg-secondary border border-gray-700 rounded-lg px-4 py-2 pl-10 text-text-primary placeholder-text-secondary focus:outline-none focus:border-accent"
          />
          <span className="absolute left-3 top-2.5 text-text-secondary">🔍</span>
        </div>
      </div>

      {/* Results count */}
      {search && (
        <p className="text-text-secondary text-sm">
          Showing {filteredCoins.length} of {coins.length} coins
        </p>
      )}

      {/* Coin Table */}
      <div className="card">
        <CoinTable coins={filteredCoins} />
      </div>
    </div>
  )
}
