/**
 * ANALYSIS PANEL COMPONENT
 * ========================
 * Displays AI-powered analysis results with clear explanations.
 * Fetches correlation, Granger causality, spike detection, and data quality.
 */

'use client'

import { useState, useEffect } from 'react'

interface CorrelationResult {
  correlation: number | null
  p_value: number | null
  significant: boolean
  strength: string
  sample_size: number
}

interface CorrelationAnalysis {
  coin_symbol: string
  data_points: number
  sentiment_vs_price_change?: CorrelationResult
  hype_vs_price_change?: CorrelationResult
  error?: string
}

interface GrangerResult {
  coin_symbol: string
  best_lag?: number
  f_statistic?: number
  p_value?: number
  significant?: boolean
  interpretation?: string
  data_points?: number
  error?: string
}

interface SpikeResult {
  coin_symbol: string
  total_spikes: number
  success_rate_3_periods: number
  avg_price_change_after_spike: number
  interpretation: string
  error?: string
}

interface ShillResult {
  coordinated: boolean
  total_posts: number
  shill_posts: number
  shill_rate: number
  avg_shill_score: number
  interpretation: string
  message?: string
}

interface QualityResult {
  anomaly_count: number
  total_records: number
  anomaly_rate: number
  status: string
  message?: string
}

interface AnalysisPanelProps {
  symbol: string
}

// Explanation tooltips for each analysis type
const EXPLANATIONS = {
  correlation: {
    title: "Sentiment-Price Correlation",
    what: "Measures how closely sentiment scores move together with price changes.",
    how: "Uses Pearson correlation coefficient (-1 to +1). Positive means they move together, negative means opposite.",
    caveat: "Correlation doesn't mean causation - both could be caused by a third factor.",
  },
  granger: {
    title: "Granger Causality Test",
    what: "Tests if past sentiment values help predict future price changes.",
    how: "Compares prediction models with and without sentiment data using statistical F-test.",
    caveat: "A significant result suggests sentiment leads price, but doesn't guarantee profitable trading.",
  },
  spikes: {
    title: "Sentiment Spike Analysis",
    what: "Identifies unusual spikes in sentiment and checks if prices rose afterward.",
    how: "Detects sentiment values >2 standard deviations above average, then tracks subsequent price movement.",
    caveat: "Past spike patterns may not predict future behavior. Markets adapt.",
  },
  shill: {
    title: "Shill Campaign Detection",
    what: "Scans for coordinated promotion attempts that might artificially inflate sentiment.",
    how: "Analyzes post patterns for promotional keywords, repeat posters, and suspicious content.",
    caveat: "High shill activity doesn't mean the coin is bad, but sentiment data may be unreliable.",
  },
  quality: {
    title: "Data Quality Check",
    what: "Validates price data for anomalies that could affect analysis accuracy.",
    how: "Checks for extreme price jumps, zero volumes, and other suspicious patterns.",
    caveat: "Clean data doesn't guarantee accurate predictions - it just means the inputs are reliable.",
  }
}

