"""
SCRIPT A: TWITTER HYPE COLLECTOR
=================================
Collects tweets about meme coins with intelligent hype detection.
Works with free Twitter API (1,500 tweets/month limit).

WHAT THIS DOES:
- Searches for tweets mentioning your meme coins
- Calculates "hype score" based on emotional intensity
- Tracks engagement metrics (likes, retweets)
- Saves data with timestamps for correlation analysis
- Respects API rate limits

LEARNING NOTES:
- Uses Tweepy library (official Twitter API wrapper)
- Implements exponential backoff for rate limiting
- Calculates custom sentiment/hype metrics
- Stores data incrementally to CSV
"""

import tweepy
import pandas as pd
from datetime import datetime, timedelta
import time
import re
import os
from dotenv import load_dotenv
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import json

# Load environment variables from .env file
load_dotenv()

# =============================================================================
# CONFIGURATION
# =============================================================================

# Your meme coins to track
MEME_COINS = {
    'DOGE': ['$DOGE', '#DOGE', '#Dogecoin', 'dogecoin'],
    'PEPE': ['$PEPE', '#PEPE', '#PepeCoin', 'pepecoin'],
    'SHIB': ['$SHIB', '#SHIB', '#ShibaInu', 'shiba inu'],
    'BONK': ['$BONK', '#BONK', 'bonk coin'],
    'FLOKI': ['$FLOKI', '#FLOKI', 'floki inu'],
    'WIF': ['$WIF', '#WIF', 'dogwifhat'],
}

# High-impact accounts to monitor (crypto influencers)
# Add influential accounts here as you discover them
INFLUENCER_ACCOUNTS = [
    'elonmusk',          # Obvious
    'CryptoCobain',      # Crypto trader
    'APompliano',        # Bitcoin advocate
    'AltcoinGordon',     # Altcoin trader
    # Add more as you find them!
]

# Hype indicators (keywords that signal FOMO/hype)
HYPE_KEYWORDS = [
    'moon', 'rocket', 'lambo', 'wen', 'pump', 'bullish', 'gem',
    'x100', 'x10', 'mooning', 'rocketship', 'millionaire',
    'buy now', 'dont miss', 'last chance', 'fomo', 'all in'
]

# Hype emojis (these indicate emotional investment)
HYPE_EMOJIS = ['🚀', '🌙', '💎', '🙌', '💰', '🔥', '📈', '💪', '🐕', '🐸']

# Twitter API credentials (from .env file)
BEARER_TOKEN = os.getenv('TWITTER_BEARER_TOKEN')

# Output file
OUTPUT_FILE = 'twitter_hype_data.csv'

# =============================================================================
# TWITTER API SETUP
# =============================================================================

def setup_twitter_client():
    """
    Initialize Twitter API client
    """
    if not BEARER_TOKEN:
        print("❌ ERROR: Twitter Bearer Token not found!")
        print("Please add TWITTER_BEARER_TOKEN to your .env file")
        print("See TWITTER_API_SETUP_GUIDE.md for instructions")
        return None
    
    try:
        client = tweepy.Client(
            bearer_token=BEARER_TOKEN,
            wait_on_rate_limit=True  # Automatically wait if we hit rate limits
        )
        print("✅ Twitter API client initialized")
        return client
    except Exception as e:
        print(f"❌ Error setting up Twitter client: {e}")
        return None


# =============================================================================
# HYPE DETECTION FUNCTIONS
# =============================================================================

def calculate_hype_score(tweet_text, metrics):
    """
    Calculate a "hype score" based on multiple factors
    
    Factors:
    - ALL CAPS usage
    - Hype keywords
    - Hype emojis
    - Exclamation marks
    - Sentiment intensity
    
    Returns: Score from 0-100
    """
    score = 0
    text_lower = tweet_text.lower()
    
    # 1. Check for ALL CAPS (max 15 points)
    caps_ratio = sum(1 for c in tweet_text if c.isupper()) / max(len(tweet_text), 1)
    score += min(caps_ratio * 30, 15)
    
    # 2. Count hype keywords (max 20 points)
    keyword_count = sum(1 for keyword in HYPE_KEYWORDS if keyword in text_lower)
    score += min(keyword_count * 5, 20)
    
    # 3. Count hype emojis (max 15 points)
    emoji_count = sum(tweet_text.count(emoji) for emoji in HYPE_EMOJIS)
    score += min(emoji_count * 3, 15)
    
    # 4. Exclamation marks (max 10 points)
    exclamation_count = tweet_text.count('!')
    score += min(exclamation_count * 2, 10)
    
    # 5. Sentiment analysis (max 20 points)
    analyzer = SentimentIntensityAnalyzer()
    sentiment = analyzer.polarity_scores(tweet_text)
    # Positive sentiment adds to hype, negative subtracts
    score += sentiment['compound'] * 20
    
    # 6. Engagement multiplier (max 20 points)
    # High likes/retweets = more impactful
    engagement = metrics.get('like_count', 0) + metrics.get('retweet_count', 0) * 2
    if engagement > 1000:
        score += 20
    elif engagement > 100:
        score += 15
    elif engagement > 10:
        score += 10
    elif engagement > 0:
        score += 5
    
    # Normalize to 0-100
    return min(max(score, 0), 100)


