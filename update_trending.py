"""
Update Trending Coins
=====================
Standalone script to update trending coins rotation
Run this periodically (e.g., every 6-12 hours) to refresh trending coins
"""

import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from collectors.trending_tracker import TrendingTracker
from database.db_manager import DatabaseManager

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("logs/trending_updates.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


def main():
    """Update trending coins in database"""
    logger.info("=" * 60)
    logger.info("TRENDING COINS UPDATE STARTED")
    logger.info("=" * 60)

    try:
        # Initialize database and tracker
        db = DatabaseManager()
        tracker = TrendingTracker(max_trending_coins=50)

        # Update trending coins
        logger.info("Fetching latest trending coins from CoinGecko...")
        stats = tracker.update_trending_coins(db)

        logger.info("")
        logger.info("UPDATE SUMMARY:")
        logger.info(f"  New coins added: {stats['new']}")
        logger.info(f"  Coins updated: {stats['updated']}")
        logger.info(f"  Coins archived: {stats['archived']}")
        logger.info(f"  Errors: {stats.get('errors', 0)}")

        # Show active coins
        active_coins = tracker.get_active_coins(db)
        logger.info(f"\nCurrently tracking {len(active_coins)} active coins")

        if active_coins:
            logger.info("\nTop 10 trending coins:")
            for coin in active_coins[:10]:
                rank = coin.get('trending_rank', 'N/A')
                rank_str = f"#{rank}" if rank else "N/A"
                logger.info(f"  {rank_str:5} {coin['symbol']:6} - {coin['name']}")

        # Cleanup
        tracker.close()
        db.close()

        logger.info("\nTRENDING UPDATE COMPLETED SUCCESSFULLY")
        logger.info("=" * 60)

        return 0

    except Exception as e:
        logger.error(f"TRENDING UPDATE FAILED: {e}", exc_info=True)
        logger.info("=" * 60)
        return 1


if __name__ == "__main__":
    exit(main())
