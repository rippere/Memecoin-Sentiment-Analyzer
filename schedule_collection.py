"""
Automated Data Collection Scheduler
===================================
Schedules regular data collection using APScheduler
Can run continuously or as a service
"""

import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from collectors.unified_collector import UnifiedCollector
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
import logging
from datetime import datetime
import argparse

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler('logs/scheduler.log'),
        logging.StreamHandler()
    ]
)


class CollectionScheduler:
    """
    Manages scheduled data collection
    """

    def __init__(self, db_path: str = None, headless: bool = True):
        """
        Initialize scheduler

        Args:
            db_path: Path to database
            headless: Run scrapers headless
        """
        self.scraper_config = {
            'headless': headless,
            'min_delay': 2,
            'max_delay': 5
        }
        self.db_path = db_path
        self.scheduler = BlockingScheduler()
        logging.info("✅ Scheduler initialized")

    def collect_data(self, collect_prices: bool = True,
                     collect_reddit: bool = True,
                     collect_tiktok: bool = True):
        """
        Run data collection cycle
        This is the function that gets scheduled
        """
        logging.info("\n" + "=" * 70)
        logging.info(f"🕐 SCHEDULED COLLECTION STARTED: {datetime.now()}")
        logging.info("=" * 70)

        try:
            collector = UnifiedCollector(
                db_path=self.db_path,
                scraper_config=self.scraper_config
            )

            collector.collect_all(
                collect_prices=collect_prices,
                collect_reddit=collect_reddit,
                collect_tiktok=collect_tiktok
            )

            stats = collector.get_stats()
            logging.info("\n📊 Current Database Stats:")
            for key, value in stats.items():
                logging.info(f"   {key}: {value}")

            collector.close()
            logging.info("✅ Scheduled collection completed successfully\n")

        except Exception as e:
            logging.error(f"❌ Scheduled collection failed: {e}\n")
            raise

    def schedule_interval(self, minutes: int = 30,
                          collect_prices: bool = True,
                          collect_reddit: bool = True,
                          collect_tiktok: bool = True):
        """
        Schedule collection to run every N minutes

        Args:
            minutes: Interval in minutes
            collect_prices: Whether to collect prices
            collect_reddit: Whether to collect Reddit
            collect_tiktok: Whether to collect TikTok
        """
        self.scheduler.add_job(
            self.collect_data,
            trigger=IntervalTrigger(minutes=minutes),
            kwargs={
                'collect_prices': collect_prices,
                'collect_reddit': collect_reddit,
                'collect_tiktok': collect_tiktok
            },
            id='collection_interval',
            name=f'Collect data every {minutes} minutes',
            replace_existing=True
        )
        logging.info(f"📅 Scheduled: Collect data every {minutes} minutes")

    def schedule_cron(self, hour: str = "*", minute: str = "0",
                      collect_prices: bool = True,
                      collect_reddit: bool = True,
                      collect_tiktok: bool = True):
        """
        Schedule collection using cron-style timing

        Args:
            hour: Hour(s) to run (e.g., "9,12,15,18" or "*")
            minute: Minute to run (e.g., "0", "30")
            collect_prices: Whether to collect prices
            collect_reddit: Whether to collect Reddit
            collect_tiktok: Whether to collect TikTok
        """
        self.scheduler.add_job(
            self.collect_data,
            trigger=CronTrigger(hour=hour, minute=minute),
            kwargs={
                'collect_prices': collect_prices,
                'collect_reddit': collect_reddit,
                'collect_tiktok': collect_tiktok
            },
            id='collection_cron',
            name=f'Collect data at {hour}:{minute}',
            replace_existing=True
        )
        logging.info(f"📅 Scheduled: Collect data at hour={hour}, minute={minute}")

    def run_once_now(self, collect_prices: bool = True,
                     collect_reddit: bool = True,
                     collect_tiktok: bool = True):
        """
        Run collection immediately (one-time)
        """
        logging.info("🚀 Running immediate collection (one-time)")
        self.collect_data(collect_prices, collect_reddit, collect_tiktok)

    def start(self):
        """
        Start the scheduler (blocks until interrupted)
        """
        logging.info("\n" + "=" * 70)
        logging.info("🚀 SCHEDULER STARTING")
        logging.info(f"   Time: {datetime.now()}")
        logging.info(f"   Jobs: {len(self.scheduler.get_jobs())}")
        logging.info("   Press Ctrl+C to stop")
        logging.info("=" * 70 + "\n")

        try:
            self.scheduler.start()
        except (KeyboardInterrupt, SystemExit):
            logging.info("\n⏹️  Scheduler stopped by user")
            self.shutdown()

    def shutdown(self):
        """Gracefully shutdown scheduler"""
        self.scheduler.shutdown(wait=False)
        logging.info("✅ Scheduler shut down")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='Memecoin Data Collection Scheduler')

    # Schedule type
    parser.add_argument('--mode', choices=['interval', 'cron', 'once'], default='interval',
                        help='Scheduling mode (default: interval)')

    # Interval options
    parser.add_argument('--minutes', type=int, default=30,
                        help='Interval in minutes (default: 30)')

    # Cron options
    parser.add_argument('--hour', type=str, default='*',
                        help='Cron hour expression (default: *)')
    parser.add_argument('--minute', type=str, default='0',
                        help='Cron minute expression (default: 0)')

    # Collection options
    parser.add_argument('--no-prices', action='store_true',
                        help='Skip price collection')
    parser.add_argument('--no-reddit', action='store_true',
                        help='Skip Reddit collection')
    parser.add_argument('--no-tiktok', action='store_true',
                        help='Skip TikTok collection')

    # Other options
    parser.add_argument('--headless', action='store_true', default=True,
                        help='Run scrapers in headless mode (default: True)')
    parser.add_argument('--db-path', type=str,
                        help='Path to database file')

    args = parser.parse_args()

    # Create logs directory
    Path('logs').mkdir(exist_ok=True)

    # Initialize scheduler
    scheduler = CollectionScheduler(
        db_path=args.db_path,
        headless=args.headless
    )

    collect_prices = not args.no_prices
    collect_reddit = not args.no_reddit
    collect_tiktok = not args.no_tiktok

    # Setup schedule based on mode
    if args.mode == 'once':
        # Run once and exit
        scheduler.run_once_now(collect_prices, collect_reddit, collect_tiktok)
        return

    elif args.mode == 'interval':
        # Run every N minutes
        scheduler.schedule_interval(
            minutes=args.minutes,
            collect_prices=collect_prices,
            collect_reddit=collect_reddit,
            collect_tiktok=collect_tiktok
        )

    elif args.mode == 'cron':
        # Run on cron schedule
        scheduler.schedule_cron(
            hour=args.hour,
            minute=args.minute,
            collect_prices=collect_prices,
            collect_reddit=collect_reddit,
            collect_tiktok=collect_tiktok
        )

    # Start scheduler
    scheduler.start()


if __name__ == "__main__":
    main()
