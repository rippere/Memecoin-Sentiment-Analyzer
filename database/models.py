"""
Database Models for Memecoin Sentiment Analyzer
==============================================
SQLAlchemy ORM models for unified data storage
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Boolean, ForeignKey, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()


# Composite indexes for common query patterns
# These significantly improve performance for queries filtering by coin_id + timestamp


class Coin(Base):
    """Cryptocurrency coin reference table"""
    __tablename__ = 'coins'

    id = Column(Integer, primary_key=True)
    symbol = Column(String(10), unique=True, nullable=False)  # DOGE, PEPE, etc.
    name = Column(String(50), nullable=False)  # Dogecoin, Pepe, etc.
    coingecko_id = Column(String(50), unique=True)  # dogecoin, pepe, etc.
    created_at = Column(DateTime, default=datetime.utcnow)

    # Classification fields
    is_control = Column(Boolean, default=False)  # BTC, ETH for comparison
    is_failed = Column(Boolean, default=False)  # Failed/dead coins (SQUID, etc.)
    notes = Column(Text)  # Optional notes (e.g., "Rug pull 2021")

    # Relationships
    prices = relationship("Price", back_populates="coin")
    reddit_posts = relationship("RedditPost", back_populates="coin")
    tiktok_videos = relationship("TikTokVideo", back_populates="coin")
    sentiment_scores = relationship("SentimentScore", back_populates="coin")


class Price(Base):
    """Price data from CoinGecko"""
    __tablename__ = 'prices'
    __table_args__ = (
        Index('ix_prices_coin_timestamp', 'coin_id', 'timestamp'),
    )

    id = Column(Integer, primary_key=True)
    coin_id = Column(Integer, ForeignKey('coins.id'), nullable=False)
    timestamp = Column(DateTime, nullable=False, index=True)

    # Price metrics
    price_usd = Column(Float, nullable=False)
    market_cap = Column(Float)
    volume_24h = Column(Float)

    # Price changes
    change_1h_pct = Column(Float)
    change_24h_pct = Column(Float)
    change_7d_pct = Column(Float)

    # Metadata
    collected_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    coin = relationship("Coin", back_populates="prices")

    def __repr__(self):
        return f"<Price(coin={self.coin.symbol}, price=${self.price_usd}, time={self.timestamp})>"


class RedditPost(Base):
    """Reddit post data"""
    __tablename__ = 'reddit_posts'
    __table_args__ = (
        Index('ix_reddit_coin_created', 'coin_id', 'created_utc'),
    )

    id = Column(Integer, primary_key=True)
    coin_id = Column(Integer, ForeignKey('coins.id'), nullable=False)

    # Reddit identifiers
    post_id = Column(String(20), unique=True, nullable=False)
    post_url = Column(Text, nullable=False)

    # Post content
    title = Column(Text, nullable=False)
    body = Column(Text)
    author = Column(String(100))
    subreddit = Column(String(50), nullable=False, index=True)
    flair = Column(String(100))

    # Engagement metrics
    score = Column(Integer, default=0)
    num_comments = Column(Integer, default=0)
    upvote_ratio = Column(Float)

    # Metadata
    is_self = Column(Boolean, default=True)
    created_utc = Column(DateTime, nullable=False, index=True)
    scraped_at = Column(DateTime, default=datetime.utcnow)
    query = Column(String(100))  # Search query used

    # Relationships
    coin = relationship("Coin", back_populates="reddit_posts")

    def __repr__(self):
        return f"<RedditPost(coin={self.coin.symbol}, subreddit={self.subreddit}, score={self.score})>"


class TikTokVideo(Base):
    """TikTok video data"""
    __tablename__ = 'tiktok_videos'
    __table_args__ = (
        Index('ix_tiktok_coin_scraped', 'coin_id', 'scraped_at'),
    )

    id = Column(Integer, primary_key=True)
    coin_id = Column(Integer, ForeignKey('coins.id'), nullable=False)

    # TikTok identifiers
    video_id = Column(String(50), unique=True, nullable=False)
    video_url = Column(Text, nullable=False)
    username = Column(String(100))

    # Video content
    caption = Column(Text)
    hashtags = Column(Text)  # Stored as comma-separated

    # Engagement metrics
    views = Column(Integer, default=0)
    likes = Column(Integer, default=0)
    shares = Column(Integer, default=0)
    comments = Column(Integer, default=0)

    # Metadata
    scraped_at = Column(DateTime, default=datetime.utcnow, index=True)
    hashtag_searched = Column(String(100))
    container_index = Column(Integer)  # Position in search results

    # Relationships
    coin = relationship("Coin", back_populates="tiktok_videos")

    def __repr__(self):
        return f"<TikTokVideo(coin={self.coin.symbol}, views={self.views}, username={self.username})>"


class SentimentScore(Base):
    """Aggregated sentiment scores by coin and timeframe"""
    __tablename__ = 'sentiment_scores'
    __table_args__ = (
        Index('ix_sentiment_coin_source_ts', 'coin_id', 'source', 'timestamp'),
    )

    id = Column(Integer, primary_key=True)
    coin_id = Column(Integer, ForeignKey('coins.id'), nullable=False)
    timestamp = Column(DateTime, nullable=False, index=True)

    # Source
    source = Column(String(20), nullable=False)  # 'reddit', 'tiktok', 'twitter'

    # Sentiment metrics (VADER scores: -1 to +1)
    sentiment_score = Column(Float)  # Compound score
    sentiment_positive = Column(Float)
    sentiment_negative = Column(Float)
    sentiment_neutral = Column(Float)

    # Volume metrics
    post_count = Column(Integer, default=0)  # Number of posts/videos analyzed
    total_engagement = Column(Integer, default=0)  # Sum of likes/comments/etc

    # Hype metrics
    hype_score = Column(Float)  # 0-100 custom hype score
    hype_keywords_count = Column(Integer, default=0)
    hype_emojis_count = Column(Integer, default=0)

    # Metadata
    calculated_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    coin = relationship("Coin", back_populates="sentiment_scores")

    def __repr__(self):
        return f"<SentimentScore(coin={self.coin.symbol}, source={self.source}, score={self.sentiment_score})>"


class CorrelationResult(Base):
    """Correlation analysis results"""
    __tablename__ = 'correlation_results'

    id = Column(Integer, primary_key=True)
    coin_id = Column(Integer, ForeignKey('coins.id'), nullable=False)

    # Analysis parameters
    analysis_date = Column(DateTime, nullable=False, index=True)
    lag_days = Column(Integer, default=0)  # How many days sentiment leads price
    source = Column(String(20), nullable=False)  # 'reddit', 'tiktok', etc.

    # Correlation metrics
    correlation_coefficient = Column(Float)  # Pearson correlation
    p_value = Column(Float)  # Statistical significance
    sample_size = Column(Integer)  # Number of data points

    # Findings
    significant = Column(Boolean, default=False)  # p < 0.05
    direction = Column(String(20))  # 'positive', 'negative', 'none'

    # Metadata
    calculated_at = Column(DateTime, default=datetime.utcnow)
    notes = Column(Text)

    def __repr__(self):
        return f"<CorrelationResult(coin_id={self.coin_id}, corr={self.correlation_coefficient}, lag={self.lag_days}d)>"


class DataCollectionLog(Base):
    """Log of data collection runs"""
    __tablename__ = 'collection_logs'

    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)

    # Collection details
    collector_type = Column(String(20), nullable=False)  # 'price', 'reddit', 'tiktok'
    status = Column(String(20), nullable=False)  # 'success', 'failed', 'partial'

    # Results
    records_collected = Column(Integer, default=0)
    errors_count = Column(Integer, default=0)
    duration_seconds = Column(Float)

    # Error details
    error_message = Column(Text)

    def __repr__(self):
        return f"<CollectionLog({self.collector_type}, {self.status}, {self.records_collected} records)>"
