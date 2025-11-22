# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Meme Coin Sentiment Analyzer** - A Python-based data science project that analyzes correlations between social media hype and cryptocurrency price movements for meme coins (DOGE, PEPE, SHIB, BONK, FLOKI, WIF).

This is an educational project progressing through phases:
- Phase 1: Price data collection via CoinGecko API
- Phase 2: Social media data scraping (TikTok, Reddit, Twitter)
- Phase 3: Sentiment analysis and correlation detection
- Phase 4: Backtesting and visualization

## Development Commands

### Installation
```bash
# Install base dependencies (price tracking)
pip install -r requirements.txt

# Install scraper dependencies (social media collection)
pip install -r requirements_scrapers.txt
```

### Running Scripts
```bash
# Collect live meme coin price data
python meme_coin_tracker.py

# Test social media scrapers
python test_scrapers.py

# Collect Twitter data (requires Twitter API credentials in .env)
python twitter_hype_collector.py

# Run backtest analysis (requires historical data)
python backtest_analyzer.py
```

### Testing Individual Scrapers
```python
# Test TikTok scraper
from scrapers.tiktok_scraper import TikTokScraper
config = {'headless': False, 'min_delay': 2, 'max_delay': 4}
with TikTokScraper(config) as scraper:
    videos = scraper.scrape_hashtag('dogecoin', max_results=10)

# Test Reddit scraper
from scrapers.reddit_scraper import RedditScraper
with RedditScraper(config) as scraper:
    posts = scraper.scrape_subreddit_search('CryptoCurrency', 'dogecoin', max_results=10)
```

## Architecture

### Core Scripts

**meme_coin_tracker.py**
- Fetches live price data from CoinGecko API (no API key required)
- Saves to `meme_coin_data.csv` for historical tracking
- Displays market stats, gainers/losers, and trends
- Can run continuously with 5-minute intervals (commented out by default)

**twitter_hype_collector.py**
- Collects tweets using Tweepy library (Twitter API required)
- Calculates custom "hype scores" based on keywords, emojis, and engagement
- Uses VADER sentiment analysis
- Requires `TWITTER_BEARER_TOKEN` in `.env` file
- Respects Twitter API rate limits (1,500 tweets/month on free tier)

**backtest_analyzer.py**
- Correlates social metrics with price movements
- Detects social volume spikes and price pumps
- Tests time-lag hypotheses (does social lead price?)
- Generates statistical correlation reports
- Creates visualizations with matplotlib/plotly

### Scraper System (`/scrapers`)

**Base Architecture:**
All scrapers inherit from `BaseScraper` class which provides:
- Selenium WebDriver setup with anti-detection measures
- Random delays to mimic human behavior
- Safe element finding (no exceptions on missing elements)
- Screenshot capability for debugging
- Context manager support for automatic cleanup

**base_scraper.py**
- Foundation class with proven anti-detection techniques from Instagram bot
- Disables automation flags (`--disable-blink-features=AutomationControlled`)
- Custom user agent and JavaScript anti-detection
- Configurable headless mode, delays, and timeouts
- Rate limiting via `random_delay()` method

**tiktok_scraper.py**
- Scrapes TikTok hashtag pages without API
- Uses specific selectors: `#challenge-item-list`, `#column-item-video-container-{n}`
- Extracts: video_id, username, views, caption, hashtags
- Auto-scrolls to load more content
- Returns structured JSON data with timestamps

**reddit_scraper.py**
- Uses old.reddit.com for simple HTML parsing
- No login required, very reliable
- Extracts: title, author, score, comments, flair, timestamps
- Can scrape multiple subreddits in batch
- Supports detailed post content retrieval

### Data Flow

```
CoinGecko API → meme_coin_tracker.py → meme_coin_data.csv
                                            ↓
Twitter API → twitter_hype_collector.py → twitter_hype_data.csv
                                            ↓
TikTok → tiktok_scraper.py → test_tiktok_results.json
                                            ↓
Reddit → reddit_scraper.py → test_reddit_results.json
                                            ↓
                              All data feeds into backtest_analyzer.py
                                            ↓
                              Correlation analysis & visualizations
```

## Configuration

### Scraper Configuration
All scrapers accept a config dict:
```python
config = {
    'headless': True,        # Hide browser window
    'min_delay': 2,          # Minimum delay between actions (seconds)
    'max_delay': 5,          # Maximum delay between actions (seconds)
    'user_agent': '...'      # Custom user agent (optional)
}
```

### Tracked Coins
Defined in each script's `MEME_COINS` dictionary:
- DOGE (dogecoin)
- PEPE (pepe)
- SHIB (shiba-inu)
- BONK (bonk)
- FLOKI (floki)
- WIF (dogwifhat)

### Environment Variables
Required in `.env` file:
```
TWITTER_BEARER_TOKEN=your_token_here
```

## Key Design Patterns

