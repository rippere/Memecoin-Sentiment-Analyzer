"""
News Sentiment Collector
=========================
Collects cryptocurrency news from multiple sources and analyzes sentiment
Supports: CryptoCompare API, RSS feeds, manual entry
"""

import sys
from pathlib import Path
import requests
from typing import List, Dict
import logging
from datetime import datetime
import time
import feedparser

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from collectors.sentiment_analyzer import SentimentAnalyzer

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


class NewsCollector:
    """
    Collects and analyzes cryptocurrency news from multiple sources
    """

    # RSS Feed sources
    RSS_FEEDS = {
        'coindesk': 'https://www.coindesk.com/arc/outboundfeeds/rss/',
        'cointelegraph': 'https://cointelegraph.com/rss',
        'decrypt': 'https://decrypt.co/feed',
        'bitcoinmagazine': 'https://bitcoinmagazine.com/.rss/full/',
    }

    def __init__(self, cryptocompare_api_key: str = None):
        """
        Initialize news collector

        Args:
            cryptocompare_api_key: CryptoCompare API key (optional)
        """
        self.cryptocompare_api_key = cryptocompare_api_key
        self.sentiment_analyzer = SentimentAnalyzer()
        logging.info("News collector initialized")

    def collect_from_cryptocompare(self, coin_symbols: List[str] = None, limit: int = 50) -> List[Dict]:
        """
        Collect news from CryptoCompare API

        Args:
            coin_symbols: Filter by specific coins (optional)
            limit: Maximum number of articles

        Returns:
            List of news articles with sentiment
        """
        if not self.cryptocompare_api_key:
            logging.warning("CryptoCompare API key not provided, skipping")
            return []

        url = 'https://min-api.cryptocompare.com/data/v2/news/'
        headers = {'authorization': f'Apikey {self.cryptocompare_api_key}'}
        params = {'lang': 'EN'}

        # Add coin filter if specified
        if coin_symbols:
            params['categories'] = ','.join(coin_symbols)

        try:
            response = requests.get(url, headers=headers, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            articles = []
            for item in data.get('Data', [])[:limit]:
                # Analyze sentiment
                text = f"{item.get('title', '')} {item.get('body', '')}"
                sentiment = self.sentiment_analyzer.analyze_text(text)

                article = {
                    'id': item.get('id'),
                    'title': item.get('title'),
                    'body': item.get('body', '')[:500],  # Truncate body
                    'source': item.get('source'),
                    'url': item.get('url'),
                    'published_at': datetime.fromtimestamp(item.get('published_on', 0)),
                    'categories': item.get('categories', '').split('|'),
                    'sentiment_analysis': sentiment,
                    'collected_at': datetime.utcnow()
                }
                articles.append(article)

            logging.info(f"Collected {len(articles)} articles from CryptoCompare")
            return articles

        except Exception as e:
            logging.error(f"Error collecting from CryptoCompare: {e}")
            return []

    def collect_from_rss(self, feed_name: str = None, coin_filter: List[str] = None) -> List[Dict]:
        """
        Collect news from RSS feeds

        Args:
            feed_name: Specific feed to collect from (optional, collects all if None)
            coin_filter: Filter articles mentioning specific coins

        Returns:
            List of news articles with sentiment
        """
        feeds_to_collect = {feed_name: self.RSS_FEEDS[feed_name]} if feed_name else self.RSS_FEEDS

        all_articles = []

        for feed_name, feed_url in feeds_to_collect.items():
            try:
                logging.info(f"Collecting from {feed_name}...")
                feed = feedparser.parse(feed_url)

                for entry in feed.entries[:20]:  # Limit per feed
                    title = entry.get('title', '')
                    summary = entry.get('summary', '') or entry.get('description', '')

                    # Filter by coin mentions if specified
                    if coin_filter:
                        text_to_check = f"{title} {summary}".lower()
                        if not any(coin.lower() in text_to_check for coin in coin_filter):
                            continue

                    # Analyze sentiment
                    text = f"{title} {summary}"
                    sentiment = self.sentiment_analyzer.analyze_text(text)

                    article = {
                        'title': title,
                        'body': summary[:500],
                        'source': feed_name,
                        'url': entry.get('link', ''),
                        'published_at': self._parse_date(entry.get('published', '')),
                        'sentiment_analysis': sentiment,
                        'collected_at': datetime.utcnow()
                    }
                    all_articles.append(article)

                time.sleep(1)  # Rate limiting

            except Exception as e:
                logging.error(f"Error collecting from {feed_name}: {e}")
                continue

        logging.info(f"Collected {len(all_articles)} articles from RSS feeds")
        return all_articles

    def _parse_date(self, date_str: str) -> datetime:
        """Parse various date formats"""
        try:
            from dateutil import parser
            return parser.parse(date_str)
        except:
            return datetime.utcnow()

    def collect_coin_news(self, coin_symbol: str, sources: List[str] = None) -> List[Dict]:
        """
        Collect news for a specific coin from all sources

        Args:
            coin_symbol: Coin symbol (e.g., 'DOGE', 'BTC')
            sources: List of sources to use (default: all)

        Returns:
            List of news articles about the coin
        """
        if sources is None:
            sources = ['cryptocompare', 'rss']

        all_articles = []

        # CryptoCompare
        if 'cryptocompare' in sources and self.cryptocompare_api_key:
            cc_articles = self.collect_from_cryptocompare(coin_symbols=[coin_symbol])
            all_articles.extend(cc_articles)

        # RSS feeds
        if 'rss' in sources:
            rss_articles = self.collect_from_rss(coin_filter=[coin_symbol])
            all_articles.extend(rss_articles)

        # Sort by published date
        all_articles.sort(key=lambda x: x.get('published_at', datetime.min), reverse=True)

        logging.info(f"Collected {len(all_articles)} news articles for {coin_symbol}")
        return all_articles

    def aggregate_news_sentiment(self, articles: List[Dict]) -> Dict:
        """
        Aggregate sentiment from multiple news articles

        Args:
            articles: List of articles with sentiment analysis

        Returns:
            Aggregated news sentiment metrics
        """
        if not articles:
            return {
                'article_count': 0,
                'avg_sentiment': 0.0,
                'positive_count': 0,
                'negative_count': 0,
                'neutral_count': 0
            }

        sentiments = [a['sentiment_analysis']['compound'] for a in articles if 'sentiment_analysis' in a]

        positive_count = sum(1 for s in sentiments if s >= 0.05)
        negative_count = sum(1 for s in sentiments if s <= -0.05)
        neutral_count = len(sentiments) - positive_count - negative_count

        return {
            'article_count': len(articles),
            'avg_sentiment': sum(sentiments) / len(sentiments) if sentiments else 0.0,
            'positive_count': positive_count,
            'negative_count': negative_count,
            'neutral_count': neutral_count,
            'sentiment_distribution': {
                'positive': positive_count / len(sentiments) if sentiments else 0,
                'negative': negative_count / len(sentiments) if sentiments else 0,
                'neutral': neutral_count / len(sentiments) if sentiments else 0
            },
            'top_sources': self._get_top_sources(articles)
        }

    def _get_top_sources(self, articles: List[Dict], top_n: int = 5) -> Dict:
        """Get top news sources by article count"""
        from collections import Counter
        sources = [a.get('source', 'unknown') for a in articles]
        return dict(Counter(sources).most_common(top_n))

    def get_trending_topics(self, articles: List[Dict], top_n: int = 10) -> List[str]:
        """
        Extract trending topics from news articles

        Args:
            articles: List of news articles
            top_n: Number of top topics to return

        Returns:
            List of trending topics/keywords
        """
        from collections import Counter
        import re

        # Extract words from titles
        all_words = []
        for article in articles:
            title = article.get('title', '').lower()
            # Remove common words and extract meaningful terms
            words = re.findall(r'\b[a-z]{4,}\b', title)  # 4+ letter words
            all_words.extend(words)

        # Filter out common words
        stop_words = {'that', 'this', 'with', 'from', 'have', 'been', 'will',
                     'about', 'after', 'could', 'would', 'should', 'their'}

        filtered_words = [w for w in all_words if w not in stop_words]

        # Get most common
        word_counts = Counter(filtered_words)
        return [word for word, count in word_counts.most_common(top_n)]


class NewsDatabase:
    """
    Stores news articles in database
    Note: Requires adding a News model to database/models.py
    """

    def __init__(self, db_manager=None):
        """Initialize news database storage"""
        self.db = db_manager
        logging.info("News database initialized")

    def add_news_article(self, coin_symbol: str, article: Dict):
        """
        Add news article to database

        Args:
            coin_symbol: Associated coin
            article: Article data
        """
        if not self.db:
            logging.warning("No database manager provided")
            return

        # TODO: Implement when News model is added to database
        logging.info(f"News article saved: {article.get('title', 'Untitled')}")


def collect_all_news(cryptocompare_key: str = None):
    """
    Collect news from all sources for demonstration

    Args:
        cryptocompare_key: CryptoCompare API key (optional)
    """
    collector = NewsCollector(cryptocompare_api_key=cryptocompare_key)

    print("\n=== Collecting Crypto News ===\n")

    # Collect from RSS feeds
    print("Collecting from RSS feeds...")
    rss_articles = collector.collect_from_rss()

    print(f"\nCollected {len(rss_articles)} articles from RSS")

    # Show sample articles
    print("\n=== Sample Articles ===\n")
    for article in rss_articles[:5]:
        print(f"Title: {article['title']}")
        print(f"Source: {article['source']}")
        print(f"Sentiment: {article['sentiment_analysis']['compound']:.3f}")
        print(f"URL: {article['url']}\n")

    # Aggregate sentiment
    agg = collector.aggregate_news_sentiment(rss_articles)
    print(f"=== Aggregate Sentiment ===\n")
    print(f"Total articles: {agg['article_count']}")
    print(f"Avg sentiment: {agg['avg_sentiment']:.3f}")
    print(f"Positive: {agg['positive_count']}, Negative: {agg['negative_count']}, Neutral: {agg['neutral_count']}")

    # Trending topics
    topics = collector.get_trending_topics(rss_articles)
    print(f"\nTrending topics: {', '.join(topics)}")


if __name__ == "__main__":
    import sys
    api_key = sys.argv[1] if len(sys.argv) > 1 else None
    collect_all_news(cryptocompare_key=api_key)
