"""
Memecoin Sentiment API
=======================
FastAPI backend for the dashboard
"""

import hashlib
import json
import sqlite3
import sys
from datetime import datetime, timedelta
from functools import wraps
from pathlib import Path
from typing import List, Optional

from cachetools import TTLCache
from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

# Initialize cache (maxsize=100 entries, TTL=300 seconds/5 minutes)
response_cache = TTLCache(maxsize=100, ttl=300)

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))


def cache_response(cache_key_prefix: str = ""):
    """
    Decorator to cache endpoint responses
    Cache key is generated from endpoint path + query params
    """

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Generate cache key from function name and kwargs
            key_parts = [cache_key_prefix or func.__name__]
            # Add sorted kwargs to ensure consistent cache keys
            for k, v in sorted(kwargs.items()):
                if k != "request":  # Skip Request object
                    key_parts.append(f"{k}={v}")
            cache_key = ":".join(key_parts)

            # Try to get from cache
            if cache_key in response_cache:
                return response_cache[cache_key]

            # Call the actual function
            result = await func(*args, **kwargs)

            # Store in cache
            response_cache[cache_key] = result
            return result

        return wrapper

    return decorator


# Rate limiter setup
limiter = Limiter(key_func=get_remote_address)

app = FastAPI(
    title="Memecoin Sentiment API", description="API for cryptocurrency sentiment analysis dashboard", version="1.0.0"
)

