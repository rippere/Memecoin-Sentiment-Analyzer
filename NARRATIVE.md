# Memecoin Sentiment Analyzer: The Story of Predicting Chaos

*A narrative journey through building a system that listens to the internet to predict cryptocurrency prices*

---

## The Big Idea: Can Social Media Predict the Future?

Imagine this scenario: A TikTok influencer with 500,000 followers posts a video about Dogecoin featuring a dancing Shiba Inu and the caption "DOGE TO THE MOON." Within hours, the video has 2 million views. Reddit's r/CryptoCurrency sees a spike in DOGE posts. Twitter crypto accounts start retweeting memes.

**Question**: Does the price pump happen before the social media frenzy, during it, or after?

This project exists to answer that question with data, not speculation. We're building a machine that watches TikTok teenagers, Reddit degenerates, and Twitter shills, then correlates their collective excitement with actual price movements.

If social sentiment leads price by even 1-3 hours, that's actionable intelligence. If it lags price, that's also valuable—it tells us when retail is buying the top.

---

## Chapter 1: The Humble Beginning

### The First Script: Proof of Concept

The journey started with `meme_coin_tracker.py`, a simple 150-line Python script that:
1. Makes HTTP requests to CoinGecko's free API
2. Fetches price data for 6 meme coins (DOGE, PEPE, SHIB, BONK, FLOKI, WIF)
3. Displays market stats in a terminal
4. Saves data to CSV with timestamps

**Why this mattered**: It proved we could collect real-time market data without spending money on API subscriptions. CoinGecko's free tier gives us everything we need—price, market cap, volume, 24h change—all through simple HTTP GET requests returning JSON.

The first run was magical in its simplicity:
```bash
$ python meme_coin_tracker.py

====================================
🐕 MEME COIN PRICES
====================================
DOGE: $0.0734 (↑ 5.2%)
PEPE: $0.0000012 (↓ 2.1%)
SHIB: $0.0000089 (↑ 8.4%)
...
```

Within minutes, we had a working proof of concept. Data was flowing. The CSV file was growing. The question shifted from "Can we collect data?" to "What do we do with it?"

---

## Chapter 2: The Scraper Challenge

### Why Scraping is Necessary (and Terrible)

Here's the problem: CoinGecko gives us price data for free. But they don't give us social media sentiment. TikTok doesn't offer a public API for hashtag searches. Twitter's API costs $100/month for basic access. Reddit's API is free but heavily rate-limited.

**Solution**: Web scraping with Selenium.

**The plan**:
- Load webpages in a headless Chrome browser
- Wait for JavaScript to render content
- Parse HTML to extract data
- Mimic human behavior to avoid detection

### Building the Base Scraper

All scrapers inherit from `BaseScraper`, a battle-tested class adapted from previous projects. It includes:

**Anti-detection techniques:**
```python
chrome_options.add_argument('--disable-blink-features=AutomationControlled')
chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
chrome_options.add_experimental_option('useAutomationExtension', False)
```

**Human-like delays:**
```python
def random_delay(self, min_seconds=2, max_seconds=5):
    time.sleep(random.uniform(min_seconds, max_seconds))
```

**Graceful error handling:**
```python
def wait_for_element(self, by, selector, timeout=10):
    try:
        return WebDriverWait(self.driver, timeout).until(
            EC.presence_of_element_located((by, selector))
        )
    except TimeoutException:
        return None  # Don't crash, return None
```

This foundation meant each new scraper (TikTok, Reddit) could focus on platform-specific logic, not reinventing browser automation.

---

## Chapter 3: The TikTok Saga

### When CSS Selectors Break at 3 AM

TikTok scraping worked beautifully for three weeks. The selectors were clean:

```python
# Find the main video container
container = driver.find_element(By.ID, 'challenge-item-list')

# Find individual videos
video = driver.find_element(By.ID, f'column-item-video-container-{n}')
```

Then one Tuesday morning, the scraper returned zero videos. Not an error. Not a timeout. Just... nothing.

**The investigation:**
1. Checked TikTok manually—hashtag pages loaded fine
2. Ran scraper with `headless=False`—saw Chrome open, saw videos load
3. Inspected HTML—found the videos, but the `id` attributes were gone

