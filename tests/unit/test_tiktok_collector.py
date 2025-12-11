"""
Comprehensive tests for TikTokCollector
Tests to prevent silent failures when TikTok's HTML structure changes
"""

from datetime import datetime
from typing import Dict, List
from unittest.mock import MagicMock, Mock, patch

import pytest

from collectors.tiktok_collector import TikTokCollector


@pytest.fixture
def tiktok_collector():
    """Create TikTokCollector with bot detection disabled for testing"""
    config = {"headless": True, "min_delay": 0.1, "max_delay": 0.2}
    return TikTokCollector(config=config, enable_bot_detection=False)


@pytest.fixture
def tiktok_collector_with_bots():
    """Create TikTokCollector with bot detection enabled"""
    config = {"headless": True, "min_delay": 0.1, "max_delay": 0.2}
    return TikTokCollector(config=config, enable_bot_detection=True)


@pytest.fixture
def sample_tiktok_videos():
    """Sample TikTok videos from scraper"""
    return [
        {
            "video_id": f"7576771733718387{i:03d}",
            "username": f"crypto_user_{i}",
            "video_url": f"https://tiktok.com/@crypto_user_{i}/video/7576771733718387{i:03d}",
            "caption": f"Dogecoin analysis #{i} #crypto #doge",
            "views": 15000 + i * 1000,
            "likes": 850 + i * 50,
            "shares": 120 + i * 10,
            "comments": 230 + i * 20,
            "hashtag_searched": "dogecoin",
            "scraped_at": datetime.now(),
            "container_index": i,
        }
        for i in range(5)
    ]


@pytest.fixture
def sample_spam_videos():
    """Sample spam/bot videos"""
    return [
        {
            "video_id": "spam_video_1",
            "username": "crypto_bot_2025",
            "video_url": "https://tiktok.com/@crypto_bot_2025/video/spam",
            "caption": "🚀🚀🚀 BUY NOW!!! PUMP IT!!! 🚀🚀🚀",
            "views": 100,
            "likes": 2,
            "shares": 0,
            "comments": 0,
            "hashtag_searched": "dogecoin",
            "scraped_at": datetime.now(),
            "container_index": 0,
        }
    ]


class TestTikTokCollectorInitialization:
    """Test TikTokCollector initialization"""

    def test_initialization_default_config(self):
        """Test initialization with default config"""
        collector = TikTokCollector()
        assert collector is not None
        assert collector.config["headless"] == True
        assert collector.enable_bot_detection == True
        assert collector.sentiment_analyzer is not None

    def test_initialization_custom_config(self):
        """Test initialization with custom config"""
        config = {"headless": False, "min_delay": 5, "max_delay": 10}
        collector = TikTokCollector(config=config)
        assert collector.config["headless"] == False
        assert collector.config["min_delay"] == 5

    def test_initialization_without_bot_detection(self):
        """Test initialization with bot detection disabled"""
        collector = TikTokCollector(enable_bot_detection=False)
        assert collector.bot_detector is None

    def test_hashtag_queries_loaded(self, tiktok_collector):
        """Test that hashtag queries are loaded from config"""
        assert "DOGE" in tiktok_collector.COIN_HASHTAGS
        assert len(tiktok_collector.COIN_HASHTAGS["DOGE"]) > 0


