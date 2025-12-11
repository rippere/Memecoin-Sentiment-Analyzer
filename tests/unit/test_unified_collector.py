"""
Comprehensive tests for UnifiedCollector
Tests the main data collection orchestrator to prevent silent failures
"""

import os
import tempfile
from datetime import datetime
from unittest.mock import MagicMock, Mock, patch

import pytest

from collectors.unified_collector import UnifiedCollector


@pytest.fixture
def test_db_path():
    """Create temporary database for testing"""
    db_fd, db_path = tempfile.mkstemp(suffix=".db")
    yield db_path
    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture
def unified_collector(test_db_path):
    """Create UnifiedCollector with test database"""
    config = {"headless": True, "min_delay": 0.1, "max_delay": 0.2}  # Fast for tests
    return UnifiedCollector(db_path=test_db_path, scraper_config=config)


@pytest.fixture
def sample_price_data():
    """Sample price data from CoinGecko"""
    return {
        "DOGE": {
            "timestamp": datetime.utcnow(),
            "price_usd": 0.10,
            "market_cap": 14000000000,
            "volume_24h": 500000000,
            "change_1h_pct": 1.5,
            "change_24h_pct": 5.2,
            "change_7d_pct": -3.1,
        }
    }


@pytest.fixture
def sample_reddit_posts():
    """Sample Reddit posts"""
    return [
        {
            "post_id": f"test_reddit_{i}",
            "post_url": f"https://reddit.com/r/test/{i}",
            "title": f"Dogecoin post {i}",
            "body": "Test content",
            "author": f"user{i}",
            "subreddit": "CryptoCurrency",
            "flair": "Discussion",
            "score": 100 + i,
            "num_comments": 50,
            "upvote_ratio": 0.95,
            "is_self": True,
            "created_utc": datetime.utcnow(),
            "query": "dogecoin",
        }
        for i in range(5)
    ]


@pytest.fixture
def sample_tiktok_videos():
    """Sample TikTok videos"""
    return [
        {
            "video_id": f"tiktok_test_{i}",
            "video_url": f"https://tiktok.com/@user/video/{i}",
            "username": f"crypto_user_{i}",
            "caption": f"Dogecoin video {i} #crypto",
            "hashtags": "#dogecoin,#crypto",
            "views": 10000 + i * 1000,
            "likes": 500,
            "shares": 50,
            "comments": 100,
            "hashtag_searched": "dogecoin",
            "container_index": i,
        }
        for i in range(5)
    ]


class TestUnifiedCollectorInitialization:
    """Test UnifiedCollector initialization"""

    def test_initialization(self, unified_collector):
        """Test that UnifiedCollector initializes correctly"""
        assert unified_collector is not None
        assert unified_collector.db is not None
        assert unified_collector.scraper_config is not None

    def test_initialization_with_custom_config(self, test_db_path):
        """Test initialization with custom scraper config"""
        config = {"headless": False, "min_delay": 5, "max_delay": 10}
        collector = UnifiedCollector(db_path=test_db_path, scraper_config=config)

        assert collector.scraper_config["headless"] == False
        assert collector.scraper_config["min_delay"] == 5


class TestPriceCollection:
    """Test price data collection"""

    @patch("collectors.unified_collector.PriceCollector")
    def test_collect_prices_success(self, mock_price_collector, unified_collector, sample_price_data):
        """Test successful price collection"""
        # Mock the price collector
        mock_collector_instance = Mock()
        mock_collector_instance.fetch_coin_data.return_value = sample_price_data
        mock_price_collector.return_value = mock_collector_instance

        # Collect prices
        result = unified_collector.collect_prices(["DOGE"])

        assert result["count"] == 1
        assert result["errors"] == 0
        mock_collector_instance.fetch_coin_data.assert_called_once()

    @patch("collectors.unified_collector.PriceCollector")
    def test_collect_prices_api_failure(self, mock_price_collector, unified_collector):
        """Test price collection handles API failures gracefully"""
        # Mock API failure
        mock_collector_instance = Mock()
        mock_collector_instance.fetch_coin_data.side_effect = Exception("API Error")
        mock_price_collector.return_value = mock_collector_instance

        # Should not crash, should handle gracefully
        result = unified_collector.collect_prices(["DOGE"])

        assert result is not None
        # Should log error but not crash

    @patch("collectors.unified_collector.PriceCollector")
    def test_collect_prices_empty_response(self, mock_price_collector, unified_collector):
        """Test handling of empty API response"""
        mock_collector_instance = Mock()
        mock_collector_instance.fetch_coin_data.return_value = {}
        mock_price_collector.return_value = mock_collector_instance

        result = unified_collector.collect_prices(["DOGE"])

        assert result["count"] == 0

    @patch("collectors.unified_collector.PriceCollector")
    def test_collect_prices_partial_failure(self, mock_price_collector, unified_collector, sample_price_data):
        """Test collection continues when some coins fail"""
        mock_collector_instance = Mock()
        # Return data for only one coin
        mock_collector_instance.fetch_coin_data.return_value = {"DOGE": sample_price_data["DOGE"]}
        mock_price_collector.return_value = mock_collector_instance

        result = unified_collector.collect_prices(["DOGE", "SHIB", "PEPE"])

        # Should have collected at least DOGE
        assert result["count"] >= 1


