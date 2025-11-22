"""
Unified Data Collector
======================
Orchestrates all data collection (Price, Reddit, TikTok)
Stores results in database with sentiment analysis
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from database.db_manager import DatabaseManager
from collectors.price_collector import PriceCollector
from collectors.reddit_collector import RedditCollector
from collectors.tiktok_collector import TikTokCollector
from collectors.quality_monitor import QualityMonitor
import logging
from datetime import datetime
from typing import Dict, List
import time

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)


class UnifiedCollector:
    """
    Main orchestrator for all data collection
    Coordinates Price, Reddit, and TikTok collectors
    """

    def __init__(self, db_path: str = None, scraper_config: Dict = None):
        """
        Initialize unified collector

        Args:
            db_path: Path to SQLite database
            scraper_config: Configuration for scrapers
        """
        self.db = DatabaseManager(db_path=db_path)

        # Default scraper config
        if scraper_config is None:
            scraper_config = {
                'headless': True,
                'min_delay': 2,
                'max_delay': 5
            }

        self.scraper_config = scraper_config
        self.price_collector = PriceCollector()
        logging.info("✅ Unified collector initialized")

    def collect_all(self, collect_prices: bool = True,
                    collect_reddit: bool = True,
                    collect_tiktok: bool = True):
        """
        Run complete data collection cycle

        Args:
            collect_prices: Whether to collect price data
            collect_reddit: Whether to collect Reddit data
            collect_tiktok: Whether to collect TikTok data
        """
        logging.info("=" * 70)
        logging.info("🚀 STARTING DATA COLLECTION CYCLE")
        logging.info(f"   Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logging.info("=" * 70)

        start_time = time.time()
        total_records = 0
        total_errors = 0

        # Get all tracked coins
        coin_symbols = list(self.price_collector.COIN_IDS.keys())

        logging.info(f"📊 Tracking {len(coin_symbols)} coins: {', '.join(coin_symbols)}")

        # Step 1: Collect price data
        if collect_prices:
            try:
                count, errors = self._collect_prices(coin_symbols)
                total_records += count
                total_errors += errors
            except Exception as e:
                logging.error(f"❌ Price collection failed: {e}")
                total_errors += 1

        # Step 2: Collect Reddit data
        if collect_reddit:
            try:
                count, errors = self._collect_reddit(coin_symbols)
                total_records += count
                total_errors += errors
            except Exception as e:
                logging.error(f"❌ Reddit collection failed: {e}")
                total_errors += 1

        # Step 3: Collect TikTok data
        if collect_tiktok:
            try:
                count, errors = self._collect_tiktok(coin_symbols)
                total_records += count
                total_errors += errors
            except Exception as e:
                logging.error(f"❌ TikTok collection failed: {e}")
                total_errors += 1

        # Log completion
        duration = time.time() - start_time
        status = 'success' if total_errors == 0 else 'partial' if total_records > 0 else 'failed'

        self.db.log_collection(
            collector_type='unified',
            status=status,
            records=total_records,
            errors=total_errors,
            duration=duration
        )

        logging.info("=" * 70)
        logging.info(f"✅ COLLECTION CYCLE COMPLETE")
        logging.info(f"   Total records: {total_records}")
        logging.info(f"   Errors: {total_errors}")
        logging.info(f"   Duration: {duration:.1f}s")
        logging.info("=" * 70)

        # Return counts for scheduler
        return (total_records, total_errors)

    def _collect_prices(self, coin_symbols: List[str]) -> tuple:
        """Collect price data for all coins"""
        logging.info("\n💰 Collecting price data...")
        start_time = time.time()
        count = 0
        errors = 0

        try:
            price_data = self.price_collector.fetch_coin_data(coin_symbols)

            # Quality assessment
            quality_monitor = QualityMonitor(db_manager=self.db)
            price_list = list(price_data.values())
            quality_metrics = quality_monitor.assess_collection_quality(price_list, 'price')

            # Log quality issues if any
            if quality_metrics['status'] in ['POOR', 'FAILED']:
                logging.warning(f"   Data quality issue: {quality_metrics['status']} (score: {quality_metrics['quality_score']:.1f}/100)")

            for symbol, data in price_data.items():
                try:
                    self.db.add_price(symbol, data)
                    count += 1
                except Exception as e:
                    logging.error(f"   Error saving price for {symbol}: {e}")
                    errors += 1

            duration = time.time() - start_time
            logging.info(f"   ✅ Collected {count} prices in {duration:.1f}s (Quality: {quality_metrics['status']})")

            self.db.log_collection('price', 'success', count, errors, duration)

        except Exception as e:
            logging.error(f"   ❌ Price collection error: {e}")
            errors += 1
            self.db.log_collection('price', 'failed', 0, 1, 0, str(e))

        return count, errors

    def _collect_reddit(self, coin_symbols: List[str]) -> tuple:
        """Collect Reddit data for all coins"""
        logging.info("\n🔍 Collecting Reddit data...")
        start_time = time.time()
        count = 0
        errors = 0

        try:
            reddit_collector = RedditCollector(self.scraper_config)
            all_posts = []

            for symbol in coin_symbols:
                try:
                    # Collect posts
                    posts = reddit_collector.collect_coin_data(symbol, max_posts=20)
                    all_posts.extend(posts)

                    # Save to database
                    for post in posts:
                        try:
                            self.db.add_reddit_post(symbol, post)
                            count += 1
                        except Exception as e:
                            logging.debug(f"   Error saving post: {e}")
                            errors += 1

                    # Calculate and save aggregated sentiment
                    if posts:
                        sentiment = reddit_collector.aggregate_sentiment(posts)
                        sentiment['timestamp'] = datetime.utcnow()
                        self.db.add_sentiment_score(symbol, sentiment)

                except Exception as e:
                    logging.error(f"   Error collecting Reddit for {symbol}: {e}")
                    errors += 1

            # Quality assessment on all collected posts
            if all_posts:
                quality_monitor = QualityMonitor(db_manager=self.db)
                quality_metrics = quality_monitor.assess_collection_quality(all_posts, 'reddit')

                if quality_metrics['status'] in ['POOR', 'FAILED']:
                    logging.warning(f"   Data quality issue: {quality_metrics['status']} (score: {quality_metrics['quality_score']:.1f}/100)")

                duration = time.time() - start_time
                logging.info(f"   ✅ Collected {count} Reddit posts in {duration:.1f}s (Quality: {quality_metrics['status']})")
            else:
                duration = time.time() - start_time
                logging.info(f"   ✅ Collected {count} Reddit posts in {duration:.1f}s")

            self.db.log_collection('reddit', 'success', count, errors, duration)

        except Exception as e:
            logging.error(f"   ❌ Reddit collection error: {e}")
            errors += 1
            self.db.log_collection('reddit', 'failed', 0, 1, 0, str(e))

        return count, errors

    def _collect_tiktok(self, coin_symbols: List[str]) -> tuple:
        """Collect TikTok data for all coins"""
        logging.info("\n🎵 Collecting TikTok data...")
        start_time = time.time()
        count = 0
        errors = 0

        try:
            tiktok_collector = TikTokCollector(self.scraper_config)
            all_videos = []

            for symbol in coin_symbols:
                try:
                    # Collect videos
                    videos = tiktok_collector.collect_coin_data(symbol, max_videos=15)
                    all_videos.extend(videos)

                    # Save to database
                    for video in videos:
                        try:
                            self.db.add_tiktok_video(symbol, video)
                            count += 1
                        except Exception as e:
                            logging.debug(f"   Error saving video: {e}")
                            errors += 1

                    # Calculate and save aggregated sentiment
                    if videos:
                        sentiment = tiktok_collector.aggregate_sentiment(videos)
                        sentiment['timestamp'] = datetime.utcnow()
                        self.db.add_sentiment_score(symbol, sentiment)

                except Exception as e:
                    logging.error(f"   Error collecting TikTok for {symbol}: {e}")
                    errors += 1

            # Quality assessment on all collected videos
            if all_videos:
                quality_monitor = QualityMonitor(db_manager=self.db)
                quality_metrics = quality_monitor.assess_collection_quality(all_videos, 'tiktok')

                if quality_metrics['status'] in ['POOR', 'FAILED']:
                    logging.warning(f"   Data quality issue: {quality_metrics['status']} (score: {quality_metrics['quality_score']:.1f}/100)")

                duration = time.time() - start_time
                logging.info(f"   ✅ Collected {count} TikTok videos in {duration:.1f}s (Quality: {quality_metrics['status']})")
            else:
                duration = time.time() - start_time
                logging.info(f"   ✅ Collected {count} TikTok videos in {duration:.1f}s")

            self.db.log_collection('tiktok', 'success', count, errors, duration)

        except Exception as e:
            logging.error(f"   ❌ TikTok collection error: {e}")
            errors += 1
            self.db.log_collection('tiktok', 'failed', 0, 1, 0, str(e))

        return count, errors

    def get_stats(self) -> Dict:
        """Get database statistics"""
        return self.db.get_stats()

    def close(self):
        """Close all connections"""
        self.price_collector.close()
        self.db.close()
        logging.info("Unified collector closed")


def main():
    """
    Main entry point for unified collector
    Can be run standalone or scheduled
    """
    import argparse

    parser = argparse.ArgumentParser(description='Memecoin Unified Data Collector')
    parser.add_argument('--no-prices', action='store_true', help='Skip price collection')
    parser.add_argument('--no-reddit', action='store_true', help='Skip Reddit collection')
    parser.add_argument('--no-tiktok', action='store_true', help='Skip TikTok collection')
    parser.add_argument('--headless', action='store_true', default=True, help='Run scrapers headless')
    parser.add_argument('--db-path', type=str, help='Path to database file')

    args = parser.parse_args()

    # Create collector
    scraper_config = {
        'headless': args.headless,
        'min_delay': 2,
        'max_delay': 5
    }

    collector = UnifiedCollector(db_path=args.db_path, scraper_config=scraper_config)

    try:
        # Run collection
        collector.collect_all(
            collect_prices=not args.no_prices,
            collect_reddit=not args.no_reddit,
            collect_tiktok=not args.no_tiktok
        )

        # Show stats
        stats = collector.get_stats()
        logging.info("\n📊 DATABASE STATISTICS:")
        for key, value in stats.items():
            logging.info(f"   {key}: {value}")

    except KeyboardInterrupt:
        logging.info("\n⏹️  Collection interrupted by user")
    except Exception as e:
        logging.error(f"\n❌ Collection failed: {e}")
        raise
    finally:
        collector.close()


if __name__ == "__main__":
    main()