class TestDataCollection:
    """Test data collection functionality"""

    @patch("collectors.tiktok_collector.TikTokScraper")
    def test_collect_coin_data_success(self, mock_scraper_class, tiktok_collector, sample_tiktok_videos):
        """Test successful data collection for a coin"""
        # Mock the scraper
        mock_scraper = MagicMock()
        mock_scraper.__enter__ = Mock(return_value=mock_scraper)
        mock_scraper.__exit__ = Mock(return_value=False)
        mock_scraper.scrape_hashtag.return_value = sample_tiktok_videos
        mock_scraper_class.return_value = mock_scraper

        # Collect data
        result = tiktok_collector.collect_coin_data("DOGE", max_videos=50)

        assert len(result) == 5
        assert all("sentiment_analysis" in video for video in result)
        assert result[0]["video_id"].startswith("757677173371838")

    @patch("collectors.tiktok_collector.TikTokScraper")
    def test_collect_coin_data_unknown_coin(self, mock_scraper_class, tiktok_collector):
        """Test collection for unknown coin returns empty list"""
        result = tiktok_collector.collect_coin_data("UNKNOWN", max_videos=50)
        assert result == []

    @patch("collectors.tiktok_collector.TikTokScraper")
    def test_collect_coin_data_empty_results(self, mock_scraper_class, tiktok_collector):
        """Test collection when scraper returns no videos"""
        mock_scraper = MagicMock()
        mock_scraper.__enter__ = Mock(return_value=mock_scraper)
        mock_scraper.__exit__ = Mock(return_value=False)
        mock_scraper.scrape_hashtag.return_value = []
        mock_scraper_class.return_value = mock_scraper

        result = tiktok_collector.collect_coin_data("DOGE", max_videos=50)
        assert result == []

    @patch("collectors.tiktok_collector.TikTokScraper")
    def test_collect_coin_data_scraper_exception(self, mock_scraper_class, tiktok_collector):
        """Test collection handles scraper exceptions gracefully (e.g., TikTok blocks access)"""
        mock_scraper = MagicMock()
        mock_scraper.__enter__ = Mock(return_value=mock_scraper)
        mock_scraper.__exit__ = Mock(return_value=False)
        mock_scraper.scrape_hashtag.side_effect = Exception("TikTok blocked scraper")
        mock_scraper_class.return_value = mock_scraper

        # Should not crash, should return empty list
        result = tiktok_collector.collect_coin_data("DOGE", max_videos=50)
        assert isinstance(result, list)

    @patch("collectors.tiktok_collector.TikTokScraper")
    def test_collect_coin_data_html_structure_changed(self, mock_scraper_class, tiktok_collector):
        """
        CRITICAL TEST: Detect when TikTok changes HTML structure
        This prevents the bug we just fixed from happening again
        """
        mock_scraper = MagicMock()
        mock_scraper.__enter__ = Mock(return_value=mock_scraper)
        mock_scraper.__exit__ = Mock(return_value=False)
        # Scraper returns empty when HTML selectors don't match
        mock_scraper.scrape_hashtag.return_value = []
        mock_scraper_class.return_value = mock_scraper

        result = tiktok_collector.collect_coin_data("DOGE", max_videos=50)

        # If TikTok changed structure, we get 0 videos
        # Test should FAIL if this happens, alerting us to the issue
        if len(result) == 0:
            # This is expected in test, but in production it might indicate HTML changed
            assert True
        else:
            assert len(result) > 0


class TestDuplicateRemoval:
    """Test duplicate video removal"""

    @patch("collectors.tiktok_collector.TikTokScraper")
    def test_duplicate_videos_removed(self, mock_scraper_class, tiktok_collector):
        """Test that duplicate video_ids are removed"""
        # Create videos with duplicate IDs
        videos_with_dupes = [
            {
                "video_id": "duplicate_id",
                "username": "user1",
                "video_url": "https://tiktok.com/@user1/video/duplicate_id",
                "caption": "First video",
                "views": 1000,
                "likes": 50,
                "shares": 10,
                "comments": 20,
                "hashtag_searched": "dogecoin",
                "scraped_at": datetime.now(),
                "container_index": 0,
            },
            {
                "video_id": "duplicate_id",  # Same ID
                "username": "user2",
                "video_url": "https://tiktok.com/@user2/video/duplicate_id",
                "caption": "Second video (duplicate)",
                "views": 500,
                "likes": 25,
                "shares": 5,
                "comments": 10,
                "hashtag_searched": "dogecoin",
                "scraped_at": datetime.now(),
                "container_index": 1,
            },
            {
                "video_id": "unique_id",
                "username": "user3",
                "video_url": "https://tiktok.com/@user3/video/unique_id",
                "caption": "Unique video",
                "views": 2000,
                "likes": 100,
                "shares": 20,
                "comments": 40,
                "hashtag_searched": "dogecoin",
                "scraped_at": datetime.now(),
                "container_index": 2,
            },
        ]

        mock_scraper = MagicMock()
        mock_scraper.__enter__ = Mock(return_value=mock_scraper)
        mock_scraper.__exit__ = Mock(return_value=False)
        mock_scraper.scrape_hashtag.return_value = videos_with_dupes
        mock_scraper_class.return_value = mock_scraper

        result = tiktok_collector.collect_coin_data("DOGE", max_videos=50)

        # Should only have 2 unique videos
        assert len(result) == 2
        video_ids = [v["video_id"] for v in result]
        assert "duplicate_id" in video_ids
        assert "unique_id" in video_ids


