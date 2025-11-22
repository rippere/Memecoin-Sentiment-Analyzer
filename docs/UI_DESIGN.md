# Memecoin Sentiment Dashboard - UI Design

## Overview

A real-time dashboard for visualizing cryptocurrency sentiment analysis, price correlations, and social media trends.

---

## Tech Stack Recommendation

### Frontend
| Technology | Purpose | Why |
|------------|---------|-----|
| **Next.js 14** | Framework | SSR, API routes, great DX |
| **TypeScript** | Type safety | Fewer bugs, better tooling |
| **Tailwind CSS** | Styling | Rapid development, consistent design |
| **shadcn/ui** | Components | Beautiful, accessible, customizable |
| **Recharts** | Charts | React-native, responsive, customizable |
| **TanStack Query** | Data fetching | Caching, real-time updates |

### Backend API
| Technology | Purpose | Why |
|------------|---------|-----|
| **FastAPI** | API server | Python, async, auto-docs |
| **SQLAlchemy** | ORM | Already using it |
| **Redis** | Caching | Fast real-time data |

### Deployment
| Service | Purpose |
|---------|---------|
| **Vercel** | Frontend hosting |
| **Railway/Render** | Backend API |
| **SQLite → PostgreSQL** | Production database |

---

## Page Structure

```
/                       → Dashboard (main overview)
/coins                  → All coins list
/coins/[symbol]         → Individual coin detail
/sentiment              → Sentiment analysis view
/correlations           → Correlation explorer
/events                 → Event timeline
/settings               → Configuration
```

---

