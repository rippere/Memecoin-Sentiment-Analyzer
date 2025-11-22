# Memecoin Data Pipeline - Quick Start Guide

## What You Just Got

A complete, production-ready data collection pipeline that:
- ✅ Collects price data from CoinGecko API
- ✅ Scrapes Reddit posts with sentiment analysis
- ✅ Scrapes TikTok videos with hype scoring
- ✅ Stores everything in SQLite database
- ✅ Calculates aggregated sentiment metrics
- ✅ Runs on automated schedule
- ✅ Logs all operations

## Installation

### 1. Install All Dependencies

```bash
cd "/mnt/c/Users/rippe/OneDrive/Desktop/Memecoin"

# Install base requirements
pip install -r requirements.txt

# Install scraper requirements
pip install -r requirements_scrapers.txt

# Install scheduler
pip install apscheduler
```

### 2. Create Logs Directory

```bash
mkdir -p logs
```

## Usage

### Option 1: Run Immediate Collection (Test)

Collect data once to test the pipeline:

```bash
# Collect everything
python collectors/unified_collector.py

# Collect only prices (fast)
python collectors/unified_collector.py --no-reddit --no-tiktok

# Collect with visible browser (for debugging)
python collectors/unified_collector.py --headless=False
```

### Option 2: Run on Schedule

#### Every 30 Minutes (Recommended for Active Data Collection)

```bash
python schedule_collection.py --mode interval --minutes 30
```

#### Every Hour

```bash
python schedule_collection.py --mode interval --minutes 60
```

#### Specific Times (Cron-style)

```bash
# Every hour at minute 0 (e.g., 1:00, 2:00, 3:00...)
python schedule_collection.py --mode cron --hour "*" --minute "0"

# Specific hours (9 AM, 12 PM, 3 PM, 6 PM, 9 PM)
python schedule_collection.py --mode cron --hour "9,12,15,18,21" --minute "0"

# Every 4 hours
python schedule_collection.py --mode cron --hour "*/4" --minute "0"
```

#### Run Once Now

```bash
python schedule_collection.py --mode once
```

### Option 3: Custom Collection

Collect specific data sources:

```bash
# Only prices (fastest, no scraping)
python schedule_collection.py --mode interval --minutes 15 --no-reddit --no-tiktok

# Only social media (prices update less frequently)
python schedule_collection.py --mode interval --minutes 60 --no-prices

# Just Reddit (TikTok can be slow)
python schedule_collection.py --mode interval --minutes 30 --no-prices --no-tiktok
```

## Database Location

Data is stored in: `data/memecoin.db`

This SQLite database contains:
- `coins` - Tracked cryptocurrencies
- `prices` - Historical price data
- `reddit_posts` - Reddit posts with metadata
- `tiktok_videos` - TikTok videos with metadata
- `sentiment_scores` - Aggregated sentiment metrics
- `collection_logs` - Operation logs

## Checking Your Data

### Quick Stats

```python
from database.db_manager import get_db

db = get_db()
stats = db.get_stats()

for key, value in stats.items():
    print(f"{key}: {value}")
```

### Query Latest Prices

```python
from database.db_manager import get_db

db = get_db()
price = db.get_latest_price('DOGE')
print(f"DOGE: ${price.price_usd}")
```

### Query Reddit Sentiment

```python
from database.db_manager import get_db

db = get_db()
posts = db.get_reddit_posts_timeframe('DOGE', hours=24)
print(f"Found {len(posts)} DOGE posts in last 24h")
```

## Monitoring

### Log Files

- `logs/scheduler.log` - Scheduled collection runs
- Console output - Real-time collection status

### What to Watch For

**Good signs:**
- ✅ "COLLECTION CYCLE COMPLETE"
- ✅ "Collected X prices/posts/videos"
- ✅ "status: success"

**Issues to investigate:**
- ⚠️ "status: partial" - Some data collected, some failed
- ❌ "status: failed" - Complete failure
- ⚠️ Views returning 0 on TikTok - HTML structure may have changed

## Recommended Schedules

### For Active Trading Signals
- **Prices**: Every 15 minutes
- **Social Media**: Every 30-60 minutes

```bash
# Run two separate schedulers (in different terminals)
python schedule_collection.py --mode interval --minutes 15 --no-reddit --no-tiktok
python schedule_collection.py --mode interval --minutes 45 --no-prices
```

### For Research/Academic Use
- **Everything**: Every 1-2 hours

```bash
python schedule_collection.py --mode interval --minutes 60
```

### For Historical Data Building
- **Everything**: Every 4-6 hours (reduces scraper load)

```bash
python schedule_collection.py --mode cron --hour "*/4" --minute "0"
```

## Next Steps

### Week 1: Data Collection
Let the system run for 7-30 days to build historical data.

### Week 2-3: Analysis
Once you have data, use the backtest analyzer to find correlations:

```bash
python backtest_analyzer.py
```

(Note: This will need minor updates to work with the new database)

### Week 4+: Dashboard
Build a Streamlit dashboard to visualize:
- Real-time sentiment trends
- Price correlations
- Alert triggers

## Troubleshooting

### "Module not found" errors
```bash
pip install -r requirements_scrapers.txt
```

### TikTok returns no videos
- TikTok may have changed HTML structure
- Set `--headless=False` to see what's happening
- Check `test_scrapers.py` with visible browser

### Reddit returns no posts
- Check if subreddit names are correct
- Verify old.reddit.com is accessible

### Scrapers are too slow
- Reduce `max_posts` and `max_videos` in collectors
- Run Reddit and TikTok on separate schedules
- Increase `min_delay` to be more polite

### Database is locked
- Only one collector should run at a time
- Check for hung processes: `ps aux | grep python`

## Cloud Deployment Notes

When moving to cloud (AWS/GCP/Azure):

1. **Use Headless Mode**: Always set `headless=True`
2. **Install Chrome**: Scrapers need Chrome browser
3. **Set up ChromeDriver**: Use `webdriver-manager` or install manually
4. **Use Screen/Tmux**: Keep scheduler running after disconnect
5. **Database Backup**: Regular backups of `data/memecoin.db`
6. **Consider PostgreSQL**: For production, migrate from SQLite

Example cloud startup:
```bash
# In tmux/screen session
nohup python schedule_collection.py --mode interval --minutes 30 > logs/collection.log 2>&1 &
```

## Data Export

Export data for external analysis:

```python
from database.db_manager import get_db
import pandas as pd

db = get_db()

# Export prices
with db.get_session() as session:
    prices = session.query(Price).all()
    df = pd.DataFrame([{
        'symbol': p.coin.symbol,
        'timestamp': p.timestamp,
        'price_usd': p.price_usd,
        'change_24h_pct': p.change_24h_pct
    } for p in prices])
    df.to_csv('exports/prices.csv', index=False)
```

## Performance Tips

- **Start small**: Test with 1-2 coins before scaling to all 6
- **Adjust delays**: Increase if getting blocked, decrease if too slow
- **Monitor rate limits**: CoinGecko has limits even on free tier
- **Database maintenance**: SQLite works well up to ~1M records

## Support

If you encounter issues:
1. Check logs in `logs/` directory
2. Run with `--headless=False` to see browser behavior
3. Test individual components (price_collector, reddit_scraper, etc.)
4. Review CLAUDE.md for architecture details

---

**You're now collecting data 24/7!** 🚀

The system will quietly build your dataset while you sleep. Check back in a week to see your historical data grow.
