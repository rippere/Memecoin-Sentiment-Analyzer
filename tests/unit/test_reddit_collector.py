"""
Comprehensive tests for RedditCollector
Tests to prevent silent failures when Reddit's structure changes
"""

from datetime import datetime
from typing import Dict, List
from unittest.mock import MagicMock, Mock, patch

import pytest

from collectors.reddit_collector import RedditCollector


@pytest.fixture
def reddit_collector():
    """Create RedditCollector with bot detection disabled for testing"""
    config = {"headless": True, "min_delay": 0.1, "max_delay": 0.2}
    return RedditCollector(config=config, enable_bot_detection=False)


@pytest.fixture
def reddit_collector_with_bots():
    """Create RedditCollector with bot detection enabled"""
    config = {"headless": True, "min_delay": 0.1, "max_delay": 0.2}
    return RedditCollector(config=config, enable_bot_detection=True)


@pytest.fixture
def sample_reddit_posts():
    """Sample Reddit posts from scraper"""
    return [
        {
            "post_id": f"reddit_test_{i}",
            "post_url": f"https://reddit.com/r/CryptoCurrency/test_{i}",
            "title": f"Dogecoin Analysis Post {i}",
            "body": "Detailed analysis of DOGE price movements",
            "author": f"crypto_analyst_{i}",
            "subreddit": "CryptoCurrency",
            "flair": "Analysis",
            "score": 150 + i * 10,
            "num_comments": 45 + i * 5,
            "upvote_ratio": 0.92,
            "is_self": True,
            "created_utc": datetime.utcnow(),
            "query": "dogecoin",
        }
        for i in range(5)
    ]


@pytest.fixture
def sample_bot_posts():
    """Sample posts from bot accounts"""
    return [
        {
            "post_id": "bot_post_1",
            "post_url": "https://reddit.com/r/CryptoCurrency/bot_1",
            "title": "BUY NOW! DOGE TO THE MOON! 🚀🚀🚀",
            "body": "PUMP IT UP! DOGE $10 SOON!!!",
            "author": "crypto_bot_2025",
            "subreddit": "CryptoCurrency",
            "flair": None,
            "score": 2,
            "num_comments": 0,
            "upvote_ratio": 0.51,
            "is_self": True,
            "created_utc": datetime.utcnow(),
            "query": "dogecoin",
        }
    ]


class TestRedditCollectorInitialization:
    """Test RedditCollector initialization"""

    def test_initialization_default_config(self):
        """Test initialization with default config"""
        collector = RedditCollector()
        assert collector is not None
        assert collector.config["headless"] == True
        assert collector.enable_bot_detection == True
        assert collector.sentiment_analyzer is not None

    def test_initialization_custom_config(self):
        """Test initialization with custom config"""
        config = {"headless": False, "min_delay": 5, "max_delay": 10}
        collector = RedditCollector(config=config)
        assert collector.config["headless"] == False
        assert collector.config["min_delay"] == 5

    def test_initialization_without_bot_detection(self):
        """Test initialization with bot detection disabled"""
        collector = RedditCollector(enable_bot_detection=False)
        assert collector.bot_detector is None

    def test_coin_queries_loaded(self, reddit_collector):
        """Test that coin queries are loaded from config"""
        assert "DOGE" in reddit_collector.COIN_QUERIES
        assert len(reddit_collector.COIN_QUERIES["DOGE"]) > 0


