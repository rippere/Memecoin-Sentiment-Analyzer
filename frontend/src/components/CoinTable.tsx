/**
 * COIN TABLE COMPONENT
 * ====================
 * Displays a table of all tracked coins with their metrics.
 * Shows symbol, name, price, 24h change, sentiment, and hype score.
 */

'use client'  // Required for sorting state

import { useState } from 'react'

interface Coin {
  symbol: string
  name: string
  price: number | null
  change_24h: number | null
  sentiment: number | null
  hype_score: number | null
}

interface CoinTableProps {
  coins: Coin[]
}

export function CoinTable({ coins }: CoinTableProps) {
  // State for sorting
  const [sortBy, setSortBy] = useState<keyof Coin>('symbol')
  const [sortAsc, setSortAsc] = useState(true)

  // Handle column header click for sorting
  const handleSort = (column: keyof Coin) => {
    if (sortBy === column) {
      // Same column - toggle direction
      setSortAsc(!sortAsc)
    } else {
      // New column - default to descending for numbers, ascending for text
      setSortBy(column)
      setSortAsc(column === 'symbol' || column === 'name')
    }
  }

  // Sort the coins
  const sortedCoins = [...coins].sort((a, b) => {
    const aVal = a[sortBy]
    const bVal = b[sortBy]

    // Handle null values
    if (aVal === null && bVal === null) return 0
    if (aVal === null) return 1
    if (bVal === null) return -1

    // Compare
    if (typeof aVal === 'string' && typeof bVal === 'string') {
      return sortAsc ? aVal.localeCompare(bVal) : bVal.localeCompare(aVal)
    }

    // Numbers
    return sortAsc ? (aVal as number) - (bVal as number) : (bVal as number) - (aVal as number)
  })

  // Format price nicely
  const formatPrice = (price: number | null) => {
    if (price === null) return '-'
    if (price < 0.01) return `$${price.toFixed(6)}`
    if (price < 1) return `$${price.toFixed(4)}`
    return `$${price.toFixed(2)}`
  }

  // Format percentage change
  const formatChange = (change: number | null) => {
    if (change === null) return '-'
    const prefix = change >= 0 ? '+' : ''
    return `${prefix}${change.toFixed(2)}%`
  }

  // Sortable column header
  const SortHeader = ({ column, children }: { column: keyof Coin, children: React.ReactNode }) => (
    <th
      onClick={() => handleSort(column)}
      className="px-4 py-3 text-left text-xs font-medium text-text-secondary uppercase tracking-wider cursor-pointer hover:text-text-primary transition-colors"
    >
      <div className="flex items-center gap-1">
        {children}
        {sortBy === column && (
          <span className="text-accent">{sortAsc ? '↑' : '↓'}</span>
        )}
      </div>
    </th>
  )

  // Show message if no coins
  if (coins.length === 0) {
    return (
      <div className="text-center py-8 text-text-secondary">
        No coins found. Make sure the data collection is running.
      </div>
    )
  }

  return (
    <div className="overflow-x-auto">
      <table className="w-full">
        <thead className="border-b border-gray-800">
          <tr>
            <SortHeader column="symbol">Symbol</SortHeader>
            <SortHeader column="name">Name</SortHeader>
            <SortHeader column="price">Price</SortHeader>
            <SortHeader column="change_24h">24h Change</SortHeader>
            <SortHeader column="sentiment">Sentiment</SortHeader>
            <SortHeader column="hype_score">Hype Score</SortHeader>
          </tr>
        </thead>
        <tbody className="divide-y divide-gray-800">
          {sortedCoins.map((coin) => (
            <tr key={coin.symbol} className="hover:bg-bg-secondary/50 transition-colors">
              {/* Symbol - bold */}
              <td className="px-4 py-3 font-mono font-bold text-accent">
                {coin.symbol}
              </td>

              {/* Name */}
              <td className="px-4 py-3 text-text-primary">
                {coin.name}
              </td>

              {/* Price */}
              <td className="px-4 py-3 font-mono">
                {formatPrice(coin.price)}
              </td>

              {/* 24h Change - colored */}
              <td className={`px-4 py-3 font-mono ${
                coin.change_24h === null ? 'text-text-secondary' :
                coin.change_24h >= 0 ? 'text-bullish' : 'text-bearish'
              }`}>
                {formatChange(coin.change_24h)}
              </td>

              {/* Sentiment - colored bar */}
              <td className="px-4 py-3">
                {coin.sentiment !== null ? (
                  <div className="flex items-center gap-2">
                    <div className="w-16 bg-gray-800 rounded-full h-2 overflow-hidden">
                      <div
                        className={`h-full ${coin.sentiment >= 0 ? 'bg-bullish' : 'bg-bearish'}`}
                        style={{ width: `${Math.abs(coin.sentiment) * 100}%` }}
                      />
                    </div>
                    <span className={`text-xs ${coin.sentiment >= 0 ? 'text-bullish' : 'text-bearish'}`}>
                      {coin.sentiment.toFixed(2)}
                    </span>
                  </div>
                ) : (
                  <span className="text-text-secondary">-</span>
                )}
              </td>

              {/* Hype Score - progress bar */}
              <td className="px-4 py-3">
                {coin.hype_score !== null ? (
                  <div className="flex items-center gap-2">
                    <div className="w-16 bg-gray-800 rounded-full h-2 overflow-hidden">
                      <div
                        className="h-full bg-accent-purple"
                        style={{ width: `${coin.hype_score}%` }}
                      />
                    </div>
                    <span className="text-xs text-text-secondary">
                      {Math.round(coin.hype_score)}
                    </span>
                  </div>
                ) : (
                  <span className="text-text-secondary">-</span>
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