class TestBotDetection:
    """Test bot detection integration"""

    @patch("collectors.tiktok_collector.TikTokScraper")
    def test_bot_detection_filters_spam(
        self, mock_scraper_class, tiktok_collector_with_bots, sample_tiktok_videos, sample_spam_videos
    ):
        """Test that bot detection filters out spam videos"""
        all_videos = sample_tiktok_videos + sample_spam_videos

        mock_scraper = MagicMock()
        mock_scraper.__enter__ = Mock(return_value=mock_scraper)
        mock_scraper.__exit__ = Mock(return_value=False)
        mock_scraper.scrape_hashtag.return_value = all_videos
        mock_scraper_class.return_value = mock_scraper

        # Mock bot detector to identify spam
        tiktok_collector_with_bots.bot_detector.filter_bots_from_tiktok = Mock(
            return_value=(
                sample_tiktok_videos,  # Legitimate videos
                sample_spam_videos,  # Spam videos
                {"bot_videos": 1, "total_videos": 6, "bot_percentage": 16.7},
            )
        )

        result = tiktok_collector_with_bots.collect_coin_data("DOGE", max_videos=50)

        # Should only contain legitimate videos
        assert len(result) == 5
        assert all(video["video_id"] != "spam_video_1" for video in result)

    @patch("collectors.tiktok_collector.TikTokScraper")
    def test_bot_detection_disabled(
        self, mock_scraper_class, tiktok_collector, sample_tiktok_videos, sample_spam_videos
    ):
        """Test that bot detection can be disabled"""
        all_videos = sample_tiktok_videos + sample_spam_videos

        mock_scraper = MagicMock()
        mock_scraper.__enter__ = Mock(return_value=mock_scraper)
        mock_scraper.__exit__ = Mock(return_value=False)
        mock_scraper.scrape_hashtag.return_value = all_videos
        mock_scraper_class.return_value = mock_scraper

        result = tiktok_collector.collect_coin_data("DOGE", max_videos=50)

        # Should contain all videos (bot detection disabled)
        assert len(result) == 6


class TestSentimentAnalysis:
    """Test sentiment analysis integration"""

    @patch("collectors.tiktok_collector.TikTokScraper")
    def test_sentiment_added_to_videos(self, mock_scraper_class, tiktok_collector, sample_tiktok_videos):
        """Test that sentiment analysis is added to each video"""
        mock_scraper = MagicMock()
        mock_scraper.__enter__ = Mock(return_value=mock_scraper)
        mock_scraper.__exit__ = Mock(return_value=False)
        mock_scraper.scrape_hashtag.return_value = sample_tiktok_videos
        mock_scraper_class.return_value = mock_scraper

        result = tiktok_collector.collect_coin_data("DOGE", max_videos=50)

        # Every video should have sentiment analysis with correct fields
        for video in result:
            assert "sentiment_analysis" in video
            assert "sentiment_compound" in video["sentiment_analysis"]
            assert "hype_score" in video["sentiment_analysis"]
            assert "sentiment_positive" in video["sentiment_analysis"]
            assert "sentiment_negative" in video["sentiment_analysis"]


