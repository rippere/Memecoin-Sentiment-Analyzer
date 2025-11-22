/**
 * EVENTS PAGE
 * ===========
 * Shows a log of significant events detected by the system.
 * Events include price spikes, sentiment changes, etc.
 */

'use client'

import { useState, useEffect } from 'react'

interface Event {
  id: number
  timestamp: string
  event_type: string
  coin_symbol: string
  description: string
  magnitude: number | null
  metadata: Record<string, any> | null
}

export default function EventsPage() {
  const [events, setEvents] = useState<Event[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [filter, setFilter] = useState<string>('all')

  const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

  useEffect(() => {
    async function fetchEvents() {
      try {
        const res = await fetch(`${API_URL}/api/events?limit=100`)
        if (!res.ok) throw new Error('Failed to fetch events')
        const data = await res.json()
        setEvents(data.events || [])
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Unknown error')
      } finally {
        setLoading(false)
      }
    }

    fetchEvents()
    const interval = setInterval(fetchEvents, 30000)  // Refresh every 30s
    return () => clearInterval(interval)
  }, [API_URL])

  // Get unique event types for filtering
  const eventTypes = ['all', ...new Set(events.map(e => e.event_type))]

  // Filter events
  const filteredEvents = filter === 'all'
    ? events
    : events.filter(e => e.event_type === filter)

  // Get icon for event type
  const getEventIcon = (type: string) => {
    switch (type) {
      case 'price_spike': return '📈'
      case 'price_drop': return '📉'
      case 'sentiment_shift': return '🔄'
      case 'volume_spike': return '🔥'
      case 'social_surge': return '💬'
      case 'anomaly': return '⚠️'
      default: return '📋'
    }
  }

  // Get color for event type
  const getEventColor = (type: string) => {
    switch (type) {
      case 'price_spike': return 'text-bullish border-bullish/30 bg-bullish/10'
      case 'price_drop': return 'text-bearish border-bearish/30 bg-bearish/10'
      case 'sentiment_shift': return 'text-accent border-accent/30 bg-accent/10'
      case 'volume_spike': return 'text-accent-purple border-accent-purple/30 bg-accent-purple/10'
      case 'social_surge': return 'text-yellow-400 border-yellow-400/30 bg-yellow-400/10'
      case 'anomaly': return 'text-orange-400 border-orange-400/30 bg-orange-400/10'
      default: return 'text-text-secondary border-gray-700 bg-bg-secondary'
    }
  }

  // Format timestamp
  const formatTime = (timestamp: string) => {
    const date = new Date(timestamp)
    const now = new Date()
    const diff = now.getTime() - date.getTime()

    // If less than 24 hours, show relative time
    if (diff < 86400000) {
      const hours = Math.floor(diff / 3600000)
      const minutes = Math.floor((diff % 3600000) / 60000)
      if (hours > 0) return `${hours}h ago`
      if (minutes > 0) return `${minutes}m ago`
      return 'Just now'
    }

    // Otherwise show date
    return date.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="text-4xl mb-4 loading">📋</div>
          <p className="text-text-secondary">Loading events...</p>
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
          <h1 className="text-3xl font-bold mb-2">Event Log</h1>
          <p className="text-text-secondary">
            {events.length} events recorded
          </p>
        </div>

        {/* Filter dropdown */}
        <select
          value={filter}
          onChange={(e) => setFilter(e.target.value)}
          className="bg-bg-secondary border border-gray-700 rounded-lg px-4 py-2 text-text-primary focus:outline-none focus:border-accent"
        >
          {eventTypes.map(type => (
            <option key={type} value={type}>
              {type === 'all' ? 'All Events' : type.replace('_', ' ')}
            </option>
          ))}
        </select>
      </div>

      {/* Events list */}
      {filteredEvents.length === 0 ? (
        <div className="card text-center py-12">
          <div className="text-4xl mb-4">📭</div>
          <p className="text-text-secondary">No events recorded yet.</p>
          <p className="text-text-secondary text-sm mt-2">
            Events will appear here when significant changes are detected.
          </p>
        </div>
      ) : (
        <div className="space-y-3">
          {filteredEvents.map((event) => (
            <div
              key={event.id}
              className={`card border ${getEventColor(event.event_type)} flex items-start gap-4`}
            >
              {/* Icon */}
              <div className="text-2xl">
                {getEventIcon(event.event_type)}
              </div>

              {/* Content */}
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 mb-1">
                  <span className="font-mono font-bold text-accent">
                    {event.coin_symbol}
                  </span>
                  <span className="text-xs px-2 py-0.5 rounded-full bg-bg-secondary text-text-secondary">
                    {event.event_type.replace('_', ' ')}
                  </span>
                </div>
                <p className="text-text-primary">
                  {event.description}
                </p>
                {event.magnitude !== null && (
                  <p className="text-sm text-text-secondary mt-1">
                    Magnitude: {event.magnitude.toFixed(2)}
                  </p>
                )}
              </div>

              {/* Timestamp */}
              <div className="text-sm text-text-secondary whitespace-nowrap">
                {formatTime(event.timestamp)}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