export function AnalysisPanel({ symbol }: AnalysisPanelProps) {
  const [correlation, setCorrelation] = useState<CorrelationAnalysis | null>(null)
  const [granger, setGranger] = useState<GrangerResult | null>(null)
  const [spikes, setSpikes] = useState<SpikeResult | null>(null)
  const [shill, setShill] = useState<ShillResult | null>(null)
  const [quality, setQuality] = useState<QualityResult | null>(null)
  const [loading, setLoading] = useState(true)
  const [activeTab, setActiveTab] = useState<'overview' | 'correlation' | 'causality' | 'spikes' | 'quality'>('overview')

  const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

  useEffect(() => {
    async function fetchAnalysis() {
      if (!symbol) return

      setLoading(true)

      // Fetch all analysis data in parallel
      const [corrRes, grangerRes, spikesRes, shillRes, qualityRes] = await Promise.allSettled([
        fetch(`${API_URL}/api/analysis/correlation/${symbol}`),
        fetch(`${API_URL}/api/analysis/granger/${symbol}`),
        fetch(`${API_URL}/api/analysis/spikes/${symbol}`),
        fetch(`${API_URL}/api/analysis/shill-detection/${symbol}?hours=168`),
        fetch(`${API_URL}/api/analysis/quality/${symbol}?hours=168`),
      ])

      // Process results
      if (corrRes.status === 'fulfilled' && corrRes.value.ok) {
        setCorrelation(await corrRes.value.json())
      }
      if (grangerRes.status === 'fulfilled' && grangerRes.value.ok) {
        setGranger(await grangerRes.value.json())
      }
      if (spikesRes.status === 'fulfilled' && spikesRes.value.ok) {
        setSpikes(await spikesRes.value.json())
      }
      if (shillRes.status === 'fulfilled' && shillRes.value.ok) {
        setShill(await shillRes.value.json())
      }
      if (qualityRes.status === 'fulfilled' && qualityRes.value.ok) {
        setQuality(await qualityRes.value.json())
      }

      setLoading(false)
    }

    fetchAnalysis()
  }, [symbol, API_URL])

  // Score card component
  const ScoreCard = ({
    title,
    score,
    status,
    color
  }: {
    title: string
    score: string
    status: string
    color: 'green' | 'yellow' | 'red' | 'blue' | 'gray'
  }) => {
    const colors = {
      green: 'border-green-500 bg-green-900/20',
      yellow: 'border-yellow-500 bg-yellow-900/20',
      red: 'border-red-500 bg-red-900/20',
      blue: 'border-blue-500 bg-blue-900/20',
      gray: 'border-gray-500 bg-gray-900/20',
    }

    return (
      <div className={`p-4 rounded-lg border ${colors[color]}`}>
        <p className="text-text-secondary text-sm">{title}</p>
        <p className="text-2xl font-bold mt-1">{score}</p>
        <p className="text-sm mt-1">{status}</p>
      </div>
    )
  }

  // Explanation card
  const ExplanationCard = ({ type }: { type: keyof typeof EXPLANATIONS }) => {
    const exp = EXPLANATIONS[type]
    return (
      <div className="bg-bg-secondary/50 rounded-lg p-4 mt-4 text-sm">
        <h4 className="font-bold text-accent mb-2">Understanding {exp.title}</h4>
        <div className="space-y-2 text-text-secondary">
          <p><span className="font-semibold text-text-primary">What it measures:</span> {exp.what}</p>
          <p><span className="font-semibold text-text-primary">How it works:</span> {exp.how}</p>
          <p><span className="font-semibold text-text-primary">Important caveat:</span> {exp.caveat}</p>
        </div>
      </div>
    )
  }

  if (loading) {
    return (
      <div className="card">
        <h2 className="text-xl font-bold mb-4">Analysis</h2>
        <div className="flex items-center justify-center py-12">
          <div className="text-center">
            <div className="text-4xl mb-2 animate-pulse">🔬</div>
            <p className="text-text-secondary">Running analysis...</p>
          </div>
        </div>
      </div>
    )
  }

  // Calculate overall signal
  const getOverallSignal = () => {
    let bullishSignals = 0
    let totalSignals = 0

    if (correlation?.sentiment_vs_price_change?.correlation) {
      totalSignals++
      if (correlation.sentiment_vs_price_change.correlation > 0.2) bullishSignals++
    }
    if (granger?.significant) {
      totalSignals++
      bullishSignals++
    }
    if (spikes && spikes.success_rate_3_periods > 50) {
      totalSignals++
      bullishSignals++
    }

    if (totalSignals === 0) return { signal: 'Insufficient Data', color: 'gray' as const, emoji: '📊' }

    const ratio = bullishSignals / totalSignals
    if (ratio >= 0.7) return { signal: 'Strong Bullish Signals', color: 'green' as const, emoji: '🚀' }
    if (ratio >= 0.5) return { signal: 'Mixed Bullish Signals', color: 'yellow' as const, emoji: '📈' }
    if (ratio >= 0.3) return { signal: 'Weak/Mixed Signals', color: 'yellow' as const, emoji: '➡️' }
    return { signal: 'Bearish/No Signals', color: 'red' as const, emoji: '📉' }
  }

  const overallSignal = getOverallSignal()

  return (
    <div className="card">
      <h2 className="text-xl font-bold mb-4">AI Analysis</h2>

      {/* Tab Navigation */}
      <div className="flex gap-2 mb-6 overflow-x-auto pb-2">
        {(['overview', 'correlation', 'causality', 'spikes', 'quality'] as const).map((tab) => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors whitespace-nowrap ${
              activeTab === tab
                ? 'bg-accent text-white'
                : 'bg-bg-secondary text-text-secondary hover:text-text-primary'
            }`}
          >
            {tab === 'overview' && '📊 Overview'}
            {tab === 'correlation' && '📈 Correlation'}
            {tab === 'causality' && '🔮 Causality'}
            {tab === 'spikes' && '⚡ Spikes'}
            {tab === 'quality' && '✅ Quality'}
          </button>
        ))}
      </div>

      {/* Overview Tab */}
      {activeTab === 'overview' && (
        <div className="space-y-6">
          {/* Overall Signal */}
          <div className={`p-6 rounded-lg border-2 ${
            overallSignal.color === 'green' ? 'border-green-500 bg-green-900/10' :
            overallSignal.color === 'yellow' ? 'border-yellow-500 bg-yellow-900/10' :
            overallSignal.color === 'red' ? 'border-red-500 bg-red-900/10' :
            'border-gray-500 bg-gray-900/10'
          }`}>
            <div className="flex items-center gap-4">
              <span className="text-4xl">{overallSignal.emoji}</span>
              <div>
                <h3 className="text-xl font-bold">{overallSignal.signal}</h3>
                <p className="text-text-secondary">Based on correlation, causality, and spike analysis</p>
              </div>
            </div>
          </div>

          {/* Quick Summary Cards */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <ScoreCard
              title="Correlation"
              score={correlation?.sentiment_vs_price_change?.correlation?.toFixed(2) || 'N/A'}
              status={correlation?.sentiment_vs_price_change?.strength || 'No data'}
              color={correlation?.sentiment_vs_price_change?.significant ? 'green' : 'gray'}
            />
            <ScoreCard
              title="Causality"
              score={granger?.significant ? 'Yes' : 'No'}
              status={granger?.best_lag ? `${granger.best_lag} period lag` : 'No pattern found'}
              color={granger?.significant ? 'green' : 'gray'}
            />
            <ScoreCard
              title="Spike Success"
              score={spikes?.total_spikes ? `${spikes.success_rate_3_periods.toFixed(0)}%` : 'N/A'}
              status={`${spikes?.total_spikes || 0} spikes detected`}
              color={spikes?.success_rate_3_periods && spikes.success_rate_3_periods > 50 ? 'green' : 'gray'}
            />
            <ScoreCard
              title="Data Quality"
              score={quality?.status || 'Unknown'}
              status={`${quality?.anomaly_count || 0} anomalies found`}
              color={quality?.status === 'OK' ? 'green' : quality?.status === 'ANOMALIES_DETECTED' ? 'yellow' : 'gray'}
            />
          </div>

          {/* Shill Warning */}
          {shill?.coordinated && (
            <div className="p-4 rounded-lg border border-red-500 bg-red-900/20">
              <div className="flex items-center gap-3">
                <span className="text-2xl">⚠️</span>
                <div>
                  <h4 className="font-bold text-red-400">Potential Shill Activity Detected</h4>
                  <p className="text-sm text-text-secondary">{shill.interpretation}</p>
                </div>
              </div>
            </div>
          )}

          {/* What This Means */}
          <div className="bg-bg-secondary/50 rounded-lg p-4">
            <h4 className="font-bold mb-2">What does this mean?</h4>
            <div className="text-sm text-text-secondary space-y-2">
              <p>
                This analysis examines if social media sentiment for {symbol} has any predictive relationship with price movements.
              </p>
              <p>
                <strong>Important:</strong> These are statistical observations, not trading advice. Past patterns may not continue.
                Always do your own research and never invest more than you can afford to lose.
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Correlation Tab */}
      {activeTab === 'correlation' && (
        <div className="space-y-4">
          {correlation?.error ? (
            <p className="text-text-secondary">{correlation.error}</p>
          ) : correlation?.sentiment_vs_price_change ? (
            <>
              <div className="grid grid-cols-2 gap-4">
                <div className="p-4 bg-bg-secondary rounded-lg">
                  <p className="text-text-secondary text-sm">Correlation Coefficient</p>
                  <p className={`text-3xl font-bold ${
                    (correlation.sentiment_vs_price_change.correlation || 0) > 0 ? 'text-bullish' : 'text-bearish'
                  }`}>
                    {correlation.sentiment_vs_price_change.correlation?.toFixed(3) || 'N/A'}
                  </p>
                </div>
                <div className="p-4 bg-bg-secondary rounded-lg">
                  <p className="text-text-secondary text-sm">Statistical Significance</p>
                  <p className="text-3xl font-bold">
                    {correlation.sentiment_vs_price_change.significant ? '✓ Yes' : '✗ No'}
                  </p>
                  <p className="text-xs text-text-secondary mt-1">
                    p-value: {correlation.sentiment_vs_price_change.p_value?.toFixed(4)}
                  </p>
                </div>
              </div>

              <div className="p-4 bg-bg-secondary/50 rounded-lg">
                <h4 className="font-bold mb-2">Interpretation</h4>
                <p className="text-text-secondary">
                  {correlation.sentiment_vs_price_change.correlation && correlation.sentiment_vs_price_change.correlation > 0.3
                    ? `There's a ${correlation.sentiment_vs_price_change.strength} positive relationship between sentiment and price changes. When sentiment improves, prices tend to rise.`
                    : correlation.sentiment_vs_price_change.correlation && correlation.sentiment_vs_price_change.correlation < -0.3
                    ? `There's a ${correlation.sentiment_vs_price_change.strength} negative relationship. When sentiment drops, prices tend to rise (contrarian indicator).`
                    : 'The relationship between sentiment and price is weak or inconsistent. Sentiment alone is not a reliable indicator.'}
                </p>
                <p className="text-xs text-text-secondary mt-2">
                  Based on {correlation.data_points} data points
                </p>
              </div>
            </>
          ) : (
            <p className="text-text-secondary">No correlation data available yet. Need more price and sentiment data.</p>
          )}

          <ExplanationCard type="correlation" />
        </div>
      )}

      {/* Causality Tab */}
      {activeTab === 'causality' && (
        <div className="space-y-4">
          {granger?.error ? (
            <p className="text-text-secondary">{granger.error}</p>
          ) : granger?.significant !== undefined ? (
            <>
              <div className={`p-6 rounded-lg border-2 ${
                granger.significant ? 'border-green-500 bg-green-900/10' : 'border-gray-500 bg-gray-900/10'
              }`}>
                <div className="flex items-center gap-4">
                  <span className="text-4xl">{granger.significant ? '✓' : '✗'}</span>
                  <div>
                    <h3 className="text-xl font-bold">
                      {granger.significant ? 'Sentiment Appears to Lead Price' : 'No Causal Relationship Found'}
                    </h3>
                    <p className="text-text-secondary">
                      {granger.interpretation || 'Granger causality test completed'}
                    </p>
                  </div>
                </div>
              </div>

              {granger.significant && granger.best_lag && (
                <div className="p-4 bg-bg-secondary rounded-lg">
                  <p className="text-text-secondary text-sm">Optimal Prediction Lag</p>
                  <p className="text-2xl font-bold">{granger.best_lag} periods</p>
                  <p className="text-xs text-text-secondary mt-1">
                    Sentiment from {granger.best_lag} time periods ago best predicts current price changes
                  </p>
                </div>
              )}

              <div className="p-4 bg-bg-secondary/50 rounded-lg">
                <h4 className="font-bold mb-2">What this means</h4>
                <p className="text-text-secondary">
                  {granger.significant
                    ? `Historical sentiment data appears to help predict future price movements for ${symbol}. This suggests sentiment might be a leading indicator, though this pattern may not persist.`
                    : `Past sentiment values don't significantly improve price predictions for ${symbol}. The two may be correlated but sentiment doesn't reliably lead price.`}
                </p>
              </div>
            </>
          ) : (
            <p className="text-text-secondary">Insufficient data for Granger causality test. Need more time-series data.</p>
          )}

          <ExplanationCard type="granger" />
        </div>
      )}

      {/* Spikes Tab */}
      {activeTab === 'spikes' && (
        <div className="space-y-4">
          {spikes?.error ? (
            <p className="text-text-secondary">{spikes.error}</p>
          ) : spikes ? (
            <>
              <div className="grid grid-cols-3 gap-4">
                <div className="p-4 bg-bg-secondary rounded-lg text-center">
                  <p className="text-4xl font-bold">{spikes.total_spikes}</p>
                  <p className="text-text-secondary text-sm">Spikes Detected</p>
                </div>
                <div className="p-4 bg-bg-secondary rounded-lg text-center">
                  <p className={`text-4xl font-bold ${
                    spikes.success_rate_3_periods > 50 ? 'text-bullish' : 'text-bearish'
                  }`}>
                    {spikes.success_rate_3_periods.toFixed(0)}%
                  </p>
                  <p className="text-text-secondary text-sm">Success Rate</p>
                </div>
                <div className="p-4 bg-bg-secondary rounded-lg text-center">
                  <p className={`text-4xl font-bold ${
                    spikes.avg_price_change_after_spike > 0 ? 'text-bullish' : 'text-bearish'
                  }`}>
                    {spikes.avg_price_change_after_spike > 0 ? '+' : ''}{spikes.avg_price_change_after_spike.toFixed(1)}%
                  </p>
                  <p className="text-text-secondary text-sm">Avg Price Change</p>
                </div>
              </div>

              <div className="p-4 bg-bg-secondary/50 rounded-lg">
                <h4 className="font-bold mb-2">Analysis</h4>
                <p className="text-text-secondary">{spikes.interpretation}</p>
              </div>
            </>
          ) : (
            <p className="text-text-secondary">No spike analysis available yet.</p>
          )}

          <ExplanationCard type="spikes" />
        </div>
      )}

      {/* Quality Tab */}
      {activeTab === 'quality' && (
        <div className="space-y-4">
          {/* Data Quality Status */}
          <div className={`p-6 rounded-lg border-2 ${
            quality?.status === 'OK' ? 'border-green-500 bg-green-900/10' :
            quality?.status === 'ANOMALIES_DETECTED' ? 'border-yellow-500 bg-yellow-900/10' :
            'border-gray-500 bg-gray-900/10'
          }`}>
            <div className="flex items-center gap-4">
              <span className="text-4xl">
                {quality?.status === 'OK' ? '✓' : quality?.status === 'ANOMALIES_DETECTED' ? '⚠️' : '❓'}
              </span>
              <div>
                <h3 className="text-xl font-bold">
                  {quality?.status === 'OK' ? 'Data Quality: Good' :
                   quality?.status === 'ANOMALIES_DETECTED' ? 'Some Anomalies Detected' :
                   'Data Quality: Unknown'}
                </h3>
                <p className="text-text-secondary">
                  {quality?.total_records || 0} records checked, {quality?.anomaly_count || 0} anomalies found
                </p>
              </div>
            </div>
          </div>

          {/* Shill Detection */}
          <div className={`p-4 rounded-lg border ${
            shill?.coordinated ? 'border-red-500 bg-red-900/10' : 'border-green-500 bg-green-900/10'
          }`}>
            <h4 className="font-bold mb-2">
              {shill?.coordinated ? '⚠️ Shill Activity Warning' : '✓ No Shill Campaign Detected'}
            </h4>
            <p className="text-text-secondary text-sm">
              {shill?.interpretation || `Analyzed ${shill?.total_posts || 0} posts`}
            </p>
            {shill?.shill_rate !== undefined && shill.shill_rate > 0 && (
              <p className="text-xs text-text-secondary mt-1">
                {shill.shill_rate.toFixed(1)}% of posts flagged as promotional
              </p>
            )}
          </div>

          <ExplanationCard type="quality" />
          <ExplanationCard type="shill" />
        </div>
      )}
    </div>
  )
}