**The revelation**: TikTok had migrated from `id` attributes to `data-e2e` attributes:

```html
<!-- BEFORE -->
<div id="challenge-item-list">
  <div id="column-item-video-container-0">...</div>
</div>

<!-- AFTER -->
<div data-e2e="challenge-item-list">
  <div data-e2e="search-video-item">...</div>
</div>
```

**The fix** was straightforward:
```python
# Updated selector
container = driver.find_element(By.CSS_SELECTOR, '[data-e2e="challenge-item-list"]')
```

**The lesson**: Web scraping is inherently fragile. Websites change without warning. The solution isn't to prevent breakage (impossible) but to:
1. **Detect it quickly** (monitoring and logging)
2. **Fix it fast** (modular code)
3. **Test it thoroughly** (automated tests)

### How TikTok Scraping Works Now

The current TikTok scraper:
1. **Navigates** to `tiktok.com/tag/{hashtag}`
2. **Waits** for `[data-e2e="challenge-item-list"]` to load
3. **Scrolls** to trigger lazy loading (TikTok loads videos as you scroll)
4. **Parses** HTML with BeautifulSoup to extract:
   - Video ID (unique identifier)
   - Username (creator)
   - Caption (text description)
   - View count (engagement metric)
   - Hashtags (topical tags)
5. **Repeats** until max results or no new videos

**Key optimization**: Batch processing. Instead of saving each video to the database individually (slow), we collect all videos first, then batch insert (5x faster).

---

## Chapter 4: The Reddit Advantage

### Why Reddit is the Reliable One

Compared to TikTok, Reddit scraping is refreshingly stable. We use `old.reddit.com` (the classic Reddit interface), which:
- Doesn't require JavaScript rendering (no Selenium needed)
- Uses simple, semantic HTML
- Rarely changes structure
- Doesn't block scrapers aggressively

**The process:**
1. Search for coin keyword (e.g., "dogecoin") in r/CryptoCurrency
2. Parse search results HTML
3. Extract post metadata:
   - Title
   - Author
   - Score (upvotes - downvotes)
   - Comment count
   - Flair (post category)
   - Timestamp

**Why this matters**: Reddit sentiment is different from TikTok sentiment. TikTok is high-energy, meme-driven, retail chaos. Reddit is community discussion, technical analysis, and informed speculation. Both are valuable, but they represent different market participants.

---

## Chapter 5: The Sentiment Engine

### From Text to Numbers

Social media posts are text. Machine learning models need numbers. That's where sentiment analysis comes in.

**We use VADER** (Valence Aware Dictionary and sEntiment Reasoner), a lexicon-based sentiment analyzer specifically designed for social media. It understands:

- **Emojis**: "DOGE 🚀🚀🚀" is more positive than "DOGE"
- **Capitalization**: "AMAZING" is more intense than "amazing"
- **Punctuation**: "This is good!!!" is more enthusiastic than "This is good"
- **Negation**: "Not bad" is different from "bad"
- **Degree modifiers**: "Very good" is more positive than "good"

**Example sentiment analysis:**
```python
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

analyzer = SentimentIntensityAnalyzer()

text = "DOGE TO THE MOON 🚀🚀🚀 100X INCOMING!!!"
scores = analyzer.polarity_scores(text)
# Returns: {'neg': 0.0, 'neu': 0.254, 'pos': 0.746, 'compound': 0.891}
```

The `compound` score (-1 to +1) is what we track. Positive scores indicate bullish sentiment, negative scores indicate bearish sentiment.

### The Hype Score: Our Secret Sauce

Raw sentiment isn't enough. A post saying "Dogecoin is great" and a viral video with 2M views saying "DOGE 100X" both score positive, but they're not equally important.

**We calculate a hype score** that combines:
1. **Sentiment polarity** (how positive/negative)
2. **Engagement metrics** (views, upvotes, retweets)
3. **Keyword density** ("moon," "pump," "100x")
4. **Emoji intensity** (rocket emojis = hype)

```python
hype_score = (
    sentiment_compound * 100 +
    keyword_bonus +
    emoji_multiplier +
    log(engagement)
)
```

This hype score lets us rank posts by influence, not just sentiment.

---

## Chapter 6: The Testing Revelation

### When Tests Exposed a Hidden Design Flaw