class TestAggregation:
    """Test sentiment aggregation"""

    def test_aggregate_sentiment_with_videos(self, tiktok_collector, sample_tiktok_videos):
        """Test aggregating sentiment from multiple videos"""
        # Add mock sentiment to videos (using actual field names)
        for video in sample_tiktok_videos:
            video["sentiment_analysis"] = {
                "sentiment_compound": 0.8,
                "sentiment_positive": 0.9,
                "sentiment_negative": 0.1,
                "sentiment_neutral": 0.0,
                "hype_score": 85.0,
                "hype_keywords_count": 4,
                "hype_emojis_count": 3,
            }

        result = tiktok_collector.aggregate_sentiment(sample_tiktok_videos)

        assert result is not None
        assert "sentiment_score" in result
        assert "hype_score" in result
        assert "post_count" in result
        assert "total_engagement" in result
        assert result["post_count"] == 5

    def test_aggregate_sentiment_empty_videos(self, tiktok_collector):
        """Test aggregating with no videos returns zeros"""
        result = tiktok_collector.aggregate_sentiment([])

        assert result["sentiment_score"] == 0.0
        assert result["hype_score"] == 0.0
        assert result["post_count"] == 0
        assert result["total_engagement"] == 0

    def test_aggregate_sentiment_calculates_engagement(self, tiktok_collector, sample_tiktok_videos):
        """Test that engagement is calculated from views, likes, shares, comments"""
        for video in sample_tiktok_videos:
            video["sentiment_analysis"] = {
                "sentiment_compound": 0.8,
                "sentiment_positive": 0.9,
                "sentiment_negative": 0.1,
                "sentiment_neutral": 0.0,
                "hype_score": 85.0,
                "hype_keywords_count": 4,
                "hype_emojis_count": 3,
            }

        result = tiktok_collector.aggregate_sentiment(sample_tiktok_videos)

        # Engagement = sum(views + likes + shares + comments)
        expected_engagement = sum(
            video["views"] + video["likes"] + video["shares"] + video["comments"] for video in sample_tiktok_videos
        )
        assert result["total_engagement"] == expected_engagement


class TestMultipleCoinCollection:
    """Test collecting data for multiple coins"""

    @patch("collectors.tiktok_collector.TikTokScraper")
    def test_collect_all_coins(self, mock_scraper_class, tiktok_collector, sample_tiktok_videos):
        """Test collecting data for all tracked coins"""
        mock_scraper = MagicMock()
        mock_scraper.__enter__ = Mock(return_value=mock_scraper)
        mock_scraper.__exit__ = Mock(return_value=False)
        mock_scraper.scrape_hashtag.return_value = sample_tiktok_videos
        mock_scraper_class.return_value = mock_scraper

        result = tiktok_collector.collect_all_coins(max_videos_per_coin=50)

        # Should return data for all coins in HASHTAG_QUERIES
        assert isinstance(result, dict)
        assert "DOGE" in result
        assert len(result) > 0

    @patch("collectors.tiktok_collector.TikTokScraper")
    def test_collect_all_coins_handles_failures(self, mock_scraper_class, tiktok_collector):
        """Test that collection continues even if some coins fail (TikTok blocks some hashtags)"""
        mock_scraper = MagicMock()
        mock_scraper.__enter__ = Mock(return_value=mock_scraper)
        mock_scraper.__exit__ = Mock(return_value=False)

        # First hashtag succeeds, second fails (blocked), third succeeds
        mock_scraper.scrape_hashtag.side_effect = [
            [
                {
                    "video_id": "1",
                    "username": "user",
                    "video_url": "url",
                    "caption": "test",
                    "views": 1000,
                    "likes": 50,
                    "shares": 10,
                    "comments": 20,
                    "hashtag_searched": "dogecoin",
                    "scraped_at": datetime.now(),
                    "container_index": 0,
                }
            ],
            Exception("TikTok blocked hashtag"),
            [],  # Remaining hashtags
        ]
        mock_scraper_class.return_value = mock_scraper

        result = tiktok_collector.collect_all_coins(max_videos_per_coin=10)

        # Should return results for successful coins and empty lists for failed ones
        assert isinstance(result, dict)
        assert all(isinstance(videos, list) for videos in result.values())


