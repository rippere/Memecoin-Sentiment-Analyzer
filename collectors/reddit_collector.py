"""
Reddit Data Collector
====================
Collects Reddit posts using the scraper and analyzes sentiment
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from scrapers.reddit_scraper import RedditScraper
from collectors.sentiment_analyzer import SentimentAnalyzer
from collectors.bot_detector import BotDetector
import logging
from typing import List, Dict
from datetime import datetime

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


class RedditCollector:
    """Collects and analyzes Reddit posts for meme coins"""

    # Subreddits to monitor
    SUBREDDITS = [
        'CryptoCurrency',
        'CryptoMoonShots',
        'SatoshiStreetBets',
        'dogecoin',
        'SHIBArmy',
    ]

    def __init__(self, config: Dict = None, enable_bot_detection: bool = True):
        """
        Initialize Reddit collector

        Args:
            config: Configuration for scraper (headless, delays, etc.)
            enable_bot_detection: Whether to filter bot accounts (default: True)
        """
        if config is None:
            config = {
                'headless': True,
                'min_delay': 2,
                'max_delay': 4
            }

        self.config = config
        self.enable_bot_detection = enable_bot_detection
        self.sentiment_analyzer = SentimentAnalyzer()
        self.bot_detector = BotDetector() if enable_bot_detection else None

        # Load coin queries from config
        try:
            from config.coin_config import get_coin_config
            coin_config = get_coin_config()
            self.COIN_QUERIES = {
                symbol: coin_config.get_social_queries(symbol)
                for symbol in coin_config.get_coin_symbols()
            }
        except Exception as e:
            logging.warning(f"Could not load queries from config: {e}, using defaults")
            self.COIN_QUERIES = {
                'DOGE': ['dogecoin', 'doge', '$doge'],
                'PEPE': ['pepe', '$pepe'],
                'SHIB': ['shiba', 'shib', '$shib'],
            }

        bot_status = "with bot detection" if enable_bot_detection else "without bot detection"
        logging.info(f"Reddit collector initialized ({len(self.COIN_QUERIES)} coins, {bot_status})")

    def collect_coin_data(self, coin_symbol: str, max_posts: int = 50) -> List[Dict]:
        """
        Collect Reddit posts for a specific coin

        Args:
            coin_symbol: Coin symbol (e.g., 'DOGE')
            max_posts: Maximum posts to collect per subreddit

        Returns:
            List of posts with sentiment analysis
        """
        if coin_symbol not in self.COIN_QUERIES:
            logging.error(f"Unknown coin: {coin_symbol}")
            return []

        queries = self.COIN_QUERIES[coin_symbol]
        all_posts = []

        logging.info(f"🔍 Collecting Reddit data for {coin_symbol}")

        with RedditScraper(self.config) as scraper:
            for query in queries:
                logging.info(f"   Searching for: {query}")

                # Search multiple subreddits
                posts = scraper.scrape_multiple_subreddits(
                    subreddits=self.SUBREDDITS,
                    query=query,
                    max_per_subreddit=max_posts // len(queries) // len(self.SUBREDDITS) + 1
                )

                for post in posts:
                    # Add sentiment analysis
                    sentiment = self.sentiment_analyzer.analyze_reddit_post(post)
                    post['sentiment_analysis'] = sentiment

                    all_posts.append(post)

        # Remove duplicates (same post_id)
        unique_posts = {}
        for post in all_posts:
            post_id = post.get('post_id')
            if post_id and post_id not in unique_posts:
                unique_posts[post_id] = post

        result = list(unique_posts.values())

        # Apply bot detection if enabled
        if self.enable_bot_detection and self.bot_detector and result:
            filtered_posts, bot_posts, stats = self.bot_detector.filter_bots_from_reddit(result)
            if stats['bot_posts'] > 0:
                logging.info(f"   Bot detection: {stats['bot_posts']}/{stats['total_posts']} posts filtered ({stats['bot_percentage']:.1f}%)")
            result = filtered_posts

        logging.info(f"Collected {len(result)} unique posts for {coin_symbol}")

        return result

    def collect_all_coins(self, max_posts_per_coin: int = 50) -> Dict[str, List[Dict]]:
        """
        Collect Reddit data for all tracked coins

        Args:
            max_posts_per_coin: Maximum posts per coin

        Returns:
            Dictionary mapping coin_symbol -> posts
        """
        results = {}

        for coin_symbol in self.COIN_QUERIES.keys():
            try:
                posts = self.collect_coin_data(coin_symbol, max_posts_per_coin)
                results[coin_symbol] = posts
            except Exception as e:
                logging.error(f"Error collecting data for {coin_symbol}: {e}")
                results[coin_symbol] = []

        total_posts = sum(len(posts) for posts in results.values())
        logging.info(f"✅ Total Reddit posts collected: {total_posts}")

        return results

    def aggregate_sentiment(self, posts: List[Dict]) -> Dict:
        """
        Aggregate sentiment scores from multiple posts

        Args:
            posts: List of posts with sentiment_analysis

        Returns:
            Aggregated sentiment metrics
        """
        if not posts:
            return {
                'sentiment_score': 0.0,
                'hype_score': 0.0,
                'post_count': 0,
                'total_engagement': 0
            }

        analyses = [post['sentiment_analysis'] for post in posts if 'sentiment_analysis' in post]

        # Calculate engagement
        total_engagement = sum(
            post.get('score', 0) + post.get('num_comments', 0)
            for post in posts
        )

        aggregated = self.sentiment_analyzer.aggregate_sentiment(analyses, 'reddit')
        aggregated['total_engagement'] = total_engagement

        return aggregated
