"""
Sentiment Analyzer for Social Media Content
===========================================
Analyzes sentiment and hype levels for Reddit posts and TikTok videos
Uses VADER sentiment analysis and custom hype scoring
"""

import re
import logging
from typing import Dict, List, Optional
from datetime import datetime
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


class SentimentAnalyzer:
    """
    Analyzes sentiment and hype for social media content
    Compatible with both Reddit posts and TikTok captions
    """

    # Hype indicators (from twitter_hype_collector.py)
    HYPE_KEYWORDS = [
        'moon', 'rocket', 'lambo', 'wen', 'pump', 'bullish', 'gem',
        'x100', 'x10', 'mooning', 'rocketship', 'millionaire',
        'buy now', 'dont miss', "don't miss", 'last chance', 'fomo', 'all in',
        'to the moon', 'lfg', 'lets go', "let's go", 'hodl', 'diamond hands',
        'paper hands', 'ape', 'yolo', 'wagmi', 'ngmi', 'gm', 'probably nothing'
    ]

    # Hype emojis
    HYPE_EMOJIS = ['🚀', '🌙', '💎', '🙌', '💰', '🔥', '📈', '💪', '🐕', '🐸', '⚡', '💯', '🤑', '🎯']

    def __init__(self):
        """Initialize sentiment analyzer"""
        self.vader = SentimentIntensityAnalyzer()
        logging.info("✅ Sentiment analyzer initialized")

    def analyze_text(self, text: str) -> Dict[str, float]:
        """
        Analyze sentiment of text using VADER

        Args:
            text: Text to analyze

        Returns:
            Dictionary with sentiment scores
        """
        if not text or not isinstance(text, str):
            return {
                'compound': 0.0,
                'positive': 0.0,
                'negative': 0.0,
                'neutral': 1.0
            }

        scores = self.vader.polarity_scores(text)
        return {
            'compound': scores['compound'],
            'positive': scores['pos'],
            'negative': scores['neg'],
            'neutral': scores['neu']
        }

    def calculate_hype_score(self, text: str) -> Dict[str, any]:
        """
        Calculate custom hype score (0-100) based on keywords and emojis

        Args:
            text: Text to analyze

        Returns:
            Dictionary with hype metrics
        """
        if not text:
            return {
                'hype_score': 0,
                'hype_keywords_count': 0,
                'hype_emojis_count': 0,
                'hype_keywords_found': []
            }

        text_lower = text.lower()

        # Count hype keywords
        keywords_found = []
        for keyword in self.HYPE_KEYWORDS:
            if keyword in text_lower:
                keywords_found.append(keyword)

        keyword_count = len(keywords_found)

        # Count hype emojis
        emoji_count = sum(1 for emoji in self.HYPE_EMOJIS if emoji in text)

        # Calculate hype score (0-100)
        # Base: keyword count * 10 (max 50)
        # Bonus: emoji count * 5 (max 25)
        # Bonus: multiple exclamation marks (max 15)
        # Bonus: all caps words (max 10)

        keyword_score = min(keyword_count * 10, 50)
        emoji_score = min(emoji_count * 5, 25)

        # Check for excessive exclamation marks (hype indicator)
        exclamation_count = text.count('!')
        exclamation_score = min(exclamation_count * 3, 15)

        # Check for all-caps words (excluding single letters)
        caps_words = [word for word in text.split() if word.isupper() and len(word) > 1]
        caps_score = min(len(caps_words) * 2, 10)

        total_score = keyword_score + emoji_score + exclamation_score + caps_score

        return {
            'hype_score': min(total_score, 100),
            'hype_keywords_count': keyword_count,
            'hype_emojis_count': emoji_count,
            'hype_keywords_found': keywords_found
        }

    def analyze_reddit_post(self, post_data: Dict) -> Dict[str, any]:
        """
        Analyze sentiment and hype for a Reddit post

        Args:
            post_data: Reddit post dictionary with 'title' and optional 'body'

        Returns:
            Complete sentiment analysis
        """
        # Combine title and body for analysis
        title = post_data.get('title', '')
        body = post_data.get('body', '')
        combined_text = f"{title} {body}".strip()

        # Get sentiment scores
        sentiment = self.analyze_text(combined_text)

        # Get hype scores
        hype = self.calculate_hype_score(combined_text)

        # Engagement-based boost (high engagement = more hype)
        score = post_data.get('score', 0)
        comments = post_data.get('num_comments', 0)
        engagement_multiplier = 1.0 + min((score + comments) / 1000, 0.5)  # Up to 50% boost

        adjusted_hype_score = min(hype['hype_score'] * engagement_multiplier, 100)

        return {
            'text_analyzed': combined_text[:500],  # First 500 chars for reference
            'sentiment_compound': sentiment['compound'],
            'sentiment_positive': sentiment['positive'],
            'sentiment_negative': sentiment['negative'],
            'sentiment_neutral': sentiment['neutral'],
            'hype_score': adjusted_hype_score,
            'hype_keywords_count': hype['hype_keywords_count'],
            'hype_emojis_count': hype['hype_emojis_count'],
            'hype_keywords_found': hype['hype_keywords_found'],
            'engagement_multiplier': engagement_multiplier,
            'analyzed_at': datetime.utcnow()
        }

    def analyze_tiktok_video(self, video_data: Dict) -> Dict[str, any]:
        """
        Analyze sentiment and hype for a TikTok video caption

        Args:
            video_data: TikTok video dictionary with 'caption'

        Returns:
            Complete sentiment analysis
        """
        caption = video_data.get('caption', '')

        # Get sentiment scores
        sentiment = self.analyze_text(caption)

        # Get hype scores
        hype = self.calculate_hype_score(caption)

        # View-based boost (viral videos = more hype)
        views = video_data.get('views', 0)
        view_multiplier = 1.0 + min(views / 1_000_000, 1.0)  # Up to 100% boost for 1M+ views

        adjusted_hype_score = min(hype['hype_score'] * view_multiplier, 100)

        return {
            'text_analyzed': caption[:500],  # First 500 chars
            'sentiment_compound': sentiment['compound'],
            'sentiment_positive': sentiment['positive'],
            'sentiment_negative': sentiment['negative'],
            'sentiment_neutral': sentiment['neutral'],
            'hype_score': adjusted_hype_score,
            'hype_keywords_count': hype['hype_keywords_count'],
            'hype_emojis_count': hype['hype_emojis_count'],
            'hype_keywords_found': hype['hype_keywords_found'],
            'view_multiplier': view_multiplier,
            'analyzed_at': datetime.utcnow()
        }

    def aggregate_sentiment(self, analyses: List[Dict], source: str) -> Dict[str, any]:
        """
        Aggregate multiple sentiment analyses into summary metrics

        Args:
            analyses: List of sentiment analysis results
            source: Source name ('reddit', 'tiktok')

        Returns:
            Aggregated metrics suitable for database storage
        """
        if not analyses:
            return {
                'source': source,
                'sentiment_score': 0.0,
                'sentiment_positive': 0.0,
                'sentiment_negative': 0.0,
                'sentiment_neutral': 1.0,
                'hype_score': 0.0,
                'hype_keywords_count': 0,
                'hype_emojis_count': 0,
                'post_count': 0,
                'total_engagement': 0
            }

        # Calculate averages
        avg_compound = sum(a['sentiment_compound'] for a in analyses) / len(analyses)
        avg_positive = sum(a['sentiment_positive'] for a in analyses) / len(analyses)
        avg_negative = sum(a['sentiment_negative'] for a in analyses) / len(analyses)
        avg_neutral = sum(a['sentiment_neutral'] for a in analyses) / len(analyses)
        avg_hype = sum(a['hype_score'] for a in analyses) / len(analyses)

        total_keywords = sum(a['hype_keywords_count'] for a in analyses)
        total_emojis = sum(a['hype_emojis_count'] for a in analyses)

        return {
            'source': source,
            'sentiment_score': round(avg_compound, 4),
            'sentiment_positive': round(avg_positive, 4),
            'sentiment_negative': round(avg_negative, 4),
            'sentiment_neutral': round(avg_neutral, 4),
            'hype_score': round(avg_hype, 2),
            'hype_keywords_count': total_keywords,
            'hype_emojis_count': total_emojis,
            'post_count': len(analyses),
            'timestamp': datetime.utcnow()
        }

    def classify_sentiment(self, compound_score: float) -> str:
        """
        Classify sentiment as positive, negative, or neutral

        Args:
            compound_score: VADER compound score (-1 to +1)

        Returns:
            'positive', 'negative', or 'neutral'
        """
        if compound_score >= 0.05:
            return 'positive'
        elif compound_score <= -0.05:
            return 'negative'
        else:
            return 'neutral'

    def classify_hype_level(self, hype_score: float) -> str:
        """
        Classify hype level

        Args:
            hype_score: Hype score (0-100)

        Returns:
            'extreme', 'high', 'moderate', 'low', 'none'
        """
        if hype_score >= 80:
            return 'extreme'
        elif hype_score >= 60:
            return 'high'
        elif hype_score >= 40:
            return 'moderate'
        elif hype_score >= 20:
            return 'low'
        else:
            return 'none'