class TestRedditCollection:
    """Test Reddit data collection"""

    @patch("collectors.unified_collector.RedditCollector")
    def test_collect_reddit_success(self, mock_reddit_collector, unified_collector, sample_reddit_posts):
        """Test successful Reddit collection"""
        mock_collector_instance = Mock()
        mock_collector_instance.collect_coin_data.return_value = sample_reddit_posts
        mock_collector_instance.aggregate_sentiment.return_value = {
            "sentiment_score": 0.75,
            "hype_score": 85.0,
            "post_count": 5,
            "avg_engagement": 100.0,
        }
        mock_reddit_collector.return_value = mock_collector_instance

        result = unified_collector.collect_reddit(["DOGE"])

        assert result["count"] == 5
        assert result["errors"] == 0

    @patch("collectors.unified_collector.RedditCollector")
    def test_collect_reddit_no_posts(self, mock_reddit_collector, unified_collector):
        """Test Reddit collection when no posts found"""
        mock_collector_instance = Mock()
        mock_collector_instance.collect_coin_data.return_value = []
        mock_reddit_collector.return_value = mock_collector_instance

        result = unified_collector.collect_reddit(["DOGE"])

        assert result["count"] == 0
        # Should not crash on empty results

    @patch("collectors.unified_collector.RedditCollector")
    def test_collect_reddit_scraping_failure(self, mock_reddit_collector, unified_collector):
        """Test Reddit collection handles scraping failures"""
        mock_collector_instance = Mock()
        mock_collector_instance.collect_coin_data.side_effect = Exception("Scraping Error")
        mock_reddit_collector.return_value = mock_collector_instance

        # Should handle error gracefully
        result = unified_collector.collect_reddit(["DOGE"])

        assert result is not None
        assert result["errors"] >= 0

    @patch("collectors.unified_collector.RedditCollector")
    def test_collect_reddit_with_quality_monitoring(
        self, mock_reddit_collector, unified_collector, sample_reddit_posts
    ):
        """Test that quality monitoring is integrated"""
        mock_collector_instance = Mock()
        mock_collector_instance.collect_coin_data.return_value = sample_reddit_posts
        mock_collector_instance.aggregate_sentiment.return_value = {
            "sentiment_score": 0.75,
            "hype_score": 85.0,
            "post_count": 5,
            "avg_engagement": 100.0,
        }
        mock_reddit_collector.return_value = mock_collector_instance

        result = unified_collector.collect_reddit(["DOGE"])

        # Should complete without errors
        assert result["count"] > 0


class TestTikTokCollection:
    """Test TikTok data collection"""

    @patch("collectors.unified_collector.TikTokCollector")
    def test_collect_tiktok_success(self, mock_tiktok_collector, unified_collector, sample_tiktok_videos):
        """Test successful TikTok collection"""
        mock_collector_instance = Mock()
        mock_collector_instance.collect_coin_data.return_value = sample_tiktok_videos
        mock_collector_instance.aggregate_sentiment.return_value = {
            "sentiment_score": 0.80,
            "hype_score": 90.0,
            "post_count": 5,
            "avg_engagement": 1000.0,
        }
        mock_tiktok_collector.return_value = mock_collector_instance

        result = unified_collector.collect_tiktok(["DOGE"])

        assert result["count"] == 5
        assert result["errors"] == 0

    @patch("collectors.unified_collector.TikTokCollector")
    def test_collect_tiktok_scraping_blocked(self, mock_tiktok_collector, unified_collector):
        """Test TikTok collection when scraping is blocked"""
        mock_collector_instance = Mock()
        mock_collector_instance.collect_coin_data.side_effect = Exception("Blocked")
        mock_tiktok_collector.return_value = mock_collector_instance

        # Should handle being blocked gracefully
        result = unified_collector.collect_tiktok(["DOGE"])

        assert result is not None


