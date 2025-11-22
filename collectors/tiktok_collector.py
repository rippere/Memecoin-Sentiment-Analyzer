"""
TikTok Data Collector
====================
Collects TikTok videos using the scraper and analyzes sentiment
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from scrapers.tiktok_scraper import TikTokScraper
from collectors.sentiment_analyzer import SentimentAnalyzer
from collectors.bot_detector import BotDetector
import logging
from typing import List, Dict

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


class TikTokCollector:
    """Collects and analyzes TikTok videos for meme coins"""

    def __init__(self, config: Dict = None, enable_bot_detection: bool = True):
        """
        Initialize TikTok collector

        Args:
            config: Configuration for scraper (headless, delays, etc.)
            enable_bot_detection: Whether to filter bot accounts (default: True)
        """
        if config is None:
            config = {
                'headless': True,
                'min_delay': 3,
                'max_delay': 6
            }

        self.config = config
        self.enable_bot_detection = enable_bot_detection
        self.sentiment_analyzer = SentimentAnalyzer()
        self.bot_detector = BotDetector() if enable_bot_detection else None

        # Load coin hashtags from config
        try:
            from config.coin_config import get_coin_config
            coin_config = get_coin_config()
            self.COIN_HASHTAGS = {
                symbol: coin_config.get_social_queries(symbol)
                for symbol in coin_config.get_coin_symbols()
            }
        except Exception as e:
            logging.warning(f"Could not load hashtags from config: {e}, using defaults")
            self.COIN_HASHTAGS = {
                'DOGE': ['dogecoin', 'doge'],
                'PEPE': ['pepe'],
                'SHIB': ['shiba', 'shib'],
            }

        bot_status = "with bot detection" if enable_bot_detection else "without bot detection"
        logging.info(f"TikTok collector initialized ({len(self.COIN_HASHTAGS)} coins, {bot_status})")

    def collect_coin_data(self, coin_symbol: str, max_videos: int = 30) -> List[Dict]:
        """
        Collect TikTok videos for a specific coin

        Args:
            coin_symbol: Coin symbol (e.g., 'DOGE')
            max_videos: Maximum videos to collect per hashtag

        Returns:
            List of videos with sentiment analysis
        """
        if coin_symbol not in self.COIN_HASHTAGS:
            logging.error(f"Unknown coin: {coin_symbol}")
            return []

        hashtags = self.COIN_HASHTAGS[coin_symbol]
        all_videos = []

        logging.info(f"🎵 Collecting TikTok data for {coin_symbol}")

        with TikTokScraper(self.config) as scraper:
            for hashtag in hashtags:
                logging.info(f"   Searching hashtag: #{hashtag}")

                try:
                    videos = scraper.scrape_hashtag(
                        hashtag,
                        max_results=max_videos // len(hashtags) + 1
                    )

                    for video in videos:
                        # Add sentiment analysis
                        sentiment = self.sentiment_analyzer.analyze_tiktok_video(video)
                        video['sentiment_analysis'] = sentiment

                        all_videos.append(video)

                except Exception as e:
                    logging.error(f"   Error scraping #{hashtag}: {e}")
                    continue

        # Remove duplicates (same video_id)
        unique_videos = {}
        for video in all_videos:
            video_id = video.get('video_id')
            if video_id and video_id not in unique_videos:
                unique_videos[video_id] = video

        result = list(unique_videos.values())

        # Apply bot detection if enabled
        if self.enable_bot_detection and self.bot_detector and result:
            filtered_videos, bot_videos, stats = self.bot_detector.filter_bots_from_tiktok(result)
            if stats['bot_videos'] > 0:
                logging.info(f"   Bot detection: {stats['bot_videos']}/{stats['total_videos']} videos filtered ({stats['bot_percentage']:.1f}%)")
            result = filtered_videos

        logging.info(f"Collected {len(result)} unique videos for {coin_symbol}")

        return result

    def collect_all_coins(self, max_videos_per_coin: int = 30) -> Dict[str, List[Dict]]:
        """
        Collect TikTok data for all tracked coins

        Args:
            max_videos_per_coin: Maximum videos per coin

        Returns:
            Dictionary mapping coin_symbol -> videos
        """
        results = {}

        for coin_symbol in self.COIN_HASHTAGS.keys():
            try:
                videos = self.collect_coin_data(coin_symbol, max_videos_per_coin)
                results[coin_symbol] = videos
            except Exception as e:
                logging.error(f"Error collecting data for {coin_symbol}: {e}")
                results[coin_symbol] = []

        total_videos = sum(len(videos) for videos in results.values())
        logging.info(f"✅ Total TikTok videos collected: {total_videos}")

        return results

    def aggregate_sentiment(self, videos: List[Dict]) -> Dict:
        """
        Aggregate sentiment scores from multiple videos

        Args:
            videos: List of videos with sentiment_analysis

        Returns:
            Aggregated sentiment metrics
        """
        if not videos:
            return {
                'sentiment_score': 0.0,
                'hype_score': 0.0,
                'post_count': 0,
                'total_engagement': 0
            }

        analyses = [video['sentiment_analysis'] for video in videos if 'sentiment_analysis' in video]

        # Calculate engagement (views + likes + comments + shares)
        total_engagement = sum(
            video.get('views', 0) +
            video.get('likes', 0) +
            video.get('comments', 0) +
            video.get('shares', 0)
            for video in videos
        )

        aggregated = self.sentiment_analyzer.aggregate_sentiment(analyses, 'tiktok')
        aggregated['total_engagement'] = total_engagement

        return aggregated