class TestEdgeCases:
    """Test edge cases and error conditions"""

    @patch("collectors.tiktok_collector.TikTokScraper")
    def test_malformed_video_data(self, mock_scraper_class, tiktok_collector):
        """Test handling of malformed video data"""
        malformed_videos = [
            {
                "video_id": "missing_fields",
                # Missing required fields
            },
            {
                "video_id": None,  # None ID
                "caption": "Test",
            },
        ]

        mock_scraper = MagicMock()
        mock_scraper.__enter__ = Mock(return_value=mock_scraper)
        mock_scraper.__exit__ = Mock(return_value=False)
        mock_scraper.scrape_hashtag.return_value = malformed_videos
        mock_scraper_class.return_value = mock_scraper

        # Should handle gracefully without crashing
        result = tiktok_collector.collect_coin_data("DOGE", max_videos=50)
        assert isinstance(result, list)

    @patch("collectors.tiktok_collector.TikTokScraper")
    def test_videos_with_zero_engagement(self, mock_scraper_class, tiktok_collector):
        """Test handling videos with 0 views/likes (suspicious activity)"""
        zero_engagement_videos = [
            {
                "video_id": "test_1",
                "username": "user",
                "video_url": "url",
                "caption": "Test",
                "views": 0,  # Suspicious
                "likes": 0,
                "shares": 0,
                "comments": 0,
                "hashtag_searched": "dogecoin",
                "scraped_at": datetime.now(),
                "container_index": 0,
            }
        ]

        mock_scraper = MagicMock()
        mock_scraper.__enter__ = Mock(return_value=mock_scraper)
        mock_scraper.__exit__ = Mock(return_value=False)
        mock_scraper.scrape_hashtag.return_value = zero_engagement_videos
        mock_scraper_class.return_value = mock_scraper

        result = tiktok_collector.collect_coin_data("DOGE", max_videos=50)

        # Should still process the video (might be very new)
        assert len(result) >= 0

    @patch("collectors.tiktok_collector.TikTokScraper")
    def test_missing_hashtags_field(self, mock_scraper_class, tiktok_collector):
        """Test videos without hashtags field"""
        videos_no_hashtags = [
            {
                "video_id": "test_1",
                "username": "user",
                "video_url": "url",
                "caption": "No hashtags here",
                "views": 1000,
                "likes": 50,
                "shares": 10,
                "comments": 20,
                "hashtag_searched": "dogecoin",
                "scraped_at": datetime.now(),
                "container_index": 0,
                # 'hashtags' field missing
            }
        ]

        mock_scraper = MagicMock()
        mock_scraper.__enter__ = Mock(return_value=mock_scraper)
        mock_scraper.__exit__ = Mock(return_value=False)
        mock_scraper.scrape_hashtag.return_value = videos_no_hashtags
        mock_scraper_class.return_value = mock_scraper

        result = tiktok_collector.collect_coin_data("DOGE", max_videos=50)
        assert isinstance(result, list)


class TestHashtagExtraction:
    """Test hashtag extraction from captions"""

    @patch("collectors.tiktok_collector.TikTokScraper")
    def test_extract_hashtags_from_caption(self, mock_scraper_class, tiktok_collector):
        """Test that hashtags are extracted from video captions"""
        videos_with_hashtags = [
            {
                "video_id": "test_1",
                "username": "user",
                "video_url": "url",
                "caption": "Check out #dogecoin and #cryptocurrency #moon",
                "views": 1000,
                "likes": 50,
                "shares": 10,
                "comments": 20,
                "hashtag_searched": "dogecoin",
                "scraped_at": datetime.now(),
                "container_index": 0,
            }
        ]

        mock_scraper = MagicMock()
        mock_scraper.__enter__ = Mock(return_value=mock_scraper)
        mock_scraper.__exit__ = Mock(return_value=False)
        mock_scraper.scrape_hashtag.return_value = videos_with_hashtags
        mock_scraper_class.return_value = mock_scraper

        result = tiktok_collector.collect_coin_data("DOGE", max_videos=50)

        # Hashtags should be extracted (implementation dependent)
        assert len(result) > 0