class TestDataCollection:
    """Test data collection functionality"""

    @patch("collectors.reddit_collector.RedditScraper")
    def test_collect_coin_data_success(self, mock_scraper_class, reddit_collector, sample_reddit_posts):
        """Test successful data collection for a coin"""
        # Mock the scraper
        mock_scraper = MagicMock()
        mock_scraper.__enter__ = Mock(return_value=mock_scraper)
        mock_scraper.__exit__ = Mock(return_value=False)
        mock_scraper.scrape_multiple_subreddits.return_value = sample_reddit_posts
        mock_scraper_class.return_value = mock_scraper

        # Collect data
        result = reddit_collector.collect_coin_data("DOGE", max_posts=50)

        assert len(result) == 5
        assert all("sentiment_analysis" in post for post in result)
        assert result[0]["post_id"] == "reddit_test_0"

    @patch("collectors.reddit_collector.RedditScraper")
    def test_collect_coin_data_unknown_coin(self, mock_scraper_class, reddit_collector):
        """Test collection for unknown coin returns empty list"""
        result = reddit_collector.collect_coin_data("UNKNOWN", max_posts=50)
        assert result == []

    @patch("collectors.reddit_collector.RedditScraper")
    def test_collect_coin_data_empty_results(self, mock_scraper_class, reddit_collector):
        """Test collection when scraper returns no posts"""
        mock_scraper = MagicMock()
        mock_scraper.__enter__ = Mock(return_value=mock_scraper)
        mock_scraper.__exit__ = Mock(return_value=False)
        mock_scraper.scrape_multiple_subreddits.return_value = []
        mock_scraper_class.return_value = mock_scraper

        result = reddit_collector.collect_coin_data("DOGE", max_posts=50)
        assert result == []

    @patch("collectors.reddit_collector.RedditScraper")
    def test_collect_coin_data_scraper_exception(self, mock_scraper_class, reddit_collector):
        """Test collection handles scraper exceptions gracefully"""
        mock_scraper = MagicMock()
        mock_scraper.__enter__ = Mock(return_value=mock_scraper)
        mock_scraper.__exit__ = Mock(return_value=False)
        mock_scraper.scrape_multiple_subreddits.side_effect = Exception("Scraping failed")
        mock_scraper_class.return_value = mock_scraper

        # Should raise exception (collector doesn't catch it - designed to fail fast)
        with pytest.raises(Exception):
            reddit_collector.collect_coin_data("DOGE", max_posts=50)


class TestDuplicateRemoval:
    """Test duplicate post removal"""

    @patch("collectors.reddit_collector.RedditScraper")
    def test_duplicate_posts_removed(self, mock_scraper_class, reddit_collector):
        """Test that duplicate post_ids are removed"""
        # Create posts with duplicate IDs
        posts_with_dupes = [
            {
                "post_id": "duplicate_id",
                "post_url": "https://reddit.com/1",
                "title": "First post",
                "body": "Content 1",
                "author": "user1",
                "subreddit": "CryptoCurrency",
                "flair": "Discussion",
                "score": 100,
                "num_comments": 10,
                "upvote_ratio": 0.95,
                "is_self": True,
                "created_utc": datetime.utcnow(),
                "query": "dogecoin",
            },
            {
                "post_id": "duplicate_id",  # Same ID
                "post_url": "https://reddit.com/2",
                "title": "Second post (duplicate)",
                "body": "Content 2",
                "author": "user2",
                "subreddit": "CryptoCurrency",
                "flair": "Discussion",
                "score": 50,
                "num_comments": 5,
                "upvote_ratio": 0.90,
                "is_self": True,
                "created_utc": datetime.utcnow(),
                "query": "dogecoin",
            },
            {
                "post_id": "unique_id",
                "post_url": "https://reddit.com/3",
                "title": "Unique post",
                "body": "Content 3",
                "author": "user3",
                "subreddit": "CryptoCurrency",
                "flair": "Discussion",
                "score": 200,
                "num_comments": 20,
                "upvote_ratio": 0.98,
                "is_self": True,
                "created_utc": datetime.utcnow(),
                "query": "dogecoin",
            },
        ]

        mock_scraper = MagicMock()
        mock_scraper.__enter__ = Mock(return_value=mock_scraper)
        mock_scraper.__exit__ = Mock(return_value=False)
        mock_scraper.scrape_multiple_subreddits.return_value = posts_with_dupes
        mock_scraper_class.return_value = mock_scraper

        result = reddit_collector.collect_coin_data("DOGE", max_posts=50)

        # Should only have 2 unique posts (first occurrence of duplicate kept)
        assert len(result) == 2
        post_ids = [p["post_id"] for p in result]
        assert "duplicate_id" in post_ids
        assert "unique_id" in post_ids


