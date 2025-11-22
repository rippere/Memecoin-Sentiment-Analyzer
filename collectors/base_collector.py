"""
Base Collector Class
====================
Common functionality for social media collectors (Reddit, TikTok, etc.)
"""

import sys
from pathlib import Path
from abc import ABC, abstractmethod
from typing import Dict, List, Optional
import logging

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from collectors.sentiment_analyzer import SentimentAnalyzer
from collectors.bot_detector import BotDetector

logger = logging.getLogger(__name__)


class BaseSocialCollector(ABC):
    """
    Abstract base class for social media collectors.
    Provides common functionality for config management, sentiment analysis,
    bot detection, and coin query loading.
    """

    # Subclasses should override these
    SOURCE_NAME = "unknown"
    DEFAULT_CONFIG = {
        'headless': True,
        'min_delay': 2,
        'max_delay': 5
    }
    DEFAULT_QUERIES = {}

    def __init__(
        self,
        config: Optional[Dict] = None,
        enable_bot_detection: bool = True
    ):
        """
        Initialize base collector.

        Args:
            config: Configuration for scraper (headless, delays, etc.)
            enable_bot_detection: Whether to filter bot accounts
        """
        # Merge provided config with defaults
        self.config = {**self.DEFAULT_CONFIG, **(config or {})}
        self.enable_bot_detection = enable_bot_detection

        # Initialize shared components
        self.sentiment_analyzer = SentimentAnalyzer()
        self.bot_detector = BotDetector() if enable_bot_detection else None

        # Load coin queries from config
        self.coin_queries = self._load_coin_queries()

        # Log initialization
        bot_status = "with bot detection" if enable_bot_detection else "without bot detection"
        logger.info(
            f"{self.SOURCE_NAME} collector initialized "
            f"({len(self.coin_queries)} coins, {bot_status})"
        )

    def _load_coin_queries(self) -> Dict[str, List[str]]:
        """Load coin search queries from configuration."""
        try:
            from config.coin_config import get_coin_config
            coin_config = get_coin_config()
            return {
                symbol: coin_config.get_social_queries(symbol)
                for symbol in coin_config.get_coin_symbols()
            }
        except Exception as e:
            logger.warning(f"Could not load queries from config: {e}, using defaults")
            return self.DEFAULT_QUERIES.copy()

    def get_queries_for_coin(self, coin_symbol: str) -> List[str]:
        """Get search queries for a specific coin."""
        return self.coin_queries.get(coin_symbol, [])

    def is_valid_coin(self, coin_symbol: str) -> bool:
        """Check if coin symbol is recognized."""
        return coin_symbol in self.coin_queries

    def filter_bots(self, items: List[Dict], username_key: str = 'author') -> List[Dict]:
        """
        Filter out likely bot accounts from results.

        Args:
            items: List of posts/videos
            username_key: Key for username in item dict

        Returns:
            Filtered list with bots removed
        """
        if not self.enable_bot_detection or not self.bot_detector:
            return items

        filtered = []
        for item in items:
            username = item.get(username_key, '')
            if username and not self.bot_detector.is_likely_bot(username):
                filtered.append(item)
            else:
                logger.debug(f"Filtered likely bot: {username}")

        if len(filtered) < len(items):
            logger.info(f"Filtered {len(items) - len(filtered)} likely bots")

        return filtered

    def aggregate_sentiment_for_coin(
        self,
        analyses: List[Dict],
        coin_symbol: str
    ) -> Dict:
        """
        Aggregate sentiment analyses for a coin.

        Args:
            analyses: List of individual sentiment analyses
            coin_symbol: Coin symbol

        Returns:
            Aggregated sentiment data
        """
        aggregated = self.sentiment_analyzer.aggregate_sentiment(
            analyses, self.SOURCE_NAME
        )
        aggregated['coin_symbol'] = coin_symbol
        return aggregated

    @abstractmethod
    def collect_coin_data(self, coin_symbol: str, max_items: int = 50) -> List[Dict]:
        """
        Collect data for a specific coin. Must be implemented by subclasses.

        Args:
            coin_symbol: Coin symbol (e.g., 'DOGE')
            max_items: Maximum items to collect

        Returns:
            List of items with sentiment analysis
        """
        pass

    @abstractmethod
    def collect_all_coins(self, max_items_per_coin: int = 30) -> Dict[str, List[Dict]]:
        """
        Collect data for all tracked coins. Must be implemented by subclasses.

        Args:
            max_items_per_coin: Maximum items per coin

        Returns:
            Dictionary mapping coin symbols to collected items
        """
        pass