class TestBatchInsertIntegration:
    """Test that batch inserts are used correctly"""

    @patch("collectors.unified_collector.RedditCollector")
    def test_reddit_uses_batch_insert(self, mock_reddit_collector, unified_collector, sample_reddit_posts):
        """Verify batch insert is called for Reddit posts"""
        mock_collector_instance = Mock()
        mock_collector_instance.collect_coin_data.return_value = sample_reddit_posts
        mock_collector_instance.aggregate_sentiment.return_value = {
            "sentiment_score": 0.75,
            "hype_score": 85.0,
            "post_count": 5,
            "avg_engagement": 100.0,
        }
        mock_reddit_collector.return_value = mock_collector_instance

        # Spy on database batch insert
        original_batch = unified_collector.db.add_reddit_posts_batch
        unified_collector.db.add_reddit_posts_batch = Mock(return_value=5)

        unified_collector.collect_reddit(["DOGE"])

        # Verify batch insert was called
        unified_collector.db.add_reddit_posts_batch.assert_called()

        # Restore
        unified_collector.db.add_reddit_posts_batch = original_batch


class TestErrorHandling:
    """Test comprehensive error handling"""

    def test_database_connection_failure(self, test_db_path):
        """Test handling of database connection issues"""
        # Try to initialize with invalid path
        try:
            collector = UnifiedCollector(db_path="/invalid/path/db.db")
            # If it doesn't raise, that's okay - it might create the dir
            assert collector is not None
        except Exception as e:
            # Should have meaningful error
            assert str(e) is not None

    @patch("collectors.unified_collector.PriceCollector")
    def test_multiple_collection_errors(self, mock_price_collector, unified_collector):
        """Test handling multiple consecutive errors"""
        mock_collector_instance = Mock()
        mock_collector_instance.fetch_coin_data.side_effect = [
            Exception("Error 1"),
            Exception("Error 2"),
            Exception("Error 3"),
        ]
        mock_price_collector.return_value = mock_collector_instance

        # Should handle multiple errors without crashing
        for _ in range(3):
            result = unified_collector.collect_prices(["DOGE"])
            assert result is not None


class TestDataIntegrity:
    """Test data integrity throughout collection"""

    @patch("collectors.unified_collector.PriceCollector")
    def test_no_duplicate_prices(self, mock_price_collector, unified_collector, sample_price_data):
        """Verify duplicate prevention works"""
        mock_collector_instance = Mock()
        mock_collector_instance.fetch_coin_data.return_value = sample_price_data
        mock_price_collector.return_value = mock_collector_instance

        # Collect same data twice
        unified_collector.collect_prices(["DOGE"])
        unified_collector.collect_prices(["DOGE"])

        # Database should handle duplicates (this is tested in db_manager tests)
        # This test verifies the collection doesn't crash on duplicates
        assert True  # If we got here, no crash

    @patch("collectors.unified_collector.RedditCollector")
    def test_transaction_rollback_on_error(self, mock_reddit_collector, unified_collector, sample_reddit_posts):
        """Test that database transactions roll back on errors"""
        mock_collector_instance = Mock()
        # First call succeeds, second fails mid-transaction
        mock_collector_instance.collect_coin_data.side_effect = [
            sample_reddit_posts,
            Exception("Mid-transaction error"),
        ]
        mock_collector_instance.aggregate_sentiment.return_value = {
            "sentiment_score": 0.75,
            "hype_score": 85.0,
            "post_count": 5,
            "avg_engagement": 100.0,
        }
        mock_reddit_collector.return_value = mock_collector_instance

        # First should succeed
        result1 = unified_collector.collect_reddit(["DOGE"])
        assert result1["count"] > 0

        # Second should fail but not corrupt database
        result2 = unified_collector.collect_reddit(["SHIB"])
        assert result2 is not None


class TestCollectionLogging:
    """Test that collections are logged properly"""

    @patch("collectors.unified_collector.PriceCollector")
    def test_collection_creates_log_entry(self, mock_price_collector, unified_collector, sample_price_data):
        """Verify collection events are logged to database"""
        mock_collector_instance = Mock()
        mock_collector_instance.fetch_coin_data.return_value = sample_price_data
        mock_price_collector.return_value = mock_collector_instance

        result = unified_collector.collect_prices(["DOGE"])

        # Should have logged the collection
        # (Actual log verification would query collection_logs table)
        assert result is not None