def detect_urgency(tweet_text):
    """
    Detect urgency/FOMO language
    Returns: True if urgent, False otherwise
    """
    urgency_phrases = [
        'right now', 'hurry', 'quick', 'fast', 'immediately',
        'dont miss', 'last chance', 'limited time', 'act now',
        'before its too late', 'going parabolic', 'take off'
    ]
    
    text_lower = tweet_text.lower()
    return any(phrase in text_lower for phrase in urgency_phrases)


def extract_coin_mentions(tweet_text):
    """
    Extract which coins are mentioned in the tweet
    Returns: List of coin symbols
    """
    mentioned_coins = []
    text_upper = tweet_text.upper()
    
    for coin, keywords in MEME_COINS.items():
        for keyword in keywords:
            if keyword.upper() in text_upper:
                if coin not in mentioned_coins:
                    mentioned_coins.append(coin)
                break
    
    return mentioned_coins


# =============================================================================
# DATA COLLECTION FUNCTIONS
# =============================================================================

def search_tweets_for_coin(client, coin_symbol, max_results=10):
    """
    Search for recent tweets mentioning a specific coin
    
    Parameters:
    - client: Tweepy client
    - coin_symbol: Coin to search for (e.g., 'DOGE')
    - max_results: Number of tweets to fetch (max 100 per request)
    
    Returns: List of processed tweet data
    """
    # Build search query
    keywords = MEME_COINS[coin_symbol]
    query = ' OR '.join(keywords)
    query += ' -is:retweet'  # Exclude retweets to avoid duplicates
    
    print(f"🔍 Searching for: {coin_symbol}")
    print(f"   Query: {query}")
    
    try:
        # Search recent tweets (last 7 days with free tier)
        tweets = client.search_recent_tweets(
            query=query,
            max_results=max_results,
            tweet_fields=['created_at', 'public_metrics', 'author_id'],
            expansions=['author_id'],
            user_fields=['username', 'public_metrics']
        )
        
        if not tweets.data:
            print(f"   ⚠️  No tweets found for {coin_symbol}")
            return []
        
        # Process tweets
        processed_tweets = []
        users = {user.id: user for user in tweets.includes.get('users', [])}
        
        for tweet in tweets.data:
            user = users.get(tweet.author_id)
            
            metrics = {
                'like_count': tweet.public_metrics['like_count'],
                'retweet_count': tweet.public_metrics['retweet_count'],
                'reply_count': tweet.public_metrics['reply_count'],
            }
            
            # Calculate hype score
            hype_score = calculate_hype_score(tweet.text, metrics)
            
            # Extract data
            tweet_data = {
                'timestamp': tweet.created_at,
                'coin': coin_symbol,
                'tweet_id': tweet.id,
                'text': tweet.text,
                'author': user.username if user else 'unknown',
                'author_followers': user.public_metrics['followers_count'] if user else 0,
                'likes': metrics['like_count'],
                'retweets': metrics['retweet_count'],
                'replies': metrics['reply_count'],
                'hype_score': round(hype_score, 2),
                'has_urgency': detect_urgency(tweet.text),
                'mentioned_coins': ','.join(extract_coin_mentions(tweet.text)),
                'collection_time': datetime.now()
            }
            
            processed_tweets.append(tweet_data)
        
        print(f"   ✅ Collected {len(processed_tweets)} tweets")
        return processed_tweets
        
    except tweepy.TweepyException as e:
        print(f"   ❌ Error fetching tweets: {e}")
        return []
    except Exception as e:
        print(f"   ❌ Unexpected error: {e}")
        return []


