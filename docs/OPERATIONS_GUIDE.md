# Operations Guide

## Daily Operations

### Starting Data Collection

**Option 1: Optimized Scheduler (Recommended)**
```bash
cd /mnt/c/Users/rippe/OneDrive/Desktop/Memecoin
python.exe schedule_optimized.py --mode optimized
```

This runs continuously:
- Price data: Every 15 minutes
- Social media: Every 60 minutes

**Option 2: One-Time Collection**
```bash
# Prices only (fast)
python.exe schedule_optimized.py --mode once --no-social

# Social only
python.exe schedule_optimized.py --mode once --no-prices

# Everything once
python.exe schedule_optimized.py --mode once
```

**Option 3: Background Collection**
```bash
# Start in background (Linux/WSL)
nohup python.exe schedule_optimized.py --mode optimized > logs/collection.log 2>&1 &

# Check if running
ps aux | grep schedule

# Stop collection
pkill -f schedule_optimized
```

---

## Event Logging

### When to Log Events

Log these events as they happen to enable correlation analysis:

| Event Type | Examples | Impact Level |
|------------|----------|--------------|
| `exchange_listing` | Binance, Coinbase listings | 8-10 |
| `influencer_mention` | Elon Musk tweets | 7-10 |
| `news_major` | CNN, Bloomberg coverage | 6-8 |
| `regulatory` | SEC announcements | 7-9 |
| `partnership` | Brand collaborations | 5-7 |
| `technical` | Hard forks, upgrades | 4-6 |

### Logging Commands

```bash
# Exchange listing
python.exe events/log_event.py DOGE exchange_listing "Listed on Kraken" \
    --impact 8 --sentiment positive --source "Kraken Twitter"

# Influencer mention
python.exe events/log_event.py PEPE influencer_mention "Elon Musk tweet about Pepe" \
    --impact 9 --sentiment positive --source "Twitter" \
    --url "https://twitter.com/elonmusk/status/..."

# Regulatory news (affects all coins)
python.exe events/log_event.py ALL regulatory "SEC crypto framework announcement" \
    --impact 7 --sentiment negative --source "SEC.gov"

# View recent events
python.exe events/log_event.py DOGE --list

# Statistics
python.exe events/log_event.py ALL --stats
```

---

## Monitoring

### Check Database Statistics

```python
from database.db_manager import DatabaseManager

db = DatabaseManager()
stats = db.get_stats()

print(f"Total prices: {stats['prices']}")
print(f"Total Reddit posts: {stats['reddit_posts']}")
print(f"Total TikTok videos: {stats['tiktok_videos']}")
print(f"Total sentiment scores: {stats['sentiment_scores']}")

db.close()
```

### Check Collection Logs

```bash
# View recent logs
tail -100 logs/scheduler_optimized.log

# Search for errors
grep -i error logs/scheduler_optimized.log

# Count successful collections today
grep "COLLECTION CYCLE COMPLETE" logs/scheduler_optimized.log | wc -l
```

### Monitor Data Quality

Quality scores appear in logs:
- `EXCELLENT` (90+): Perfect data
- `GOOD` (75-89): Minor issues
- `ACCEPTABLE` (50-74): Some gaps
- `POOR` (25-49): Needs attention
- `FAILED` (<25): Collection broken

---

## Weekly Tasks

### 1. Validate Sentiment Model

Add 10-20 labeled samples weekly to track accuracy:

```bash
# Interactive labeling
python.exe validation/validate_sentiment.py --label

# Generate report
python.exe validation/validate_sentiment.py --report --output weekly_validation.md

# Check current accuracy
python.exe validation/validate_sentiment.py --stats
```

### 2. Review Volume Anomalies

```bash
# Check specific coins
python.exe analysis/volume_analyzer.py DOGE
python.exe analysis/volume_analyzer.py PEPE
python.exe analysis/volume_analyzer.py SHIB
```

Look for:
- Volume spikes without corresponding price moves
- Wash trading indicators
- Unusual correlations