Writing integration tests for `UnifiedCollector` revealed an embarrassing problem: **our public API didn't exist**.

The class had private methods:
- `_collect_prices()` (note the underscore)
- `_collect_reddit()`
- `_collect_tiktok()`

These were internal implementation details. But when we tried to test individual collectors, we realized there was no way to call them from outside the class without violating Python conventions.

**The fix**: Add public wrapper methods:

```python
def collect_prices(self, coin_symbols: List[str]) -> Dict:
    """Public API for price collection"""
    count, errors = self._collect_prices(coin_symbols)
    return {'count': count, 'errors': errors}
```

This is **Test-Driven Development in action**. We didn't realize our API was incomplete until tests forced us to think like users of the code.

**Outcome**: 124 tests now passing. Test suite validates:
- Price data fetching and parsing
- Reddit scraping and sentiment analysis
- TikTok scraping and video extraction
- Database operations (inserts, queries, constraints)
- Scheduler timing and error handling

Current coverage: 30%. Target: 80%+ for critical paths (collectors, database operations).

---

## Chapter 7: The Database Architecture

### Why SQLite is Perfect (for Now)

We use **SQLite** instead of PostgreSQL or MySQL because:
1. **Zero configuration**: No server to run, no credentials to manage
2. **Portable**: Database is a single file (`memecoin.db`)
3. **Fast enough**: Can handle millions of records on a laptop
4. **Full SQL**: Supports complex queries, indexes, constraints
5. **ACID compliant**: Transactions are safe

**Database schema:**

```sql
-- Price data from CoinGecko
CREATE TABLE prices (
    id INTEGER PRIMARY KEY,
    coin_symbol TEXT NOT NULL,
    price REAL NOT NULL,
    market_cap REAL,
    volume_24h REAL,
    price_change_24h REAL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(coin_symbol, timestamp)  -- Prevent duplicates
);

-- Reddit posts with sentiment
CREATE TABLE reddit_posts (
    id INTEGER PRIMARY KEY,
    coin_symbol TEXT NOT NULL,
    post_id TEXT UNIQUE NOT NULL,
    title TEXT NOT NULL,
    author TEXT,
    score INTEGER,
    num_comments INTEGER,
    sentiment_score REAL,
    hype_score REAL,
    created_at DATETIME,
    collected_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- TikTok videos with engagement
CREATE TABLE tiktok_videos (
    id INTEGER PRIMARY KEY,
    coin_symbol TEXT NOT NULL,
    video_id TEXT UNIQUE NOT NULL,
    username TEXT,
    caption TEXT,
    view_count INTEGER,
    sentiment_score REAL,
    hype_score REAL,
    created_at DATETIME,
    collected_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Aggregated sentiment scores
CREATE TABLE sentiment_scores (
    id INTEGER PRIMARY KEY,
    coin_symbol TEXT NOT NULL,
    source TEXT NOT NULL,  -- 'reddit', 'tiktok', 'twitter'
    avg_sentiment REAL,
    total_volume INTEGER,
    total_hype REAL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

**Key design decisions:**
- **Unique constraints** prevent duplicate data
- **Indexes** on `coin_symbol` and `timestamp` speed up queries
- **Separate tables** for different data types (prices vs. social)
- **Audit fields** (`collected_at`) track when we scraped data

---

## Chapter 8: The Scheduler Symphony

### Background Collection That Never Sleeps

Manual data collection doesn't scale. We need continuous collection, even when we're asleep.

**The scheduler** (`schedule_optimized.py`) runs in the background:

```python
# Collect prices every 15 minutes (cheap, fast)
schedule.every(15).minutes.do(collect_prices)

