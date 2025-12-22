"""
Reddit Data Collector using PRAW (Official API)
================================================
Collects Reddit posts using Python Reddit API Wrapper (PRAW)
More reliable than web scraping, respects rate limits

For read-only access (no credentials needed):
- Uses Reddit's public API
- Rate limited to ~60 requests/minute
- No posting or commenting (just reading)

For authenticated access (better rate limits):
- Add to .env:
  REDDIT_CLIENT_ID=your_client_id
  REDDIT_CLIENT_SECRET=your_secret
  REDDIT_USER_AGENT=MemecoinsAnalyzer/1.0
"""

import praw
import os
import logging
from typing import List, Dict, Optional
from datetime import datetime
from dotenv import load_dotenv
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from collectors.sentiment_analyzer import SentimentAnalyzer

load_dotenv()
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


class RedditPRAWCollector:
    """Collects Reddit data using official PRAW library"""

    # Crypto-focused subreddits
    SUBREDDITS = [
        'CryptoCurrency',
        'CryptoMoonShots',
        'SatoshiStreetBets',
        'dogecoin',
        'SHIBArmy',
        'pepe_official',
        'memecoins',
        'CryptoMarkets'
    ]

    def __init__(self, use_auth: bool = True):
        """
        Initialize Reddit collector with PRAW

        Args:
            use_auth: Whether to use authenticated access (better rate limits)
        """
        self.sentiment_analyzer = SentimentAnalyzer()

        # Try authenticated access first
        client_id = os.getenv('REDDIT_CLIENT_ID')
        client_secret = os.getenv('REDDIT_CLIENT_SECRET')
        user_agent = os.getenv('REDDIT_USER_AGENT', 'MemecoinsAnalyzer/1.0')

        if use_auth and client_id and client_secret:
            logging.info("Initializing PRAW with authenticated access")
            self.reddit = praw.Reddit(
                client_id=client_id,
                client_secret=client_secret,
                user_agent=user_agent
            )
            self.authenticated = True
            logging.info(f"PRAW initialized (authenticated: True)")
        else:
            # Reddit API requires authentication
            logging.error("=" * 60)
            logging.error("Reddit API credentials required!")
            logging.error("=" * 60)
            logging.error("Reddit's API requires authentication even for reading public posts.")
            logging.error("")
            logging.error("Quick setup (takes 5 minutes, completely free):")
            logging.error("1. Go to: https://www.reddit.com/prefs/apps")
            logging.error("2. Click 'create app' or 'create another app'")
            logging.error("3. Fill in:")
            logging.error("   - Name: Memecoin Sentiment Analyzer")
            logging.error("   - Type: script")
            logging.error("   - Redirect URI: http://localhost:8000")
            logging.error("4. Copy your credentials to .env:")
            logging.error("   REDDIT_CLIENT_ID=your_client_id")
            logging.error("   REDDIT_CLIENT_SECRET=your_secret")
            logging.error("")
            logging.error("See docs/REDDIT_API_SETUP.md for detailed instructions")
            logging.error("=" * 60)
            raise ValueError("Reddit API credentials required. See error message above.")

    def search_subreddit(
        self,
        subreddit_name: str,
        query: str,
        limit: int = 50,
        time_filter: str = 'week'
    ) -> List[Dict]:
        """
        Search a subreddit for posts matching query

        Args:
            subreddit_name: Subreddit to search (without r/)
            query: Search query (coin name, ticker, etc.)
            limit: Maximum posts to return
            time_filter: Time filter (hour, day, week, month, year, all)

        Returns:
            List of post dictionaries
        """
        try:
            subreddit = self.reddit.subreddit(subreddit_name)
            posts = []

            for submission in subreddit.search(query, time_filter=time_filter, limit=limit):
                post_data = {
                    'post_id': submission.id,
                    'title': submission.title,
                    'text': submission.selftext,
                    'author': str(submission.author) if submission.author else '[deleted]',
                    'subreddit': subreddit_name,
                    'score': submission.score,
                    'upvote_ratio': submission.upvote_ratio,
                    'num_comments': submission.num_comments,
                    'created_utc': submission.created_utc,
                    'url': submission.url,
                    'permalink': f"https://reddit.com{submission.permalink}",
                    'flair': submission.link_flair_text,
                    'timestamp': datetime.fromtimestamp(submission.created_utc).isoformat()
                }

                # Add sentiment analysis
                sentiment = self.sentiment_analyzer.analyze_reddit_post(post_data)
                post_data['sentiment_analysis'] = sentiment

                posts.append(post_data)

            return posts

        except Exception as e:
            logging.error(f"Error searching r/{subreddit_name} for '{query}': {e}")
            return []

    def collect_coin_mentions(
        self,
        coin_symbol: str,
        coin_name: str,
        max_posts: int = 100,
        time_filter: str = 'week'
    ) -> List[Dict]:
        """
        Collect Reddit posts mentioning a specific coin

        Args:
            coin_symbol: e.g., 'DOGE'
            coin_name: e.g., 'dogecoin'
            max_posts: Maximum total posts to collect
            time_filter: Time period to search

        Returns:
            List of posts with sentiment analysis
        """
        all_posts = []
        posts_per_subreddit = max(10, max_posts // len(self.SUBREDDITS))

        # Search variations
        queries = [
            coin_name.lower(),
            f"${coin_symbol}",
            coin_symbol.upper(),
            coin_symbol.lower()
        ]

        logging.info(f"Collecting Reddit posts for {coin_symbol} ({coin_name})")

        for subreddit_name in self.SUBREDDITS:
            for query in queries:
                posts = self.search_subreddit(
                    subreddit_name,
                    query,
                    limit=posts_per_subreddit // len(queries),
                    time_filter=time_filter
                )
                all_posts.extend(posts)

        # Deduplicate by post_id
        unique_posts = {}
        for post in all_posts:
            post_id = post['post_id']
            if post_id not in unique_posts:
                unique_posts[post_id] = post

        result = list(unique_posts.values())[:max_posts]

        logging.info(f"Collected {len(result)} unique posts for {coin_symbol}")

        return result

    def get_hot_posts(self, subreddit_name: str, limit: int = 50) -> List[Dict]:
        """
        Get hot/trending posts from a subreddit

        Args:
            subreddit_name: Subreddit to fetch from
            limit: Maximum posts to return

        Returns:
            List of hot posts
        """
        try:
            subreddit = self.reddit.subreddit(subreddit_name)
            posts = []

            for submission in subreddit.hot(limit=limit):
                post_data = {
                    'post_id': submission.id,
                    'title': submission.title,
                    'text': submission.selftext,
                    'author': str(submission.author) if submission.author else '[deleted]',
                    'subreddit': subreddit_name,
                    'score': submission.score,
                    'upvote_ratio': submission.upvote_ratio,
                    'num_comments': submission.num_comments,
                    'created_utc': submission.created_utc,
                    'timestamp': datetime.fromtimestamp(submission.created_utc).isoformat(),
                    'permalink': f"https://reddit.com{submission.permalink}"
                }

                # Add sentiment
                sentiment = self.sentiment_analyzer.analyze_reddit_post(post_data)
                post_data['sentiment_analysis'] = sentiment

                posts.append(post_data)

            return posts

        except Exception as e:
            logging.error(f"Error fetching hot posts from r/{subreddit_name}: {e}")
            return []

    def collect_trending_coins_data(
        self,
        coins: List[Dict],
        max_posts_per_coin: int = 50
    ) -> Dict[str, List[Dict]]:
        """
        Collect Reddit data for multiple coins (from trending list)

        Args:
            coins: List of coin dicts with 'symbol' and 'name' keys
            max_posts_per_coin: Max posts per coin

        Returns:
            Dictionary mapping coin_symbol -> posts
        """
        results = {}

        for coin in coins:
            symbol = coin.get('symbol', '').upper()
            name = coin.get('name', symbol).lower()

            try:
                posts = self.collect_coin_mentions(
                    coin_symbol=symbol,
                    coin_name=name,
                    max_posts=max_posts_per_coin
                )
                results[symbol] = posts
            except Exception as e:
                logging.error(f"Error collecting data for {symbol}: {e}")
                results[symbol] = []

        total_posts = sum(len(posts) for posts in results.values())
        logging.info(f"Total Reddit posts collected: {total_posts} across {len(coins)} coins")

        return results

    def aggregate_sentiment(self, posts: List[Dict]) -> Dict:
        """
        Aggregate sentiment from multiple posts

        Args:
            posts: List of posts with sentiment_analysis

        Returns:
            Aggregated sentiment metrics
        """
        if not posts:
            return {
                'sentiment_score': 0.0,
                'hype_score': 0.0,
                'post_count': 0,
                'total_engagement': 0
            }

        analyses = [post['sentiment_analysis'] for post in posts if 'sentiment_analysis' in post]

        total_engagement = sum(
            post.get('score', 0) + post.get('num_comments', 0)
            for post in posts
        )

        aggregated = self.sentiment_analyzer.aggregate_sentiment(analyses, 'reddit')
        aggregated['total_engagement'] = total_engagement

        return aggregated


def main():
    """Test the Reddit collector"""
    collector = RedditPRAWCollector()

    # Test with a popular coin
    posts = collector.collect_coin_mentions(
        coin_symbol='DOGE',
        coin_name='dogecoin',
        max_posts=20
    )

    print(f"\nCollected {len(posts)} posts")

    if posts:
        # Show first post
        print("\nSample post:")
        print(f"Title: {posts[0]['title']}")
        print(f"Subreddit: r/{posts[0]['subreddit']}")
        print(f"Score: {posts[0]['score']}")
        print(f"Sentiment: {posts[0]['sentiment_analysis']['sentiment']}")
        print(f"Hype Score: {posts[0]['sentiment_analysis']['hype_score']:.2f}")

        # Aggregate sentiment
        agg = collector.aggregate_sentiment(posts)
        print(f"\nAggregate Sentiment:")
        print(f"  Sentiment Score: {agg['sentiment_score']:.2f}")
        print(f"  Hype Score: {agg['hype_score']:.2f}")
        print(f"  Total Engagement: {agg['total_engagement']}")


if __name__ == '__main__':
    main()
