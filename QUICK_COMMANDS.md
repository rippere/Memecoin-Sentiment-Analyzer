# Memecoin Sentiment Analyzer - Quick Commands

## Monitor Active Collection

```bash
# View live logs
tail -f logs/collection_session.log

# Check if scheduler is running
ps aux | grep schedule_optimized.py | grep -v grep

# View recent database stats
source venv/bin/activate && python3 -c "from database.db_manager import DatabaseManager; db = DatabaseManager(); print(db.get_stats())"
```

## Control the Scheduler

```bash
# Stop data collection
pkill -f schedule_optimized.py

# Start optimized scheduler (recommended)
source venv/bin/activate && nohup python schedule_optimized.py --mode optimized --price-interval 15 --social-interval 60 > logs/collection_session.log 2>&1 &

# Run one-time collection (test)
source venv/bin/activate && python schedule_optimized.py --mode once

# Run only price collection (fast)
source venv/bin/activate && python schedule_optimized.py --mode once --no-social
```

## Check Data

```bash
# Query recent prices
source venv/bin/activate && python3 -c "
import sqlite3
conn = sqlite3.connect('data/memecoin.db')
cursor = conn.cursor()
cursor.execute('SELECT c.symbol, p.price_usd, p.change_24h_pct, datetime(p.timestamp) FROM coins c JOIN prices p ON c.id = p.coin_id ORDER BY p.timestamp DESC LIMIT 10')
for row in cursor.fetchall():
    print(f'{row[0]:8} ${row[1]:12.8f} {row[2]:+6.2f}% {row[3]}')
conn.close()
"

# Count recent Reddit posts
source venv/bin/activate && python3 -c "
import sqlite3
conn = sqlite3.connect('data/memecoin.db')
cursor = conn.cursor()
cursor.execute('SELECT COUNT(*) FROM reddit_posts WHERE created_utc > datetime(\"now\", \"-24 hours\")')
print(f'Reddit posts in last 24h: {cursor.fetchone()[0]}')
conn.close()
"
```

## Logs

```bash
# View all log files
ls -lh logs/

# View recent scheduler activity
tail -100 logs/collection_session.log

# Search for errors
grep -i error logs/collection_session.log | tail -20
```

## Database

```bash
# Backup database
cp data/memecoin.db data/memecoin_backup_$(date +%Y%m%d_%H%M%S).db

# Check database size
du -h data/memecoin.db

# Open database with SQLite
sqlite3 data/memecoin.db
```

## Troubleshooting

```bash
# Check Python environment
source venv/bin/activate && pip list | grep -E "(requests|pandas|selenium|tweepy|apscheduler)"

# Test price collector only
source venv/bin/activate && python collectors/price_collector.py

# Test Reddit collector (visible browser)
source venv/bin/activate && python3 -c "from collectors.reddit_collector import RedditCollector; rc = RedditCollector({'headless': False}); posts = rc.collect_coin_data('DOGE', max_posts=5); print(f'Collected {len(posts)} posts')"

# Check for stuck processes
ps aux | grep python
```

## Current Status

Scheduler Running: YES (PID 1323)
Schedule:
- Prices every 15 minutes
- Social media every 60 minutes

Next Runs:
- Price: Every :00, :15, :30, :45 of each hour
- Social: Every hour at :44

## File Locations

- Database: `data/memecoin.db`
- Logs: `logs/collection_session.log`
- Config: `.env`, `config/coins.yaml`
- Main Scheduler: `schedule_optimized.py`
