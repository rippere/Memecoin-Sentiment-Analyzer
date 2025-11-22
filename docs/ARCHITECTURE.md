# Memecoin Sentiment Analyzer - Architecture Documentation

## System Overview

The Memecoin Sentiment Analyzer is a data pipeline that collects, analyzes, and correlates cryptocurrency price data with social media sentiment to identify predictive patterns.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           MEMECOIN SENTIMENT ANALYZER                        │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐                   │
│  │   CoinGecko  │    │    Reddit    │    │    TikTok    │   DATA SOURCES   │
│  │     API      │    │   Scraper    │    │   Scraper    │                   │
│  └──────┬───────┘    └──────┬───────┘    └──────┬───────┘                   │
│         │                   │                   │                            │
│         ▼                   ▼                   ▼                            │
│  ┌──────────────────────────────────────────────────────┐                   │
│  │              UNIFIED COLLECTOR                        │   ORCHESTRATION  │
│  │  - Price Collection (15 min)                         │                   │
│  │  - Social Collection (60 min)                        │                   │
│  │  - Quality Monitoring                                │                   │
│  │  - Bot Detection                                     │                   │
│  └──────────────────────────┬───────────────────────────┘                   │
│                             │                                                │
│                             ▼                                                │
│  ┌──────────────────────────────────────────────────────┐                   │
│  │              SENTIMENT ANALYZER                       │   PROCESSING     │
│  │  - VADER Sentiment Analysis                          │                   │
│  │  - Custom Hype Scoring                               │                   │
│  │  - Engagement Multipliers                            │                   │
│  └──────────────────────────┬───────────────────────────┘                   │
│                             │                                                │
│                             ▼                                                │
│  ┌──────────────────────────────────────────────────────┐                   │
│  │              SQLite DATABASE                          │   STORAGE        │
│  │  - Coins, Prices, Reddit Posts, TikTok Videos        │                   │
│  │  - Sentiment Scores, Correlation Results             │                   │
│  │  - Collection Logs, Events                           │                   │
│  └──────────────────────────┬───────────────────────────┘                   │
│                             │                                                │
│                             ▼                                                │
│  ┌──────────────────────────────────────────────────────┐                   │
│  │              ANALYSIS TOOLS                           │   ANALYSIS       │
│  │  - Volume Analyzer (spikes, wash trading)            │                   │
│  │  - Correlation Calculator                            │                   │
│  │  - Sentiment Validator                               │                   │
│  └──────────────────────────────────────────────────────┘                   │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Directory Structure

```
Memecoin/
├── analysis/                    # Analysis tools
│   └── volume_analyzer.py       # Volume spike & wash trading detection
│
├── collectors/                  # Data collection modules
│   ├── unified_collector.py     # Main orchestrator
│   ├── price_collector.py       # CoinGecko API integration
│   ├── reddit_collector.py      # Reddit scraping + sentiment
│   ├── tiktok_collector.py      # TikTok scraping + sentiment
│   ├── sentiment_analyzer.py    # VADER + hype scoring
│   ├── quality_monitor.py       # Data quality assessment
│   ├── bot_detector.py          # Bot account filtering
│   ├── news_collector.py        # News aggregation
│   └── influencer_tracker.py    # Influencer impact tracking
│
├── config/                      # Configuration files
│   ├── coins.yaml               # Coin definitions (35+ coins)
│   ├── coin_config.py           # Configuration loader
│   └── influencers.json         # Influencer database
│
├── database/                    # Database layer
│   ├── models.py                # SQLAlchemy ORM models
│   └── db_manager.py            # Database operations
│
├── data/                        # Data storage
│   └── memecoin.db              # SQLite database
│
├── docs/                        # Documentation
│   └── ARCHITECTURE.md          # This file
│
├── events/                      # Event tracking
│   ├── event_logger.py          # Event logging system
│   ├── log_event.py             # CLI tool
│   └── events.json              # Event storage
│
├── logs/                        # Log files
│   ├── scheduler.log            # Collection logs
│   └── scheduler_optimized.log  # Optimized scheduler logs
│
├── scrapers/                    # Web scrapers
│   ├── reddit_scraper.py        # Reddit scraping logic
│   └── tiktok_scraper.py        # TikTok scraping logic
│
├── validation/                  # Model validation
│   ├── sentiment_validator.py   # Sentiment accuracy testing
│   ├── validate_sentiment.py    # Validation CLI
│   └── labeled_data.json        # Human-labeled samples
│
├── schedule_collection.py       # Basic scheduler
├── schedule_optimized.py        # Optimized dual scheduler
├── CLAUDE.md                    # AI assistant context
├── IMPLEMENTATION_SUMMARY.md    # Implementation details
└── RESEARCH_METHODOLOGY.md      # Statistical methodology
```

---

## Data Flow

### 1. Price Data Collection