### 3. Collect News

```bash
# Collect from RSS feeds
python.exe collectors/news_collector.py

# If you have CryptoCompare API key
python.exe collectors/news_collector.py YOUR_API_KEY
```

### 4. Database Maintenance

```python
# Check database size
import os
db_path = 'data/memecoin.db'
size_mb = os.path.getsize(db_path) / (1024 * 1024)
print(f"Database size: {size_mb:.1f} MB")

# Vacuum database (reclaim space)
import sqlite3
conn = sqlite3.connect(db_path)
conn.execute('VACUUM')
conn.close()
```

---

## Troubleshooting

### Collection Not Running

1. **Check if process is running:**
   ```bash
   ps aux | grep python
   ```

2. **Check logs for errors:**
   ```bash
   tail -50 logs/scheduler_optimized.log
   ```

3. **Test manual collection:**
   ```bash
   python.exe schedule_optimized.py --mode once --no-social
   ```

### No Data for Some Coins

Some coins may not have CoinGecko data:
- Check `coingecko_id` in `config/coins.yaml`
- Verify coin exists on CoinGecko
- Some failed coins (SQUID, TITAN) may have no data

### High Error Rate

1. **Network issues:** Check internet connection
2. **Rate limiting:** Increase delays in scraper config
3. **Website changes:** Scrapers may need updates
4. **Bot detection:** Reduce collection frequency

### Database Errors

```bash
# Backup database
cp data/memecoin.db data/memecoin_backup.db

# Reset database (loses all data!)
rm data/memecoin.db
python.exe schedule_optimized.py --mode once --no-social
```

---

## Adding New Coins

### 1. Edit coins.yaml

```yaml
coins:
  # Add new coin
  - symbol: NEWCOIN
    name: New Coin Name
    coingecko_id: new-coin-id  # From CoinGecko URL
```

### 2. Restart Collection

The database will auto-initialize new coins on next run:

```bash
python.exe schedule_optimized.py --mode once --no-social
```

### 3. Verify

```python
from config.coin_config import get_coin_config
config = get_coin_config()
print(config.get_coin_symbols())  # Should include NEWCOIN
```

---

## Backup Strategy

### Daily Backup

```bash
# Create timestamped backup
cp data/memecoin.db "backups/memecoin_$(date +%Y%m%d).db"
```

### Export to CSV

```python
import sqlite3
import pandas as pd

conn = sqlite3.connect('data/memecoin.db')

# Export prices
prices_df = pd.read_sql('SELECT * FROM prices', conn)
prices_df.to_csv('exports/prices.csv', index=False)

# Export sentiment
sentiment_df = pd.read_sql('SELECT * FROM sentiment_scores', conn)
sentiment_df.to_csv('exports/sentiment.csv', index=False)

conn.close()
```

---

## Performance Tips

### Reduce Collection Time

1. **Skip TikTok** (slowest):
   ```bash
   python.exe schedule_collection.py --no-tiktok
   ```

2. **Reduce coins:** Edit `coins.yaml` to track fewer coins

3. **Increase intervals:**
   ```bash
   python.exe schedule_optimized.py --price-interval 30 --social-interval 120
   ```

### Reduce Database Size

1. **Delete old data:**
   ```sql
   DELETE FROM prices WHERE timestamp < date('now', '-90 days');
   DELETE FROM reddit_posts WHERE created_utc < date('now', '-90 days');
   ```

2. **Vacuum after deletion:**
   ```sql
   VACUUM;
   ```

---

## Checklist

### Before Going Live
- [ ] Test price collection works
- [ ] Verify coin list is correct
- [ ] Set up log monitoring
- [ ] Create backup schedule
- [ ] Document any API keys used

### Daily
- [ ] Check collection is running
- [ ] Review error logs
- [ ] Log any major events

### Weekly
- [ ] Label sentiment samples (10-20)
- [ ] Review data quality scores
- [ ] Check volume anomalies
- [ ] Backup database
