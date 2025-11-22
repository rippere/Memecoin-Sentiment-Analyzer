"""
Memecoin Sentiment API
=======================
FastAPI backend for the dashboard
"""

import sys
from pathlib import Path
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
from datetime import datetime, timedelta
import sqlite3
import json

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

app = FastAPI(
    title="Memecoin Sentiment API",
    description="API for cryptocurrency sentiment analysis dashboard",
    version="1.0.0"
)

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
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
async def get_coins():
    """Get all tracked coins with latest data"""
    conn = get_db()
    try:
        # Get coins with latest price and sentiment
        query = """
            SELECT
                c.id, c.symbol, c.name, c.is_control, c.is_failed,
                (SELECT price_usd FROM prices WHERE coin_id = c.id ORDER BY timestamp DESC LIMIT 1) as price,
                (SELECT change_24h_pct FROM prices WHERE coin_id = c.id ORDER BY timestamp DESC LIMIT 1) as change_24h,
                (SELECT market_cap FROM prices WHERE coin_id = c.id ORDER BY timestamp DESC LIMIT 1) as market_cap,
                (SELECT volume_24h FROM prices WHERE coin_id = c.id ORDER BY timestamp DESC LIMIT 1) as volume_24h,
                (SELECT sentiment_score FROM sentiment_scores WHERE coin_id = c.id ORDER BY timestamp DESC LIMIT 1) as sentiment,
                (SELECT hype_score FROM sentiment_scores WHERE coin_id = c.id ORDER BY timestamp DESC LIMIT 1) as hype_score
            FROM coins c
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
        cursor = conn.execute(
            "SELECT * FROM coins WHERE symbol = ?", (symbol.upper(),)
        )
        coin = cursor.fetchone()

        if not coin:
            raise HTTPException(status_code=404, detail="Coin not found")

        coin_dict = dict(coin)

        # Get latest price
        cursor = conn.execute("""
            SELECT * FROM prices WHERE coin_id = ? ORDER BY timestamp DESC LIMIT 1
        """, (coin_dict['id'],))
        price = cursor.fetchone()
        if price:
            coin_dict['latest_price'] = dict(price)

        # Get latest sentiment
        cursor = conn.execute("""
            SELECT * FROM sentiment_scores WHERE coin_id = ? ORDER BY timestamp DESC LIMIT 1
        """, (coin_dict['id'],))
        sentiment = cursor.fetchone()
        if sentiment:
            coin_dict['latest_sentiment'] = dict(sentiment)

        # Get data counts
        cursor = conn.execute("""
            SELECT
                (SELECT COUNT(*) FROM prices WHERE coin_id = ?) as price_count,
                (SELECT COUNT(*) FROM reddit_posts WHERE coin_id = ?) as reddit_count,
                (SELECT COUNT(*) FROM tiktok_videos WHERE coin_id = ?) as tiktok_count,
                (SELECT COUNT(*) FROM sentiment_scores WHERE coin_id = ?) as sentiment_count
        """, (coin_dict['id'], coin_dict['id'], coin_dict['id'], coin_dict['id']))
        counts = cursor.fetchone()
        coin_dict['data_counts'] = dict(counts)

        return coin_dict
    finally:
        conn.close()


@app.get("/api/coins/{symbol}/prices")
async def get_coin_prices(
    symbol: str,
    hours: int = Query(default=24, ge=1, le=720),
    interval: str = Query(default="raw", regex="^(raw|hourly|daily)$")
):
    """Get price history for a coin"""
    conn = get_db()
    try:
        # Get coin ID
        cursor = conn.execute(
            "SELECT id FROM coins WHERE symbol = ?", (symbol.upper(),)
        )
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

        cursor = conn.execute(query, (coin['id'], since.isoformat()))
        prices = [dict(row) for row in cursor.fetchall()]

        return {
            "symbol": symbol.upper(),
            "interval": interval,
            "hours": hours,
            "data": prices,
            "count": len(prices)
        }
    finally:
        conn.close()


@app.get("/api/coins/{symbol}/sentiment")
async def get_coin_sentiment(
    symbol: str,
    hours: int = Query(default=24, ge=1, le=720),
    source: Optional[str] = Query(default=None, regex="^(reddit|tiktok)$")
):
    """Get sentiment history for a coin"""
    conn = get_db()
    try:
        cursor = conn.execute(
            "SELECT id FROM coins WHERE symbol = ?", (symbol.upper(),)
        )
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
        params = [coin['id'], since.isoformat()]

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
            "count": len(sentiment)
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
        stats['total_coins'] = cursor.fetchone()['count']

        # Record counts
        cursor = conn.execute("""
            SELECT
                (SELECT COUNT(*) FROM prices) as prices,
                (SELECT COUNT(*) FROM reddit_posts) as reddit_posts,
                (SELECT COUNT(*) FROM tiktok_videos) as tiktok_videos,
                (SELECT COUNT(*) FROM sentiment_scores) as sentiment_scores
        """)
        counts = dict(cursor.fetchone())
        stats['record_counts'] = counts

        # Average sentiment (last 24h)
        cursor = conn.execute("""
            SELECT AVG(sentiment_score) as avg_sentiment, AVG(hype_score) as avg_hype
            FROM sentiment_scores
            WHERE timestamp >= datetime('now', '-24 hours')
        """)
        row = cursor.fetchone()
        stats['avg_sentiment_24h'] = row['avg_sentiment']
        stats['avg_hype_24h'] = row['avg_hype']

        # Date range
        cursor = conn.execute("""
            SELECT MIN(timestamp) as earliest, MAX(timestamp) as latest
            FROM prices
        """)
        row = cursor.fetchone()
        stats['date_range'] = {
            'earliest': row['earliest'],
            'latest': row['latest']
        }

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

        return {
            "gainers": gainers,
            "losers": losers
        }
    finally:
        conn.close()


# ==================== EVENTS ====================

@app.get("/api/events")
async def get_events(
    coin: Optional[str] = None,
    limit: int = Query(default=20, ge=1, le=100)
):
    """Get logged events"""
    events_path = Path(__file__).parent.parent / "events" / "events.json"

    if not events_path.exists():
        return {"events": [], "count": 0}

    with open(events_path, 'r') as f:
        events = json.load(f)

    if coin:
        events = [e for e in events if e['coin_symbol'] == coin.upper() or e['coin_symbol'] == 'ALL']

    # Sort by timestamp descending
    events = sorted(events, key=lambda x: x['timestamp'], reverse=True)[:limit]

    return {"events": events, "count": len(events)}


@app.post("/api/events")
async def create_event(
    coin_symbol: str,
    category: str,
    description: str,
    sentiment: str = "neutral",
    impact_score: float = 5.0,
    source: Optional[str] = None,
    url: Optional[str] = None
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
        url=url
    )

    return {"success": True, "event": event}


# ==================== HEALTH ====================

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "database": str(DB_PATH),
        "timestamp": datetime.utcnow().isoformat()
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