### Anti-Detection for Web Scraping
- Disable Selenium automation flags
- Randomized delays between actions (2-5 seconds default)
- Custom user agents
- JavaScript to mask WebDriver property
- Headless mode with proper window sizing

### Error Handling
- All API calls wrapped in try-except blocks
- Safe element finding (returns None instead of raising exceptions)
- Automatic rate limit handling with exponential backoff
- Graceful degradation when data sources unavailable

### Data Storage
- CSV files for historical price/social data
- JSON files for scraper test results
- Incremental appending (doesn't overwrite historical data)
- ISO timestamps for all records

### Context Managers
All scrapers implement context manager protocol:
```python
with TikTokScraper(config) as scraper:
    data = scraper.scrape_hashtag('dogecoin')
# Driver automatically closes
```

## Important Implementation Notes

### Selenium WebDriver
- Uses Chrome with ChromeDriver (auto-managed by webdriver-manager)
- Requires Chrome browser installed on system
- Set `headless=False` during debugging to see browser actions
- Screenshots saved to `debug_screenshots/` directory

### API Rate Limits
- **CoinGecko**: Free tier has rate limits, built-in delays recommended
- **Twitter**: 1,500 tweets/month on free tier, client uses `wait_on_rate_limit=True`
- **TikTok/Reddit**: No official API used, scrapers should be polite (2-5 second delays)

### Data Quality
- CoinGecko data is real-time and reliable
- Scraper data depends on HTML structure (may break if sites update)
- TikTok view counts are from listing page (likes/shares require clicking into videos)
- Reddit data uses old.reddit.com for stability

### Testing Scrapers
When scrapers fail:
1. Set `headless=False` to observe browser behavior
2. Check if website HTML structure changed (update selectors)
3. Verify ChromeDriver version matches Chrome version
4. Take screenshots using `scraper.take_screenshot('debug.png')`
5. Check for anti-bot challenges or IP blocks

## File Structure
```
├── schedule_optimized.py          # Main scheduler (prices 15min, social 60min)
├── schedule_collection.py         # DEPRECATED - use schedule_optimized.py
├── meme_coin_tracker.py           # Price data collection (standalone)
├── twitter_hype_collector.py      # Twitter sentiment collection
├── backtest_analyzer.py           # Statistical analysis
├── sync_to_github.sh              # Auto-sync to GitHub repo
│
├── api/                           # FastAPI backend
│   ├── main.py                   # API endpoints (rate-limited)
│   └── requirements.txt          # API dependencies
│
├── collectors/                    # Data collection modules
│   ├── unified_collector.py      # Orchestrates all collectors
│   ├── price_collector.py        # CoinGecko price data
│   ├── reddit_collector.py       # Reddit data collection
│   ├── tiktok_collector.py       # TikTok data collection
│   ├── sentiment_analyzer.py     # VADER sentiment + hype scoring
│   ├── bot_detector.py           # Bot/spam detection
│   ├── quality_monitor.py        # Data quality checks
│   ├── influencer_tracker.py     # Track key influencers
│   └── news_collector.py         # News aggregation
│
├── scrapers/                      # Selenium-based web scrapers
│   ├── base_scraper.py           # Base class with anti-detection
│   ├── tiktok_scraper.py         # TikTok hashtag scraper
│   └── reddit_scraper.py         # Reddit search scraper
│
├── database/                      # Database layer
│   ├── models.py                 # SQLAlchemy ORM models
│   └── db_manager.py             # Database operations
│
├── analysis/                      # Data analysis modules
│   ├── correlation_analyzer.py   # Price-sentiment correlation
│   ├── volume_analyzer.py        # Volume spike detection
│   └── data_pipeline.py          # Data processing pipeline
│
├── validation/                    # Sentiment validation
│   ├── sentiment_validator.py    # Accuracy testing
│   └── validate_sentiment.py     # Validation runner
│
├── events/                        # Event logging
│   ├── event_logger.py           # Log market events
│   └── log_event.py              # Event utilities
│
├── config/                        # Configuration
│   ├── coins.yaml                # Coin definitions
│   └── coin_config.py            # Config loader
│
├── utils/                         # Utilities
│   └── logging_config.py         # Centralized logging
│
├── frontend/                      # Next.js dashboard
│   ├── src/app/                  # App routes
│   └── src/components/           # React components
│
├── tests/                         # Test suite (pytest)
│   ├── conftest.py               # Shared fixtures
│   └── unit/                     # Unit tests
│
├── docs/                          # Documentation
│   ├── ARCHITECTURE.md
│   ├── OPERATIONS_GUIDE.md
│   └── UI_DESIGN.md
│
├── data/                          # Generated data (gitignored)
│   └── memecoin.db               # SQLite database
│
├── logs/                          # Log files (gitignored)
├── requirements.txt               # Base dependencies
├── requirements_scrapers.txt      # Scraper dependencies
└── pytest.ini                     # Test configuration
```
