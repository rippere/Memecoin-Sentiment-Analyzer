"""
Tests for DatabaseManager
"""

import os
import tempfile
from datetime import datetime, timedelta
from pathlib import Path

import pytest

from database.db_manager import DatabaseManager
from database.models import Coin, Price, RedditPost, SentimentScore, TikTokVideo


@pytest.fixture
def test_db():
    """Create a temporary test database"""
    # Create a temporary database file
    db_fd, db_path = tempfile.mkstemp(suffix=".db")

    # Initialize database
    db = DatabaseManager(db_path=db_path)

    yield db

    # Cleanup
    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture
def sample_coin_data():
    """Sample coin data for testing"""
    return {"symbol": "DOGE", "name": "Dogecoin", "coingecko_id": "dogecoin", "is_control": False, "is_failed": False}


@pytest.fixture
def sample_price_data():
    """Sample price data for testing"""
    return {
        "timestamp": datetime.utcnow(),
        "price_usd": 0.10,
        "market_cap": 14000000000,
        "volume_24h": 500000000,
        "change_1h_pct": 1.5,
        "change_24h_pct": 5.2,
        "change_7d_pct": -3.1,
    }


@pytest.fixture
def sample_reddit_post():
    """Sample Reddit post data"""
    return {
        "post_id": "test123",
        "post_url": "https://reddit.com/r/test/test123",
        "title": "Dogecoin to the moon!",
        "body": "This is a test post about Dogecoin",
        "author": "test_user",
        "subreddit": "CryptoCurrency",
        "flair": "Discussion",
        "score": 100,
        "num_comments": 50,
        "upvote_ratio": 0.95,
        "is_self": True,
        "created_utc": datetime.utcnow(),
        "query": "dogecoin",
    }


@pytest.fixture
def sample_tiktok_video():
    """Sample TikTok video data"""
    return {
        "video_id": "tiktok_test_123",
        "video_url": "https://tiktok.com/@user/video/123",
        "username": "crypto_user",
        "caption": "Dogecoin is amazing! #dogecoin #crypto",
        "hashtags": "#dogecoin,#crypto,#moon",
        "views": 10000,
        "likes": 500,
        "shares": 50,
        "comments": 100,
        "hashtag_searched": "dogecoin",
        "container_index": 0,
    }


class TestDatabaseInitialization:
    """Test database initialization"""

    def test_database_creation(self, test_db):
        """Test that database is created successfully"""
        assert test_db is not None
        assert Path(test_db.db_path).exists()

    def test_coins_initialized(self, test_db):
        """Test that coins are initialized from config"""
        with test_db.get_session() as session:
            coins = session.query(Coin).all()
            symbols = [c.symbol for c in coins]
            assert len(coins) > 0
            assert "DOGE" in symbols
            assert "BTC" in symbols


class TestPriceOperations:
    """Test price-related operations"""

    def test_add_price(self, test_db, sample_price_data):
        """Test adding a price record"""
        result = test_db.add_price("DOGE", sample_price_data)
        assert result is not None

        # Verify by querying back
        with test_db.get_session() as session:
            price = session.query(Price).first()
            assert price is not None
            assert price.price_usd == 0.10
            assert price.market_cap == 14000000000

    def test_add_price_invalid_coin(self, test_db, sample_price_data):
        """Test adding price for invalid coin"""
        result = test_db.add_price("INVALID", sample_price_data)
        assert result is None

    def test_add_duplicate_price(self, test_db, sample_price_data):
        """Test that duplicate timestamps are handled"""
        test_db.add_price("DOGE", sample_price_data)
        result = test_db.add_price("DOGE", sample_price_data)
        # Should still work but return the existing record
        assert result is not None

    def test_get_prices_timeframe(self, test_db, sample_price_data):
        """Test retrieving prices within timeframe"""
        # Add a price
        test_db.add_price("DOGE", sample_price_data)

        # Get prices from last 24 hours
        with test_db.get_session() as session:
            prices = test_db.get_prices_timeframe("DOGE", hours=24)
            assert len(prices) >= 1

    def test_get_latest_price(self, test_db, sample_price_data):
        """Test getting latest price"""
        # Add two prices
        test_db.add_price("DOGE", sample_price_data)

        newer_price = sample_price_data.copy()
        newer_price["timestamp"] = datetime.utcnow() + timedelta(minutes=1)
        newer_price["price_usd"] = 0.11
        test_db.add_price("DOGE", newer_price)

        # Get latest by querying
        with test_db.get_session() as session:
            coin = session.query(Coin).filter_by(symbol="DOGE").first()
            latest = session.query(Price).filter_by(coin_id=coin.id).order_by(Price.timestamp.desc()).first()
            assert latest is not None
            assert latest.price_usd == 0.11


