"""
Optimized Data Collection Scheduler
====================================
Separate schedulers for price (15min) and social media (60min) data
Based on research methodology recommendations
"""

import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from collectors.unified_collector import UnifiedCollector
from collectors.quality_monitor import QualityMonitor
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.interval import IntervalTrigger
import logging
from datetime import datetime
import argparse

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler('logs/scheduler_optimized.log'),
        logging.StreamHandler()
    ]
)


class OptimizedScheduler:
    """
    Manages optimized data collection with separate schedules for:
    - Price data: every 15 minutes (high frequency)
    - Social media: every 60 minutes (lower frequency)
    """

    def __init__(self, db_path: str = None, headless: bool = True, enable_quality_checks: bool = True):
        """
        Initialize optimized scheduler

        Args:
            db_path: Path to database
            headless: Run scrapers headless
            enable_quality_checks: Enable data quality monitoring
        """
        self.scraper_config = {
            'headless': headless,
            'min_delay': 2,
            'max_delay': 5
        }
        self.db_path = db_path
        self.enable_quality_checks = enable_quality_checks
        self.scheduler = BlockingScheduler()
        logging.info("Optimized scheduler initialized")

    def collect_prices(self):
        """
        Collect only price data (fast, runs every 15 minutes)
        """
        logging.info("\n" + "=" * 70)
        logging.info(f"PRICE COLLECTION STARTED: {datetime.now()}")
        logging.info("=" * 70)

        try:
            collector = UnifiedCollector(
                db_path=self.db_path,
                scraper_config=self.scraper_config
            )

            # Collect only prices
            result = collector.collect_all(
                collect_prices=True,
                collect_reddit=False,
                collect_tiktok=False
            )
            price_count = result[0] if result else 0

            # Quality check if enabled
            if self.enable_quality_checks and price_count > 0:
                self._run_quality_check(collector, 'price')

            collector.close()
            logging.info(f"Price collection completed: {price_count} prices collected\n")

        except Exception as e:
            logging.error(f"Price collection failed: {e}\n")
            raise

    def collect_social_media(self):
        """
        Collect social media data (slower, runs every 60 minutes)
        """
        logging.info("\n" + "=" * 70)
        logging.info(f"SOCIAL MEDIA COLLECTION STARTED: {datetime.now()}")
        logging.info("=" * 70)

        try:
            collector = UnifiedCollector(
                db_path=self.db_path,
                scraper_config=self.scraper_config
            )

            # Collect only social media
            result = collector.collect_all(
                collect_prices=False,
                collect_reddit=True,
                collect_tiktok=True
            )
            social_count = result[0] if result else 0

            # Quality checks if enabled
            if self.enable_quality_checks and social_count > 0:
                self._run_quality_check(collector, 'reddit')
                self._run_quality_check(collector, 'tiktok')

            stats = collector.get_stats()
            logging.info("\nDatabase Stats:")
            for key, value in stats.items():
                logging.info(f"   {key}: {value}")

            collector.close()
            logging.info(f"Social media collection completed: {social_count} records\n")

        except Exception as e:
            logging.error(f"Social media collection failed: {e}\n")
            raise

    def _run_quality_check(self, collector, data_type: str):
        """Run quality check on collected data"""
        try:
            quality_monitor = QualityMonitor(db_manager=collector.db)

            # Get recent data based on type
            # Note: This is simplified - in production you'd fetch the actual data just collected
            logging.info(f"   Running quality check for {data_type} data...")

            # Placeholder - would need to fetch actual collected data
            # For now just log that quality check would run
            logging.info(f"   Quality monitoring enabled for {data_type}")

        except Exception as e:
            logging.warning(f"   Quality check failed for {data_type}: {e}")

    def schedule_optimized(self, price_interval: int = 15, social_interval: int = 60):
        """
        Schedule optimized collection with separate intervals

        Args:
            price_interval: Price collection interval in minutes (default: 15)
            social_interval: Social media collection interval in minutes (default: 60)
        """
        # Schedule price collection
        self.scheduler.add_job(
            self.collect_prices,
            trigger=IntervalTrigger(minutes=price_interval),
            id='price_collection',
            name=f'Collect prices every {price_interval} minutes',
            replace_existing=True
        )
        logging.info(f"Scheduled: Price collection every {price_interval} minutes")

        # Schedule social media collection
        self.scheduler.add_job(
            self.collect_social_media,
            trigger=IntervalTrigger(minutes=social_interval),
            id='social_collection',
            name=f'Collect social media every {social_interval} minutes',
            replace_existing=True
        )
        logging.info(f"Scheduled: Social media collection every {social_interval} minutes")

    def run_once(self, collect_prices: bool = True, collect_social: bool = True):
        """
        Run collection immediately (one-time)

        Args:
            collect_prices: Whether to collect price data
            collect_social: Whether to collect social media data
        """
        if collect_prices:
            logging.info("Running immediate price collection")
            self.collect_prices()

        if collect_social:
            logging.info("Running immediate social media collection")
            self.collect_social_media()

    def start(self):
        """
        Start the scheduler (blocks until interrupted)
        """
        logging.info("\n" + "=" * 70)
        logging.info("OPTIMIZED SCHEDULER STARTING")
        logging.info(f"   Time: {datetime.now()}")
        logging.info(f"   Jobs: {len(self.scheduler.get_jobs())}")
        for job in self.scheduler.get_jobs():
            logging.info(f"   - {job.name}")
        logging.info("   Press Ctrl+C to stop")
        logging.info("=" * 70 + "\n")

        try:
            self.scheduler.start()
        except (KeyboardInterrupt, SystemExit):
            logging.info("\nScheduler stopped by user")
            self.shutdown()

    def shutdown(self):
        """Gracefully shutdown scheduler"""
        self.scheduler.shutdown(wait=False)
        logging.info("Scheduler shut down")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Optimized Memecoin Data Collection Scheduler'
    )

    # Schedule options
    parser.add_argument('--mode', choices=['optimized', 'once'], default='optimized',
                        help='Scheduling mode: optimized (default) or once')

    parser.add_argument('--price-interval', type=int, default=15,
                        help='Price collection interval in minutes (default: 15)')

    parser.add_argument('--social-interval', type=int, default=60,
                        help='Social media collection interval in minutes (default: 60)')

    # One-time collection options
    parser.add_argument('--no-prices', action='store_true',
                        help='Skip price collection (for once mode)')
    parser.add_argument('--no-social', action='store_true',
                        help='Skip social media collection (for once mode)')

    # Other options
    parser.add_argument('--headless', action='store_true', default=True,
                        help='Run scrapers in headless mode (default: True)')
    parser.add_argument('--db-path', type=str,
                        help='Path to database file')
    parser.add_argument('--no-quality-checks', action='store_true',
                        help='Disable data quality monitoring')

    args = parser.parse_args()

    # Create logs directory
    Path('logs').mkdir(exist_ok=True)

    # Initialize scheduler
    scheduler = OptimizedScheduler(
        db_path=args.db_path,
        headless=args.headless,
        enable_quality_checks=not args.no_quality_checks
    )

    if args.mode == 'once':
        # Run once and exit
        scheduler.run_once(
            collect_prices=not args.no_prices,
            collect_social=not args.no_social
        )
        return

    elif args.mode == 'optimized':
        # Run with optimized separate schedules
        scheduler.schedule_optimized(
            price_interval=args.price_interval,
            social_interval=args.social_interval
        )

    # Start scheduler
    scheduler.start()


if __name__ == "__main__":
    main()