## Dashboard Layout

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  HEADER                                                                      │
│  ┌──────────────────┐  ┌─────────────────────────────────────────┐          │
│  │ 🪙 MemeTracker   │  │ 🔍 Search coins...                      │  ⚙️ 👤   │
│  └──────────────────┘  └─────────────────────────────────────────┘          │
├─────────────────────────────────────────────────────────────────────────────┤
│  NAVIGATION                                                                  │
│  [Dashboard] [Coins] [Sentiment] [Correlations] [Events]                    │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  STATS ROW                                                                   │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐        │
│  │ 📊 Coins     │ │ 📈 Avg Sent. │ │ 🔥 Hype Index│ │ ⚠️ Alerts    │        │
│  │    35        │ │   +0.24      │ │    67/100    │ │    3         │        │
│  │ Tracking     │ │ Bullish      │ │ Elevated     │ │ New spikes   │        │
│  └──────────────┘ └──────────────┘ └──────────────┘ └──────────────┘        │
│                                                                              │
│  MAIN CONTENT                                                                │
│  ┌────────────────────────────────────────┐ ┌─────────────────────────────┐ │
│  │ SENTIMENT HEATMAP                       │ │ TOP MOVERS                  │ │
│  │                                         │ │                             │ │
│  │  DOGE  ████████████  +0.45             │ │ 🚀 PEPE    +24.5%          │ │
│  │  SHIB  ██████████    +0.32             │ │ 🚀 FLOKI   +18.2%          │ │
│  │  PEPE  ████████████████  +0.67         │ │ 📉 DOGE    -5.3%           │ │
│  │  FLOKI ███████       +0.21             │ │ 📉 SHIB    -3.1%           │ │
│  │  WIF   █████████████  +0.52            │ │                             │ │
│  │                                         │ │ Based on 24h price change   │ │
│  └────────────────────────────────────────┘ └─────────────────────────────┘ │
│                                                                              │
│  ┌────────────────────────────────────────────────────────────────────────┐ │
│  │ PRICE VS SENTIMENT CHART                                                │ │
│  │                                                                          │ │
│  │     ^                                              ___                   │ │
│  │     │                              ___-------‾‾‾‾‾                       │ │
│  │     │                    ___---‾‾‾‾                                      │ │
│  │     │           ___---‾‾‾                                                │ │
│  │     │    ___--‾‾                                                         │ │
│  │     │___/                                                                │ │
│  │     └──────────────────────────────────────────────────────────────→    │ │
│  │       1h    4h    12h    1d    3d    7d    [DOGE ▼] [Price/Sentiment]   │ │
│  └────────────────────────────────────────────────────────────────────────┘ │
│                                                                              │
│  ┌──────────────────────────────────┐ ┌───────────────────────────────────┐ │
│  │ RECENT EVENTS                    │ │ SOCIAL ACTIVITY                   │ │
│  │                                  │ │                                   │ │
│  │ 🏦 DOGE listed on Kraken        │ │ Reddit: 1,234 posts (↑12%)       │ │
│  │    2 hours ago • Impact: 8/10   │ │ TikTok: 456 videos (↑8%)         │ │
│  │                                  │ │                                   │ │
│  │ 🐦 Elon mentioned PEPE          │ │ Most discussed:                   │ │
│  │    5 hours ago • Impact: 9/10   │ │ #1 PEPE  #2 DOGE  #3 SHIB        │ │
│  │                                  │ │                                   │ │
│  │ [View All Events →]             │ │ [View Details →]                  │ │
│  └──────────────────────────────────┘ └───────────────────────────────────┘ │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Individual Coin Page

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  ← Back to Dashboard                                                         │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  COIN HEADER                                                                 │
│  ┌────────┐                                                                  │
│  │  🐕    │  DOGECOIN (DOGE)                                                │
│  │        │  $0.0842  ↑ +5.2% (24h)                                         │
│  └────────┘  Market Cap: $11.2B  •  Volume: $892M                           │
│                                                                              │
│  TABS: [Overview] [Sentiment] [Correlations] [Events] [Raw Data]            │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  SENTIMENT SUMMARY                                                           │
│  ┌────────────────┐ ┌────────────────┐ ┌────────────────┐                   │
│  │ Overall Score  │ │ Hype Level     │ │ Social Volume  │                   │
│  │   +0.42        │ │   72/100       │ │   2,341        │                   │
│  │   Bullish 📈   │ │   High 🔥      │ │   posts/day    │                   │
│  └────────────────┘ └────────────────┘ └────────────────┘                   │
│                                                                              │
│  PRICE & SENTIMENT CHART                                                     │
│  ┌────────────────────────────────────────────────────────────────────────┐ │
│  │                                                                          │ │
│  │  Price ─────   Sentiment ─ ─ ─                                          │ │
│  │                                                                          │ │
│  │      ^                                                                   │ │
│  │      │     ╱╲      ╱‾‾╲                                                 │ │
│  │      │    ╱  ╲    ╱    ╲    ╱‾‾                                         │ │
│  │      │___╱    ╲__╱      ╲__╱                                             │ │
│  │      └────────────────────────────────────────────→                     │ │
│  │                                                                          │ │
│  │  [1H] [4H] [1D] [1W] [1M] [ALL]                                         │ │
│  └────────────────────────────────────────────────────────────────────────┘ │
│                                                                              │
│  CORRELATION ANALYSIS                                                        │
│  ┌────────────────────────────────────────────────────────────────────────┐ │
│  │                                                                          │ │
│  │  Sentiment → Price Correlation: 0.34 (moderate, p < 0.05) ✓            │ │
│  │  Optimal Lag: 4 hours (sentiment leads price)                           │ │
│  │                                                                          │ │
│  │  [Scatter Plot]                    [Lag Analysis Chart]                 │ │
│  │      •  •                              ┌─────────────┐                   │ │
│  │    •   • •                             │    ╱╲       │                   │ │
│  │   •  •  •  •                           │   ╱  ╲      │                   │ │
│  │    •  • •                              │__╱    ╲___  │                   │ │
│  │      •                                 └─────────────┘                   │ │
│  │                                         0h  12h  24h  48h                │ │
│  └────────────────────────────────────────────────────────────────────────┘ │
│                                                                              │
│  RECENT SOCIAL POSTS                                                         │
│  ┌────────────────────────────────────────────────────────────────────────┐ │
│  │ Reddit • r/dogecoin • 2h ago                              Sentiment: +  │ │
│  │ "DOGE to the moon! 🚀 Just bought another 10k"                          │ │
│  │ ↑ 234  💬 45                                                            │ │
│  ├────────────────────────────────────────────────────────────────────────┤ │
│  │ TikTok • @cryptoguy • 4h ago                              Sentiment: +  │ │
│  │ "Why Dogecoin will 10x this year..."                                    │ │
│  │ 👁 12.4K  ❤️ 892                                                        │ │
│  └────────────────────────────────────────────────────────────────────────┘ │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Component Library

### Cards

```tsx
// StatsCard - For key metrics
<StatsCard
  title="Average Sentiment"
  value="+0.42"
  subtitle="Bullish"
  icon={<TrendingUp />}
  trend={{ value: 12, direction: 'up' }}
/>

// CoinCard - For coin listings
<CoinCard
  symbol="DOGE"
  name="Dogecoin"
  price={0.0842}
  change24h={5.2}
  sentiment={0.42}
  hypeScore={72}
/>
```

### Charts

```tsx
// Price/Sentiment dual-axis chart
<PriceSentimentChart
  data={chartData}
  timeRange="7d"
  showPrice={true}
  showSentiment={true}
/>

// Sentiment heatmap
<SentimentHeatmap
  coins={coinData}
  metric="sentiment" // or "hype", "volume"
/>

// Correlation scatter plot
<CorrelationScatter
  xData={sentimentScores}
  yData={priceChanges}
  correlation={0.34}
  pValue={0.02}
/>
```

### Tables

```tsx
// Sortable coin table
<CoinTable
  data={coins}
  columns={['symbol', 'price', 'change24h', 'sentiment', 'hype']}
  sortable={true}
  onRowClick={(coin) => router.push(`/coins/${coin.symbol}`)}
/>
```

---

## Color Scheme