# Add rate limiter to app
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS for frontend - restrict to known origins
ALLOWED_ORIGINS = [
    "http://localhost:3000",  # Next.js dev server
    "http://127.0.0.1:3000",
    "http://localhost:8000",  # API dev server
    "http://127.0.0.1:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

DB_PATH = Path(__file__).parent.parent / "data" / "memecoin.db"


def get_db():
    """Get database connection"""
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


# ==================== COINS ====================


@app.get("/api/coins")
@limiter.limit("30/minute")
@cache_response("coins")
async def get_coins(request: Request):
    """Get all tracked coins with latest data (cached for 5 minutes)"""
    conn = get_db()
    try:
        # Optimized query using JOINs with pre-computed latest values
        # This avoids N+1 subqueries by getting latest prices/sentiment in CTEs
        query = """
            WITH latest_prices AS (
                SELECT coin_id, price_usd, change_24h_pct, market_cap, volume_24h,
                       ROW_NUMBER() OVER (PARTITION BY coin_id ORDER BY timestamp DESC) as rn
                FROM prices
            ),
            latest_sentiment AS (
                SELECT coin_id, sentiment_score, hype_score,
                       ROW_NUMBER() OVER (PARTITION BY coin_id ORDER BY timestamp DESC) as rn
                FROM sentiment_scores
            )
            SELECT
                c.id, c.symbol, c.name, c.is_control, c.is_failed,
                p.price_usd as price,
                p.change_24h_pct as change_24h,
                p.market_cap,
                p.volume_24h,
                s.sentiment_score as sentiment,
                s.hype_score
            FROM coins c
            LEFT JOIN latest_prices p ON c.id = p.coin_id AND p.rn = 1
            LEFT JOIN latest_sentiment s ON c.id = s.coin_id AND s.rn = 1
            ORDER BY c.symbol
        """
        cursor = conn.execute(query)
        coins = [dict(row) for row in cursor.fetchall()]
        return {"coins": coins, "count": len(coins)}
    finally:
        conn.close()


@app.get("/api/coins/{symbol}")
async def get_coin(symbol: str):
    """Get detailed coin information"""
    conn = get_db()
    try:
        # Get coin info
        cursor = conn.execute("SELECT * FROM coins WHERE symbol = ?", (symbol.upper(),))
        coin = cursor.fetchone()

        if not coin:
            raise HTTPException(status_code=404, detail="Coin not found")

        coin_dict = dict(coin)

        # Get latest price
        cursor = conn.execute(
            """
            SELECT * FROM prices WHERE coin_id = ? ORDER BY timestamp DESC LIMIT 1
        """,
            (coin_dict["id"],),
        )
        price = cursor.fetchone()
        if price:
            coin_dict["latest_price"] = dict(price)

        # Get latest sentiment
        cursor = conn.execute(
            """
            SELECT * FROM sentiment_scores WHERE coin_id = ? ORDER BY timestamp DESC LIMIT 1
        """,
            (coin_dict["id"],),
        )
        sentiment = cursor.fetchone()
        if sentiment:
            coin_dict["latest_sentiment"] = dict(sentiment)

        # Get data counts
        cursor = conn.execute(
            """
            SELECT
                (SELECT COUNT(*) FROM prices WHERE coin_id = ?) as price_count,
                (SELECT COUNT(*) FROM reddit_posts WHERE coin_id = ?) as reddit_count,
                (SELECT COUNT(*) FROM tiktok_videos WHERE coin_id = ?) as tiktok_count,
                (SELECT COUNT(*) FROM sentiment_scores WHERE coin_id = ?) as sentiment_count
        """,
            (coin_dict["id"], coin_dict["id"], coin_dict["id"], coin_dict["id"]),
        )
        counts = cursor.fetchone()
        coin_dict["data_counts"] = dict(counts)

        return coin_dict
    finally:
        conn.close()


@app.get("/api/coins/{symbol}/prices")
async def get_coin_prices(
    symbol: str,
    hours: int = Query(default=24, ge=1, le=720),
    interval: str = Query(default="raw", regex="^(raw|hourly|daily)$"),
):
    """Get price history for a coin"""
    conn = get_db()
    try:
        # Get coin ID
        cursor = conn.execute("SELECT id FROM coins WHERE symbol = ?", (symbol.upper(),))
        coin = cursor.fetchone()
        if not coin:
            raise HTTPException(status_code=404, detail="Coin not found")

        since = datetime.utcnow() - timedelta(hours=hours)

        if interval == "raw":
            query = """
                SELECT timestamp, price_usd, market_cap, volume_24h,
                       change_1h_pct, change_24h_pct, change_7d_pct
                FROM prices
                WHERE coin_id = ? AND timestamp >= ?
                ORDER BY timestamp
            """
        elif interval == "hourly":
            query = """
                SELECT
                    strftime('%Y-%m-%d %H:00:00', timestamp) as timestamp,
                    AVG(price_usd) as price_usd,
                    AVG(market_cap) as market_cap,
                    AVG(volume_24h) as volume_24h,
                    AVG(change_24h_pct) as change_24h_pct
                FROM prices
                WHERE coin_id = ? AND timestamp >= ?
                GROUP BY strftime('%Y-%m-%d %H', timestamp)
                ORDER BY timestamp
            """
        else:  # daily
            query = """
                SELECT
                    date(timestamp) as timestamp,
                    AVG(price_usd) as price_usd,
                    AVG(market_cap) as market_cap,
                    AVG(volume_24h) as volume_24h,
                    AVG(change_24h_pct) as change_24h_pct
                FROM prices
                WHERE coin_id = ? AND timestamp >= ?
                GROUP BY date(timestamp)
                ORDER BY timestamp
            """

        cursor = conn.execute(query, (coin["id"], since.isoformat()))
        prices = [dict(row) for row in cursor.fetchall()]

        return {"symbol": symbol.upper(), "interval": interval, "hours": hours, "data": prices, "count": len(prices)}
    finally:
        conn.close()


@app.get("/api/coins/{symbol}/sentiment")
async def get_coin_sentiment(
    symbol: str,
    hours: int = Query(default=24, ge=1, le=720),
    source: Optional[str] = Query(default=None, regex="^(reddit|tiktok)$"),
):
    """Get sentiment history for a coin"""
    conn = get_db()
    try:
        cursor = conn.execute("SELECT id FROM coins WHERE symbol = ?", (symbol.upper(),))
        coin = cursor.fetchone()
        if not coin:
            raise HTTPException(status_code=404, detail="Coin not found")

        since = datetime.utcnow() - timedelta(hours=hours)

        query = """
            SELECT timestamp, source, sentiment_score, sentiment_positive,
                   sentiment_negative, sentiment_neutral, hype_score, post_count
            FROM sentiment_scores
            WHERE coin_id = ? AND timestamp >= ?
        """
        params = [coin["id"], since.isoformat()]

        if source:
            query += " AND source = ?"
            params.append(source)

        query += " ORDER BY timestamp"

        cursor = conn.execute(query, params)
        sentiment = [dict(row) for row in cursor.fetchall()]

        return {
            "symbol": symbol.upper(),
            "source": source or "all",
            "hours": hours,
            "data": sentiment,
            "count": len(sentiment),
        }
    finally:
        conn.close()


# ==================== DASHBOARD ====================


@app.get("/api/stats")
async def get_stats():
    """Get dashboard statistics"""
    conn = get_db()
    try:
        stats = {}

        # Coin count
        cursor = conn.execute("SELECT COUNT(*) as count FROM coins")
        stats["total_coins"] = cursor.fetchone()["count"]

        # Record counts
        cursor = conn.execute(
            """
            SELECT
                (SELECT COUNT(*) FROM prices) as prices,
                (SELECT COUNT(*) FROM reddit_posts) as reddit_posts,
                (SELECT COUNT(*) FROM tiktok_videos) as tiktok_videos,
                (SELECT COUNT(*) FROM sentiment_scores) as sentiment_scores
        """
        )
        counts = dict(cursor.fetchone())
        stats["record_counts"] = counts

        # Average sentiment (last 24h)
        cursor = conn.execute(
            """
            SELECT AVG(sentiment_score) as avg_sentiment, AVG(hype_score) as avg_hype
            FROM sentiment_scores
            WHERE timestamp >= datetime('now', '-24 hours')
        """
        )
        row = cursor.fetchone()
        stats["avg_sentiment_24h"] = row["avg_sentiment"]
        stats["avg_hype_24h"] = row["avg_hype"]

        # Date range
        cursor = conn.execute(
            """
            SELECT MIN(timestamp) as earliest, MAX(timestamp) as latest
            FROM prices
        """
        )
        row = cursor.fetchone()
        stats["date_range"] = {"earliest": row["earliest"], "latest": row["latest"]}

        return stats
    finally:
        conn.close()


@app.get("/api/sentiment/heatmap")
async def get_sentiment_heatmap():
    """Get sentiment data for heatmap visualization"""
    conn = get_db()
    try:
        query = """
            SELECT
                c.symbol,
                c.name,
                s.sentiment_score,
                s.hype_score,
                s.post_count,
                p.price_usd,
                p.change_24h_pct
            FROM coins c
            LEFT JOIN (
                SELECT coin_id, sentiment_score, hype_score, post_count
                FROM sentiment_scores
                WHERE id IN (
                    SELECT MAX(id) FROM sentiment_scores GROUP BY coin_id
                )
            ) s ON c.id = s.coin_id
            LEFT JOIN (
                SELECT coin_id, price_usd, change_24h_pct
                FROM prices
                WHERE id IN (
                    SELECT MAX(id) FROM prices GROUP BY coin_id
                )
            ) p ON c.id = p.coin_id
            WHERE c.is_control = 0
            ORDER BY s.sentiment_score DESC
        """
        cursor = conn.execute(query)
        data = [dict(row) for row in cursor.fetchall()]

        return {"data": data, "count": len(data)}
    finally:
        conn.close()


@app.get("/api/sentiment/top-movers")
async def get_top_movers(limit: int = Query(default=5, ge=1, le=20)):
    """Get top gaining and losing coins"""
    conn = get_db()
    try:
        query = """
            SELECT
                c.symbol,
                c.name,
                p.price_usd,
                p.change_24h_pct
            FROM coins c
            JOIN (
                SELECT coin_id, price_usd, change_24h_pct
                FROM prices
                WHERE id IN (
                    SELECT MAX(id) FROM prices GROUP BY coin_id
                )
            ) p ON c.id = p.coin_id
            WHERE c.is_control = 0 AND p.change_24h_pct IS NOT NULL
            ORDER BY p.change_24h_pct DESC
        """
        cursor = conn.execute(query)
        all_coins = [dict(row) for row in cursor.fetchall()]

        gainers = all_coins[:limit]
        losers = list(reversed(all_coins[-limit:]))

        return {"gainers": gainers, "losers": losers}
    finally:
        conn.close()


# ==================== EVENTS ====================


@app.get("/api/events")
async def get_events(coin: Optional[str] = None, limit: int = Query(default=20, ge=1, le=100)):
    """Get logged events"""
    events_path = Path(__file__).parent.parent / "events" / "events.json"

    if not events_path.exists():
        return {"events": [], "count": 0}

    with open(events_path, "r") as f:
        events = json.load(f)

    if coin:
        events = [e for e in events if e["coin_symbol"] == coin.upper() or e["coin_symbol"] == "ALL"]

    # Sort by timestamp descending
    events = sorted(events, key=lambda x: x["timestamp"], reverse=True)[:limit]

    return {"events": events, "count": len(events)}


@app.post("/api/events")
@limiter.limit("10/minute")
async def create_event(
    request: Request,
    coin_symbol: str,
    category: str,
    description: str,
    sentiment: str = "neutral",
    impact_score: float = 5.0,
    source: Optional[str] = None,
    url: Optional[str] = None,
):
    """Create a new event"""
    from events.event_logger import EventLogger

    logger = EventLogger()
    event = logger.log_event(
        coin_symbol=coin_symbol,
        category=category,
        description=description,
        sentiment=sentiment,
        impact_score=impact_score,
        source=source,
        url=url,
    )

    return {"success": True, "event": event}


# ==================== ANALYSIS ====================


@app.get("/api/analysis/correlation/{symbol}")
@limiter.limit("10/minute")
async def get_correlation_analysis(request: Request, symbol: str):
    """Get correlation analysis for a coin"""
    try:
        from analysis.correlation_analyzer import CorrelationAnalyzer

        analyzer = CorrelationAnalyzer()

        result = analyzer.analyze_price_sentiment_correlation(symbol.upper())

        analyzer.close()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/analysis/granger/{symbol}")
@limiter.limit("10/minute")
async def get_granger_causality(request: Request, symbol: str):
    """Test if sentiment Granger-causes price changes"""
    try:
        from analysis.correlation_analyzer import CorrelationAnalyzer

        analyzer = CorrelationAnalyzer()

        result = analyzer.granger_causality_analysis(symbol.upper())

        analyzer.close()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/analysis/spikes/{symbol}")
@limiter.limit("10/minute")
async def get_spike_analysis(request: Request, symbol: str):
    """Detect sentiment spikes and analyze price movements after"""
    try:
        from analysis.correlation_analyzer import CorrelationAnalyzer

        analyzer = CorrelationAnalyzer()

        result = analyzer.detect_sentiment_spikes(symbol.upper())

        analyzer.close()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/analysis/shill-detection/{symbol}")
@limiter.limit("10/minute")
async def get_shill_detection(request: Request, symbol: str, hours: int = 24):
    """Detect potential shill campaigns for a coin"""
    conn = get_db()
    try:
        from collectors.quality_monitor import ShillDetector

        # Get recent posts for the coin
        cursor = conn.execute(
            """
            SELECT rp.title, rp.body, rp.author, rp.score, rp.num_comments
            FROM reddit_posts rp
            JOIN coins c ON rp.coin_id = c.id
            WHERE c.symbol = ? AND rp.created_utc >= datetime('now', ?)
        """,
            (symbol.upper(), f"-{hours} hours"),
        )

        posts = [dict(row) for row in cursor.fetchall()]

        if not posts:
            return {"message": "No posts found", "posts_analyzed": 0}

        detector = ShillDetector()
        result = detector.detect_coordinated_campaign(posts)

        return result
    finally:
        conn.close()


@app.get("/api/analysis/quality/{symbol}")
async def get_data_quality(symbol: str, hours: int = 24):
    """Get data quality metrics for a coin"""
    conn = get_db()
    try:
        from collectors.quality_monitor import PriceAnomalyDetector

        # Get recent prices
        cursor = conn.execute(
            """
            SELECT p.price_usd, p.change_1h_pct, p.change_24h_pct, p.volume_24h,
                   p.timestamp, c.symbol
            FROM prices p
            JOIN coins c ON p.coin_id = c.id
            WHERE c.symbol = ? AND p.timestamp >= datetime('now', ?)
        """,
            (symbol.upper(), f"-{hours} hours"),
        )

        prices = [dict(row) for row in cursor.fetchall()]

        if not prices:
            return {"message": "No price data found", "records": 0}

        detector = PriceAnomalyDetector()
        result = detector.detect_anomalies(prices)

        return result
    finally:
        conn.close()


@app.get("/api/analysis/summary")
async def get_analysis_summary():
    """Get analysis summary across all coins"""
    conn = get_db()
    try:
        # Get coins with sufficient data
        cursor = conn.execute(
            """
            SELECT c.symbol, c.name,
                   COUNT(DISTINCT p.id) as price_count,
                   COUNT(DISTINCT s.id) as sentiment_count
            FROM coins c
            LEFT JOIN prices p ON c.id = p.coin_id
            LEFT JOIN sentiment_scores s ON c.id = s.coin_id
            WHERE c.is_control = 0
            GROUP BY c.id
            HAVING price_count > 10 AND sentiment_count > 0
        """
        )

        coins_with_data = [dict(row) for row in cursor.fetchall()]

        return {
            "coins_ready_for_analysis": len(coins_with_data),
            "coins": coins_with_data,
            "note": "Run correlation analysis on individual coins via /api/analysis/correlation/{symbol}",
        }
    finally:
        conn.close()


# ==================== HEALTH ====================


@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    # Check if database is accessible
    db_status = "connected"
    try:
        conn = get_db()
        conn.execute("SELECT 1")
        conn.close()
    except Exception:
        db_status = "disconnected"

    return {
        "status": "healthy" if db_status == "connected" else "degraded",
        "database": db_status,  # Don't expose full path
        "timestamp": datetime.utcnow().isoformat(),
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
