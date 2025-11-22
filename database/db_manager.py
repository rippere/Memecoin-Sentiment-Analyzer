"""
Database Manager for Memecoin Sentiment Analyzer
==============================================
Handles all database operations with connection pooling and error handling
"""

from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.pool import StaticPool
from contextlib import contextmanager
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any

from .models import Base, Coin, Price, RedditPost, TikTokVideo, SentimentScore, CorrelationResult, DataCollectionLog

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


class DatabaseManager:
    """
    Central database management class
    Provides high-level operations for data storage and retrieval
    """

    def __init__(self, db_path: str = None, echo: bool = False):
        """
        Initialize database connection

        Args:
            db_path: Path to SQLite database file (defaults to data/memecoin.db)
            echo: If True, log all SQL statements
        """
        if db_path is None:
            # Default to data directory in project root
            project_root = Path(__file__).parent.parent
            db_dir = project_root / 'data'
            db_dir.mkdir(exist_ok=True)
            db_path = str(db_dir / 'memecoin.db')

        self.db_path = db_path
        self.engine = create_engine(
            f'sqlite:///{db_path}',
            echo=echo,
            connect_args={'check_same_thread': False},
            poolclass=StaticPool
        )

        # Create session factory
        session_factory = sessionmaker(bind=self.engine)
        self.Session = scoped_session(session_factory)

        # Create all tables
        Base.metadata.create_all(self.engine)
        logging.info(f"✅ Database initialized: {db_path}")

        # Initialize default coins
        self._initialize_coins()

    def _initialize_coins(self):
        """Initialize coins from config file"""
        try:
            from config.coin_config import get_coin_config
            coin_config = get_coin_config()
            coins_from_config = coin_config.get_all_coins()
        except Exception as e:
            logging.warning(f"Could not load coins from config: {e}, using defaults")
            coins_from_config = [
                {'symbol': 'DOGE', 'name': 'Dogecoin', 'coingecko_id': 'dogecoin'},
                {'symbol': 'PEPE', 'name': 'Pepe', 'coingecko_id': 'pepe'},
                {'symbol': 'SHIB', 'name': 'Shiba Inu', 'coingecko_id': 'shiba-inu'},
            ]

        with self.get_session() as session:
            for coin_data in coins_from_config:
                existing = session.query(Coin).filter_by(symbol=coin_data['symbol']).first()
                if not existing:
                    coin = Coin(**coin_data)
                    session.add(coin)
            session.commit()
            logging.info(f"✅ Initialized {len(coins_from_config)} coins")

    @contextmanager
    def get_session(self):
        """
        Context manager for database sessions
        Automatically commits on success, rolls back on error

        Usage:
            with db.get_session() as session:
                session.add(object)
        """
        session = self.Session()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logging.error(f"Database error: {e}")
            raise
        finally:
            session.close()

    # =========================================================================
    # COIN OPERATIONS
    # =========================================================================

    def get_coin_by_symbol(self, symbol: str) -> Optional[Coin]:
        """Get coin by symbol (e.g., 'DOGE')"""
        with self.get_session() as session:
            return session.query(Coin).filter_by(symbol=symbol.upper()).first()

    def get_all_coins(self) -> List[Coin]:
        """Get all tracked coins"""
        with self.get_session() as session:
            return session.query(Coin).all()

    # =========================================================================
    # PRICE OPERATIONS
    # =========================================================================

    def add_price(self, coin_symbol: str, price_data: Dict[str, Any]) -> Optional[Price]:
        """
        Add price data for a coin

        Args:
            coin_symbol: Coin symbol (e.g., 'DOGE')
            price_data: Dictionary with price information

        Returns:
            Price object or None if failed
        """
        with self.get_session() as session:
            coin = session.query(Coin).filter_by(symbol=coin_symbol.upper()).first()
            if not coin:
                logging.error(f"Coin {coin_symbol} not found")
                return None

            price = Price(
                coin_id=coin.id,
                timestamp=price_data.get('timestamp', datetime.utcnow()),
                price_usd=price_data['price_usd'],
                market_cap=price_data.get('market_cap'),
                volume_24h=price_data.get('volume_24h'),
                change_1h_pct=price_data.get('change_1h_pct'),
                change_24h_pct=price_data.get('change_24h_pct'),
                change_7d_pct=price_data.get('change_7d_pct')
            )
            session.add(price)
            session.commit()
            logging.debug(f"Added price: {coin_symbol} @ ${price_data['price_usd']}")
            return price

    def get_latest_price(self, coin_symbol: str) -> Optional[Price]:
        """Get most recent price for a coin"""
        with self.get_session() as session:
            coin = session.query(Coin).filter_by(symbol=coin_symbol.upper()).first()
            if not coin:
                return None
            return session.query(Price)\
                .filter_by(coin_id=coin.id)\
                .order_by(Price.timestamp.desc())\
                .first()

    def get_prices_timeframe(self, coin_symbol: str, hours: int = 24) -> List[Price]:
        """Get prices for last N hours"""
        with self.get_session() as session:
            coin = session.query(Coin).filter_by(symbol=coin_symbol.upper()).first()
            if not coin:
                return []

            cutoff = datetime.utcnow() - timedelta(hours=hours)
            return session.query(Price)\
                .filter(Price.coin_id == coin.id, Price.timestamp >= cutoff)\
                .order_by(Price.timestamp.desc())\
                .all()

    # =========================================================================
    # REDDIT OPERATIONS
    # =========================================================================

    def add_reddit_post(self, coin_symbol: str, post_data: Dict[str, Any]) -> Optional[RedditPost]:
        """Add Reddit post"""
        with self.get_session() as session:
            coin = session.query(Coin).filter_by(symbol=coin_symbol.upper()).first()
            if not coin:
                logging.error(f"Coin {coin_symbol} not found")
                return None

            # Check if post already exists
            existing = session.query(RedditPost).filter_by(post_id=post_data['post_id']).first()
            if existing:
                logging.debug(f"Reddit post {post_data['post_id']} already exists")
                return existing

            post = RedditPost(
                coin_id=coin.id,
                post_id=post_data['post_id'],
                post_url=post_data['post_url'],
                title=post_data['title'],
                body=post_data.get('body'),
                author=post_data.get('author'),
                subreddit=post_data['subreddit'],
                flair=post_data.get('flair'),
                score=post_data.get('score', 0),
                num_comments=post_data.get('num_comments', 0),
                upvote_ratio=post_data.get('upvote_ratio'),
                is_self=post_data.get('is_self', True),
                created_utc=post_data['created_utc'],
                query=post_data.get('query')
            )
            session.add(post)
            session.commit()
            logging.debug(f"Added Reddit post: {post_data['post_id']}")
            return post

    def get_reddit_posts_timeframe(self, coin_symbol: str, hours: int = 24) -> List[RedditPost]:
        """Get Reddit posts for last N hours"""
        with self.get_session() as session:
            coin = session.query(Coin).filter_by(symbol=coin_symbol.upper()).first()
            if not coin:
                return []

            cutoff = datetime.utcnow() - timedelta(hours=hours)
            return session.query(RedditPost)\
                .filter(RedditPost.coin_id == coin.id, RedditPost.created_utc >= cutoff)\
                .order_by(RedditPost.created_utc.desc())\
                .all()

    # =========================================================================
    # TIKTOK OPERATIONS
    # =========================================================================

    def add_tiktok_video(self, coin_symbol: str, video_data: Dict[str, Any]) -> Optional[TikTokVideo]:
        """Add TikTok video"""
        with self.get_session() as session:
            coin = session.query(Coin).filter_by(symbol=coin_symbol.upper()).first()
            if not coin:
                logging.error(f"Coin {coin_symbol} not found")
                return None

            # Check if video already exists
            existing = session.query(TikTokVideo).filter_by(video_id=video_data['video_id']).first()
            if existing:
                logging.debug(f"TikTok video {video_data['video_id']} already exists")
                return existing

            video = TikTokVideo(
                coin_id=coin.id,
                video_id=video_data['video_id'],
                video_url=video_data['video_url'],
                username=video_data.get('username'),
                caption=video_data.get('caption'),
                hashtags=video_data.get('hashtags'),
                views=video_data.get('views', 0),
                likes=video_data.get('likes', 0),
                shares=video_data.get('shares', 0),
                comments=video_data.get('comments', 0),
                hashtag_searched=video_data.get('hashtag_searched'),
                container_index=video_data.get('container_index')
            )
            session.add(video)
            session.commit()
            logging.debug(f"Added TikTok video: {video_data['video_id']}")
            return video

    def get_tiktok_videos_timeframe(self, coin_symbol: str, hours: int = 24) -> List[TikTokVideo]:
        """Get TikTok videos for last N hours"""
        with self.get_session() as session:
            coin = session.query(Coin).filter_by(symbol=coin_symbol.upper()).first()
            if not coin:
                return []

            cutoff = datetime.utcnow() - timedelta(hours=hours)
            return session.query(TikTokVideo)\
                .filter(TikTokVideo.coin_id == coin.id, TikTokVideo.scraped_at >= cutoff)\
                .order_by(TikTokVideo.scraped_at.desc())\
                .all()

    # =========================================================================
    # SENTIMENT OPERATIONS
    # =========================================================================

    def add_sentiment_score(self, coin_symbol: str, sentiment_data: Dict[str, Any]) -> Optional[SentimentScore]:
        """Add aggregated sentiment score"""
        with self.get_session() as session:
            coin = session.query(Coin).filter_by(symbol=coin_symbol.upper()).first()
            if not coin:
                logging.error(f"Coin {coin_symbol} not found")
                return None

            sentiment = SentimentScore(
                coin_id=coin.id,
                timestamp=sentiment_data.get('timestamp', datetime.utcnow()),
                source=sentiment_data['source'],
                sentiment_score=sentiment_data.get('sentiment_score'),
                sentiment_positive=sentiment_data.get('sentiment_positive'),
                sentiment_negative=sentiment_data.get('sentiment_negative'),
                sentiment_neutral=sentiment_data.get('sentiment_neutral'),
                post_count=sentiment_data.get('post_count', 0),
                total_engagement=sentiment_data.get('total_engagement', 0),
                hype_score=sentiment_data.get('hype_score'),
                hype_keywords_count=sentiment_data.get('hype_keywords_count', 0),
                hype_emojis_count=sentiment_data.get('hype_emojis_count', 0)
            )
            session.add(sentiment)
            session.commit()
            logging.debug(f"Added sentiment: {coin_symbol} ({sentiment_data['source']})")
            return sentiment

    # =========================================================================
    # LOGGING OPERATIONS
    # =========================================================================

    def log_collection(self, collector_type: str, status: str, records: int = 0,
                       errors: int = 0, duration: float = 0, error_msg: str = None):
        """Log data collection run"""
        with self.get_session() as session:
            log = DataCollectionLog(
                collector_type=collector_type,
                status=status,
                records_collected=records,
                errors_count=errors,
                duration_seconds=duration,
                error_message=error_msg
            )
            session.add(log)
            session.commit()

    # =========================================================================
    # STATISTICS
    # =========================================================================

    def get_stats(self) -> Dict[str, Any]:
        """Get database statistics"""
        with self.get_session() as session:
            stats = {
                'coins': session.query(Coin).count(),
                'prices': session.query(Price).count(),
                'reddit_posts': session.query(RedditPost).count(),
                'tiktok_videos': session.query(TikTokVideo).count(),
                'sentiment_scores': session.query(SentimentScore).count(),
                'collection_logs': session.query(DataCollectionLog).count()
            }

            # Latest collection times
            latest_price = session.query(func.max(Price.timestamp)).scalar()
            latest_reddit = session.query(func.max(RedditPost.scraped_at)).scalar()
            latest_tiktok = session.query(func.max(TikTokVideo.scraped_at)).scalar()

            stats['latest_price'] = latest_price
            stats['latest_reddit'] = latest_reddit
            stats['latest_tiktok'] = latest_tiktok

            return stats

    def close(self):
        """Close database connection"""
        self.Session.remove()
        self.engine.dispose()
        logging.info("Database connection closed")


# Singleton instance for easy import
_db_instance = None


def get_db(db_path: str = None) -> DatabaseManager:
    """Get or create database manager instance"""
    global _db_instance
    if _db_instance is None:
        _db_instance = DatabaseManager(db_path=db_path)
    return _db_instance