```
CoinGecko API
     │
     ▼
┌─────────────────┐
│ PriceCollector  │
│ - fetch_coin_data()
│ - Rate limiting │
│ - Error handling│
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ QualityMonitor  │
│ - Null rate     │
│ - Outlier check │
│ - Quality score │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ DatabaseManager │
│ - add_price()   │
│ - Timestamp     │
│ - Market cap    │
│ - Volume 24h    │
└─────────────────┘
```

**Data collected per coin:**
- `price_usd` - Current price in USD
- `market_cap` - Total market capitalization
- `volume_24h` - 24-hour trading volume
- `change_1h_pct` - 1-hour price change %
- `change_24h_pct` - 24-hour price change %
- `change_7d_pct` - 7-day price change %

### 2. Social Media Collection

```
Reddit/TikTok
     │
     ▼
┌─────────────────┐
│ Scraper         │
│ - Selenium      │
│ - Anti-detection│
│ - Rate limiting │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ BotDetector     │
│ - Username check│
│ - Account age   │
│ - Engagement    │
│ - Filter bots   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│SentimentAnalyzer│
│ - VADER scores  │
│ - Hype score    │
│ - Engagement    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ DatabaseManager │
│ - add_post()    │
│ - add_sentiment │
└─────────────────┘
```

**Reddit data collected:**
- Post ID, URL, title, body
- Author, subreddit, flair
- Score, comments, upvote ratio
- Sentiment scores (compound, pos, neg, neu)
- Hype score (0-100)

**TikTok data collected:**
- Video ID, URL, username, caption
- Views, likes, shares, comments
- Hashtags
- Sentiment and hype scores

### 3. Sentiment Analysis Pipeline

```
Raw Text (title + body/caption)
            │
            ▼
    ┌───────────────┐
    │ Preprocessing │
    │ - Lowercase   │
    │ - Clean text  │
    └───────┬───────┘
            │
            ▼
    ┌───────────────┐
    │ VADER Analysis│
    │ - compound    │  (-1 to +1)
    │ - positive    │  (0 to 1)
    │ - negative    │  (0 to 1)
    │ - neutral     │  (0 to 1)
    └───────┬───────┘
            │
            ▼
    ┌───────────────┐
    │ Hype Scoring  │
    │ - Keywords    │  (moon, rocket, lambo...)
    │ - Emojis      │  (🚀, 🌙, 💎...)
    │ - Exclamation │
    │ - ALL CAPS    │
    └───────┬───────┘
            │
            ▼
    ┌───────────────┐
    │ Engagement    │
    │ Multiplier    │
    │ - Upvotes     │
    │ - Comments    │
    │ - Views       │
    └───────┬───────┘
            │
            ▼
    Final Sentiment Score
    (weighted by engagement)
```

---

## Database Schema

### Entity Relationship Diagram

```
┌──────────────┐       ┌──────────────┐
│    Coins     │       │    Prices    │
├──────────────┤       ├──────────────┤
│ id (PK)      │───┐   │ id (PK)      │
│ symbol       │   │   │ coin_id (FK) │───┐
│ name         │   │   │ timestamp    │   │
│ coingecko_id │   │   │ price_usd    │   │
│ is_control   │   │   │ market_cap   │   │
│ is_failed    │   │   │ volume_24h   │   │
│ notes        │   │   │ change_*_pct │   │
└──────────────┘   │   └──────────────┘   │
                   │                       │
                   │   ┌──────────────┐   │
                   │   │ RedditPosts  │   │
                   │   ├──────────────┤   │
                   ├───│ coin_id (FK) │   │
                   │   │ post_id      │   │
                   │   │ title, body  │   │
                   │   │ score        │   │
                   │   │ sentiment    │   │
                   │   └──────────────┘   │
                   │                       │
                   │   ┌──────────────┐   │
                   │   │ TikTokVideos │   │
                   │   ├──────────────┤   │
                   ├───│ coin_id (FK) │   │
                   │   │ video_id     │   │
                   │   │ views, likes │   │
                   │   │ sentiment    │   │
                   │   └──────────────┘   │
                   │                       │
                   │   ┌──────────────┐   │
                   │   │SentimentScore│   │
                   │   ├──────────────┤   │
                   └───│ coin_id (FK) │   │
                       │ timestamp    │   │
                       │ source       │   │
                       │ sentiment_*  │   │
                       │ hype_score   │   │
                       └──────────────┘   │
                                          │
┌──────────────────────────────────────────┘
│
│   ┌──────────────┐    ┌──────────────┐
│   │Correlation   │    │CollectionLog │
│   │Results       │    ├──────────────┤
│   ├──────────────┤    │ id (PK)      │
└───│ coin_id (FK) │    │ timestamp    │
    │ lag_days     │    │ collector    │
    │ correlation  │    │ status       │
    │ p_value      │    │ records      │
    │ significant  │    │ errors       │
    └──────────────┘    └──────────────┘
```