class TestBotDetection:
    """Test bot detection integration"""

    @patch("collectors.reddit_collector.RedditScraper")
    def test_bot_detection_filters_bots(
        self, mock_scraper_class, reddit_collector_with_bots, sample_reddit_posts, sample_bot_posts
    ):
        """Test that bot detection filters out bot posts"""
        all_posts = sample_reddit_posts + sample_bot_posts

        mock_scraper = MagicMock()
        mock_scraper.__enter__ = Mock(return_value=mock_scraper)
        mock_scraper.__exit__ = Mock(return_value=False)
        mock_scraper.scrape_multiple_subreddits.return_value = all_posts
        mock_scraper_class.return_value = mock_scraper

        # Mock bot detector to identify the bot post
        reddit_collector_with_bots.bot_detector.filter_bots_from_reddit = Mock(
            return_value=(
                sample_reddit_posts,  # Legitimate posts
                sample_bot_posts,  # Bot posts
                {"bot_posts": 1, "total_posts": 6, "bot_percentage": 16.7},
            )
        )

        result = reddit_collector_with_bots.collect_coin_data("DOGE", max_posts=50)

        # Should only contain legitimate posts
        assert len(result) == 5
        assert all(post["post_id"] != "bot_post_1" for post in result)

    @patch("collectors.reddit_collector.RedditScraper")
    def test_bot_detection_disabled(self, mock_scraper_class, reddit_collector, sample_reddit_posts, sample_bot_posts):
        """Test that bot detection can be disabled"""
        all_posts = sample_reddit_posts + sample_bot_posts

        mock_scraper = MagicMock()
        mock_scraper.__enter__ = Mock(return_value=mock_scraper)
        mock_scraper.__exit__ = Mock(return_value=False)
        mock_scraper.scrape_multiple_subreddits.return_value = all_posts
        mock_scraper_class.return_value = mock_scraper

        result = reddit_collector.collect_coin_data("DOGE", max_posts=50)

        # Should contain all posts (bot detection disabled)
        assert len(result) == 6


class TestSentimentAnalysis:
    """Test sentiment analysis integration"""

    @patch("collectors.reddit_collector.RedditScraper")
    def test_sentiment_added_to_posts(self, mock_scraper_class, reddit_collector, sample_reddit_posts):
        """Test that sentiment analysis is added to each post"""
        mock_scraper = MagicMock()
        mock_scraper.__enter__ = Mock(return_value=mock_scraper)
        mock_scraper.__exit__ = Mock(return_value=False)
        mock_scraper.scrape_multiple_subreddits.return_value = sample_reddit_posts
        mock_scraper_class.return_value = mock_scraper

        result = reddit_collector.collect_coin_data("DOGE", max_posts=50)

        # Every post should have sentiment analysis with correct fields
        for post in result:
            assert "sentiment_analysis" in post
            assert "sentiment_compound" in post["sentiment_analysis"]
            assert "hype_score" in post["sentiment_analysis"]
            assert "sentiment_positive" in post["sentiment_analysis"]
            assert "sentiment_negative" in post["sentiment_analysis"]


class TestAggregation:
    """Test sentiment aggregation"""

    def test_aggregate_sentiment_with_posts(self, reddit_collector, sample_reddit_posts):
        """Test aggregating sentiment from multiple posts"""
        # Add mock sentiment to posts (using actual field names from sentiment analyzer)
        for post in sample_reddit_posts:
            post["sentiment_analysis"] = {
                "sentiment_compound": 0.7,
                "sentiment_positive": 0.8,
                "sentiment_negative": 0.1,
                "sentiment_neutral": 0.1,
                "hype_score": 80.0,
                "hype_keywords_count": 3,
                "hype_emojis_count": 2,
            }

        result = reddit_collector.aggregate_sentiment(sample_reddit_posts)

        assert result is not None
        assert "sentiment_score" in result
        assert "hype_score" in result
        assert "post_count" in result
        assert "total_engagement" in result  # Changed from avg_engagement
        assert result["post_count"] == 5

    def test_aggregate_sentiment_empty_posts(self, reddit_collector):
        """Test aggregating with no posts returns zeros"""
        result = reddit_collector.aggregate_sentiment([])

        assert result["sentiment_score"] == 0.0
        assert result["hype_score"] == 0.0
        assert result["post_count"] == 0
        assert result["total_engagement"] == 0

    def test_aggregate_sentiment_calculates_engagement(self, reddit_collector, sample_reddit_posts):
        """Test that engagement is calculated from scores and comments"""
        for post in sample_reddit_posts:
            post["sentiment_analysis"] = {
                "sentiment_compound": 0.7,
                "sentiment_positive": 0.8,
                "sentiment_negative": 0.1,
                "sentiment_neutral": 0.1,
                "hype_score": 80.0,
                "hype_keywords_count": 3,
                "hype_emojis_count": 2,
            }

        result = reddit_collector.aggregate_sentiment(sample_reddit_posts)

        # Engagement = sum(score + num_comments)
        expected_engagement = sum(post["score"] + post["num_comments"] for post in sample_reddit_posts)
        assert result["total_engagement"] == expected_engagement


