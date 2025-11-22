"""
Unit tests for SentimentAnalyzer
"""
import pytest


class TestAnalyzeText:
    """Tests for analyze_text method"""

    def test_positive_text(self, sentiment_analyzer):
        """Test positive sentiment detection"""
        result = sentiment_analyzer.analyze_text("This is amazing! I love it!")
        assert result['compound'] > 0
        assert result['positive'] > result['negative']

    def test_negative_text(self, sentiment_analyzer):
        """Test negative sentiment detection"""
        result = sentiment_analyzer.analyze_text("This is terrible. I hate it.")
        assert result['compound'] < 0
        assert result['negative'] > result['positive']

    def test_neutral_text(self, sentiment_analyzer):
        """Test neutral sentiment detection"""
        result = sentiment_analyzer.analyze_text("The price is 100 dollars.")
        assert result['neutral'] > 0.5

    def test_empty_text(self, sentiment_analyzer):
        """Test empty text returns neutral sentiment"""
        result = sentiment_analyzer.analyze_text("")
        assert result['compound'] == 0.0
        assert result['neutral'] == 1.0

    def test_none_text(self, sentiment_analyzer):
        """Test None text returns neutral sentiment"""
        result = sentiment_analyzer.analyze_text(None)
        assert result['compound'] == 0.0
        assert result['neutral'] == 1.0


class TestCalculateHypeScore:
    """Tests for calculate_hype_score method"""

    def test_high_hype_keywords(self, sentiment_analyzer):
        """Test hype score with multiple keywords"""
        result = sentiment_analyzer.calculate_hype_score(
            "HODL! Diamond hands! To the moon! LFG!"
        )
        assert result['hype_score'] >= 40
        assert 'hodl' in result['hype_keywords_found']
        assert 'diamond hands' in result['hype_keywords_found']

    def test_hype_emojis(self, sentiment_analyzer):
        """Test hype score with emojis"""
        result = sentiment_analyzer.calculate_hype_score("Going up! 🚀🚀🚀💎🔥")
        assert result['hype_emojis_count'] >= 3

    def test_no_hype(self, sentiment_analyzer):
        """Test low hype score for normal text"""
        result = sentiment_analyzer.calculate_hype_score(
            "The market closed at normal levels today."
        )
        assert result['hype_score'] < 20
        assert result['hype_keywords_count'] == 0

    def test_empty_text_hype(self, sentiment_analyzer):
        """Test empty text returns zero hype"""
        result = sentiment_analyzer.calculate_hype_score("")
        assert result['hype_score'] == 0
        assert result['hype_keywords_count'] == 0

    def test_max_hype_score(self, sentiment_analyzer):
        """Test hype score doesn't exceed 100"""
        result = sentiment_analyzer.calculate_hype_score(
            "MOON ROCKET LAMBO PUMP BULLISH HODL LFG WAGMI!!!!!!"
        )
        assert result['hype_score'] <= 100


class TestAnalyzeRedditPost:
    """Tests for analyze_reddit_post method"""

    def test_positive_post(self, sentiment_analyzer, sample_reddit_post):
        """Test positive Reddit post analysis"""
        result = sentiment_analyzer.analyze_reddit_post(sample_reddit_post)
        assert result['sentiment_compound'] > 0
        assert result['hype_score'] > 0
        assert 'analyzed_at' in result

    def test_negative_post(self, sentiment_analyzer, negative_post):
        """Test negative Reddit post analysis"""
        result = sentiment_analyzer.analyze_reddit_post(negative_post)
        assert result['sentiment_compound'] < 0

    def test_engagement_boost(self, sentiment_analyzer):
        """Test engagement multiplier increases hype"""
        low_engagement = {'title': 'Moon!', 'body': '', 'score': 1, 'num_comments': 0}
        high_engagement = {'title': 'Moon!', 'body': '', 'score': 5000, 'num_comments': 500}

        low_result = sentiment_analyzer.analyze_reddit_post(low_engagement)
        high_result = sentiment_analyzer.analyze_reddit_post(high_engagement)

        assert high_result['engagement_multiplier'] > low_result['engagement_multiplier']


class TestAnalyzeTiktokVideo:
    """Tests for analyze_tiktok_video method"""

    def test_tiktok_analysis(self, sentiment_analyzer, sample_tiktok_video):
        """Test TikTok video analysis"""
        result = sentiment_analyzer.analyze_tiktok_video(sample_tiktok_video)
        assert 'sentiment_compound' in result
        assert 'hype_score' in result
        assert 'view_multiplier' in result

    def test_viral_video_boost(self, sentiment_analyzer):
        """Test view multiplier for viral videos"""
        normal = {'caption': 'DOGE', 'views': 1000}
        viral = {'caption': 'DOGE', 'views': 2_000_000}

        normal_result = sentiment_analyzer.analyze_tiktok_video(normal)
        viral_result = sentiment_analyzer.analyze_tiktok_video(viral)

        assert viral_result['view_multiplier'] > normal_result['view_multiplier']


class TestAggregateSentiment:
    """Tests for aggregate_sentiment method"""

    def test_aggregate_multiple(self, sentiment_analyzer):
        """Test aggregation of multiple analyses"""
        analyses = [
            {'sentiment_compound': 0.5, 'sentiment_positive': 0.6,
             'sentiment_negative': 0.1, 'sentiment_neutral': 0.3,
             'hype_score': 60, 'hype_keywords_count': 3, 'hype_emojis_count': 2},
            {'sentiment_compound': 0.3, 'sentiment_positive': 0.4,
             'sentiment_negative': 0.2, 'sentiment_neutral': 0.4,
             'hype_score': 40, 'hype_keywords_count': 2, 'hype_emojis_count': 1}
        ]

        result = sentiment_analyzer.aggregate_sentiment(analyses, 'reddit')

        assert result['source'] == 'reddit'
        assert result['sentiment_score'] == 0.4  # Average of 0.5 and 0.3
        assert result['post_count'] == 2
        assert result['hype_keywords_count'] == 5  # Sum

    def test_aggregate_empty(self, sentiment_analyzer):
        """Test aggregation with empty list"""
        result = sentiment_analyzer.aggregate_sentiment([], 'reddit')

        assert result['sentiment_score'] == 0.0
        assert result['post_count'] == 0


class TestClassifications:
    """Tests for classification methods"""

    def test_classify_positive_sentiment(self, sentiment_analyzer):
        """Test positive sentiment classification"""
        assert sentiment_analyzer.classify_sentiment(0.5) == 'positive'
        assert sentiment_analyzer.classify_sentiment(0.05) == 'positive'

    def test_classify_negative_sentiment(self, sentiment_analyzer):
        """Test negative sentiment classification"""
        assert sentiment_analyzer.classify_sentiment(-0.5) == 'negative'
        assert sentiment_analyzer.classify_sentiment(-0.05) == 'negative'

    def test_classify_neutral_sentiment(self, sentiment_analyzer):
        """Test neutral sentiment classification"""
        assert sentiment_analyzer.classify_sentiment(0.0) == 'neutral'
        assert sentiment_analyzer.classify_sentiment(0.04) == 'neutral'

    def test_classify_hype_levels(self, sentiment_analyzer):
        """Test hype level classification"""
        assert sentiment_analyzer.classify_hype_level(90) == 'extreme'
        assert sentiment_analyzer.classify_hype_level(70) == 'high'
        assert sentiment_analyzer.classify_hype_level(50) == 'moderate'
        assert sentiment_analyzer.classify_hype_level(30) == 'low'
        assert sentiment_analyzer.classify_hype_level(10) == 'none'