---

## Component Reference

### UnifiedCollector

**Purpose:** Orchestrates all data collection

**Methods:**
| Method | Description |
|--------|-------------|
| `collect_all(prices, reddit, tiktok)` | Run full collection cycle |
| `get_stats()` | Get database statistics |
| `close()` | Close all connections |

**Usage:**
```python
collector = UnifiedCollector(db_path='data/memecoin.db')
result = collector.collect_all(
    collect_prices=True,
    collect_reddit=True,
    collect_tiktok=True
)
collector.close()
```

### SentimentAnalyzer

**Purpose:** Analyze text sentiment and hype

**Methods:**
| Method | Description |
|--------|-------------|
| `analyze_text(text)` | Get VADER sentiment scores |
| `calculate_hype_score(text)` | Calculate 0-100 hype score |
| `analyze_reddit_post(post)` | Full Reddit post analysis |
| `aggregate_sentiment(analyses)` | Aggregate multiple scores |

**Hype Keywords:**
`moon, rocket, lambo, pump, bullish, x100, fomo, all in, diamond hands, hodl`

**Hype Emojis:**
`🚀, 🌙, 💎, 🙌, 💰, 🔥`

### QualityMonitor

**Purpose:** Assess data quality

**Methods:**
| Method | Description |
|--------|-------------|
| `assess_collection_quality(data, type)` | Calculate quality metrics |

**Quality Thresholds:**
- Null rate: max 5%
- Duplicate rate: max 2%
- Outlier rate: max 10%

**Quality Scores:**
- EXCELLENT: 90-100
- GOOD: 75-89
- ACCEPTABLE: 50-74
- POOR: 25-49
- FAILED: 0-24

### BotDetector

**Purpose:** Filter bot accounts

**Reddit Signals:**
- Account age < 7 days
- Low karma on old accounts
- Suspicious username patterns
- Low engagement

**TikTok Signals:**
- Low follower/following ratio
- Round number metrics
- Low engagement rate

### VolumeAnalyzer

**Purpose:** Detect volume anomalies

**Methods:**
| Method | Description |
|--------|-------------|
| `detect_volume_spike(coin)` | Find unusual volume increases |
| `detect_volume_anomaly(coin)` | IQR/Z-score anomaly detection |
| `analyze_volume_price_correlation(coin)` | Correlation analysis |
| `detect_wash_trading_indicators(coin)` | Suspicious pattern detection |

---

## Configuration

### coins.yaml Structure

```yaml
# Control coins (for confound analysis)
control_coins:
  - symbol: BTC
    name: Bitcoin
    coingecko_id: bitcoin
    is_control: true

# Meme coins
coins:
  - symbol: DOGE
    name: Dogecoin
    coingecko_id: dogecoin

  # Failed coins (survivorship bias control)
  - symbol: SQUID
    name: Squid Game
    coingecko_id: squid-game
    is_failed: true
    notes: "Rug pull 2021"
```

### Scheduler Configuration

```bash
# Optimized scheduler (recommended)
python schedule_optimized.py --mode optimized \
    --price-interval 15 \
    --social-interval 60

# Basic scheduler
python schedule_collection.py --mode interval --minutes 30
```

---

## Error Handling

### Common Errors

| Error | Cause | Solution |
|-------|-------|----------|
| `DetachedInstanceError` | SQLAlchemy session closed | Use coin symbols from config, not DB objects |
| `EACCES` | Permission denied | Run with appropriate permissions |
| `Rate limit` | Too many API requests | Increase delays between requests |
| `Selenium timeout` | Page didn't load | Increase timeout, check network |

### Logging

All logs are written to `logs/` directory:
- `scheduler.log` - Basic scheduler logs
- `scheduler_optimized.log` - Optimized scheduler logs

Log levels: INFO, WARNING, ERROR

---

## Performance Considerations

### Collection Timing

| Data Type | Frequency | Duration | API Calls |
|-----------|-----------|----------|-----------|
| Prices | 15 min | ~2 sec | 1 (batch) |
| Reddit | 60 min | ~5 min | 5 subreddits |
| TikTok | 60 min | ~3 min | Per hashtag |

### Database Size Estimates

| Timeframe | Prices | Reddit | TikTok | Total Size |
|-----------|--------|--------|--------|------------|
| 1 day | 3,168 | ~1,000 | ~500 | ~5 MB |
| 30 days | 95,040 | ~30,000 | ~15,000 | ~150 MB |
| 90 days | 285,120 | ~90,000 | ~45,000 | ~450 MB |

*Based on 33 coins, 15-min price intervals, 60-min social intervals*

---

## Security Notes

1. **No API keys stored in code** - Use environment variables
2. **Rate limiting** - Respect API and website limits
3. **No credentials** - Scrapers don't require login
4. **Local storage** - All data stored locally in SQLite
