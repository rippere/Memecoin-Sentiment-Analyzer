"""
Pytest configuration and shared fixtures
"""
import sys
from pathlib import Path

import pytest

# Add project root to path for imports
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


@pytest.fixture
def sentiment_analyzer():
    """Create a SentimentAnalyzer instance"""
    from collectors.sentiment_analyzer import SentimentAnalyzer
    return SentimentAnalyzer()


@pytest.fixture
def sample_reddit_post():
    """Sample Reddit post data"""
    return {
        'title': 'DOGE to the moon! This is going to explode!',
        'body': 'Just bought 10000 DOGE, diamond hands forever! HODL!',
        'score': 500,
        'num_comments': 150
    }


@pytest.fixture
def sample_tiktok_video():
    """Sample TikTok video data"""
    return {
        'caption': 'PEPE is going crazy right now! Buy before its too late!',
        'views': 50000,
        'likes': 2000
    }


@pytest.fixture
def negative_post():
    """Sample negative sentiment post"""
    return {
        'title': 'SHIB is a scam, lost everything',
        'body': 'This coin crashed and I lost all my money. Total rug pull.',
        'score': 100,
        'num_comments': 50
    }


@pytest.fixture
def neutral_post():
    """Sample neutral sentiment post"""
    return {
        'title': 'Analysis of DOGE price movement',
        'body': 'The price moved 2% today. Volume was average.',
        'score': 20,
        'num_comments': 5
    }