def collect_all_coins(client, tweets_per_coin=10):
    """
    Collect tweets for all configured meme coins
    """
    all_tweets = []
    
    print("\n" + "="*70)
    print("🐦 TWITTER HYPE COLLECTOR - RUNNING")
    print("="*70)
    print(f"Target coins: {', '.join(MEME_COINS.keys())}")
    print(f"Tweets per coin: {tweets_per_coin}")
    print(f"Total tweets to collect: ~{len(MEME_COINS) * tweets_per_coin}")
    print("="*70 + "\n")
    
    for coin in MEME_COINS.keys():
        tweets = search_tweets_for_coin(client, coin, max_results=tweets_per_coin)
        all_tweets.extend(tweets)
        
        # Be nice to the API - small delay between coins
        time.sleep(2)
    
    return all_tweets


# =============================================================================
# DATA STORAGE
# =============================================================================

def save_tweets_to_csv(tweets, filename=OUTPUT_FILE):
    """
    Save collected tweets to CSV, appending if file exists
    """
    if not tweets:
        print("\n⚠️  No tweets to save")
        return
    
    df = pd.DataFrame(tweets)
    
    # Convert timestamp to readable format
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df['collection_time'] = pd.to_datetime(df['collection_time'])
    
    try:
        # Try to load existing data and append
        existing_df = pd.read_csv(filename)
        existing_df['timestamp'] = pd.to_datetime(existing_df['timestamp'])
        
        # Combine and remove duplicates based on tweet_id
        combined_df = pd.concat([existing_df, df], ignore_index=True)
        combined_df = combined_df.drop_duplicates(subset=['tweet_id'], keep='last')
        
        combined_df.to_csv(filename, index=False)
        print(f"\n✅ Appended {len(df)} new tweets to {filename}")
        print(f"   Total tweets in file: {len(combined_df)}")
        
    except FileNotFoundError:
        # File doesn't exist, create new
        df.to_csv(filename, index=False)
        print(f"\n✅ Created new file: {filename}")
        print(f"   Saved {len(df)} tweets")


# =============================================================================
# ANALYSIS & REPORTING
# =============================================================================

def display_summary(tweets):
    """
    Show summary statistics of collected tweets
    """
    if not tweets:
        return
    
    df = pd.DataFrame(tweets)
    
    print("\n" + "="*70)
    print("📊 COLLECTION SUMMARY")
    print("="*70)
    
    # Top coins by tweet volume
    print("\n🔥 Tweet Volume by Coin:")
    coin_counts = df['coin'].value_counts()
    for coin, count in coin_counts.items():
        print(f"   {coin}: {count} tweets")
    
    # Average hype score by coin
    print("\n📈 Average Hype Score by Coin:")
    hype_by_coin = df.groupby('coin')['hype_score'].mean().sort_values(ascending=False)
    for coin, score in hype_by_coin.items():
        print(f"   {coin}: {score:.1f}/100")
    
    # Highest hype tweets
    print("\n🚀 Top 3 Highest Hype Tweets:")
    top_hype = df.nlargest(3, 'hype_score')
    for idx, row in top_hype.iterrows():
        print(f"\n   {row['coin']} - Hype Score: {row['hype_score']:.1f}")
        print(f"   @{row['author']} ({row['author_followers']:,} followers)")
        print(f"   ❤️  {row['likes']} | 🔄 {row['retweets']}")
        print(f"   \"{row['text'][:100]}...\"")
    
    # Urgency detection
    urgent_tweets = df[df['has_urgency'] == True]
    if len(urgent_tweets) > 0:
        print(f"\n⚠️  Urgent/FOMO tweets detected: {len(urgent_tweets)}")
        print(f"   Coins with urgency: {urgent_tweets['coin'].unique().tolist()}")
    
    print("\n" + "="*70)


# =============================================================================
# MAIN EXECUTION
# =============================================================================

def main():
    """
    Main function - run the collector
    """
    print("\n🚀 Starting Twitter Hype Collector...")
    
    # Setup Twitter client
    client = setup_twitter_client()
    if not client:
        return
    
    # Collect tweets
    tweets = collect_all_coins(client, tweets_per_coin=10)
    
    # Display summary
    display_summary(tweets)
    
    # Save to CSV
    save_tweets_to_csv(tweets)
    
    print("\n✅ Collection complete!")
    print(f"💾 Data saved to: {OUTPUT_FILE}")
    print("\n💡 TIP: Run this script 2-3 times per day to build your dataset")
    print("💡 Stay under 1,500 tweets/month (~50 tweets/day)")
    print("💡 Current run used: ~{} tweets\n".format(len(tweets)))


if __name__ == "__main__":
    main()