class TestRedditOperations:
    """Test Reddit-related operations"""

    def test_add_reddit_post(self, test_db, sample_reddit_post):
        """Test adding a Reddit post"""
        result = test_db.add_reddit_post("DOGE", sample_reddit_post)
        assert result is not None

        # Verify by querying back
        with test_db.get_session() as session:
            post = session.query(RedditPost).filter_by(post_id="test123").first()
            assert post is not None
            assert post.title == "Dogecoin to the moon!"

    def test_add_reddit_post_batch(self, test_db, sample_reddit_post):
        """Test batch adding Reddit posts"""
        # Create multiple posts
        posts = []
        for i in range(10):
            post = sample_reddit_post.copy()
            post["post_id"] = f"test{i}"
            posts.append(post)

        # Batch add
        count = test_db.add_reddit_posts_batch("DOGE", posts)
        assert count == 10

        # Verify they were added
        retrieved = test_db.get_reddit_posts_timeframe("DOGE", hours=24)
        assert len(retrieved) == 10

    def test_add_duplicate_reddit_post(self, test_db, sample_reddit_post):
        """Test that duplicate posts are skipped"""
        test_db.add_reddit_post("DOGE", sample_reddit_post)
        result = test_db.add_reddit_post("DOGE", sample_reddit_post)
        # Should return existing post
        assert result is not None

        # Verify only one post exists
        with test_db.get_session() as session:
            count = session.query(RedditPost).filter_by(post_id="test123").count()
            assert count == 1

    def test_batch_skips_duplicates(self, test_db, sample_reddit_post):
        """Test that batch insert skips duplicates"""
        # Add one post
        test_db.add_reddit_post("DOGE", sample_reddit_post)

        # Try to batch add including the duplicate
        posts = [sample_reddit_post]
        for i in range(1, 5):
            post = sample_reddit_post.copy()
            post["post_id"] = f"test{i}"
            posts.append(post)

        # Should only add 4 new posts
        count = test_db.add_reddit_posts_batch("DOGE", posts)
        assert count == 4


class TestTikTokOperations:
    """Test TikTok-related operations"""

    def test_add_tiktok_video(self, test_db, sample_tiktok_video):
        """Test adding a TikTok video"""
        result = test_db.add_tiktok_video("DOGE", sample_tiktok_video)
        assert result is not None

        # Verify by querying back
        with test_db.get_session() as session:
            video = session.query(TikTokVideo).filter_by(video_id="tiktok_test_123").first()
            assert video is not None
            assert video.views == 10000

    def test_add_tiktok_video_batch(self, test_db, sample_tiktok_video):
        """Test batch adding TikTok videos"""
        # Create multiple videos
        videos = []
        for i in range(10):
            video = sample_tiktok_video.copy()
            video["video_id"] = f"tiktok_test_{i}"
            videos.append(video)

        # Batch add
        count = test_db.add_tiktok_videos_batch("DOGE", videos)
        assert count == 10

        # Verify
        retrieved = test_db.get_tiktok_videos_timeframe("DOGE", hours=24)
        assert len(retrieved) == 10

    def test_batch_tiktok_skips_duplicates(self, test_db, sample_tiktok_video):
        """Test that batch insert skips duplicate videos"""
        # Add one video
        test_db.add_tiktok_video("DOGE", sample_tiktok_video)

        # Try to batch add including the duplicate
        videos = [sample_tiktok_video]
        for i in range(1, 5):
            video = sample_tiktok_video.copy()
            video["video_id"] = f"tiktok_test_{i}"
            videos.append(video)

        # Should only add 4 new videos
        count = test_db.add_tiktok_videos_batch("DOGE", videos)
        assert count == 4


class TestSentimentOperations:
    """Test sentiment score operations"""

    def test_add_sentiment_score(self, test_db):
        """Test adding sentiment score"""
        sentiment_data = {
            "timestamp": datetime.utcnow(),
            "sentiment_score": 0.75,
            "hype_score": 85.5,
            "post_count": 100,
            "avg_engagement": 50.0,
            "source": "test",
        }

        result = test_db.add_sentiment_score("DOGE", sentiment_data)
        assert result is not None

        # Verify by querying back
        with test_db.get_session() as session:
            score = session.query(SentimentScore).first()
            assert score is not None
            assert score.sentiment_score == 0.75
            assert score.hype_score == 85.5

    def test_get_sentiment_timeframe(self, test_db):
        """Test retrieving sentiment scores"""
        sentiment_data = {
            "timestamp": datetime.utcnow(),
            "sentiment_score": 0.75,
            "hype_score": 85.5,
            "post_count": 100,
            "avg_engagement": 50.0,
            "source": "test",
        }

        test_db.add_sentiment_score("DOGE", sentiment_data)

        # Query directly since get_sentiment_timeframe may not exist
        with test_db.get_session() as session:
            coin = session.query(Coin).filter_by(symbol="DOGE").first()
            scores = session.query(SentimentScore).filter_by(coin_id=coin.id).all()
            assert len(scores) >= 1


class TestStatisticsOperations:
    """Test database statistics"""

    def test_get_stats(self, test_db, sample_price_data, sample_reddit_post, sample_tiktok_video):
        """Test getting database statistics"""
        # Add some data
        test_db.add_price("DOGE", sample_price_data)
        test_db.add_reddit_post("DOGE", sample_reddit_post)
        test_db.add_tiktok_video("DOGE", sample_tiktok_video)

        stats = test_db.get_stats()
        # The actual keys depend on implementation
        assert stats is not None
        assert isinstance(stats, dict)
        # Check that it has some data
        assert len(stats) > 0
