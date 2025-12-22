# Trending Coins Rotation System

## Overview

The Memecoin Sentiment Analyzer now uses a **dynamic trending coin rotation system** instead of tracking a static list of coins. This allows the system to automatically discover and track the hottest coins as they emerge and trend across market cycles.

## How It Works

### 1. Trending Detection

The system fetches trending coins from multiple sources:

- **CoinGecko Trending API**: Official trending coins list
- **Top Gainers**: Coins with highest 24h price gains (>5%)
- Combined and deduplicated for comprehensive coverage

### 2. Coin Lifecycle

Coins move through different states:

```
New Trending Coin
    ↓
[Active Tracking] ← Trending, collecting data
    ↓
[Archived] ← No longer trending, historical data preserved
```

**States:**
- `active` - Currently trending, being tracked
- `archived` - Was trending, now inactive (data preserved)
- `control` - Always tracked (BTC, ETH for comparison)

### 3. Database Schema

**Coins Table:**
- `is_trending` - Boolean flag for current trending status
- `trending_since` - When coin entered trending rotation
- `trending_rank` - Current rank (1-50)
- `last_trending_check` - Last trending update timestamp
- `status` - Coin lifecycle status

**Trending History Table:**
- Tracks all trending events (entered, exited, rank_change)
- Preserves price/volume metrics at time of event
- Useful for analyzing trending patterns

## Usage

### Update Trending Coins

Run this periodically (recommended: every 6-12 hours):

```bash
python update_trending.py
```

This will:
1. Fetch latest trending coins from CoinGecko
2. Add new trending coins to tracking
3. Archive coins that are no longer trending
4. Update trending ranks

### Manual Test

Test the trending tracker:

```bash
python collectors/trending_tracker.py
```

### View Active Coins

```python
from database.db_manager import DatabaseManager
from collectors.trending_tracker import TrendingTracker

db = DatabaseManager()
tracker = TrendingTracker()

# Get all active (trending) coins
active_coins = tracker.get_active_coins(db)

for coin in active_coins:
    print(f"#{coin['trending_rank']} {coin['symbol']} - {coin['name']}")
```

### GitHub Actions Integration

The system automatically updates trending coins via scheduled workflows:

- `update-trending.yml` - Runs every 12 hours
- Commits new coins to repository
- Archived coins remain in database with historical data

## Configuration

### Max Trending Coins

Default: 50 coins
Adjust in `TrendingTracker` initialization:

```python
tracker = TrendingTracker(max_trending_coins=100)
```

### Update Frequency

Recommended schedules:

- **Bull market**: Every 6 hours (fast rotation)
- **Bear market**: Every 12-24 hours (slower rotation)
- **During volatility**: Every 3-6 hours

## Data Collection

The data collection system automatically uses trending coins:

```python
from collectors.trending_tracker import TrendingTracker

tracker = TrendingTracker()
active_coins = tracker.get_active_coins(db)

# Collect data for trending coins
for coin in active_coins:
    collect_price(coin['coingecko_id'])
    collect_sentiment(coin['symbol'])
```

## Benefits

### 1. Automatic Discovery
- No manual coin list maintenance
- Catches new memecoins as they trend
- Misses no opportunities

### 2. Historical Preservation
- Archived coins retain all historical data
- Can analyze entire lifecycle (pre-trend → trending → post-trend)
- Perfect for backtesting strategies

### 3. Efficient Resource Use
- Focus collection on active coins
- Archive inactive coins
- Optimal API usage

### 4. Cycle Analysis
- Track coins across multiple trending cycles
- Identify recurring patterns
- Study memecoin seasonality

## API Limits

**CoinGecko Free Tier:**
- 10-30 calls/minute
- Trending endpoint: ~1 call
- Market data: ~1 call

**Recommended:**
- Update trending every 6-12 hours
- Respect rate limits
- Cache results

## Example Workflow

### Initial Setup

```bash
# 1. Migrate database (add trending columns)
python migrate_trending.py

# 2. Fetch initial trending coins
python update_trending.py
```

### Daily Operations

```bash
# Morning: Update trending coins
python update_trending.py

# Continuous: Collect data for active coins
python schedule_optimized.py  # Uses trending coins automatically
```

### Analysis

```python
# Find coins that were trending multiple times
from database.models import TrendingHistory

# Get coins with multiple trending cycles
SELECT coin_id, COUNT(DISTINCT DATE(timestamp)) as trending_days
FROM trending_history
WHERE event_type = 'entered'
GROUP BY coin_id
HAVING trending_days > 1
ORDER BY trending_days DESC;
```

## Trending Criteria

A coin enters trending rotation if:

1. **CoinGecko Trending**: Listed in top trending
2. **OR High Gains**: >5% gain in 24h
3. **AND**: Rank <= 50 (configurable)

A coin exits trending if:

- Not in trending API results
- AND not in top gainers
- AND last check was < 24 hours ago

## Monitoring

Check trending update logs:

```bash
tail -f logs/trending_updates.log
```

View trending history:

```sql
SELECT c.symbol, th.event_type, th.trending_rank, th.timestamp
FROM trending_history th
JOIN coins c ON th.coin_id = c.id
ORDER BY th.timestamp DESC
LIMIT 20;
```

## Future Enhancements

Planned features:

- [ ] Social media trending integration (Twitter, Reddit)
- [ ] Volume spike detection
- [ ] Whale wallet activity tracking
- [ ] Influencer mention tracking
- [ ] Multi-source trending scores
- [ ] Predictive trending (before CoinGecko lists)

## Troubleshooting

### No Trending Coins Found

**Cause**: API rate limit or network error
**Solution**: Wait 1-2 minutes, retry

### Coins Not Archiving

**Cause**: `last_trending_check` not updating
**Solution**: Run `python update_trending.py` manually

### Too Many Active Coins

**Cause**: High trending threshold
**Solution**: Reduce `max_trending_coins` parameter

## API Reference

### TrendingTracker Methods

```python
fetch_trending_coins() -> List[Dict]
# Fetch from CoinGecko trending API

fetch_top_gainers(limit=30) -> List[Dict]
# Fetch top gaining coins

update_trending_coins(db_manager) -> Dict[str, int]
# Update database with latest trending

get_active_coins(db_manager, include_control=True) -> List[Dict]
# Get list of active coins for data collection
```

---

**Last Updated**: 2025-12-22
**Status**: ✅ Production Ready