class TestMultipleCoinCollection:
    """Test collecting data for multiple coins"""

    @patch("collectors.reddit_collector.RedditScraper")
    def test_collect_all_coins(self, mock_scraper_class, reddit_collector, sample_reddit_posts):
        """Test collecting data for all tracked coins"""
        mock_scraper = MagicMock()
        mock_scraper.__enter__ = Mock(return_value=mock_scraper)
        mock_scraper.__exit__ = Mock(return_value=False)
        mock_scraper.scrape_multiple_subreddits.return_value = sample_reddit_posts
        mock_scraper_class.return_value = mock_scraper

        result = reddit_collector.collect_all_coins(max_posts_per_coin=50)

        # Should return data for all coins in COIN_QUERIES
        assert isinstance(result, dict)
        assert "DOGE" in result
        assert len(result) > 0

    @patch("collectors.reddit_collector.RedditScraper")
    def test_collect_all_coins_handles_failures(self, mock_scraper_class, reddit_collector):
        """Test that collection continues even if some coins fail"""
        mock_scraper = MagicMock()
        mock_scraper.__enter__ = Mock(return_value=mock_scraper)
        mock_scraper.__exit__ = Mock(return_value=False)

        # First coin succeeds, second fails
        mock_scraper.scrape_multiple_subreddits.side_effect = [
            [
                {
                    "post_id": "1",
                    "post_url": "url",
                    "title": "test",
                    "body": "body",
                    "author": "user",
                    "subreddit": "sub",
                    "flair": None,
                    "score": 10,
                    "num_comments": 5,
                    "upvote_ratio": 0.9,
                    "is_self": True,
                    "created_utc": datetime.utcnow(),
                    "query": "doge",
                }
            ],
            Exception("Reddit API error"),
            [],  # Remaining coins
        ]
        mock_scraper_class.return_value = mock_scraper

        result = reddit_collector.collect_all_coins(max_posts_per_coin=10)

        # Should return results for successful coins and empty lists for failed ones
        assert isinstance(result, dict)
        assert all(isinstance(posts, list) for posts in result.values())


class TestEdgeCases:
    """Test edge cases and error conditions"""

    @patch("collectors.reddit_collector.RedditScraper")
    def test_malformed_post_data(self, mock_scraper_class, reddit_collector):
        """Test handling of malformed post data"""
        malformed_posts = [
            {
                "post_id": "missing_fields",
                # Missing required fields
            },
            {
                "post_id": None,  # None ID
                "title": "Test",
            },
        ]

        mock_scraper = MagicMock()
        mock_scraper.__enter__ = Mock(return_value=mock_scraper)
        mock_scraper.__exit__ = Mock(return_value=False)
        mock_scraper.scrape_multiple_subreddits.return_value = malformed_posts
        mock_scraper_class.return_value = mock_scraper

        # Should handle gracefully without crashing
        result = reddit_collector.collect_coin_data("DOGE", max_posts=50)
        assert isinstance(result, list)

    @patch("collectors.reddit_collector.RedditScraper")
    def test_posts_without_sentiment_field(self, mock_scraper_class, reddit_collector):
        """Test that posts missing sentiment analysis are handled"""
        posts = [
            {
                "post_id": "test_1",
                "post_url": "url",
                "title": "Test",
                "body": "Body",
                "author": "user",
                "subreddit": "sub",
                "flair": None,
                "score": 10,
                "num_comments": 5,
                "upvote_ratio": 0.9,
                "is_self": True,
                "created_utc": datetime.utcnow(),
                "query": "doge",
                # sentiment_analysis will be added by collector
            }
        ]

        mock_scraper = MagicMock()
        mock_scraper.__enter__ = Mock(return_value=mock_scraper)
        mock_scraper.__exit__ = Mock(return_value=False)
        mock_scraper.scrape_multiple_subreddits.return_value = posts
        mock_scraper_class.return_value = mock_scraper

        result = reddit_collector.collect_coin_data("DOGE", max_posts=50)

        # Sentiment should be added by collector
        assert all("sentiment_analysis" in post for post in result)
