# Memecoin Sentiment Analyzer

A data pipeline that collects social media signals from Reddit and TikTok, scores them for sentiment and hype intensity, and correlates those signals with meme coin price movements.

The core question: does retail social media hype lead price action, lag it, or run independent of it? This project builds the data infrastructure to answer that empirically.

## Data Sources

| Source | Data Collected |
|---|---|
| Reddit (PRAW) | Posts, comments, upvote velocity from r/CryptoCurrency, r/memecoins, coin-specific subreddits |
| TikTok | Captions, hashtags, view/like counts from crypto-tagged content |
| CoinGecko API | Price, volume, market cap for DOGE, PEPE, SHIB, BONK, FLOKI, WIF |

GitHub Actions workflows run collection on a schedule and commit the data to the repo.

## Methodology

**Sentiment scoring** uses [VADER](https://github.com/cjhutto/vaderSentiment) (Valence Aware Dictionary and sEntiment Reasoner), a lexicon-based model calibrated for social media language.

**Hype scoring** overlays a custom keyword and emoji classifier on top of VADER compound scores:

- Hype keywords: `moon`, `rocket`, `lfg`, `wagmi`, `x100`, `all in`, `dont miss`, etc.
- Hype emojis: 🚀 🌙 💎 🙌 📈 and others
- Final hype score combines VADER compound + keyword density + emoji density

**Correlation analysis** computes rolling correlations between aggregated daily sentiment/hype scores and next-day price returns, testing for lead/lag relationships.

## Architecture

```
collectors/          Data ingestion layer
  price_collector    CoinGecko price + volume data
  reddit_collector   Reddit PRAW-based post + comment scraper
  tiktok_collector   TikTok caption + engagement scraper
  sentiment_analyzer VADER + custom hype scoring
  quality_monitor    Data quality validation
  influencer_tracker High-follower account flagging
  bot_detector       Anomalous posting pattern detection

analysis/            Analysis layer
  data_pipeline      Preprocessing and normalization
  correlation_analyzer Rolling correlation between sentiment and price
  volume_analyzer    Social volume vs. trading volume signals

api/                 FastAPI endpoint for querying results
validation/          Labeled test data for sentiment model validation
tests/               Unit + integration test suite
```

## Quickstart

```bash
git clone https://github.com/rippere/Memecoin-Sentiment-Analyzer
cd Memecoin-Sentiment-Analyzer

python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env
# Fill in: REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET, REDDIT_USER_AGENT

# Collect price data
python collectors/price_collector.py

# Collect Reddit sentiment
python collectors/reddit_praw_collector.py

# Run correlation analysis
python analysis/correlation_analyzer.py
```

## Automated Collection

GitHub Actions workflows handle scheduled data collection:

- `.github/workflows/collect-prices.yml` — daily price snapshots
- `.github/workflows/collect-data.yml` — Reddit + sentiment pipeline
- `.github/workflows/collect-trending-data.yml` — trending coin detection

## Stack

Python · VADER · PRAW (Reddit API) · TikTok scraping · CoinGecko API · Pandas · NumPy · FastAPI · GitHub Actions

## Research Questions

1. Does aggregate social hype score for a coin lead next-day price returns?
2. Is influencer-driven hype more predictive than organic community sentiment?
3. Do bot-detected accounts (anomalous posting patterns) correlate with pump-and-dump events?