# Collect social media every 60 minutes (expensive, slow)
schedule.every(60).minutes.do(collect_social)
```

**Why different intervals?**
- **Price data** changes constantly. A 15-minute delay is acceptable.
- **Social sentiment** is sticky. Viral TikToks stay viral for hours. Checking every 60 minutes is sufficient and reduces scraper load.

**Logging every cycle:**
```
2025-11-28 14:30:00 - INFO - 🚀 STARTING DATA COLLECTION CYCLE
2025-11-28 14:30:05 - INFO - 💰 Collected 6 prices in 2.3s (Quality: GOOD)
2025-11-28 14:30:42 - INFO - 🔍 Collected 87 Reddit posts in 34.1s (Quality: GOOD)
2025-11-28 14:32:15 - INFO - 🎵 Collected 63 TikTok videos in 91.2s (Quality: FAIR)
2025-11-28 14:32:15 - INFO - ✅ COLLECTION CYCLE COMPLETE
```

This logging creates an audit trail. We can see:
- When collection succeeded/failed
- How long each source took
- Data quality scores
- Error messages

**Current uptime**: 14+ days of continuous collection. The database has grown to 50,000+ records.

---

## Chapter 9: The Quality Monitor

### Not All Data is Created Equal

Collecting 1,000 Reddit posts sounds great until you realize 800 are spam bots. That's why we built `QualityMonitor`.

**Quality checks:**
1. **Bot detection**: Flags posts from known bot accounts
2. **Duplicate detection**: Identifies copy-paste spam
3. **Engagement validation**: Filters posts with suspiciously high/low engagement
4. **Completeness**: Ensures required fields aren't missing
5. **Freshness**: Warns if data is stale

**Quality scores** (0-100):
- **90-100**: Excellent data quality
- **70-89**: Good data quality
- **50-69**: Fair data quality (warnings logged)
- **0-49**: Poor data quality (investigation needed)

This system helps us trust the data feeding into correlation analysis.

---

## Chapter 10: What's Next

### The Correlation Engine (Coming Soon)

With months of data collected, the next phase is **correlation analysis**:

**Hypothesis**: Social sentiment spikes lead price pumps by 1-3 hours.

**Test**: For each coin, correlate:
- Reddit post volume vs. price (1h, 3h, 6h, 24h lags)
- TikTok view counts vs. price (same lags)
- Hype scores vs. price changes

**Expected output**: Correlation coefficients and p-values showing whether sentiment predicts price.

### The Visualization Dashboard

A Plotly Dash web app showing:
- **Live price charts** with overlaid sentiment scores
- **Heatmaps** of cross-coin correlations
- **Timeline** of viral posts and price movements
- **Alerts** for unusual sentiment spikes

### The Backtesting Engine

Test historical predictions:
1. Identify past sentiment spikes
2. Check if price pumped 1-3 hours later
3. Calculate win rate, average gain, max drawdown
4. Validate strategy profitability

---

## Lessons Learned: What Actually Mattered

### 1. Start Simple, Iterate Fast
The first script was 100 lines. Now it's 8,500 lines across 30+ files. Starting simple validated the idea. Scaling happened after proof of concept.

### 2. Web Scraping Will Break
TikTok selectors broke after 3 weeks. This will happen again. The solution: monitoring, logging, and modular code.

### 3. Tests Are Design Tools
Tests exposed API gaps and design flaws before they became production bugs. TDD isn't just validation—it shapes architecture.

### 4. Data Quality > Data Quantity
1,000 genuine posts beat 10,000 spam posts. Quality monitoring is infrastructure, not an afterthought.

### 5. Logs Tell Stories
Every collection cycle logs success, duration, and errors. These logs reveal patterns (TikTok slow on weekends, Reddit busier during US evenings).

### 6. Configuration is Code
Scraper delays, max results, database paths—all configuration. Changing them shouldn't require code edits.

---

## The Value Proposition: Why This Matters

### For Traders
Know when retail is piling into a coin before the pump. See sentiment divergences (high hype, falling price = potential reversal).

### For Researchers
Open-source tool for studying social sentiment and market behavior. Reproducible analysis with real data.

### For Learners
Educational codebase demonstrating:
- Web scraping with Selenium
- Sentiment analysis with VADER
- Database design with SQLite
- Testing with pytest
- Task scheduling
- Error handling and logging

---

## The Journey Continues

This project started as a curiosity: "Can TikTok predict Dogecoin pumps?" It's evolved into a robust data collection and analysis system.

The data is flowing. The tests are passing. The scheduler is humming along in the background.

Next up: Answering the original question with statistical rigor.

**Stay tuned.**

---

**Project Status**: 🟢 Active Development
**Total Records Collected**: 50,000+
**Uptime**: 14+ days continuous
**Next Milestone**: Correlation analysis engine
**Last Updated**: November 28, 2025
