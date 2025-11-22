"""
Bot Detection System
====================
Identifies suspicious/bot accounts in social media data
Based on research methodology recommendations for data quality
"""

import re
import logging
from datetime import datetime, timedelta
from typing import Dict, List
from collections import Counter

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


class BotDetector:
    """Detects bot accounts in Reddit and TikTok data"""

    def __init__(self):
        """Initialize bot detector with heuristic thresholds"""

        # Reddit bot detection thresholds
        self.reddit_thresholds = {
            'min_account_age_days': 7,  # Accounts younger than 7 days are suspicious
            'max_post_frequency_per_hour': 10,  # More than 10 posts/hour is suspicious
            'min_karma_for_age': 10,  # Accounts with <10 karma and >30 days old
            'username_pattern_weight': 0.3,  # Weight for random username pattern
            'low_engagement_threshold': 5,  # Posts with <5 upvotes consistently
        }

        # TikTok bot detection thresholds
        self.tiktok_thresholds = {
            'min_account_age_days': 7,
            'follower_following_ratio': 0.1,  # Following many, few followers
            'max_following_ratio': 10.0,  # Many followers, following few (influencer farm)
            'min_avg_engagement': 0.01,  # <1% engagement rate is suspicious
            'username_pattern_weight': 0.3,
        }

        # Suspicious username patterns (bots often use these)
        self.suspicious_patterns = [
            r'^[a-z]+\d{4,}$',  # lowercase + 4+ digits
            r'^\w{1,3}\d{6,}$',  # 1-3 chars + 6+ digits
            r'^(crypto|moon|rocket|pump)\w+\d+$',  # crypto-related + numbers
            r'^bot\w+',  # starts with "bot"
            r'^\d+\w+\d+$',  # numbers-letters-numbers
        ]

        logging.info("Bot detector initialized")

    def analyze_reddit_account(self, post_data: Dict) -> Dict:
        """
        Analyze a Reddit account for bot characteristics

        Args:
            post_data: Reddit post data with author info

        Returns:
            Dict with bot_score (0-100) and flags
        """
        flags = []
        score = 0.0

        username = post_data.get('author', '')
        if username in ['[deleted]', 'AutoModerator']:
            return {'bot_score': 0.0, 'flags': ['system_account'], 'is_bot': False}

        # Check username pattern
        if self._check_suspicious_username(username):
            score += 20
            flags.append('suspicious_username')

        # Check account age (if available)
        account_age = post_data.get('author_created_utc')
        if account_age:
            age_days = (datetime.utcnow() - datetime.fromtimestamp(account_age)).days
            if age_days < self.reddit_thresholds['min_account_age_days']:
                score += 30
                flags.append('new_account')

        # Check karma (if available)
        karma = post_data.get('author_karma', 0)
        if karma < self.reddit_thresholds['min_karma_for_age'] and account_age:
            if age_days > 30:  # Old account with low karma
                score += 25
                flags.append('low_karma_old_account')

        # Check engagement on this post
        upvotes = post_data.get('score', 0)
        if upvotes < self.reddit_thresholds['low_engagement_threshold']:
            score += 10
            flags.append('low_engagement')

        # Check for excessive posting (if we have multiple posts from same author)
        # This would require tracking across multiple posts - simplified here

        return {
            'bot_score': min(100.0, score),
            'flags': flags,
            'is_bot': score >= 50  # 50+ score = likely bot
        }

    def analyze_tiktok_account(self, video_data: Dict) -> Dict:
        """
        Analyze a TikTok account for bot characteristics

        Args:
            video_data: TikTok video data with account info

        Returns:
            Dict with bot_score (0-100) and flags
        """
        flags = []
        score = 0.0

        username = video_data.get('username', '')

        # Check username pattern
        if self._check_suspicious_username(username):
            score += 20
            flags.append('suspicious_username')

        # Check follower/following ratio
        followers = video_data.get('followers', 0)
        following = video_data.get('following', 0)

        if following > 0:
            ratio = followers / following

            # Bot pattern 1: Following many, few followers
            if ratio < self.tiktok_thresholds['follower_following_ratio']:
                score += 30
                flags.append('low_follower_ratio')

            # Bot pattern 2: Many followers, following few (influencer farms)
            if ratio > self.tiktok_thresholds['max_following_ratio'] and followers > 10000:
                score += 20
                flags.append('influencer_farm_pattern')

        # Check engagement rate
        views = video_data.get('views', 0)
        likes = video_data.get('likes', 0)

        if views > 0:
            engagement_rate = likes / views
            if engagement_rate < self.tiktok_thresholds['min_avg_engagement']:
                score += 25
                flags.append('low_engagement_rate')

        # Check if all metrics are suspiciously round numbers (often indicates fake data)
        if self._check_round_numbers(video_data):
            score += 15
            flags.append('suspicious_metrics')

        return {
            'bot_score': min(100.0, score),
            'flags': flags,
            'is_bot': score >= 50
        }

    def _check_suspicious_username(self, username: str) -> bool:
        """Check if username matches bot patterns"""
        username_lower = username.lower()

        for pattern in self.suspicious_patterns:
            if re.match(pattern, username_lower):
                return True

        return False

    def _check_round_numbers(self, data: Dict) -> bool:
        """Check if metrics are suspiciously round numbers"""
        metrics = [
            data.get('views', 0),
            data.get('likes', 0),
            data.get('followers', 0),
            data.get('following', 0)
        ]

        # Count how many are perfectly divisible by 1000
        round_count = sum(1 for m in metrics if m > 0 and m % 1000 == 0)

        # If 3+ metrics are round thousands, suspicious
        return round_count >= 3

    def filter_bots_from_reddit(self, posts: List[Dict], threshold: float = 50.0) -> tuple:
        """
        Filter bot posts from Reddit data

        Args:
            posts: List of Reddit posts
            threshold: Bot score threshold (default 50)

        Returns:
            (filtered_posts, bot_posts, statistics)
        """
        filtered_posts = []
        bot_posts = []
        bot_scores = []

        for post in posts:
            analysis = self.analyze_reddit_account(post)
            post['bot_analysis'] = analysis
            bot_scores.append(analysis['bot_score'])

            if analysis['bot_score'] >= threshold:
                bot_posts.append(post)
            else:
                filtered_posts.append(post)

        stats = {
            'total_posts': len(posts),
            'filtered_posts': len(filtered_posts),
            'bot_posts': len(bot_posts),
            'bot_percentage': (len(bot_posts) / len(posts) * 100) if posts else 0,
            'avg_bot_score': sum(bot_scores) / len(bot_scores) if bot_scores else 0,
            'common_flags': self._get_common_flags([p['bot_analysis'] for p in posts])
        }

        if bot_posts:
            logging.info(f"Reddit bot detection: {len(bot_posts)}/{len(posts)} posts flagged ({stats['bot_percentage']:.1f}%)")

        return filtered_posts, bot_posts, stats

    def filter_bots_from_tiktok(self, videos: List[Dict], threshold: float = 50.0) -> tuple:
        """
        Filter bot videos from TikTok data

        Args:
            videos: List of TikTok videos
            threshold: Bot score threshold (default 50)

        Returns:
            (filtered_videos, bot_videos, statistics)
        """
        filtered_videos = []
        bot_videos = []
        bot_scores = []

        for video in videos:
            analysis = self.analyze_tiktok_account(video)
            video['bot_analysis'] = analysis
            bot_scores.append(analysis['bot_score'])

            if analysis['bot_score'] >= threshold:
                bot_videos.append(video)
            else:
                filtered_videos.append(video)

        stats = {
            'total_videos': len(videos),
            'filtered_videos': len(filtered_videos),
            'bot_videos': len(bot_videos),
            'bot_percentage': (len(bot_videos) / len(videos) * 100) if videos else 0,
            'avg_bot_score': sum(bot_scores) / len(bot_scores) if bot_scores else 0,
            'common_flags': self._get_common_flags([v['bot_analysis'] for v in videos])
        }

        if bot_videos:
            logging.info(f"TikTok bot detection: {len(bot_videos)}/{len(videos)} videos flagged ({stats['bot_percentage']:.1f}%)")

        return filtered_videos, bot_videos, stats

    def _get_common_flags(self, analyses: List[Dict]) -> Dict:
        """Get most common bot flags"""
        all_flags = []
        for analysis in analyses:
            all_flags.extend(analysis.get('flags', []))

        flag_counts = Counter(all_flags)
        return dict(flag_counts.most_common(5))

    def get_bot_statistics(self, data: List[Dict], platform: str) -> Dict:
        """
        Get bot detection statistics without filtering

        Args:
            data: List of posts/videos
            platform: 'reddit' or 'tiktok'

        Returns:
            Statistics dictionary
        """
        bot_scores = []
        all_flags = []

        for item in data:
            if platform == 'reddit':
                analysis = self.analyze_reddit_account(item)
            elif platform == 'tiktok':
                analysis = self.analyze_tiktok_account(item)
            else:
                continue

            bot_scores.append(analysis['bot_score'])
            all_flags.extend(analysis.get('flags', []))

        flag_counts = Counter(all_flags)

        return {
            'total_items': len(data),
            'avg_bot_score': sum(bot_scores) / len(bot_scores) if bot_scores else 0,
            'high_risk_count': sum(1 for score in bot_scores if score >= 70),
            'medium_risk_count': sum(1 for score in bot_scores if 50 <= score < 70),
            'low_risk_count': sum(1 for score in bot_scores if score < 50),
            'common_flags': dict(flag_counts.most_common(5))
        }


def detect_bots_in_reddit(posts: List[Dict], threshold: float = 50.0) -> tuple:
    """
    Convenience function for Reddit bot detection

    Args:
        posts: List of Reddit posts
        threshold: Bot score threshold

    Returns:
        (filtered_posts, bot_posts, statistics)
    """
    detector = BotDetector()
    return detector.filter_bots_from_reddit(posts, threshold)


def detect_bots_in_tiktok(videos: List[Dict], threshold: float = 50.0) -> tuple:
    """
    Convenience function for TikTok bot detection

    Args:
        videos: List of TikTok videos
        threshold: Bot score threshold

    Returns:
        (filtered_videos, bot_videos, statistics)
    """
    detector = BotDetector()
    return detector.filter_bots_from_tiktok(videos, threshold)
