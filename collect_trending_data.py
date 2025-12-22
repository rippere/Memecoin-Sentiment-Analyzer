"""
Trending Coin Data Collection
==============================
Integrated script that:
1. Updates trending coin list
2. Collects social media data for trending coins
3. Stores sentiment scores in database

Run this script via GitHub Actions or cron job
"""

import sys
import logging
from pathlib import Path
from typing import Dict, List
from datetime import datetime

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from collectors.trending_tracker import TrendingTracker
from collectors.reddit_praw_collector import RedditPRAWCollector
from database.db_manager import DatabaseManager
from collectors.sentiment_analyzer import SentimentAnalyzer

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)


class TrendingDataCollector:
    """Orchestrates data collection for trending coins"""

    def __init__(self, max_posts_per_coin: int = 50):
        """
        Initialize trending data collector

        Args:
            max_posts_per_coin: Maximum Reddit posts to collect per coin
        """
        self.max_posts_per_coin = max_posts_per_coin
        self.db = DatabaseManager()
        self.trending_tracker = TrendingTracker(max_trending_coins=50)
        self.sentiment_analyzer = SentimentAnalyzer()

        # Initialize Reddit collector (will fail if credentials not set)
        try:
            self.reddit_collector = RedditPRAWCollector(use_auth=True)
            self.reddit_enabled = True
        except ValueError as e:
            logging.warning(f"Reddit collector not available: {e}")
            logging.warning("Skipping Reddit data collection")
            self.reddit_enabled = False

    def update_trending_coins(self) -> Dict:
        """
        Update the list of trending coins

        Returns:
            Dictionary with update statistics
        """
        logging.info("=" * 60)
        logging.info("STEP 1: Updating trending coins")
        logging.info("=" * 60)

        stats = self.trending_tracker.update_trending_coins(self.db)

        logging.info(f"Trending update complete:")
        logging.info(f"  - Active trending coins: {stats['active_trending']}")
        logging.info(f"  - Newly added: {stats['new_trending']}")
        logging.info(f"  - Removed from trending: {stats['removed_trending']}")

        return stats

    def get_active_coins(self) -> List[Dict]:
        """
        Get currently trending coins from database

        Returns:
            List of coin dictionaries with id, symbol, name
        """
        active_coins = self.trending_tracker.get_active_coins(
            self.db,
            include_control=True  # Include Bitcoin for comparison
        )

        logging.info(f"\nCollecting data for {len(active_coins)} coins")

        return active_coins

    def collect_reddit_data(self, coins: List[Dict]) -> Dict[str, List[Dict]]:
        """
        Collect Reddit data for trending coins

        Args:
            coins: List of coin dictionaries

        Returns:
            Dictionary mapping coin_symbol -> posts
        """
        if not self.reddit_enabled:
            logging.warning("Reddit collector not enabled, skipping")
            return {}

        logging.info("\n" + "=" * 60)
        logging.info("STEP 2: Collecting Reddit data")
        logging.info("=" * 60)

        results = self.reddit_collector.collect_trending_coins_data(
            coins,
            max_posts_per_coin=self.max_posts_per_coin
        )

        # Summary
        total_posts = sum(len(posts) for posts in results.values())
        coins_with_data = sum(1 for posts in results.values() if len(posts) > 0)

        logging.info(f"\nReddit collection complete:")
        logging.info(f"  - Total posts: {total_posts}")
        logging.info(f"  - Coins with data: {coins_with_data}/{len(coins)}")

        return results

    def store_reddit_data(self, reddit_data: Dict[str, List[Dict]]) -> int:
        """
        Store Reddit posts and sentiment in database

        Args:
            reddit_data: Dictionary mapping coin_symbol -> posts

        Returns:
            Number of posts stored
        """
        logging.info("\n" + "=" * 60)
        logging.info("STEP 3: Storing data in database")
        logging.info("=" * 60)

        total_stored = 0

        for coin_symbol, posts in reddit_data.items():
            if not posts:
                continue

            # Prepare posts for batch insertion
            posts_for_db = []

            for post in posts:
                try:
                    # Convert to database format
                    post_data = {
                        'post_id': post['post_id'],
                        'post_url': post.get('permalink', ''),
                        'title': post.get('title', ''),
                        'body': post.get('text', ''),
                        'author': post.get('author', '[deleted]'),
                        'subreddit': post.get('subreddit', 'unknown'),
                        'flair': post.get('flair'),
                        'score': post.get('score', 0),
                        'num_comments': post.get('num_comments', 0),
                        'upvote_ratio': post.get('upvote_ratio', 0.5),
                        'is_self': True,
                        'created_utc': post.get('created_utc', datetime.now().timestamp()),
                        'query': coin_symbol.lower()
                    }

                    posts_for_db.append(post_data)

                except Exception as e:
                    logging.error(f"Error preparing post {post.get('post_id')}: {e}")
                    continue

            # Batch insert Reddit posts
            if posts_for_db:
                stored = self.db.add_reddit_posts_batch(coin_symbol, posts_for_db)
                total_stored += stored
                logging.info(f"  Stored {stored} posts for {coin_symbol}")

            # Store aggregated sentiment
            try:
                sentiment_agg = self.reddit_collector.aggregate_sentiment(posts)
                sentiment_data = {
                    'timestamp': datetime.now(),
                    'source': 'reddit',
                    'sentiment_score': sentiment_agg.get('sentiment_score', 0.0),
                    'sentiment_positive': sentiment_agg.get('positive_ratio', 0.0),
                    'sentiment_negative': sentiment_agg.get('negative_ratio', 0.0),
                    'sentiment_neutral': sentiment_agg.get('neutral_ratio', 0.0),
                    'post_count': len(posts),
                    'total_engagement': sentiment_agg.get('total_engagement', 0),
                    'hype_score': sentiment_agg.get('hype_score', 0.0),
                    'hype_keywords_count': sentiment_agg.get('hype_keywords', 0),
                    'hype_emojis_count': sentiment_agg.get('hype_emojis', 0)
                }

                self.db.add_sentiment_score(coin_symbol, sentiment_data)
                logging.info(f"  Stored sentiment for {coin_symbol} (score: {sentiment_agg.get('sentiment_score', 0):.2f})")

            except Exception as e:
                logging.error(f"Error storing sentiment for {coin_symbol}: {e}")

        logging.info(f"\nStored {total_stored} posts in database")

        return total_stored

    def run_collection(self) -> Dict:
        """
        Run the full collection pipeline

        Returns:
            Statistics about the collection run
        """
        start_time = datetime.now()

        logging.info("=" * 60)
        logging.info("TRENDING COIN DATA COLLECTION")
        logging.info(f"Started at: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        logging.info("=" * 60)

        # Step 1: Update trending coins
        trending_stats = self.update_trending_coins()

        # Step 2: Get active coins
        active_coins = self.get_active_coins()

        # Step 3: Collect Reddit data
        reddit_data = self.collect_reddit_data(active_coins)

        # Step 4: Store in database
        posts_stored = self.store_reddit_data(reddit_data)

        # Summary
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        stats = {
            'start_time': start_time.isoformat(),
            'end_time': end_time.isoformat(),
            'duration_seconds': duration,
            'coins_processed': len(active_coins),
            'posts_collected': sum(len(posts) for posts in reddit_data.values()),
            'posts_stored': posts_stored,
            'trending_stats': trending_stats
        }

        logging.info("\n" + "=" * 60)
        logging.info("COLLECTION COMPLETE")
        logging.info("=" * 60)
        logging.info(f"Duration: {duration:.1f} seconds")
        logging.info(f"Coins processed: {stats['coins_processed']}")
        logging.info(f"Posts collected: {stats['posts_collected']}")
        logging.info(f"Posts stored: {stats['posts_stored']}")
        logging.info("=" * 60)

        return stats


def main():
    """Run data collection"""
    try:
        collector = TrendingDataCollector(max_posts_per_coin=50)
        stats = collector.run_collection()

        # Exit with success
        sys.exit(0)

    except Exception as e:
        logging.error(f"Collection failed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