### Sentiment Colors
```css
--sentiment-very-positive: #22c55e;  /* Green 500 */
--sentiment-positive: #86efac;       /* Green 300 */
--sentiment-neutral: #94a3b8;        /* Slate 400 */
--sentiment-negative: #fca5a5;       /* Red 300 */
--sentiment-very-negative: #ef4444;  /* Red 500 */
```

### Theme
```css
/* Dark Mode (Primary) */
--bg-primary: #0f172a;    /* Slate 900 */
--bg-secondary: #1e293b;  /* Slate 800 */
--bg-card: #334155;       /* Slate 700 */
--text-primary: #f8fafc;  /* Slate 50 */
--text-secondary: #94a3b8; /* Slate 400 */
--accent: #3b82f6;        /* Blue 500 */

/* Light Mode */
--bg-primary: #ffffff;
--bg-secondary: #f8fafc;
--bg-card: #ffffff;
--text-primary: #0f172a;
--text-secondary: #64748b;
--accent: #2563eb;
```

---

## API Endpoints

### REST API Structure

```
GET  /api/coins                    → List all coins
GET  /api/coins/:symbol            → Coin details
GET  /api/coins/:symbol/prices     → Price history
GET  /api/coins/:symbol/sentiment  → Sentiment history
GET  /api/coins/:symbol/correlation → Correlation analysis

GET  /api/sentiment/overview       → Overall sentiment metrics
GET  /api/sentiment/heatmap        → Heatmap data

GET  /api/events                   → Event list
POST /api/events                   → Create event

GET  /api/stats                    → Dashboard statistics
```

### Response Examples

```json
// GET /api/coins/DOGE
{
  "symbol": "DOGE",
  "name": "Dogecoin",
  "price": 0.0842,
  "change_24h": 5.2,
  "market_cap": 11200000000,
  "volume_24h": 892000000,
  "sentiment": {
    "score": 0.42,
    "hype": 72,
    "post_count": 2341,
    "trend": "bullish"
  },
  "correlation": {
    "value": 0.34,
    "p_value": 0.02,
    "significant": true,
    "optimal_lag_hours": 4
  }
}
```

---

## Responsive Design

### Breakpoints
```css
sm: 640px   /* Mobile landscape */
md: 768px   /* Tablet */
lg: 1024px  /* Desktop */
xl: 1280px  /* Large desktop */
```

### Mobile Layout
- Single column layout
- Collapsible navigation (hamburger menu)
- Swipeable charts
- Bottom navigation bar
- Cards stack vertically

---

## Real-Time Features

### WebSocket Events
```typescript
// Subscribe to real-time updates
socket.on('price_update', (data) => {
  // Update price display
});

socket.on('sentiment_update', (data) => {
  // Update sentiment indicators
});

socket.on('event_created', (data) => {
  // Show notification
});
```

### Polling Fallback
- Price data: Poll every 60 seconds
- Sentiment: Poll every 5 minutes
- Events: Poll every minute

---

## User Features

### Watchlist
- Save favorite coins
- Custom alerts
- Email notifications

### Export
- Download CSV data
- Generate PDF reports
- Share charts as images

---

## File Structure

```
frontend/
├── app/
│   ├── layout.tsx
│   ├── page.tsx              # Dashboard
│   ├── coins/
│   │   ├── page.tsx          # Coins list
│   │   └── [symbol]/
│   │       └── page.tsx      # Coin detail
│   ├── sentiment/
│   │   └── page.tsx
│   ├── correlations/
│   │   └── page.tsx
│   └── events/
│       └── page.tsx
├── components/
│   ├── ui/                   # shadcn components
│   ├── charts/
│   │   ├── PriceSentimentChart.tsx
│   │   ├── SentimentHeatmap.tsx
│   │   └── CorrelationScatter.tsx
│   ├── cards/
│   │   ├── StatsCard.tsx
│   │   └── CoinCard.tsx
│   └── layout/
│       ├── Header.tsx
│       ├── Sidebar.tsx
│       └── Footer.tsx
├── lib/
│   ├── api.ts                # API client
│   ├── utils.ts
│   └── types.ts
├── hooks/
│   ├── useCoins.ts
│   ├── useSentiment.ts
│   └── useRealtime.ts
└── styles/
    └── globals.css
```

---

## Next Steps

1. **Set up Next.js project**
   ```bash
   npx create-next-app@latest frontend --typescript --tailwind --app
   cd frontend
   npx shadcn-ui@latest init
   ```

2. **Install dependencies**
   ```bash
   npm install recharts @tanstack/react-query axios date-fns
   ```

3. **Create FastAPI backend**
   ```bash
   pip install fastapi uvicorn
   ```

4. **Implement core components**
   - Dashboard layout
   - Price/Sentiment chart
   - Coin cards
   - API integration

5. **Add real-time updates**
   - WebSocket connection
   - Auto-refresh

6. **Deploy**
   - Frontend → Vercel
   - Backend → Railway
   - Database → PostgreSQL
